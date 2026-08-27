"""pyttsx3 text-to-speech wrapper for Atom."""

from __future__ import annotations

import queue
from threading import Thread


class TTSEngine:
    def __init__(self):
        self._engine = None
        self._queue: queue.Queue[str | None] = queue.Queue()
        self._worker = None
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", 175)
        except Exception:
            self._engine = None
        if self._engine:
            self._worker = Thread(target=self._run, daemon=True)
            self._worker.start()

    @property
    def available(self):
        return self._engine is not None

    def say(self, text: str):
        if not self._engine or not text:
            return
        self._queue.put(text)

    def stop(self):
        if self._engine:
            self._queue.put(None)

    def _run(self):
        while True:
            text = self._queue.get()
            if text is None:
                break
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception:
                pass
