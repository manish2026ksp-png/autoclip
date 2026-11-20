"""Settings, secrets, provider health, and system status."""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException

from .. import config, models, system
from ..providers import PROVIDERS, build_provider
from ..providers.base import ProviderStatus
from .schemas import ProviderStatusOut, SecretIn, SettingsIn, SettingsOut, SystemOut

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["settings"])


def _settings_out(settings: config.Settings) -> SettingsOut:
    payload = settings.model_dump(mode="json")
    return SettingsOut(
        active_provider=payload["active_provider"],
        highlight_mode=payload["highlight_mode"],
        providers=payload["providers"],
        whisper=payload["whisper"],
        clips=payload["clips"],
        ingest=payload["ingest"],
        export=payload["export"],
        insecure_secret_storage=payload["insecure_secret_storage"],
        keys_present={
            name: config.get_secret(name, settings) is not None for name in config.KEYED_PROVIDERS
        }
        | {config.HF_TOKEN_KEY: config.get_secret(config.HF_TOKEN_KEY, settings) is not None},
    )


@router.get("/settings", response_model=SettingsOut)
async def get_settings() -> SettingsOut:
    return _settings_out(config.load())


@router.put("/settings", response_model=SettingsOut)
async def put_settings(payload: SettingsIn) -> SettingsOut:
    """Merge a partial settings update and persist it."""
    settings = config.load()
    updates = payload.model_dump(exclude_none=True)

    if "highlight_mode" in updates:
        settings.highlight_mode = updates["highlight_mode"]

    if "active_provider" in updates:
        if updates["active_provider"] not in PROVIDERS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown provider. Available: {', '.join(PROVIDERS)}",
            )
        settings.active_provider = updates["active_provider"]

    for section in ("whisper", "clips", "ingest", "export"):
        if section in updates:
            current = getattr(settings, section)
            try:
                setattr(
                    settings,
                    section,
                    current.model_copy(update=updates[section]).model_validate(
                        current.model_dump() | updates[section]
                    ),
                )
            except Exception as exc:
                raise HTTPException(
                    status_code=400, detail=f"Invalid {section} settings: {exc}"
                ) from exc

    if "providers" in updates:
        for name, values in updates["providers"].items():
            provider_settings = settings.provider(name)
            settings.providers[name] = provider_settings.model_copy(update=values)

    if settings.clips.min_duration_s >= settings.clips.max_duration_s:
        raise HTTPException(
            status_code=400, detail="Minimum clip length must be below the maximum."
        )

    config.save(settings)
    return _settings_out(settings)


@router.put("/settings/secrets", status_code=204)
async def put_secret(payload: SecretIn) -> None:
    """Store an API key or token. Values are write-only — never read back."""
    valid = (*config.KEYED_PROVIDERS, config.HF_TOKEN_KEY)
    if payload.key not in valid:
        raise HTTPException(
            status_code=400, detail=f"Unknown secret. Expected one of: {', '.join(valid)}"
        )
    if not payload.value.strip():
        raise HTTPException(status_code=400, detail="The value cannot be empty.")

    config.set_secret(payload.key, payload.value.strip())


@router.delete("/settings/secrets/{key}", status_code=204)
async def delete_secret(key: str) -> None:
    config.delete_secret(key)


@router.get("/providers/status", response_model=list[ProviderStatusOut])
async def providers_status() -> list[ProviderStatusOut]:
    """Live health for every provider, checked concurrently."""
    settings = config.load()

    async def check(name: str) -> ProviderStatusOut:
        provider_cls = PROVIDERS[name]
        has_key = (
            config.get_secret(name, settings) is not None if provider_cls.requires_key else True
        )
        try:
            provider = build_provider(name, settings)
            status: ProviderStatus = await provider.health_check()
        except Exception as exc:
            status = ProviderStatus(name=name, available=False, detail=str(exc)[:200])

        return ProviderStatusOut(
            name=name,
            available=status.available,
            detail=status.detail,
            models=status.models,
            requires_key=provider_cls.requires_key,
            has_key=has_key,
        )

    return list(await asyncio.gather(*(check(name) for name in PROVIDERS)))


@router.get("/system", response_model=SystemOut)
async def system_status() -> SystemOut:
    report = await asyncio.to_thread(system.refresh)
    return SystemOut(
        ready=report.ready,
        python_version=report.python_version,
        platform=report.platform,
        ffmpeg_version=report.ffmpeg.version,
        has_libass=report.ffmpeg.has_libass,
        nvenc_works=report.ffmpeg.nvenc_works,
        accel=report.gpu.accel,
        gpu_name=report.gpu.name,
        compute_type=report.gpu.compute_type,
        diarization_available=report.deps.whisperx,
    )


@router.post("/system/models/whisper/{model_name}", status_code=204)
async def download_whisper_model(model_name: str) -> None:
    """Explicitly download one selected Whisper model; never called by a job."""
    allowed = {"tiny", "base", "small", "medium", "large-v3"}
    if model_name not in allowed:
        raise HTTPException(
            status_code=400, detail=f"Unsupported Whisper model. Choose: {', '.join(sorted(allowed))}"
        )

    def download() -> None:
        from faster_whisper import WhisperModel

        cache_root = models.whisper_models_dir()
        cache_root.mkdir(parents=True, exist_ok=True)
        # This endpoint is the explicit user-consent boundary. Normal jobs use
        # local_files_only=True and cannot trigger a network request.
        WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8",
            download_root=str(cache_root),
            local_files_only=False,
        )

    try:
        await asyncio.to_thread(download)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not download Whisper model '{model_name}': {exc}",
        ) from exc


@router.post("/system/models/{model_key}", status_code=204)
async def download_model(model_key: str) -> None:
    """Download exactly one explicitly selected model bundle."""
    if model_key not in models.MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model. Available: {', '.join(sorted(models.MODELS))}",
        )
    try:
        await asyncio.to_thread(models.download, model_key)
    except models.ModelDownloadError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
