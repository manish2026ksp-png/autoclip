"""Model installation must never trigger implicit downloads."""

from __future__ import annotations

from io import BytesIO

import pytest
from autoclip import models


class _FakeResponse(BytesIO):
    def __init__(self, payload: bytes, content_length: int | None = None) -> None:
        super().__init__(payload)
        self.headers = {}
        if content_length is not None:
            self.headers["Content-Length"] = str(content_length)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def test_missing_model_is_not_downloaded_implicitly(autoclip_home, monkeypatch) -> None:
    def unexpected_network(*args, **kwargs):
        raise AssertionError("ensure() must never access the network")

    monkeypatch.setattr(models.urllib.request, "urlopen", unexpected_network)

    with pytest.raises(models.ModelDownloadError, match="Download it explicitly"):
        models.ensure("face_landmarker")


def test_installed_model_is_returned_without_network(autoclip_home) -> None:
    destination = models.model_path("face_landmarker")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(b"local-model")

    assert models.ensure("face_landmarker") == destination


def test_download_installs_only_after_complete_transfer(autoclip_home, monkeypatch) -> None:
    payload = b"complete-model-payload"
    monkeypatch.setattr(
        models.urllib.request,
        "urlopen",
        lambda *args, **kwargs: _FakeResponse(payload, len(payload)),
    )

    destination = models.download("face_landmarker")

    assert destination.read_bytes() == payload
    assert not destination.with_suffix(destination.suffix + ".part").exists()


def test_download_rejects_content_length_mismatch_and_cleans_partial_file(
    autoclip_home, monkeypatch
) -> None:
    payload = b"truncated"
    monkeypatch.setattr(
        models.urllib.request,
        "urlopen",
        lambda *args, **kwargs: _FakeResponse(payload, len(payload) + 10),
    )

    with pytest.raises(models.ModelDownloadError, match="download was incomplete"):
        models.download("face_landmarker")

    destination = models.model_path("face_landmarker")
    assert not destination.exists()
    assert not destination.with_suffix(destination.suffix + ".part").exists()


def test_download_cleans_partial_file_after_network_error(autoclip_home, monkeypatch) -> None:
    class InterruptedResponse(_FakeResponse):
        def read(self, size: int = -1) -> bytes:
            if self.tell() > 0:
                raise OSError("connection interrupted")
            return super().read(4)

    monkeypatch.setattr(
        models.urllib.request,
        "urlopen",
        lambda *args, **kwargs: InterruptedResponse(b"partial-model", 100),
    )

    with pytest.raises(models.ModelDownloadError, match="Could not download"):
        models.download("face_landmarker")

    destination = models.model_path("face_landmarker")
    assert not destination.exists()
    assert not destination.with_suffix(destination.suffix + ".part").exists()
