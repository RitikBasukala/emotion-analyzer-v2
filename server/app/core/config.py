"""Centralized application configuration.

This is the single source of truth for environment-driven configuration.
Every other module (database engine, ML model configs, fusion engine,
CORS, logging) derives its settings from this module instead of reading
`os.environ` directly. This keeps configuration parsing decoupled from
business/domain logic, per the project's Separation of Concerns rules.
"""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> backend/
BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Strictly typed environment configuration.

    Values are loaded from a `.env` file (backend/.env, falling back to the
    repository root `.env`) and/or real environment variables. Docker
    Compose and the FastAPI app read from the same variable names so a
    single `.env` file can drive both.
    """

    model_config = SettingsConfigDict(
        env_file=(
            str(BACKEND_ROOT / ".env"),
            str(BACKEND_ROOT.parent / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    app_name: str = "Multimodal Emotion Recognition API"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # ------------------------------------------------------------------
    # PostgreSQL (async via asyncpg) - banned: Supabase
    # ------------------------------------------------------------------
    postgres_user: str = "emotion_ai"
    postgres_password: str = "change_me_in_production"
    postgres_db: str = "emotion_recognition"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # ------------------------------------------------------------------
    # ML / device configuration
    # ------------------------------------------------------------------
    device: str = "cpu"
    preload_models: bool = False

    # Text emotion model (local safetensors checkpoint)
    text_model_dir: str = "app/ml/text_emotion/text_model"
    text_model_max_length: int = 512

    # Audio emotion model (transcription + acoustic tone)
    audio_whisper_model: str = "openai/whisper-base"
    audio_emotion_model: str = "audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim"
    audio_sample_rate: int = 16000
    audio_max_length_seconds: float = 30.0

    # Facial / video emotion model
    facial_detector_backend: str = "opencv"
    facial_frame_extraction_fps: int = 2
    facial_max_frames: int = 30

    # ------------------------------------------------------------------
    # Fusion engine weights (must sum to 1.0)
    # ------------------------------------------------------------------
    fusion_text_weight: float = 0.30
    fusion_audio_weight: float = 0.30
    fusion_facial_weight: float = 0.40
    fusion_method: str = "weighted_average"
    fusion_mid_late_blend: float = 0.5

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 100

    @field_validator("fusion_facial_weight")
    @classmethod
    def _validate_weights_sum(cls, v: float, info) -> float:
        data = info.data
        text_w = data.get("fusion_text_weight", 0.30)
        audio_w = data.get("fusion_audio_weight", 0.30)
        total = text_w + audio_w + v
        if abs(total - 1.0) > 0.01:
            raise ValueError(
                f"fusion weights must sum to 1.0 (got {total:.3f}); "
                "check FUSION_TEXT_WEIGHT / FUSION_AUDIO_WEIGHT / FUSION_FACIAL_WEIGHT"
            )
        return v

    @property
    def database_url(self) -> str:
        """Async SQLAlchemy DSN using the asyncpg driver."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_origin_list(self) -> List[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def text_model_path(self) -> Path:
        path = Path(self.text_model_dir)
        if not path.is_absolute():
            path = BACKEND_ROOT / path
        return path

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        if not path.is_absolute():
            path = BACKEND_ROOT / path
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor so `.env` is parsed exactly once."""
    return Settings()


settings = get_settings()
