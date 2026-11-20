"""Storage diagnostics and safe destination validation endpoints."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import paths

router = APIRouter(prefix="/api/system/storage", tags=["storage"])


class StoragePathIn(BaseModel):
    path: str = Field(min_length=1, max_length=4096)


def _storage_entry(name: str, path: Path) -> dict:
    exists = path.exists()
    probe = path if exists and path.is_dir() else path.parent
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    try:
        usage = shutil.disk_usage(probe)
        free_bytes = usage.free
    except OSError:
        free_bytes = None
    return {
        "name": name,
        "path": str(path),
        "exists": exists,
        "is_directory": path.is_dir() if exists else False,
        "writable": path.is_dir() and os.access(path, os.W_OK)
        if exists
        else os.access(probe, os.W_OK),
        "free_bytes": free_bytes,
    }


@router.get("")
async def storage_status() -> dict:
    """Report configured storage locations without creating or modifying them."""
    entries = [
        _storage_entry("Application data", paths.root()),
        _storage_entry("Media", paths.media_dir()),
        _storage_entry("Projects and work", paths.work_dir()),
        _storage_entry("Models", paths.models_dir()),
        _storage_entry("Temporary files and cache", paths.temp_dir()),
        _storage_entry("Exports", paths.exports_dir()),
    ]
    return {"locations": entries, "migration_supported": False}


@router.post("/validate")
async def validate_storage_path(payload: StoragePathIn) -> dict:
    """Create the selected directory if needed and verify a real write/delete cycle."""
    candidate = Path(payload.path).expanduser()
    if not candidate.is_absolute():
        raise HTTPException(status_code=400, detail="Path must be absolute.")
    try:
        candidate.mkdir(parents=True, exist_ok=True)
        if not candidate.is_dir():
            raise OSError("The selected path is not a directory.")
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=".melyqon-write-test-", dir=candidate, delete=True
        ) as probe:
            probe.write(b"melyqon-storage-check")
            probe.flush()
        usage = shutil.disk_usage(candidate)
    except OSError as exc:
        raise HTTPException(
            status_code=400, detail=f"Cannot use this storage location: {exc}"
        ) from exc

    return {
        "valid": True,
        "path": str(candidate.resolve()),
        "free_bytes": usage.free,
        "directory_created": True,
    }
