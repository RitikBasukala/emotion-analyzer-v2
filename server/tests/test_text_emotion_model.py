import numpy as np
import pytest

from app.ml.text_emotion.model import TextEmotionModel


def test_assert_softmax_outputs_accepts_normalized_distribution() -> None:
    probs = np.array([0.2, 0.3, 0.5], dtype=np.float32)

    TextEmotionModel._assert_softmax_outputs(probs)


def test_assert_softmax_outputs_rejects_non_normalized_distribution() -> None:
    probs = np.array([0.2, 0.3, 0.4], dtype=np.float32)

    with pytest.raises(AssertionError, match="Expected softmax probabilities"):
        TextEmotionModel._assert_softmax_outputs(probs)
