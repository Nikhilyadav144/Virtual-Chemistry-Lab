"""
pages/class_page.py
──────────────────────────────────────────────────────────────────
Class selection screen.
Renders a large card for each class (8-12) showing the class
number, a colour accent, and the count of available experiments.
Clicking a card fires on_select(class_num).
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QGraphicsDropShadowEffect
)
from PyQt5.QtCore  import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui   import QFont, QColor, QCursor, QPainter, QLinearGradient, QBrush

from data.experiments import EXPERIMENTS
from utils.theme      import *
from utils.widgets    import NavBar


# ──────────────────────────────────────────────────────────────────
#  CLASS CARD WIDGET
# ──────────────────────────────────────────────────────────────────
class ClassCard(QFrame):
    clicked = pyqtSignal(int)  # emits the class number

    _ICONS = {8: "🧪", 9: "⚗️", 10: "⚡", 11: "🔥", 12: "🧬"}
    _LABELS = {
        8:  ("Physical Science",  "Mixtures, magnetism & separation"),
        9:  ("General Chemistry", "Reactions, gases & pH"),
        10: ("Applied Chemistry", "Electrolysis & reactivity"),
        11: ("Advanced Chem I",   "Flame tests & thermochemistry"),
        12: ("Advanced Chem II",  "Titration & chromatography"),
    }

    def __init__(self, class_num, parent=None):
        super().__init__(parent)
        self.class_num = class_num
        self.accent    = CLASS_COLORS[class_num]
        n_exp          = len(EXPERIMENTS[class_num])

        self.setFixedSize(240, 300)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._apply_style(False)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(0)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)
        self._shadow = shadow

        # Layout
        lay = QVBoxLayout(self)
        lay.setContentsMargins(PAD_XL, PAD_XL, PAD_XL, PAD_LG)
        lay.setSpacing(PAD_SM)
        lay.setAlignment(Qt.AlignCenter)

        # Icon
        icon = QLabel(self._ICONS.get(class_num, "⚗"))
        icon.setFont(QFont("Segoe UI Emoji", 46))
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background: transparent;")
        lay.addWidget(icon)

        # Class number
        num = QLabel(f"Class  {class_num}")
        num.setFont(QFont(FONT_FAMILY_HEADING, FONT_SIZE_H1, QFont.Bold))
        num.setAlignment(Qt.AlignCenter)
        num.setStyleSheet(f"color: {self.accent}; background: transparent;")
        lay.addWidget(num)

        # Subject label
        subj, desc = self._LABELS[class_num]
        s_lbl = QLabel(subj)
        s_lbl.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_BODY, QFont.Bold))
        s_lbl.setAlignment(Qt.AlignCenter)
        s_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        lay.addWidget(s_lbl)

        d_lbl = QLabel(desc)
        d_lbl.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL))
        d_lbl.setAlignment(Qt.AlignCenter)
        d_lbl.setWordWrap(True)
        d_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        lay.addWidget(d_lbl)

        lay.addStretch()

        # Experiment count badge
        badge_frame = QFrame()
        badge_frame.setStyleSheet(f"""
            QFrame {{
                background: {BG_PRIMARY};
                border: 1px solid {self.accent};
                border-radius: 12px;
            }}
        """)
        badge_lay = QHBoxLayout(badge_frame)
        badge_lay.setContentsMargins(PAD_MD, 6, PAD_MD, 6)
        badge_lay.setSpacing(6)

        dot = QLabel("●")
        dot.setFont(QFont(FONT_FAMILY_BODY, 8))
        dot.setStyleSheet(f"color: {self.accent}; background: transparent;")
        badge_lay.addWidget(dot)

        badge_txt = QLabel(f"{n_exp} Experiment{'s' if n_exp != 1 else ''}")
        badge_txt.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL, QFont.Bold))
        badge_txt.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        badge_lay.addWidget(badge_txt)

        lay.addWidget(badge_frame)

    def _apply_style(self, hovered):
        bg     = BG_HOVER if hovered else BG_CARD
        border = self.accent if hovered else BORDER_COLOR
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border: 2px solid {border};
                border-radius: {RADIUS_XL}px;
            }}
        """)

    def enterEvent(self, e):
        self._apply_style(True)
        self._shadow.setBlurRadius(30)
        self._shadow.setColor(QColor(self.accent))
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._apply_style(False)
        self._shadow.setBlurRadius(0)
        self._shadow.setColor(QColor(0, 0, 0, 120))
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.class_num)


# ──────────────────────────────────────────────────────────────────
#  CLASS SELECTION PAGE
# ──────────────────────────────────────────────────────────────────
class ClassPage(QWidget):
    def __init__(self, on_select, on_back, parent=None):
        super().__init__(parent)
        self.on_select = on_select
        self.on_back   = on_back
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"background: {BG_PRIMARY};")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Nav bar
        nav = NavBar("Select Your Class", show_back=True)
        nav.back_clicked.connect(self.on_back)
        root.addWidget(nav)

        # Sub-heading
        sub_area = QWidget()
        sub_area.setStyleSheet("background: transparent;")
        sub_lay = QVBoxLayout(sub_area)
        sub_lay.setAlignment(Qt.AlignCenter)
        sub_lay.setContentsMargins(PAD_XL, PAD_XL, PAD_XL, PAD_SM)

        sub = QLabel("Choose the class you are studying in to see available experiments")
        sub.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_H3))
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        sub_lay.addWidget(sub)
        root.addWidget(sub_area)

        # Cards grid
        cards_area = QWidget()
        cards_area.setStyleSheet("background: transparent;")
        grid = QHBoxLayout(cards_area)
        grid.setAlignment(Qt.AlignCenter)
        grid.setSpacing(PAD_MD)
        grid.setContentsMargins(PAD_XL, PAD_LG, PAD_XL, PAD_XL)

        for cls in sorted(EXPERIMENTS.keys()):
            card = ClassCard(cls)
            card.clicked.connect(self.on_select)
            grid.addWidget(card)

        root.addWidget(cards_area, 1)

        # Footer hint
        hint = QLabel("Click a class card to view its experiments")
        hint.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL))
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; margin-bottom: {PAD_LG}px;")
        root.addWidget(hint)

    def paintEvent(self, e):
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0, QColor("#0A0E1A"))
        grad.setColorAt(1, QColor("#080C18"))
        painter.fillRect(self.rect(), QBrush(grad))
        painter.end()
