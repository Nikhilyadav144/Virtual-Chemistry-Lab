"""
utils/widgets.py
──────────────────────────────────────────────────────────────────
Shared custom PyQt5 widgets:
  • NavBar            — top navigation bar with back button + title
  • GlowButton        — modern accent-coloured button with hover glow
  • SectionCard       — rounded card panel for grouping content
  • TagBadge          — small coloured pill badge
  • BulletList        — styled bullet-point list widget
  • SeparatorLine     — thin horizontal rule
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QFrame, QListWidget, QListWidgetItem, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore  import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize
from PyQt5.QtGui   import QFont, QColor, QCursor

from utils.theme import *


# ──────────────────────────────────────────────────────────────────
#  NAV BAR
# ──────────────────────────────────────────────────────────────────
class NavBar(QWidget):
    back_clicked = pyqtSignal()

    def __init__(self, title="", show_back=True, accent=ACCENT_CYAN, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setStyleSheet(f"background: {BG_SECONDARY}; border-bottom: 1px solid {BORDER_COLOR};")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(PAD_LG, 0, PAD_LG, 0)

        if show_back:
            self.back_btn = QPushButton("← Back")
            self.back_btn.setFixedSize(90, 36)
            self.back_btn.setCursor(QCursor(Qt.PointingHandCursor))
            self.back_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {TEXT_SECONDARY};
                    font-family: "{FONT_FAMILY_BODY}";
                    font-size: {FONT_SIZE_BODY}pt;
                    border: 1px solid {BORDER_COLOR};
                    border-radius: {RADIUS_SM}px;
                    padding: 4px 12px;
                }}
                QPushButton:hover {{
                    background: {BG_HOVER};
                    color: {TEXT_PRIMARY};
                    border-color: {accent};
                }}
            """)
            self.back_btn.clicked.connect(self.back_clicked.emit)
            layout.addWidget(self.back_btn)
        else:
            layout.addStretch(1)

        lbl = QLabel(title)
        lbl.setFont(QFont(FONT_FAMILY_HEADING, FONT_SIZE_H3, QFont.Bold))
        lbl.setStyleSheet(f"color: {accent}; background: transparent; border: none;")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl, 1)

        # Right spacer (symmetry)
        if show_back:
            spacer = QWidget()
            spacer.setFixedWidth(90)
            spacer.setStyleSheet("background: transparent;")
            layout.addWidget(spacer)
        else:
            layout.addStretch(1)


# ──────────────────────────────────────────────────────────────────
#  GLOW BUTTON
# ──────────────────────────────────────────────────────────────────
class GlowButton(QPushButton):
    def __init__(self, text, accent=ACCENT_CYAN, height=BTN_HEIGHT_MD, parent=None):
        super().__init__(text, parent)
        self._accent = accent
        self.setFixedHeight(height)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_BODY, QFont.Bold))
        self._apply_style(False)

        self._shadow = QGraphicsDropShadowEffect()
        self._shadow.setBlurRadius(0)
        self._shadow.setColor(QColor(accent))
        self._shadow.setOffset(0, 0)
        self.setGraphicsEffect(self._shadow)

    def _apply_style(self, hovered):
        bg = self._accent if hovered else "transparent"
        txt = BG_PRIMARY if hovered else self._accent
        border = self._accent
        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {txt};
                border: 2px solid {border};
                border-radius: {RADIUS_MD}px;
                padding: 0 {PAD_LG}px;
                letter-spacing: 0.5px;
            }}
        """)

    def enterEvent(self, e):
        self._apply_style(True)
        self._shadow.setBlurRadius(20)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._apply_style(False)
        self._shadow.setBlurRadius(0)
        super().leaveEvent(e)


# ──────────────────────────────────────────────────────────────────
#  SECONDARY (GHOST) BUTTON
# ──────────────────────────────────────────────────────────────────
class GhostButton(QPushButton):
    def __init__(self, text, accent=TEXT_SECONDARY, height=BTN_HEIGHT_SM, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(height)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL))
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {accent};
                border: 1px solid {BORDER_COLOR};
                border-radius: {RADIUS_SM}px;
                padding: 0 {PAD_MD}px;
            }}
            QPushButton:hover {{
                background: {BG_HOVER};
                color: {TEXT_PRIMARY};
                border-color: {accent};
            }}
        """)


# ──────────────────────────────────────────────────────────────────
#  SECTION CARD
# ──────────────────────────────────────────────────────────────────
class SectionCard(QFrame):
    def __init__(self, title="", accent=ACCENT_CYAN, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border: 1px solid {BORDER_COLOR};
                border-radius: {RADIUS_LG}px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(PAD_LG, PAD_MD, PAD_LG, PAD_LG)
        layout.setSpacing(PAD_SM)

        if title:
            # Accent stripe + title row
            header = QWidget()
            header.setStyleSheet("background: transparent; border: none;")
            hrow = QHBoxLayout(header)
            hrow.setContentsMargins(0, 0, 0, 0)
            hrow.setSpacing(PAD_SM)

            stripe = QFrame()
            stripe.setFixedSize(4, 20)
            stripe.setStyleSheet(f"background: {accent}; border-radius: 2px; border: none;")
            hrow.addWidget(stripe)

            lbl = QLabel(title.upper())
            lbl.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL, QFont.Bold))
            lbl.setStyleSheet(f"color: {accent}; background: transparent; border: none; letter-spacing: 1px;")
            hrow.addWidget(lbl)
            hrow.addStretch()
            layout.addWidget(header)

            # Divider
            div = QFrame()
            div.setFrameShape(QFrame.HLine)
            div.setStyleSheet(f"color: {BORDER_COLOR}; background: {BORDER_COLOR}; border: none; max-height: 1px;")
            layout.addWidget(div)

        self.content_layout = layout

    def add_widget(self, w):
        self.content_layout.addWidget(w)

    def add_layout(self, l):
        self.content_layout.addLayout(l)


# ──────────────────────────────────────────────────────────────────
#  TAG BADGE
# ──────────────────────────────────────────────────────────────────
class TagBadge(QLabel):
    def __init__(self, text, bg=BG_HOVER, fg=TEXT_PRIMARY, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_TINY, QFont.Bold))
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border-radius: 10px;
                padding: 2px 10px;
            }}
        """)


# ──────────────────────────────────────────────────────────────────
#  BULLET LIST
# ──────────────────────────────────────────────────────────────────
class BulletList(QWidget):
    """Renders a list of strings as styled bullet items with optional numbering."""

    def __init__(self, items, numbered=False, accent=ACCENT_CYAN, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        for i, item in enumerate(items):
            row = QHBoxLayout()
            row.setSpacing(10)

            bullet = QLabel(f"{i+1}." if numbered else "◆")
            bullet.setFixedWidth(22 if numbered else 16)
            bullet.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL, QFont.Bold))
            bullet.setStyleSheet(f"color: {accent}; background: transparent;")
            bullet.setAlignment(Qt.AlignTop | Qt.AlignRight)
            row.addWidget(bullet)

            text = QLabel(item)
            text.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_BODY))
            text.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
            text.setWordWrap(True)
            row.addWidget(text, 1)

            layout.addLayout(row)


# ──────────────────────────────────────────────────────────────────
#  SEPARATOR LINE
# ──────────────────────────────────────────────────────────────────
class SeparatorLine(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background: {BORDER_COLOR}; border: none;")
