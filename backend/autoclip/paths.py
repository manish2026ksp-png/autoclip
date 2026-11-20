"""Filesystem layout and independently configurable storage roots.

All paths default beneath ~/.autoclip (or AUTOCLIP_HOME), preserving existing
installations. Optional environment overrides let users place large media,
model and temporary data on another drive without moving app state.
"""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path

log = logging.getLogger(__name__)

ENV_HOME = "AUTOCLIP_HOME"
ENV_MEDIA = "AUTOCLIP_MEDIA_DIR"
ENV_WORK = "AUTOCLIP_WORK_DIR"
ENV_EXPORTS = "AUTOCLIP_EXPORTS_DIR"
ENV_MODELS = "AUTOCLIP_MODELS_DIR"
ENV_TEMP = "AUTOCLIP_TEMP_DIR"

DEFAULT_DIR_NAME = ".autoclip"
LEGACY_DIR_NAME = ".clipforge"
DB_NAME = "autoclip.db"
LEGACY_DB_NAME = "clipforge.db"


def _configured_path(variable: str, fallback: Path) -> Path:
    """Resolve an optional absolute path override."""
    value = os.environ.get(variable)
    if not value:
        return fallback.resolve()
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        raise ValueError(f"{variable} must be an absolute path, got: {value!r}")
    return candidate.resolve()


def root() -> Path:
    """Return app state root, retaining legacy-directory adoption."""
    override = os.environ.get(ENV_HOME)
    if override:
        return _configured_path(ENV_HOME, Path(override))
    default = Path.home() / DEFAULT_DIR_NAME
    if not default.exists():
        legacy = Path.home() / LEGACY_DIR_NAME
        if legacy.is_dir():
            log.info("Using legacy data directory %s.", legacy)
            return legacy.resolve()
    return default.resolve()


def media_dir() -> Path:
    return _configured_path(ENV_MEDIA, root() / "media")


def work_dir() -> Path:
    return _configured_path(ENV_WORK, root() / "work")


def exports_dir() -> Path:
    return _configured_path(ENV_EXPORTS, root() / "exports")


def models_dir() -> Path:
    return _configured_path(ENV_MODELS, root() / "models")


def temp_dir() -> Path:
    return _configured_path(ENV_TEMP, root() / "tmp")


def cache_dir() -> Path:
    """Library cache root beneath the configurable temp directory."""
    return temp_dir() / "cache"


def db_path() -> Path:
    """Return SQLite path, adopting a legacy filename in place."""
    base = root()
    current = base / DB_NAME
    if not current.exists():
        legacy = base / LEGACY_DB_NAME
        if legacy.is_file():
            return legacy
    return current


def config_path() -> Path:
    return root() / "config.json"


def job_work_dir(job_id: str) -> Path:
    return work_dir() / job_id


def source_media_dir(source_id: str) -> Path:
    return media_dir() / source_id


def configure_cache_environment() -> None:
    """Redirect common library caches before ML libraries are imported."""
    cache = cache_dir()
    os.environ.setdefault("HF_HOME", str(cache / "huggingface"))
    os.environ.setdefault("HF_HUB_CACHE", str(cache / "huggingface" / "hub"))
    os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(cache / "huggingface" / "hub"))
    os.environ.setdefault("TORCH_HOME", str(cache / "torch"))
    os.environ.setdefault("XDG_CACHE_HOME", str(cache))
    temporary = temp_dir()
    os.environ.setdefault("TMP", str(temporary))
    os.environ.setdefault("TEMP", str(temporary))
    os.environ.setdefault("TMPDIR", str(temporary))
    tempfile.tempdir = os.environ.get("TMP") or os.environ.get("TEMP")


def ensure_layout() -> Path:
    """Create all configured storage directories; safe to call repeatedly."""
    base = root()
    for directory in (base, media_dir(), work_dir(), exports_dir(), models_dir(), temp_dir()):
        directory.mkdir(parents=True, exist_ok=True)
    return base
