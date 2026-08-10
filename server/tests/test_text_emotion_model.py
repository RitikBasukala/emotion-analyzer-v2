import numpy as np
import pytest

from app.ml.text_emotion.config import TextEmotionConfig
from app.ml.text_emotion.model import TextEmotionModel


def test_assert_softmax_outputs_accepts_normalized_distribution() -> None:
    probs = np.array([0.2, 0.3, 0.5], dtype=np.float32)

    TextEmotionModel._assert_softmax_outputs(probs)


def test_assert_softmax_outputs_rejects_non_normalized_distribution() -> None:
    probs = np.array([0.2, 0.3, 0.4], dtype=np.float32)

    with pytest.raises(AssertionError, match="Expected softmax probabilities"):
        TextEmotionModel._assert_softmax_outputs(probs)


class _DummyTextModel:
    def __init__(self) -> None:
        self.config = type(
            "Config",
            (),
            {
                "id2label": {
                    0: "admiration",
                    1: "amusement",
                    2: "anger",
                    3: "neutral",
                }
            },
        )()


def test_fine27_distribution_excludes_neutral_and_normalizes() -> None:
    model = TextEmotionModel(
        TextEmotionConfig(model_path="/tmp/model", output_mode="fine27")
    )
    model.model = _DummyTextModel()

    probs = np.array([0.2, 0.3, 0.4, 0.1], dtype=np.float32)
    distribution = model._fine27_distribution(probs)

    assert "neutral" not in distribution
    assert distribution == {
        "admiration": pytest.approx(0.2 / 0.9),
        "amusement": pytest.approx(0.3 / 0.9),
        "anger": pytest.approx(0.4 / 0.9),
    }


def test_coarse7_distribution_normalizes_to_seven_labels() -> None:
    model = TextEmotionModel(
        TextEmotionConfig(model_path="/tmp/model", output_mode="coarse7")
    )
    model.model = _DummyTextModel()

    probs = np.array([0.2, 0.3, 0.4, 0.1], dtype=np.float32)
    distribution = model._aggregate_to_coarse(probs)

    assert set(distribution) == {
        "Happy",
        "Sad",
        "Angry",
        "Fear",
        "Surprise",
        "Disgust",
        "Neutral",
    }
    assert sum(distribution.values()) == pytest.approx(1.0)
