"""Deterministic, fully offline highlight candidates.

This is a transparent baseline, not a semantic substitute for a human editor:
it ranks complete transcript spans using punctuation, pacing, and a small
multilingual cue vocabulary. It performs no network or model calls.
"""

from __future__ import annotations

import re

from ..providers import ClipCandidate, DetectionConfig
from .transcript import Transcript

_HOOK_CUES = {
    "en": {
        "but",
        "because",
        "secret",
        "mistake",
        "important",
        "remember",
        "never",
        "always",
        "why",
        "how",
        "result",
        "learn",
        "problem",
        "solution",
        "tip",
        "first",
        "finally",
        "imagine",
        "actually",
    },
    "hi": {
        "लेकिन",
        "क्योंकि",
        "जरूरी",
        "महत्वपूर्ण",
        "याद",
        "गलती",
        "समस्या",
        "समाधान",
        "तरीका",
        "सीख",
        "पहला",
        "आखिर",
        "मतलब",
        "ध्यान",
        "सच",
        "कभी",
        "हमेशा",
        "कैसे",
        "क्यों",
    },
}
_TOKEN = re.compile(r"[\w]+", re.UNICODE)


def _tokens(text: str) -> set[str]:
    return {token.casefold() for token in _TOKEN.findall(text)}


def _sentence_starts(transcript: Transcript) -> list[int]:
    starts = [0]
    for index in range(1, len(transcript.words)):
        previous = transcript.words[index - 1]
        current = transcript.words[index]
        if previous.ends_sentence or current.start - previous.end >= 0.8:
            starts.append(index)
    return starts


def detect_candidates(
    transcript: Transcript,
    config: DetectionConfig,
) -> list[ClipCandidate]:
    """Return explainable candidate spans without invoking an AI provider."""
    words = transcript.words
    if not words:
        return []

    starts = _sentence_starts(transcript)
    cue_words = _HOOK_CUES["en"] | _HOOK_CUES["hi"]
    candidates: list[ClipCandidate] = []
    seen: set[tuple[int, int]] = set()

    for first in starts:
        first_time = words[first].start
        target_end = first_time + min(config.max_duration_s, max(config.min_duration_s, 45.0))
        last = first
        while last + 1 < len(words) and words[last].end < target_end:
            last += 1

        # Prefer a complete sentence close to the target duration.
        sentence_ends = [i for i in range(first, last + 1) if words[i].ends_sentence]
        if sentence_ends:
            last = min(sentence_ends, key=lambda i: abs(words[i].end - target_end))
        if words[last].end - first_time < config.min_duration_s:
            # Extend to the first sentence end that reaches the minimum.
            eligible = [
                i
                for i in range(last + 1, len(words))
                if words[i].ends_sentence and words[i].end - first_time <= config.max_duration_s
            ]
            if eligible:
                last = eligible[0]
            elif words[-1].end - first_time >= config.min_duration_s:
                last = len(words) - 1
            else:
                continue

        duration = words[last].end - first_time
        if duration < config.min_duration_s or duration > config.max_duration_s:
            continue
        key = (first, last)
        if key in seen:
            continue
        seen.add(key)

        span = words[first : last + 1]
        text = " ".join(word.text for word in span)
        tokens = _tokens(text)
        cue_count = len(tokens & cue_words)
        sentence_end_count = sum(word.ends_sentence for word in span)
        pause_count = sum(
            1 for i in range(first + 1, last + 1) if transcript.pause_before(i) >= 0.5
        )
        speech_density = len(span) / max(duration, 1.0)

        # Transparent 0-100 heuristic; no claim of semantic/viral prediction.
        score = min(
            100,
            35
            + min(cue_count * 5, 20)
            + min(sentence_end_count * 3, 15)
            + min(pause_count * 3, 12)
            + (8 if 30 <= duration <= 60 else 0)
            + (5 if speech_density >= 1.5 else 0),
        )
        title = " ".join(word.text.strip() for word in span[:8]).strip()
        reasons = ["complete transcript span"]
        if cue_count:
            reasons.append(f"{cue_count} topic/emphasis cue(s)")
        if sentence_end_count:
            reasons.append("sentence boundaries")
        if pause_count:
            reasons.append("natural pacing pauses")
        candidates.append(
            ClipCandidate(
                start_word_index=first,
                end_word_index=last,
                title=title,
                hook=title,
                score=score,
                reason="; ".join(reasons),
            )
        )

    candidates.sort(key=lambda item: item.score, reverse=True)
    return candidates[: config.max_clips * 3]
