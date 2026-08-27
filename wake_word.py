"""
voice_assistant.wake_word
Wake phrase handling for Atom.

This module intentionally does not perform acoustic wake-word detection. Vosk
recognizes short utterances in the background thread, then this detector decides
whether a transcript is addressed to Atom.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


DEFAULT_WAKE_PHRASES = ("hey atom", "atom")


@dataclass(frozen=True)
class WakeResult:
    woke: bool
    command_text: str
    original_text: str


class WakeWordDetector:
    def __init__(self, wake_phrases=DEFAULT_WAKE_PHRASES):
        self.wake_phrases = tuple(self._normalize(p) for p in wake_phrases)

    def detect(self, text: str) -> WakeResult:
        original = text or ""
        normalized = self._normalize(original)
        for phrase in self.wake_phrases:
            if normalized == phrase:
                return WakeResult(True, "", normalized)
            if normalized.startswith(phrase + " "):
                return WakeResult(True, normalized[len(phrase):].strip(), normalized)
        return WakeResult(False, normalized, normalized)

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.lower().replace(",", " ").replace(".", " ")
        return re.sub(r"\s+", " ", text).strip()
