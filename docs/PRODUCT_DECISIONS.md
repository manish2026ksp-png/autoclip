# Product Architecture Decisions

## 001 — Reuse AutoClip rather than rewrite
**Decision:** Keep the existing Python/FastAPI + React pipeline as the starting foundation. Evaluate a desktop shell only after core offline behavior is proven.

**Reason:** The existing pipeline already contains ingestion, transcription, clip review, reframing, captions, export, job persistence, and stage resume. A Rust rewrite would create cost and risk without proving better user value.

**Consequence:** The backend must be modularized at the boundaries needed for deterministic clip selection, ASR adapters, model management, and packaging.

## 002 — No mandatory generative model
**Decision:** Core clip suggestions must work without a cloud API, Ollama, or local LLM.

**Reason:** The target laptop has 16 GB RAM and integrated graphics; a mandatory local LLM adds storage and performance burden. Cloud LLM use conflicts with the offline/privacy promise.

**Consequence:** Build deterministic transcript-based candidate scoring first. Any future generative enhancement is optional, separately consented, and off by default.

## 003 — Explicit language-specific model installation
**Decision:** Users select a language and explicitly approve each model download. Do not prebundle or silently fetch all language models.

**Reason:** Model size, storage, bandwidth, and user choice are central product constraints.

**Consequence:** Model registry must expose language, engine, version, source, license, size, checksum, installed state, and storage path. Download flow must be cancellable and verifiable.

## 004 — Hindi/Hinglish benchmark before ASR selection
**Decision:** No ASR engine is declared the winner before same-sample testing on the target Windows hardware.

**Reason:** Published aggregate metrics do not guarantee Roman Hinglish, code-switching, names, timestamps, or acceptable CPU performance.

**Consequence:** Maintain an adapter interface and benchmark report; preserve alternate engines until evidence supports removal.

## 005 — Windows-first, CPU-capable
**Decision:** Optimize first for Windows 11 x64 and a 16 GB integrated-graphics laptop, while keeping architecture portable where low-cost.

**Reason:** This is the immediate target environment and makes performance constraints concrete.

**Consequence:** One heavy job at a time, CPU fallback, user-controlled storage, and functional hardware probing are defaults.

## 006 — Local-first storage
**Decision:** Projects, model files, temporary media, and exports must use configurable paths.

**Reason:** Users may have limited C: drive space or external storage.

**Consequence:** Audit all libraries and subprocesses for hidden caches and ensure configured paths are passed through consistently.

## 007 — Claims require tests
**Decision:** "Offline", "private", "Hindi-first", "lightweight", and performance claims are release-gated.

**Reason:** These are the product's differentiators and must be demonstrably true.

**Consequence:** Add offline network tests, model-consent tests, Hindi/Hinglish benchmarks, and target-hardware performance reports before launch.
