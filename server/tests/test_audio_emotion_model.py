from pathlib import Path

from app.ml.audio_emotion import AudioEmotionConfig, AudioEmotionModel


def test_audio_model_uses_local_checkpoint_first(monkeypatch, tmp_path: Path) -> None:
    config = AudioEmotionConfig(
        whisper_model="whisper-test",
        emotion_model="hf-fallback",
        emotion_model_path=str(tmp_path),
    )
    model = AudioEmotionModel(config)

    calls: list[str] = []

    def fake_whisper_model() -> None:
        calls.append("whisper")

    def fake_local_tone_model(model_dir: Path) -> None:
        calls.append(f"local:{model_dir}")
        model._tone_backend = "local"
        model._tone_model_name = "local:audio_bilstm_checkpoint.keras"

    def fake_hf_tone_model() -> None:
        calls.append("huggingface")

    monkeypatch.setattr(model, "_load_whisper_model", fake_whisper_model)
    monkeypatch.setattr(model, "_load_local_tone_model", fake_local_tone_model)
    monkeypatch.setattr(model, "_load_hf_tone_model", fake_hf_tone_model)

    model.load_model()

    assert calls == ["whisper", f"local:{tmp_path}"]
    assert model.is_initialized()
    assert model._tone_backend == "local"
    assert model._tone_model_name == "local:audio_bilstm_checkpoint.keras"
