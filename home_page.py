"""
pages/home_page.py
──────────────────────────────────────────────────────────────────
Home / landing screen.
Shows the app hero section and a "Get Started" button that
navigates to the class-selection screen.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QSizePolicy
)
from PyQt5.QtCore  import Qt
from PyQt5.QtGui   import QFont, QPainter, QLinearGradient, QColor, QBrush

from utils.theme   import *
from utils.widgets import GlowButton, SectionCard, TagBadge


# ──────────────────────────────────────────────────────────────────
#  FEATURE CARD  (small info tile on home screen)
# ──────────────────────────────────────────────────────────────────
class _FeatureCard(QFrame):
    def __init__(self, icon, title, desc, accent, parent=None):
        super().__init__(parent)
        self.setFixedSize(240, 150)
        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border: 1px solid {BORDER_COLOR};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame:hover {{
                border-color: {accent};
                background: {BG_HOVER};
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(PAD_MD, PAD_MD, PAD_MD, PAD_MD)
        lay.setSpacing(6)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 26))
        icon_lbl.setStyleSheet(f"color: {accent}; background: transparent;")
        lay.addWidget(icon_lbl)

        t = QLabel(title)
        t.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_BODY, QFont.Bold))
        t.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        lay.addWidget(t)

        d = QLabel(desc)
        d.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL))
        d.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        d.setWordWrap(True)
        lay.addWidget(d)
        lay.addStretch()


# ──────────────────────────────────────────────────────────────────
#  HOME PAGE
# ──────────────────────────────────────────────────────────────────
class HomePage(QWidget):
    def __init__(self, on_start, parent=None):
        super().__init__(parent)
        self.on_start = on_start
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"background: {BG_PRIMARY};")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── TOP NAV BAR ───────────────────────────
        nav = QFrame()
        nav.setFixedHeight(60)
        nav.setStyleSheet(f"background: {BG_SECONDARY}; border-bottom: 1px solid {BORDER_COLOR};")
        nav_lay = QHBoxLayout(nav)
        nav_lay.setContentsMargins(PAD_XL, 0, PAD_XL, 0)

        logo = QLabel("⚗  Virtual Chemistry Lab")
        logo.setFont(QFont(FONT_FAMILY_HEADING, 15, QFont.Bold))
        logo.setStyleSheet(f"color: {ACCENT_CYAN}; background: transparent;")
        nav_lay.addWidget(logo)
        nav_lay.addStretch()

        ver = QLabel("v1.0  ·  B.Tech Project")
        ver.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_TINY))
        ver.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        nav_lay.addWidget(ver)
        root.addWidget(nav)

        # ── HERO SECTION ──────────────────────────
        hero = QWidget()
        hero.setStyleSheet("background: transparent;")
        hero_lay = QVBoxLayout(hero)
        hero_lay.setAlignment(Qt.AlignCenter)
        hero_lay.setSpacing(16)
        hero_lay.setContentsMargins(PAD_XXL, PAD_XXL, PAD_XXL, PAD_XL)

        flask = QLabel("⚗")
        flask.setFont(QFont("Segoe UI Emoji", 60))
        flask.setAlignment(Qt.AlignCenter)
        flask.setStyleSheet(f"color: {ACCENT_CYAN}; background: transparent;")
        hero_lay.addWidget(flask)

        h1 = QLabel("Welcome to the Virtual Chemistry Lab")
        h1.setFont(QFont(FONT_FAMILY_HEADING, FONT_SIZE_H1, QFont.Bold))
        h1.setAlignment(Qt.AlignCenter)
        h1.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        hero_lay.addWidget(h1)

        tagline = QLabel(
            "Conduct real curriculum experiments through AI-powered, gesture-controlled simulations.\n"
            "Classes 8 – 12  ·  10 Experiments  ·  Particle Physics  ·  Webcam Hand Tracking"
        )
        tagline.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_H3))
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; line-height: 1.6;")
        tagline.setWordWrap(True)
        hero_lay.addWidget(tagline)

        hero_lay.addSpacing(PAD_LG)

        btn = GlowButton("🚀  Select Your Class  →", accent=ACCENT_CYAN, height=BTN_HEIGHT_LG)
        btn.setFixedWidth(320)
        btn.clicked.connect(self.on_start)
        hero_lay.addWidget(btn, 0, Qt.AlignCenter)

        # Tags row
        tags_row = QHBoxLayout()
        tags_row.setAlignment(Qt.AlignCenter)
        tags_row.setSpacing(10)
        for tag_text, color in [
            ("MediaPipe", ACCENT_TEAL),
            ("OpenCV", ACCENT_CYAN),
            ("Particle Engine", ACCENT_ORANGE),
            ("PyQt5", ACCENT_PURPLE),
        ]:
            tags_row.addWidget(TagBadge(f"  {tag_text}  ", BG_CARD, color))
        hero_lay.addLayout(tags_row)

        root.addWidget(hero, 1)

        # ── FEATURE CARDS ─────────────────────────
        cards_container = QWidget()
        cards_container.setStyleSheet("background: transparent;")
        cards_lay = QHBoxLayout(cards_container)
        cards_lay.setAlignment(Qt.AlignCenter)
        cards_lay.setSpacing(PAD_MD)
        cards_lay.setContentsMargins(PAD_XXL, 0, PAD_XXL, PAD_XL)

        features = [
            ("🖐", "Hand Tracking",   "Grab, pour, and mix virtual reagents with real hand gestures.",     ACCENT_CYAN),
            ("⚗",  "10 Experiments",  "Full NCERT curriculum coverage from Class 8 to Class 12.",           ACCENT_TEAL),
            ("💥", "Live Reactions",  "Particle-based simulation of acid-base, flame, and other reactions.", ACCENT_ORANGE),
            ("📋", "Full Details",    "Aim, theory, apparatus, procedure, and safety for every experiment.", ACCENT_PURPLE),
            ("🎓", "Student-Friendly","Clean step-by-step guidance designed for secondary school students.", ACCENT_YELLOW),
        ]
        for icon, title, desc, accent in features:
            cards_lay.addWidget(_FeatureCard(icon, title, desc, accent))

        root.addWidget(cards_container)

        # ── FOOTER ────────────────────────────────
        footer = QFrame()
        footer.setFixedHeight(44)
        footer.setStyleSheet(f"background: {BG_SECONDARY}; border-top: 1px solid {BORDER_COLOR};")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(PAD_XL, 0, PAD_XL, 0)

        fl = QLabel("B.Tech Major Project  ·  Computer Science Department")
        fl.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_TINY))
        fl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        f_lay.addWidget(fl)
        f_lay.addStretch()

        fr = QLabel("Press  F11  for fullscreen  ·  ESC  to exit")
        fr.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_TINY))
        fr.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        f_lay.addWidget(fr)

        root.addWidget(footer)

    def paintEvent(self, e):
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0, QColor("#0A0E1A"))
        grad.setColorAt(1, QColor("#080C18"))
        painter.fillRect(self.rect(), QBrush(grad))
        painter.end()
