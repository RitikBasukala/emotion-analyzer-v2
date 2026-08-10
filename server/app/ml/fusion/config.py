"""Configuration for the multi-tier fusion engine."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FusionConfig:
    """Fusion engine configuration for combining modalities.

    `text_weight` + `audio_weight` + `facial_weight` must sum to 1.0 — this
    is enforced centrally by `app.core.config.Settings`.
    """

    text_weight: float = 0.30
    audio_weight: float = 0.30
    facial_weight: float = 0.40

    # "weighted_average" (late fusion only), "cross_attention" (gated
    # cross-modal fusion blended with late fusion), or "multi_tier"
    # (compatibility alias for the cross-attention path).
    fusion_method: str = "cross_attention"

    # When fusion_method == "multi_tier", this controls how much weight the
    # gated mid-level fusion tier gets vs. the late (soft-voting) tier when
    # they're blended into the final decision. 0.5 = equal blend.
    mid_late_blend: float = 0.5
