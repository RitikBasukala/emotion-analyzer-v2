"""Configuration for the text emotion model.

This is a plain, non-environment-parsing config object. It is constructed
from the central `app.core.config.Settings` instance (single source of
environment truth) rather than reading `os.environ` itself.
"""

from dataclasses import dataclass, field
from typing import Dict, Literal, Optional


@dataclass(frozen=True)
class TextEmotionConfig:
    """Text emotion model configuration."""

    model_path: str
    device: str = "cpu"
    max_length: int = 512
    enabled: bool = True
    output_mode: Literal["fine27", "coarse7"] = "fine27"

    # The local checkpoint is a BERT model fine-tuned on GoEmotions (28
    # labels, softmax activation). `fine27` returns the 27 non-neutral
    # emotions for direct text analysis. `coarse7` aggregates the same
    # checkpoint down to the 7 shared emotion classes used by fusion.
    goemotions_to_coarse: Dict[str, str] = field(
        default_factory=lambda: {
            "admiration": "Happy",
            "amusement": "Happy",
            "joy": "Happy",
            "excitement": "Happy",
            "love": "Happy",
            "optimism": "Happy",
            "pride": "Happy",
            "relief": "Happy",
            "gratitude": "Happy",
            "approval": "Happy",
            "caring": "Happy",
            "desire": "Happy",
            "sadness": "Sad",
            "grief": "Sad",
            "disappointment": "Sad",
            "remorse": "Sad",
            "embarrassment": "Sad",
            "anger": "Angry",
            "annoyance": "Angry",
            "disapproval": "Angry",
            "fear": "Fear",
            "nervousness": "Fear",
            "surprise": "Surprise",
            "realization": "Surprise",
            "curiosity": "Surprise",
            "confusion": "Surprise",
            "disgust": "Disgust",
            "neutral": "Neutral",
        }
    )
    optional_model_name: Optional[str] = None
