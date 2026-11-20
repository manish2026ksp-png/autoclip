"""Explicit download and local caching of ML model bundles.

Model files live outside the repository. Inference must only use files already
installed by an explicit user action; this module never downloads implicitly.
"""

from __future__ import annotations

import logging
import shutil
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from . import paths

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ModelSpec:
    key: str
    filename: str
    url: str
    description: str
    approx_bytes: int


MODELS: dict[str, ModelSpec] = {
    "face_landmarker": ModelSpec(
        key="face_landmarker",
        filename="face_landmarker.task",
        url=(
            "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
            "face_landmarker/float16/1/face_landmarker.task"
        ),
        description="MediaPipe face landmarks — face tracking and mouth movement",
        approx_bytes=3_758_596,
    ),
}


class ModelDownloadError(RuntimeError):
    """A model bundle could not be fetched."""


def models_dir() -> Path:
    return paths.root() / "models"


def model_path(key: str) -> Path:
    spec = _spec(key)
    return models_dir() / spec.filename


def whisper_models_dir() -> Path:
    """Dedicated Hugging Face cache root for faster-whisper weights."""
    return models_dir() / "whisper"


def is_available(key: str) -> bool:
    path = model_path(key)
    return path.exists() and path.stat().st_size > 0


def ensure(key: str) -> Path:
    """Return an installed model path; never access the network implicitly."""
    _spec(key)  # Validate the model key before checking its installed state.
    destination = model_path(key)
    if destination.exists() and destination.stat().st_size > 0:
        return destination
    raise ModelDownloadError(
        f"The {key} model is not installed. Download it explicitly from Settings first. "
        f"Expected location: {destination}"
    )


def download(key: str, *, timeout: float = 120.0) -> Path:
    """Download a model only when called by an explicit user-requested action."""
    spec = _spec(key)
    destination = model_path(key)
    if destination.exists() and destination.stat().st_size > 0:
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    log.info("Downloading %s (~%.1f MB)...", spec.filename, spec.approx_bytes / 1_048_576)

    # Download to a temp file and move into place, so an interrupted fetch can
    # never leave a truncated model that then fails cryptically at inference.
    temporary = destination.with_suffix(destination.suffix + ".part")
    try:
        with (
            urllib.request.urlopen(spec.url, timeout=timeout) as response,  # noqa: S310
            temporary.open("wb") as handle,
        ):
            shutil.copyfileobj(response, handle)
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        temporary.unlink(missing_ok=True)
        raise ModelDownloadError(
            f"Could not download the {spec.key} model.\n"
            f"URL: {spec.url}\n"
            f"Error: {exc}\n\n"
            f"If this machine has no internet access, download the file manually "
            f"and place it at {destination}."
        ) from exc

    if temporary.stat().st_size == 0:
        temporary.unlink(missing_ok=True)
        raise ModelDownloadError(f"The downloaded {spec.key} model was empty.")

    temporary.replace(destination)
    log.info("Saved %s", destination)
    return destination


def _spec(key: str) -> ModelSpec:
    spec = MODELS.get(key)
    if spec is None:
        raise ModelDownloadError(f"Unknown model {key!r}. Available: {', '.join(MODELS)}")
    return spec
