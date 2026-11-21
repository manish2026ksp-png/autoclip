# Melyqon Offline Video Studio — Product Specification

Status: Product direction locked; implementation and benchmark gates remain open.

## Product promise

Turn long-form video into editable, captioned short-form clips on the user's Windows PC, with Hindi/Hinglish as the first-class language experience. Core processing must work offline after the user explicitly installs the model(s) they choose.

The product must be honest about quality and speed. Never promise viral clips, perfect Hinglish, real-time processing, or universal hardware compatibility.

## Target customers

1. Hindi/Hinglish creators and educators.
2. Coaching businesses, trainers, and consultants.
3. Freelance video editors and small creator agencies.
4. English-language creators as a secondary market after the Hindi-first workflow is proven.

## Core user journey

1. Install the Windows app.
2. Choose a storage location for projects, temporary media, and models.
3. Import a local video. URL ingestion is optional and must not be required for the offline workflow.
4. Choose a transcription language and explicitly download only that language's model.
5. Transcribe with word timings; clearly label uncertain or approximate timing.
6. Generate explainable clip suggestions without requiring an LLM or cloud API.
7. Review, accept/reject, trim and edit captions.
8. Reframe to vertical or choose another supported aspect ratio.
9. Export MP4 and optional SRT to a user-selected location.

## Non-negotiable product principles

- Offline-first: no account, telemetry, mandatory cloud, API key, subscription, or network dependency for the core workflow.
- No mandatory LLM, Ollama, cloud model, or external AI service.
- Model downloads are explicit opt-in actions. Never download a model silently during import, transcription, startup, or export.
- Download only the selected language model. English and other languages remain optional and can be added later.
- Explain model size, storage requirement, source, license, and checksum before download where available.
- User controls model, project, cache, and export locations. Do not force large media/model data onto C:.
- Preserve original media. Never overwrite source files.
- One heavy video job at a time on low-end hardware; cancellation and resumable stages are required.
- Privacy claims must be verified with network monitoring/firewall tests before release.
- Accessibility, clear progress, useful error messages, and recovery are product features—not polish.

## Language and transcription policy

- Hindi/Hinglish is the first benchmark priority.
- English is a separately selectable optional model/download, not bundled by default.
- Do not claim Hinglish accuracy without a representative, manually verified benchmark.
- Evaluate Roman Hinglish, Devanagari Hindi, English code-switching, names, numbers, technical vocabulary, noise, music, multiple speakers, and fast speech.
- Keep an ASR adapter boundary so engines can be compared without rewriting the pipeline.
- Candidate engines are benchmark candidates, not preselected winners. Record model/runtime license, weight license, size, Windows support, CPU performance, timestamps, and redistribution rights separately.

## Clip intelligence

The base workflow must not depend on a generative model. Build deterministic candidate detection using transcript structure, sentence boundaries, pauses, duration, and configurable heuristics. Surface why a segment was suggested and let users correct it.

An optional AI provider may be considered only as a separately disabled extension. It must never be required for offline operation or silently transmit transcript text.

## Windows and hardware target

Primary validation device: HP EliteBook 840 G5, Windows 11 Pro, 16 GB RAM, Intel 8th-generation mobile CPU class, integrated graphics, no assumed NVIDIA GPU.

Support a broader Windows 10/11 x64 range only after CI and clean-machine installation tests. CPU fallback is mandatory. Hardware acceleration is optional and capability-probed.

## MVP scope

- Windows installable desktop experience.
- Local file import and metadata validation.
- Explicit model manager and selectable storage paths.
- Hindi/Hinglish-first ASR adapter and benchmarked default.
- Transcript review with editable text and timing.
- Offline deterministic clip suggestions.
- Vertical reframing with safe manual positioning fallback.
- Caption editing and readable presets.
- MP4 + SRT export.
- Job progress, cancellation, resume, logs, and actionable diagnostics.

## Explicitly out of scope for MVP

- Direct publishing to social platforms.
- Cloud accounts, collaboration, team workspaces, and hosted rendering.
- Mandatory LLM/agent/Ollama setup.
- Full professional multitrack timeline editor.
- Automatic music generation, stock libraries, or paid asset services.
- Bundling every language model.
- Unsupported claims of perfect face tracking or viral clip selection.

## Release gates

A feature is not "done" because it compiles. Release requires:
1. Windows clean-install and uninstall test.
2. Core workflow completed with network disconnected after opted-in model installation.
3. No model download without explicit consent.
4. Only the selected language model is downloaded.
5. User-selected storage paths honored for models, temp files, projects, and exports.
6. Hindi/Hinglish benchmark published internally with WER/CER, term accuracy, hallucinations, timestamp error, real-time factor, RAM, and thermal behavior.
7. Reframing golden-set passes; manual crop fallback works.
8. Export validated for aspect ratio, audio, captions, rotation, variable frame rate, and common codecs.
9. 30-minute sustained processing and cancellation/recovery test on target laptop.
10. Network audit supports every privacy claim.
11. Legal review of source, dependencies, ASR runtime, model weights, fonts, FFmpeg distribution, and bundled assets.

## Commercial principle

Validate willingness to pay before scaling features. Initial pricing remains a hypothesis, not a committed price. Do not add recurring infrastructure costs until paid demand proves they are justified.
