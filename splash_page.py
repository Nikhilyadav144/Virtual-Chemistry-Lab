"""
pages/splash_page.py
──────────────────────────────────────────────────────────────────
Animated splash / welcome screen shown for ~2.5 seconds on launch.
Displays the app logo, name, and a loading bar, then auto-navigates
to the home screen.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout
from PyQt5.QtCore    import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui     import QFont, QPainter, QLinearGradient, QColor, QBrush

from utils.theme import *


class SplashPage(QWidget):
    def __init__(self, on_done, parent=None):
        super().__init__(parent)
        self.on_done   = on_done
        self._progress = 0
        self._setup_ui()
        self._start_animation()

    # ── UI BUILD ────────────────────────────────
    def _setup_ui(self):
        self.setStyleSheet(f"background: {BG_PRIMARY};")

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setSpacing(0)
        outer.setContentsMargins(0, 0, 0, 0)

        center = QVBoxLayout()
        center.setAlignment(Qt.AlignCenter)
        center.setSpacing(20)

        # ── Flask icon (unicode chemistry flask) ──
        icon = QLabel("⚗")
        icon.setFont(QFont("Segoe UI Emoji", 72))
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(f"color: {ACCENT_CYAN}; background: transparent;")
        center.addWidget(icon)

        # ── App title ─────────────────────────────
        title = QLabel("Virtual Chemistry Lab")
        title.setFont(QFont(FONT_FAMILY_HEADING, FONT_SIZE_HERO, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        center.addWidget(title)

        # ── Subtitle ──────────────────────────────
        sub = QLabel("AI-Powered  ·  Hand-Tracked  ·  Interactive Simulations")
        sub.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_H3))
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"color: {ACCENT_CYAN}; background: transparent; letter-spacing: 1px;")
        center.addWidget(sub)

        center.addSpacing(40)

        # ── Loading bar ───────────────────────────
        bar_container = QWidget()
        bar_container.setFixedWidth(420)
        bar_container.setStyleSheet("background: transparent;")
        bar_layout = QVBoxLayout(bar_container)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.setSpacing(10)

        self.status_lbl = QLabel("Initialising modules…")
        self.status_lbl.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL))
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        bar_layout.addWidget(self.status_lbl)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setFixedHeight(6)
        self.bar.setTextVisible(False)
        self.bar.setStyleSheet(f"""
            QProgressBar {{
                background: {BG_CARD};
                border-radius: 3px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT_CYAN}, stop:1 {ACCENT_TEAL});
                border-radius: 3px;
            }}
        """)
        bar_layout.addWidget(self.bar)
        center.addWidget(bar_container, 0, Qt.AlignCenter)

        outer.addLayout(center)

        # ── Version / credit ──────────────────────
        footer = QLabel("v1.0  ·  B.Tech Major Project  ·  Computer Science")
        footer.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_TINY))
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; margin-bottom: 20px;")
        outer.addWidget(footer)

    # ── ANIMATION ───────────────────────────────
    _STATUS_MSGS = [
        "Initialising modules…",
        "Loading experiment database…",
        "Calibrating particle engine…",
        "Setting up hand tracker…",
        "Almost ready…",
    ]

    def _start_animation(self):
        self._step = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(46)   # ~2.3 s total for 50 ticks

    def _tick(self):
        self._progress += 2
        self.bar.setValue(self._progress)

        # Update status label at intervals
        idx = min(int(self._progress / 20), len(self._STATUS_MSGS) - 1)
        self.status_lbl.setText(self._STATUS_MSGS[idx])

        if self._progress >= 100:
            self._timer.stop()
            QTimer.singleShot(400, self.on_done)

    # ── BACKGROUND PAINT ─────────────────────────
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Subtle radial-ish gradient from centre
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0, QColor(10, 20, 40))
        grad.setColorAt(1, QColor(8, 12, 24))
        painter.fillRect(self.rect(), QBrush(grad))
        painter.end()
