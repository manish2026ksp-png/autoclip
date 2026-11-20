"""Model installation must never trigger implicit downloads."""
from __future__ import annotations

import pytest

from autoclip import models


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
