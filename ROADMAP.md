# Melyqon Offline Video Studio — Roadmap

This roadmap is ordered by risk reduction, not by visual excitement. Each phase must pass its exit gate before the next phase is treated as complete.

## Phase 0 — Establish a safe product baseline
- [x] Fork upstream AutoClip into the Melyqon-owned repository.
- [x] Preserve upstream history and MIT license.
- [x] Create a dedicated product branch.
- [ ] Run and record current upstream tests on the fork.
- [ ] Inventory every pipeline stage, model download, provider/network path, storage path, and UI surface.
- [ ] Record dependency and asset licensing obligations.

Exit gate: reproducible baseline and an accurate reuse/replace/defer map.

## Phase 1 — Offline-first foundation
- [ ] Make the core pipeline independent of LLM providers.
- [ ] Add deterministic, explainable clip candidate generation.
- [ ] Remove cloud provider setup from the default first-run path; keep any optional provider isolated and disabled.
- [ ] Implement explicit per-model download consent, progress, cancellation, checksum/size validation, and clear storage accounting.
- [ ] Ensure language selection downloads only the selected model.
- [ ] Add configurable model, project, cache, and temp roots.
- [ ] Audit every implicit network call, including transcription/model libraries and URL ingestion.

Exit gate: with models explicitly installed, local-file workflow completes offline; no unapproved download or transcript upload occurs.

## Phase 2 — Hindi/Hinglish quality and performance
- [ ] Build a reproducible audio benchmark harness and annotation format.
- [ ] Compare candidate ASR engines on the same Hindi/Hinglish samples.
- [ ] Measure accuracy, timestamps, speed, peak RAM, CPU load, and thermal throttling on the target EliteBook.
- [ ] Select a default only from measured results.
- [ ] Add transcript correction and robust timestamp editing.

Exit gate: benchmark report exists, regressions are detectable, and the default is chosen on evidence.

## Phase 3 — Creator workflow and Windows desktop
- [ ] Simplify onboarding and first-run system checks.
- [ ] Build an installable Windows desktop distribution around the existing backend/frontend where technically sound.
- [ ] Provide storage setup before any large model/media operation.
- [ ] Add accessible review, crop correction, caption editing, and export flows.
- [ ] Test clean install, upgrades, uninstall, crash recovery, and low-disk conditions.

Exit gate: a non-technical Windows user can install and finish a project without command-line setup.

## Phase 4 — Reliability and release readiness
- [ ] Run Windows CI, render tests, API tests, and frontend build on every change.
- [ ] Add representative golden videos and measurable reframing acceptance.
- [ ] Validate codecs, rotation, VFR, audio sync, subtitle rendering, and export integrity.
- [ ] Complete offline/network audit and legal inventory.
- [ ] Run sustained target-hardware tests and publish realistic performance guidance.

Exit gate: all release gates in PRODUCT_SPEC.md pass.

## Phase 5 — Paid validation and launch
- [ ] Recruit 10 paid pre-sale customers across at least 3 target segments.
- [ ] Observe real projects and measure time saved, correction burden, and repeat use.
- [ ] Finalize India/global pricing only after willingness-to-pay evidence.
- [ ] Ship a small, supportable release; avoid cloud costs and feature sprawl.

Exit gate: repeatable customer value and support burden are understood.

## Engineering rules
- Keep upstream code reuse where it serves the product; do not rewrite for aesthetic reasons.
- Use small, reviewable commits and run the relevant tests after each change.
- Never weaken or delete tests merely to make CI green.
- Do not commit copyrighted customer media, model weights, API keys, or secrets.
- Keep model weights out of the installer unless licensing and explicit product strategy justify it.
- A feature that increases install size, storage, startup time, or RAM must justify that cost.
