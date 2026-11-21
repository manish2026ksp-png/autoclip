"""Transcription must use only explicitly installed local model files."""

from __future__ import annotations

import importlib
import sys
import types

from autoclip import models
from autoclip.config import WhisperSettings


def test_transcription_loads_selected_model_without_network(tmp_path, monkeypatch) -> None:
    transcribe_module = importlib.import_module("autoclip.pipeline.transcribe")
    cache_root = tmp_path / "models" / "whisper"
    calls = []

    class FakeWhisperModel:
        def __init__(self, model_name, **kwargs):
            calls.append((model_name, kwargs))

        def transcribe(self, audio, **kwargs):
            word = types.SimpleNamespace(word=" hello", start=0.0, end=0.5)
            segment = types.SimpleNamespace(text="hello", start=0.0, end=0.5, words=[word])
            info = types.SimpleNamespace(duration=0.5, language="en")
            return iter([segment]), info

    monkeypatch.setattr(models, "whisper_models_dir", lambda: cache_root)
    monkeypatch.setattr(transcribe_module, "resolve_compute", lambda settings: ("cpu", "int8"))
    monkeypatch.setattr("autoclip.cuda.ensure_cuda_libraries", lambda: None)
    monkeypatch.setitem(
        sys.modules,
        "faster_whisper",
        types.SimpleNamespace(WhisperModel=FakeWhisperModel),
    )

    transcript = transcribe_module.transcribe(
        tmp_path / "sample.wav",
        WhisperSettings(model="tiny", language="en"),
    )

    assert len(calls) == 1
    assert calls[0][0] == "tiny"
    assert calls[0][1]["download_root"] == str(cache_root)
    assert calls[0][1]["local_files_only"] is True
    assert transcript.words[0].text == "hello"


def test_missing_whisper_model_gives_explicit_download_guidance(tmp_path, monkeypatch) -> None:
    transcribe_module = importlib.import_module("autoclip.pipeline.transcribe")

    class MissingWhisperModel:
        def __init__(self, model_name, **kwargs):
            raise RuntimeError(
                f"Model {model_name!r} not found in local cache (local_files_only=True)"
            )

    monkeypatch.setattr(models, "whisper_models_dir", lambda: tmp_path / "models" / "whisper")
    monkeypatch.setattr(transcribe_module, "resolve_compute", lambda settings: ("cpu", "int8"))
    monkeypatch.setattr("autoclip.cuda.ensure_cuda_libraries", lambda: None)
    monkeypatch.setitem(
        sys.modules,
        "faster_whisper",
        types.SimpleNamespace(WhisperModel=MissingWhisperModel),
    )

    try:
        transcribe_module.transcribe(
            tmp_path / "sample.wav",
            WhisperSettings(model="tiny", language="hi"),
        )
    except transcribe_module.TranscriptionError as exc:
        assert "not installed in the local cache" in str(exc)
        assert "explicitly download this model" in str(exc)
        assert "never downloads models automatically" in str(exc)
    else:
        raise AssertionError("missing local model should fail with actionable guidance")
