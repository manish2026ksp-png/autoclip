"""Tests for the deterministic offline highlight baseline."""
from __future__ import annotations

from autoclip.pipeline.offline_highlights import detect_candidates
from autoclip.pipeline.transcript import Transcript, Word
from autoclip.providers import DetectionConfig


def make_words(text: str, *, step: float = 0.5) -> list[Word]:
    words = []
    for index, token in enumerate(text.split()):
        clean = token.rstrip(".!?")
        punctuated = clean + ("." if token.endswith((".", "!", "?")) else "")
        start = index * step
        words.append(Word(text=punctuated, start=start, end=start + step * 0.8))
    return words


def test_empty_transcript_returns_no_candidates() -> None:
    assert detect_candidates(Transcript(), DetectionConfig()) == []


def test_offline_candidates_use_valid_word_indices_and_duration() -> None:
    text = " ".join(
        "यह बहुत जरूरी बात है और इसे ध्यान से समझना चाहिए।"
        for _ in range(18)
    )
    transcript = Transcript(words=make_words(text))
    config = DetectionConfig(min_duration_s=20, max_duration_s=90, max_clips=5)

    candidates = detect_candidates(transcript, config)

    assert candidates
    for candidate in candidates:
        assert 0 <= candidate.start_word_index < candidate.end_word_index < len(transcript.words)
        start = transcript.words[candidate.start_word_index].start
        end = transcript.words[candidate.end_word_index].end
        assert config.min_duration_s <= end - start <= config.max_duration_s


def test_offline_detection_is_deterministic() -> None:
    transcript = Transcript(words=make_words(
        "This is important. Remember this useful lesson. " * 12
    ))
    config = DetectionConfig(min_duration_s=10, max_duration_s=30, max_clips=4)

    first = detect_candidates(transcript, config)
    second = detect_candidates(transcript, config)

    assert [item.model_dump() for item in first] == [item.model_dump() for item in second]


def test_reason_explains_the_scoring_signals() -> None:
    transcript = Transcript(words=make_words(
        "This important solution works. " * 15
    ))
    candidates = detect_candidates(
        transcript, DetectionConfig(min_duration_s=10, max_duration_s=30)
    )

    assert candidates
    assert "complete transcript span" in candidates[0].reason
