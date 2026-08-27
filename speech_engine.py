"""Background Vosk speech recognizer for Atom."""

from __future__ import annotations

import json
import os
import queue
from pathlib import Path

from PyQt5.QtCore import QThread, pyqtSignal


class SpeechEngine(QThread):
    transcript_ready = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self, model_path: str | None = None, parent=None):
        super().__init__(parent)
        self.model_path = model_path or os.environ.get("ATOM_VOSK_MODEL", "")
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        try:
            import sounddevice as sd
            import vosk
        except Exception as exc:
            self.status_changed.emit("Atom text mode")
            self.status_changed.emit(f"Speech unavailable: {exc}")
            return

        model_path = self._resolve_model_path()
        if not model_path:
            self.status_changed.emit("Atom needs Vosk model")
            return

        try:
            input_devices = [
                device for device in sd.query_devices()
                if device.get("max_input_channels", 0) > 0
            ]
        except Exception as exc:
            input_devices = []
            self.status_changed.emit(f"Microphone check failed: {exc}")
        if not input_devices:
            self.status_changed.emit("Requesting microphone access")

        audio_queue: queue.Queue[bytes] = queue.Queue()

        def callback(indata, frames, time_info, status):
            if status:
                self.status_changed.emit(str(status))
            audio_queue.put(bytes(indata))

        try:
            model = vosk.Model(str(model_path))
            recognizer = vosk.KaldiRecognizer(model, 16000)
            recognizer.SetWords(False)
            self.status_changed.emit("Atom listening")
            with sd.RawInputStream(
                samplerate=16000,
                blocksize=8000,
                dtype="int16",
                channels=1,
                callback=callback,
            ):
                while not self._stop:
                    try:
                        data = audio_queue.get(timeout=0.25)
                    except queue.Empty:
                        continue
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "").strip()
                        if text:
                            self.transcript_ready.emit(text)
        except Exception as exc:
            self.status_changed.emit(f"Atom offline: {exc}")

    def _resolve_model_path(self) -> Path | None:
        candidates = []
        if self.model_path:
            candidates.append(Path(self.model_path).expanduser())
        candidates.extend([
            Path("models/vosk-model-small-en-us-0.15"),
            Path("models/vosk-model-en-us-0.22"),
            Path("vosk-model-small-en-us-0.15"),
        ])
        for path in candidates:
            if path.is_dir():
                return path
        return None
