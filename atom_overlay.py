"""
voice_assistant.atom_overlay
Floating Siri-style overlay for Atom.
"""

from __future__ import annotations

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from utils.theme import *


class ListeningOrb(QWidget):
    """Animated microphone orb used by the floating Atom overlay."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(132, 132)
        self._phase = 0
        self._active = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(45)

    def set_active(self, active: bool):
        self._active = active
        self.update()

    def _tick(self):
        self._phase = (self._phase + 1) % 120
        if self._active:
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cx = self.width() / 2
        cy = self.height() / 2

        rings = 3 if self._active else 1
        for i in range(rings):
            radius = 40 + ((self._phase + i * 18) % 54)
            alpha = max(0, 110 - radius)
            painter.setPen(QPen(QColor(0, 245, 196, alpha), 3))
            painter.drawEllipse(int(cx - radius), int(cy - radius), int(radius * 2), int(radius * 2))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 212, 255, 230))
        painter.drawEllipse(30, 30, 72, 72)
        painter.setBrush(QColor(0, 245, 196, 225))
        painter.drawEllipse(42, 42, 48, 48)

        painter.setPen(QPen(QColor(BG_PRIMARY), 5, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(66, 50, 66, 74)
        painter.drawArc(52, 60, 28, 28, 200 * 16, 140 * 16)
        painter.drawLine(66, 88, 66, 96)
        painter.drawLine(56, 96, 76, 96)


class AtomOverlay(QFrame):
    listen_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AtomOverlay")
        self.setFixedSize(420, 300)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            QFrame#AtomOverlay {{
                background: rgba(17, 24, 39, 242);
                border: 1px solid {ACCENT_TEAL};
                border-radius: 22px;
            }}
        """)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.fade_out)

        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity)

        self._fade = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade.setDuration(180)
        self._fade.setEasingCurve(QEasingCurve.OutCubic)
        self._hiding = False
        self._fade.finished.connect(self._on_fade_finished)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        self.orb = ListeningOrb(self)
        layout.addWidget(self.orb, 0, Qt.AlignHCenter)

        self.title = QLabel("Atom")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont(FONT_FAMILY_HEADING, FONT_SIZE_H2, QFont.Bold))
        self.title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(self.title)

        self.status = QLabel("Listening")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_BODY, QFont.Bold))
        self.status.setStyleSheet(f"color: {ACCENT_TEAL}; background: transparent;")
        layout.addWidget(self.status)

        self.transcript = QLabel("Say a command")
        self.transcript.setAlignment(Qt.AlignCenter)
        self.transcript.setWordWrap(True)
        self.transcript.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL))
        self.transcript.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        layout.addWidget(self.transcript)

        self.response = QLabel("")
        self.response.setAlignment(Qt.AlignCenter)
        self.response.setWordWrap(True)
        self.response.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL, QFont.Bold))
        self.response.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(self.response)

        listen_btn = QPushButton("Listen")
        listen_btn.setFixedSize(86, 32)
        listen_btn.setCursor(Qt.PointingHandCursor)
        listen_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_TEAL};
                color: {BG_PRIMARY};
                border: none;
                border-radius: 8px;
                font-size: {FONT_SIZE_SMALL}pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {ACCENT_CYAN};
            }}
        """)
        listen_btn.clicked.connect(self.listen_requested.emit)
        layout.addWidget(listen_btn, 0, Qt.AlignHCenter)

        close_btn = QPushButton("Close")
        close_btn.setFixedSize(78, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD};
                color: {TEXT_SECONDARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 7px;
                font-size: {FONT_SIZE_TINY}pt;
            }}
            QPushButton:hover {{
                color: {TEXT_PRIMARY};
                border-color: {ACCENT_TEAL};
            }}
        """)
        close_btn.clicked.connect(self.fade_out)
        layout.addWidget(close_btn, 0, Qt.AlignHCenter)

        self.hide()

    def wake(self, text: str = ""):
        self.response.clear()
        if text:
            self.transcript.setText(text)
        self.set_status("Listening")
        self.show_overlay(auto_hide=False)

    def set_status(self, text: str):
        self.status.setText(text)
        lower = text.lower()
        active = "listening" in lower or "processing" in lower or "starting" in lower
        self.orb.set_active(active)
        color = ACCENT_TEAL if active else TEXT_SECONDARY
        self.status.setStyleSheet(f"color: {color}; background: transparent;")

    def set_transcript(self, text: str):
        self.transcript.setText(text)
        self.show_overlay(auto_hide=False)

    def set_response(self, text: str):
        self.response.setText(text)
        self.set_status("Done")
        self.show_overlay(auto_hide=True)

    def show_overlay(self, auto_hide: bool):
        self._hide_timer.stop()
        self._hiding = False
        self.raise_()
        self.show()
        self._fade.stop()
        self._fade.setStartValue(self._opacity.opacity())
        self._fade.setEndValue(1.0)
        self._fade.start()
        if auto_hide:
            self._hide_timer.start(5200)

    def fade_out(self):
        self._hide_timer.stop()
        self._hiding = True
        self._fade.stop()
        self._fade.setStartValue(self._opacity.opacity())
        self._fade.setEndValue(0.0)
        self._fade.start()

    def _on_fade_finished(self):
        if self._hiding:
            self.hide()
