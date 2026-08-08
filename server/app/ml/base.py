"""Model Service Layer - base interfaces shared by every emotion model.

All concrete models (text/audio/facial) implement this interface so the
service layer and fusion engine can treat them interchangeably, and so
any model can be swapped out via configuration without touching callers.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel

from app.schemas.common import EmotionPrediction

logger = logging.getLogger(__name__)

__all__ = ["EmotionPrediction", "ModelConfig", "BaseModelService"]


class ModelConfig(BaseModel):
    """Configuration for a single model."""

    model_name: str
    model_path: Optional[str] = None
    device: str = "cpu"
    batch_size: int = 1
    enabled: bool = True


class BaseModelService(ABC):
    """Abstract base class for all emotion model services."""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None
        self._initialized = False

    @abstractmethod
    def load_model(self) -> None:
        """Load the model into memory. Should be idempotent."""

    @abstractmethod
    def predict(self, input_data: Any) -> EmotionPrediction:
        """Run inference on model-specific input and return a standardized prediction."""

    @abstractmethod
    def preprocess(self, raw_input: Any) -> Any:
        """Transform raw input into model-compatible tensors/arrays."""

    def ensure_loaded(self) -> None:
        """Lazily load the model on first use, logging load latency."""
        if self._initialized:
            return
        logger.info("model.load.start", extra={"model": self.config.model_name})
        self.load_model()
        logger.info(
            "model.load.complete",
            extra={"model": self.config.model_name, "device": self.config.device},
        )

    def is_initialized(self) -> bool:
        return self._initialized

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": self.config.model_name,
            "device": self.config.device,
            "initialized": self._initialized,
        }
