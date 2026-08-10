"""FastAPI dependency providers - the wiring between routers and services.

Routers depend only on these functions; they never import service
constructors or ML model classes directly. This is the seam that lets
tests substitute fakes for the DB session or model registry.
"""

from functools import lru_cache

from app.core.config import Settings, settings
from app.ml.registry import ModelRegistry, get_model_registry
from app.services.analysis_repository import AnalysisRepository
from app.services.audio_service import AudioEmotionService
from app.services.fusion_service import FusionService
from app.services.text_service import TextEmotionService
from app.services.video_service import VideoEmotionService


def get_settings() -> Settings:
    return settings


def get_registry() -> ModelRegistry:
    return get_model_registry(settings)


@lru_cache
def get_repository() -> AnalysisRepository:
    return AnalysisRepository()


@lru_cache
def get_fusion_service() -> FusionService:
    return FusionService(get_registry().fusion)


@lru_cache
def get_text_service() -> TextEmotionService:
    return TextEmotionService(get_registry().text, get_repository())


@lru_cache
def get_fusion_text_service() -> TextEmotionService:
    return TextEmotionService(get_registry().fusion_text, get_repository())


@lru_cache
def get_audio_service() -> AudioEmotionService:
    return AudioEmotionService(
        get_registry().audio,
        get_fusion_text_service(),
        get_fusion_service(),
        get_repository(),
        settings,
    )


@lru_cache
def get_video_service() -> VideoEmotionService:
    return VideoEmotionService(
        get_registry().facial,
        get_audio_service(),
        get_fusion_service(),
        get_repository(),
        settings,
    )
