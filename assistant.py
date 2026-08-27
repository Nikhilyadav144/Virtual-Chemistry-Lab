"""
voice_assistant.assistant
Atom orchestration: recognition, parsing, actions, and TTS.
"""

from PyQt5.QtCore import QObject, pyqtSignal

from voice_assistant.command_parser import CommandParser
from voice_assistant.speech_engine import SpeechEngine
from voice_assistant.tts_engine import TTSEngine
from voice_assistant.voice_actions import VoiceActionRouter


class AtomAssistant(QObject):
    transcript = pyqtSignal(str)
    response = pyqtSignal(str)
    status = pyqtSignal(str)
    activated = pyqtSignal(str)

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.parser = CommandParser()
        self.tts = TTSEngine()
        self.actions = VoiceActionRouter(main_window)
        self.speech = None
        self._make_speech_engine()

    def start(self):
        self.status.emit("Atom starting")
        self.start_listening()

    def stop(self):
        if self.speech:
            self.speech.stop()
            self.speech.wait(1200)
        self.tts.stop()

    def activate(self):
        self.activated.emit("Atom")
        self.transcript.emit("Atom selected. Speak now.")
        self.response.emit("Listening for your voice command.")
        self.start_listening()

    def start_listening(self):
        if self.speech and self.speech.isRunning():
            self.status.emit("Atom listening")
            return
        self._make_speech_engine()
        self.status.emit("Atom starting")
        self.speech.start()

    def handle_text(self, text: str):
        command = self.parser.parse(text)
        if not command:
            return
        self.activated.emit(text)
        self.transcript.emit(text)
        self.status.emit("Atom processing")
        reply = self.actions.execute(command)
        self.response.emit(reply)
        self.status.emit("Atom ready")
        self.tts.say(reply)

    def _make_speech_engine(self):
        self.speech = SpeechEngine(parent=self)
        self.speech.transcript_ready.connect(self.handle_text)
        self.speech.status_changed.connect(self.status)
