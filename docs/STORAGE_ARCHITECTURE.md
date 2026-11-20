# Storage Architecture — Audit and Implementation Plan

## Current behaviour (audited on `melyqon-product`)

The application currently has one storage root, resolved by `AUTOCLIP_HOME` (default `~/.autoclip`, with legacy `.clipforge` adoption). The root contains:

- `media/`: uploaded and downloaded source videos
- `work/<job_id>/`: extracted audio, transcript, thumbnails, crop metadata and caption intermediates
- `exports/`: rendered clips
- `models/`: MediaPipe model and the dedicated faster-whisper download root
- `autoclip.db`: SQLite database (with legacy database adoption)
- `config.json`: non-secret settings

The database stores absolute paths for source media, transcripts and exports. Changing storage roots therefore cannot be treated as a simple settings update.

## Gaps confirmed

1. Media, work files, exports, database and models are all derived from the same root.
2. `faster-whisper` is given a dedicated model download root, but hidden Hugging Face / Torch / XDG caches are not centrally redirected.
3. ffmpeg and Python temporary files may use the operating system's default temp directory.
4. Storage diagnostics and destination validation are available in Settings, but selecting and persisting independent roots is not yet implemented.
5. The existing `AUTOCLIP_HOME` behaviour and legacy adoption must remain supported for existing installs.

## Target layout

Use independently resolvable roots, each falling back under the existing home root:

| Purpose | Default child | Must contain |
| --- | --- | --- |
| App state | root | config, SQLite database |
| Media | `media/` | imported/uploaded source videos |
| Work | `work/` | per-job intermediates and resumable artifacts |
| Exports | `exports/` | finished clips and sidecars |
| Models | `models/` | explicitly downloaded inference weights |
| Temp/cache | `tmp/` | disposable ffmpeg and library scratch files |

Each root should support an environment override first. Persisted UI settings can be introduced after the path registry and migration rules are stable. Relative paths should be rejected; resolved absolute paths should be displayed back to the user.

## Non-negotiable safety rules

- Existing installs without new settings must resolve to exactly the same paths as today.
- Never move or delete user data when a path setting changes. A path change affects future writes only until the user explicitly starts a verified migration.
- Do not migrate SQLite while the application or a job is active.
- Validate each target by creating it, writing a small probe file, flushing it, and removing only that probe file.
- Show available disk space and warn before ingest/export when the destination is low on space.
- Keep model downloads opt-in and language/model-specific where the underlying model format permits it. Never prefetch all models.
- Redirect library caches before importing libraries that initialise those caches; changing environment variables after import is not sufficient.
- Temporary data must be disposable; source media, database, transcripts and exports are not.

## Implementation sequence

1. Add a central path registry with backward-compatible defaults and tests for independent overrides.
2. Audit every filesystem write and route it through the registry; identify any library cache that needs an environment variable set before import.
3. Add path validation and disk-space reporting APIs.
4. Add Settings UI for current locations, free-space reporting and candidate-folder write validation.
5. Add persisted path selection only after restart semantics, active-job protection and cache initialization are designed.
6. Add explicit, staged migration with a dry-run estimate, no overwrite, verification, rollback, and a requirement that no jobs are active.
7. Test Windows paths, spaces, Unicode, removable drives, unavailable drives, low disk, interrupted migration, and existing legacy installs.

## Implemented in the product-foundation branch

- Independent environment overrides now exist for media, work, exports, models and temporary storage.
- Existing installs retain the same default directory layout and legacy `.clipforge` adoption.
- Relative override paths are rejected; overrides must be absolute paths.
- Common Hugging Face, Torch, XDG and Python temporary-directory settings are configured during package initialization, before application modules import inference libraries. Existing explicit cache environment variables are respected.
- Model storage and Whisper's dedicated cache now resolve through the model storage root.
- Tests cover independent overrides, relative-path rejection, directory creation and cache environment behaviour.

## Storage UI status

- Settings now displays all six configured storage locations, directory state, write-access status and available disk space.
- Users can validate a candidate absolute folder with a real create/write/delete probe; the UI clearly states that this does not change active storage.
- Path selection/persistence and safe migration remain intentionally disabled until active-job handling, process restart behaviour and cache reinitialization are implemented.

## Still not implemented

- Persisted UI selection of independent storage paths.
- Safe data migration, dry-run sizing, rollback and active-job protection.
- Auditing every optional dependency's cache/temp behaviour on Windows.

This is a staged foundation, not a claim that all storage requirements are complete.
