"""SQLAlchemy ORM models — the persistence tier.

Schema mirrors the previous Supabase design (see the now-removed
`supabase/migrations` folder) minus anything Supabase-specific: no
`auth.uid()` Row Level Security policies, no `users`/`uploads` tables tied
to Supabase Auth. Access control, if ever required again, belongs in the
service/API layer, not the database layer.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Analysis(Base):
    """Top-level record for a single analysis request, any modality."""

    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    modality: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    input_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_emotion: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    fusion_weights: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    fusion_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    text_result: Mapped["TextResult"] = relationship(
        back_populates="analysis", uselist=False, cascade="all, delete-orphan"
    )
    audio_result: Mapped["AudioResult"] = relationship(
        back_populates="analysis", uselist=False, cascade="all, delete-orphan"
    )
    video_result: Mapped["VideoResult"] = relationship(
        back_populates="analysis", uselist=False, cascade="all, delete-orphan"
    )


class TextResult(Base):
    """Detailed result of the text-modality pipeline."""

    __tablename__ = "text_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    emotion: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    probabilities: Mapped[dict[str, float]] = mapped_column(JSONB, nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    inference_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    analysis: Mapped[Analysis] = relationship(back_populates="text_result")


class AudioResult(Base):
    """Detailed result of the audio-modality pipeline (tone + transcript cascade)."""

    __tablename__ = "audio_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript_emotion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    transcript_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    tone_emotion: Mapped[str] = mapped_column(String(50), nullable=False)
    tone_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    tone_probabilities: Mapped[dict[str, float]] = mapped_column(JSONB, nullable=False)
    audio_duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    inference_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    analysis: Mapped[Analysis] = relationship(back_populates="audio_result")


class VideoResult(Base):
    """Detailed result of the video-modality pipeline (facial + audio + text cascade)."""

    __tablename__ = "video_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    facial_emotion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    facial_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    facial_probabilities: Mapped[dict[str, float] | None] = mapped_column(
        JSONB, nullable=True
    )
    audio_emotion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    audio_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    text_emotion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    text_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    frame_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frame_emotions: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSONB, nullable=True
    )
    audio_duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    inference_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    analysis: Mapped[Analysis] = relationship(back_populates="video_result")
