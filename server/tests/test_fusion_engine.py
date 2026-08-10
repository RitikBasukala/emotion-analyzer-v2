import pytest

from app.ml.fusion import FusionConfig, FusionEngine
from app.schemas.common import EmotionPrediction


def _prediction(emotion: str, probabilities: dict[str, float]) -> EmotionPrediction:
    confidence = probabilities[emotion]
    return EmotionPrediction(
        emotion=emotion,
        confidence=confidence,
        probabilities=probabilities,
    )


def test_cross_attention_uses_gated_fusion_path() -> None:
    engine = FusionEngine(
        FusionConfig(fusion_method="cross_attention", mid_late_blend=1.0)
    )

    output = engine.fuse(
        text_prediction=_prediction(
            "Happy",
            {
                "Happy": 0.70,
                "Sad": 0.10,
                "Angry": 0.05,
                "Fear": 0.05,
                "Surprise": 0.05,
                "Disgust": 0.03,
                "Neutral": 0.02,
            },
        ),
        audio_prediction=_prediction(
            "Sad",
            {
                "Happy": 0.08,
                "Sad": 0.62,
                "Angry": 0.08,
                "Fear": 0.06,
                "Surprise": 0.06,
                "Disgust": 0.05,
                "Neutral": 0.05,
            },
        ),
        facial_prediction=_prediction(
            "Neutral",
            {
                "Happy": 0.12,
                "Sad": 0.08,
                "Angry": 0.08,
                "Fear": 0.07,
                "Surprise": 0.07,
                "Disgust": 0.08,
                "Neutral": 0.50,
            },
        ),
    )

    assert output.fusion_method == "cross_attention"
    assert output.final_probabilities.keys() == output.mid_fusion_probabilities.keys()
    for label, probability in output.mid_fusion_probabilities.items():
        assert output.final_probabilities[label] == pytest.approx(probability)


def test_cross_attention_output_remains_normalized() -> None:
    engine = FusionEngine(FusionConfig(fusion_method="cross_attention"))

    output = engine.fuse(
        text_prediction=_prediction(
            "Neutral",
            {
                "Happy": 0.10,
                "Sad": 0.10,
                "Angry": 0.10,
                "Fear": 0.10,
                "Surprise": 0.10,
                "Disgust": 0.10,
                "Neutral": 0.40,
            },
        )
    )

    assert sum(output.mid_fusion_probabilities.values()) == pytest.approx(1.0)
    assert sum(output.final_probabilities.values()) == pytest.approx(1.0)
