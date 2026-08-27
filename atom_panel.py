"""
voice_assistant.atom_panel
Persistent Atom status/transcript panel.
"""

from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QCursor, QFont

from utils.theme import *


class AtomPanel(QFrame):
    typed_command = pyqtSignal(str)
    atom_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(72)
        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_SECONDARY};
                border-top: 1px solid {BORDER_COLOR};
            }}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(PAD_MD, 8, PAD_MD, 8)
        lay.setSpacing(PAD_SM)

        self.mic = QPushButton("🎙 Atom")
        self.mic.setCursor(QCursor(Qt.PointingHandCursor))
        self.mic.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_BODY, QFont.Bold))
        self.mic.setStyleSheet(f"""
            QPushButton {{
                color: {ACCENT_TEAL};
                background: {BG_CARD};
                border: 1px solid {ACCENT_TEAL};
                border-radius: 8px;
                padding: 6px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: {BG_PRIMARY};
                background: {ACCENT_TEAL};
            }}
        """)
        self.mic.clicked.connect(self.atom_requested.emit)
        lay.addWidget(self.mic)

        self.status = QLabel("Text mode")
        self.status.setMinimumWidth(120)
        self.status.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL))
        self.status.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        lay.addWidget(self.status)

        speech_col = QVBoxLayout()
        speech_col.setContentsMargins(0, 0, 0, 0)
        speech_col.setSpacing(2)

        self.transcript = QLabel("Heard: Say or type, Hey Atom, select hydrochloric acid")
        self.transcript.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.transcript.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL))
        self.transcript.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        self.transcript.setWordWrap(False)
        speech_col.addWidget(self.transcript)

        self.response = QLabel("Atom: Ready for secondary voice controls")
        self.response.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.response.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_TINY))
        self.response.setStyleSheet(f"color: {ACCENT_TEAL}; background: transparent;")
        self.response.setWordWrap(False)
        speech_col.addWidget(self.response)
        lay.addLayout(speech_col, 1)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type Atom command...")
        self.input.setFixedWidth(250)
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_CARD};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 7px;
                padding: 6px 8px;
            }}
            QLineEdit:focus {{ border-color: {ACCENT_TEAL}; }}
        """)
        self.input.returnPressed.connect(self._send)
        lay.addWidget(self.input)

        send = QPushButton("Send")
        send.setCursor(QCursor(Qt.PointingHandCursor))
        send.setFixedHeight(34)
        send.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_TEAL};
                color: {BG_PRIMARY};
                border: none;
                border-radius: 7px;
                padding: 0 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {ACCENT_CYAN}; }}
        """)
        send.clicked.connect(self._send)
        lay.addWidget(send)

        listen = QPushButton("Listen")
        listen.setCursor(QCursor(Qt.PointingHandCursor))
        listen.setFixedHeight(34)
        listen.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD};
                color: {ACCENT_CYAN};
                border: 1px solid {ACCENT_CYAN};
                border-radius: 7px;
                padding: 0 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {ACCENT_CYAN};
                color: {BG_PRIMARY};
            }}
        """)
        listen.clicked.connect(self.atom_requested.emit)
        lay.addWidget(listen)

    def _send(self):
        text = self.input.text().strip()
        if text:
            self.input.clear()
            self.typed_command.emit(text)

    def set_status(self, text):
        self.status.setText(text)
        active = "listening" in text.lower() or "processing" in text.lower()
        color = ACCENT_TEAL if active else TEXT_SECONDARY
        self.status.setStyleSheet(f"color: {color}; background: transparent;")

    def set_transcript(self, text):
        self.transcript.setText(f"Heard: {text}")

    def set_response(self, text):
        self.response.setText(f"Atom: {text}")
