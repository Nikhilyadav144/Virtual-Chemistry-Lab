"""
pages/experiment_list_page.py
──────────────────────────────────────────────────────────────────
Shows the list of experiments available for a chosen class.
Each experiment is shown as a clickable card with its name,
a short aim excerpt, and an apparatus count badge.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtCore  import Qt, pyqtSignal
from PyQt5.QtGui   import QFont, QColor, QCursor, QPainter, QLinearGradient, QBrush

from data.experiments import get_experiments
from utils.theme      import *
from utils.widgets    import NavBar, TagBadge


# ──────────────────────────────────────────────────────────────────
#  EXPERIMENT CARD
# ──────────────────────────────────────────────────────────────────
class ExpCard(QFrame):
    clicked = pyqtSignal(str)   # emits experiment ID

    def __init__(self, exp_data, accent, parent=None):
        super().__init__(parent)
        self.exp_id = exp_data["id"]
        self.accent = accent
        self._apply_style(False)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedHeight(130)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(0)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)
        self._shadow = shadow

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, PAD_LG, 0)
        lay.setSpacing(0)

        # Left accent stripe
        stripe = QFrame()
        stripe.setFixedWidth(5)
        stripe.setStyleSheet(f"background: {accent}; border-radius: 3px; border: none;")
        lay.addWidget(stripe)

        lay.addSpacing(PAD_LG)

        # Text block
        text_block = QVBoxLayout()
        text_block.setSpacing(6)
        text_block.setContentsMargins(0, PAD_MD, 0, PAD_MD)

        name = QLabel(exp_data["name"])
        name.setFont(QFont(FONT_FAMILY_HEADING, FONT_SIZE_H3, QFont.Bold))
        name.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        text_block.addWidget(name)

        aim_short = exp_data["aim"][:100] + ("…" if len(exp_data["aim"]) > 100 else "")
        aim_lbl = QLabel(aim_short)
        aim_lbl.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL))
        aim_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        aim_lbl.setWordWrap(True)
        text_block.addWidget(aim_lbl)

        # Bottom row: tags
        tags_row = QHBoxLayout()
        tags_row.setSpacing(8)
        tags_row.addWidget(TagBadge(
            f"  🔬 {len(exp_data['apparatus'])} apparatus  ",
            BG_PRIMARY, accent
        ))
        tags_row.addWidget(TagBadge(
            f"  ⚗ {len(exp_data['chemicals'])} chemicals  ",
            BG_PRIMARY, TEXT_SECONDARY
        ))
        tags_row.addWidget(TagBadge(
            f"  📋 {len(exp_data['steps'])} steps  ",
            BG_PRIMARY, TEXT_SECONDARY
        ))
        tags_row.addStretch()
        text_block.addLayout(tags_row)
        lay.addLayout(text_block, 1)

        # Right arrow
        arrow = QLabel("›")
        arrow.setFont(QFont(FONT_FAMILY_BODY, 28))
        arrow.setStyleSheet(f"color: {accent}; background: transparent;")
        arrow.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        lay.addWidget(arrow)

    def _apply_style(self, hovered):
        bg     = BG_HOVER if hovered else BG_CARD
        border = self.accent if hovered else BORDER_COLOR
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border: 1px solid {border};
                border-radius: {RADIUS_LG}px;
            }}
        """)

    def enterEvent(self, e):
        self._apply_style(True)
        self._shadow.setBlurRadius(20)
        self._shadow.setColor(QColor(self.accent))
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._apply_style(False)
        self._shadow.setBlurRadius(0)
        self._shadow.setColor(QColor(0, 0, 0, 100))
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.exp_id)


# ──────────────────────────────────────────────────────────────────
#  EXPERIMENT LIST PAGE
# ──────────────────────────────────────────────────────────────────
class ExperimentListPage(QWidget):
    def __init__(self, class_num, on_select, on_back, parent=None):
        super().__init__(parent)
        self.class_num = class_num
        self.on_select = on_select
        self.on_back   = on_back
        self.accent    = CLASS_COLORS.get(class_num, ACCENT_CYAN)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Nav
        nav = NavBar(f"Class {self.class_num}  ·  Experiments", show_back=True, accent=self.accent)
        nav.back_clicked.connect(self.on_back)
        root.addWidget(nav)

        # Sub heading
        exps = get_experiments(self.class_num)
        sub_row = QHBoxLayout()
        sub_row.setContentsMargins(PAD_XL, PAD_LG, PAD_XL, PAD_SM)

        sub_lbl = QLabel(f"{len(exps)} experiment{'s' if len(exps) != 1 else ''} available for Class {self.class_num}")
        sub_lbl.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_H3))
        sub_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        sub_row.addWidget(sub_lbl)
        sub_row.addStretch()

        hint = QLabel("Click an experiment to view full details")
        hint.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL))
        hint.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        sub_row.addWidget(hint)

        sub_widget = QWidget()
        sub_widget.setStyleSheet("background: transparent;")
        sub_widget.setLayout(sub_row)
        root.addWidget(sub_widget)

        # Scrollable list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QWidget#scroll_content {{
                background: transparent;
            }}
            {SCROLLBAR_STYLE}
        """)

        scroll_content = QWidget()
        scroll_content.setObjectName("scroll_content")
        scroll_content.setStyleSheet("background: transparent;")
        list_lay = QVBoxLayout(scroll_content)
        list_lay.setContentsMargins(PAD_XL, PAD_MD, PAD_XL, PAD_XL)
        list_lay.setSpacing(PAD_MD)

        for exp in exps:
            card = ExpCard(exp, self.accent)
            card.clicked.connect(self.on_select)
            list_lay.addWidget(card)

        list_lay.addStretch()
        scroll.setWidget(scroll_content)
        root.addWidget(scroll, 1)

    def paintEvent(self, e):
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0, QColor("#0A0E1A"))
        grad.setColorAt(1, QColor("#080C18"))
        painter.fillRect(self.rect(), QBrush(grad))
        painter.end()
