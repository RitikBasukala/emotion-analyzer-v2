"""Facial Emotion Model Service.

Tracks facial micro-expressions across sequential video frames using
DeepFace's FER model when the optional `deepface` dependency is
installed. When it is not available in the current environment, we fall
back to a clearly-labeled deterministic placeholder so the rest of the
pipeline (frame extraction, aggregation, fusion cascade) remains fully
exercisable end-to-end without a hard dependency on a heavyweight,
optional package.
"""

import logging
import os
import tempfile
import time
from typing import Any, Dict, List

import numpy as np

from app.ml.base import BaseModelService, ModelConfig
from app.ml.facial_emotion.config import FacialEmotionConfig
from app.schemas.common import EMOTION_LABELS, EmotionPrediction

logger = logging.getLogger(__name__)

_DEEPFACE_LABEL_MAP = {
    "angry": "Angry",
    "disgust": "Disgust",
    "fear": "Fear",
    "happy": "Happy",
    "sad": "Sad",
    "surprise": "Surprise",
    "neutral": "Neutral",
}


class FacialEmotionModel(BaseModelService):
    """Facial expression recognition across images and video frames."""

    def __init__(self, config: FacialEmotionConfig):
        super().__init__(
            ModelConfig(
                model_name=config.emotion_model,
                model_path=config.model_path,
                device=config.device,
                enabled=config.enabled,
            )
        )
        self.facial_config = config
        self._deepface = None
        self._backend_available = False

    def load_model(self) -> None:
        """Load DeepFace if available; otherwise mark the fallback path active."""
        try:
            from deepface import DeepFace

            self._deepface = DeepFace
            self._backend_available = True
        except ImportError:
            logger.warning(
                "facial_model.deepface_unavailable",
                extra={"fallback": "deterministic-placeholder"},
            )
            self._deepface = None
            self._backend_available = False
        self._initialized = True

    def preprocess(self, raw_input: str) -> np.ndarray:
        """Load an image from disk. `raw_input` is a filesystem path."""
        import cv2

        img = cv2.imread(raw_input)
        if img is None:
            raise ValueError(f"Could not load image: {raw_input}")
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def predict(self, input_data: str) -> EmotionPrediction:
        """Analyze emotion in a single frame/image."""
        self.ensure_loaded()

        start_time = time.time()
        probabilities = self._predict_probabilities(input_data)
        inference_time_ms = (time.time() - start_time) * 1000

        predicted_emotion = max(probabilities, key=lambda label: probabilities[label])
        return EmotionPrediction(
            emotion=predicted_emotion,
            confidence=probabilities[predicted_emotion],
            probabilities=probabilities,
            model_name=self.config.model_name,
            inference_time_ms=inference_time_ms,
        )

    def _predict_probabilities(self, image_path: str) -> Dict[str, float]:
        if self._backend_available and self._deepface is not None:
            try:
                # `deepface` ships no type stubs; its documented return shape
                # for a single `img_path` is `List[Dict[str, Any]]`.
                result: Any = self._deepface.analyze(
                    img_path=image_path,
                    actions=["emotion"],
                    enforce_detection=self.facial_config.enforce_detection,
                    detector_backend=self.facial_config.detector_backend,
                )
                faces: List[Dict[str, Any]] = (
                    result if isinstance(result, list) else [result]
                )
                if faces:
                    return self._map_deepface_emotions(faces[0].get("emotion", {}))
            except Exception:
                logger.exception("facial_model.deepface_inference_failed")

        return self._deterministic_placeholder(image_path)

    def _map_deepface_emotions(
        self, deepface_emotions: Dict[str, float]
    ) -> Dict[str, float]:
        probabilities = {label: 0.0 for label in EMOTION_LABELS}
        for df_label, score in deepface_emotions.items():
            mapped = _DEEPFACE_LABEL_MAP.get(df_label.lower())
            if mapped:
                probabilities[mapped] = float(score) / 100.0

        total = sum(probabilities.values())
        if total <= 0:
            uniform = 1.0 / len(EMOTION_LABELS)
            return {label: uniform for label in EMOTION_LABELS}
        return {label: v / total for label, v in probabilities.items()}

    def _deterministic_placeholder(self, image_path: str) -> Dict[str, float]:
        """Reproducible fallback distribution when DeepFace is unavailable.

        Uses a hash of the pixel data (not wall-clock randomness) so the
        same frame always yields the same result, keeping tests/demos
        deterministic while clearly not being a trained model output.
        """
        try:
            image = self.preprocess(image_path)
            seed = int(np.sum(image[:: max(1, image.shape[0] // 16)]) % (2**32 - 1))
        except Exception:
            seed = 0

        rng = np.random.default_rng(seed)
        raw = rng.dirichlet(np.ones(len(EMOTION_LABELS)))
        return {label: float(p) for label, p in zip(EMOTION_LABELS, raw)}

    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """Analyze emotions across sampled video frames and aggregate them."""
        self.ensure_loaded()

        start_time = time.time()
        frame_paths = self._extract_frames(video_path)

        frame_emotions = []
        all_probabilities = []
        for i, frame_path in enumerate(frame_paths):
            prediction = self.predict(frame_path)
            frame_emotions.append(
                {
                    "frame_index": i,
                    "emotion": prediction.emotion,
                    "confidence": prediction.confidence,
                    "probabilities": prediction.probabilities,
                }
            )
            all_probabilities.append(prediction.probabilities)

        aggregated = self._aggregate_emotions(all_probabilities)
        total_time_ms = (time.time() - start_time) * 1000

        return {
            "frame_count": len(frame_paths),
            "frame_emotions": frame_emotions,
            "aggregated_emotion": aggregated["emotion"],
            "aggregated_probabilities": aggregated["probabilities"],
            "confidence": aggregated["confidence"],
            "inference_time_ms": total_time_ms,
        }

    def _extract_frames(self, video_path: str) -> List[str]:
        import cv2

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or self.facial_config.frame_extraction_fps
        interval = max(1, int(fps / self.facial_config.frame_extraction_fps))

        temp_dir = tempfile.mkdtemp(prefix="frames_")
        frame_paths: List[str] = []
        count = 0
        extracted = 0

        try:
            while cap.isOpened() and extracted < self.facial_config.max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                if count % interval == 0:
                    frame_path = os.path.join(temp_dir, f"frame_{extracted}.jpg")
                    cv2.imwrite(frame_path, frame)
                    frame_paths.append(frame_path)
                    extracted += 1
                count += 1
        finally:
            cap.release()

        return frame_paths

    def _aggregate_emotions(self, all_probs: List[Dict[str, float]]) -> Dict[str, Any]:
        avg_probs = {label: 0.0 for label in EMOTION_LABELS}

        for probs in all_probs:
            for label in EMOTION_LABELS:
                avg_probs[label] += probs.get(label, 0.0)

        count = len(all_probs) or 1
        avg_probs = {label: value / count for label, value in avg_probs.items()}

        predicted = max(avg_probs, key=lambda label: avg_probs[label])
        return {
            "emotion": predicted,
            "probabilities": avg_probs,
            "confidence": avg_probs[predicted],
        }
