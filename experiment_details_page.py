"""
pages/experiment_details_page.py
──────────────────────────────────────────────────────────────────
Full experiment detail view showing:
  • Title + class badge
  • Aim
  • Theory
  • Apparatus list
  • Chemicals list
  • Procedure (numbered steps)
  • Safety instructions
  • "Start Simulation" button
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QBoxLayout,
    QScrollArea, QSizePolicy, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui  import QFont, QPainter, QLinearGradient, QColor, QBrush

from data.experiments import get_experiment
from utils.theme      import *
from utils.widgets    import NavBar, GlowButton, SectionCard, BulletList, TagBadge, SeparatorLine


# ──────────────────────────────────────────────────────────────────
#  INLINE LABEL HELPERS
# ──────────────────────────────────────────────────────────────────
def _h(text, font_size=FONT_SIZE_H3, color=TEXT_PRIMARY, bold=True):
    lbl = QLabel(text)
    lbl.setFont(QFont(FONT_FAMILY_HEADING if bold else FONT_FAMILY_BODY, font_size,
                      QFont.Bold if bold else QFont.Normal))
    lbl.setStyleSheet(f"color: {color}; background: transparent;")
    lbl.setWordWrap(True)
    return lbl


def _body(text, color=TEXT_SECONDARY, wrap=True):
    lbl = QLabel(text)
    lbl.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_BODY))
    lbl.setStyleSheet(f"color: {color}; background: transparent; line-height: 1.6;")
    lbl.setWordWrap(wrap)
    return lbl


# ──────────────────────────────────────────────────────────────────
#  PILL CHIP LIST  (apparatus / chemicals displayed as chips)
# ──────────────────────────────────────────────────────────────────
class ChipFlow(QWidget):
    """Wrapping flow of chip/pill widgets."""

    def __init__(self, items, accent=ACCENT_CYAN, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        lay = _FlowLayout(self, spacing=8)
        for item in items:
            chip = QLabel(f"  {item}  ")
            chip.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL))
            chip.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_PRIMARY};
                    background: {BG_PRIMARY};
                    border: 1px solid {accent};
                    border-radius: 14px;
                    padding: 4px 2px;
                }}
            """)
            lay.addWidget(chip)


class _FlowLayout(object):
    """Very simple horizontal-wrapping layout via QHBoxLayout rows."""
    def __init__(self, parent, spacing=8):
        self._parent  = parent
        self._spacing = spacing
        self._outer   = QVBoxLayout(parent)
        self._outer.setContentsMargins(0, 0, 0, 0)
        self._outer.setSpacing(spacing)
        self._row     = None
        self._new_row()

    def _new_row(self):
        row_w = QWidget()
        row_w.setStyleSheet("background: transparent;")
        self._row = QHBoxLayout(row_w)
        self._row.setContentsMargins(0, 0, 0, 0)
        self._row.setSpacing(self._spacing)
        self._row.addStretch()
        self._outer.addWidget(row_w)

    def addWidget(self, w):
        # Insert before the trailing stretch
        idx = self._row.count() - 1
        self._row.insertWidget(idx, w)


# ──────────────────────────────────────────────────────────────────
#  EXPERIMENT DETAILS PAGE
# ──────────────────────────────────────────────────────────────────
class ExperimentDetailsPage(QWidget):
    def __init__(self, exp_id, class_num, on_start, on_back, parent=None):
        super().__init__(parent)
        self.exp      = get_experiment(exp_id)
        self.class_num = class_num
        self.on_start = on_start
        self.on_back  = on_back
        self.accent   = CLASS_COLORS.get(class_num, ACCENT_CYAN)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self._root_layout = root

        exp = self.exp

        # ── NAV ─────────────────────────────────────
        nav = NavBar(exp["name"], show_back=True, accent=self.accent)
        nav.back_clicked.connect(self.on_back)
        root.addWidget(nav)

        # ── SCROLLABLE BODY ─────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QWidget#body {{ background: transparent; }}
            {SCROLLBAR_STYLE}
        """)

        body = QWidget()
        body.setObjectName("body")
        body.setStyleSheet("background: transparent;")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(PAD_XXL, PAD_XL, PAD_XXL, PAD_XL)
        body_lay.setSpacing(PAD_LG)
        self._body_layout = body_lay

        # ── HEADER HERO ──────────────────────────────
        hero_card = QFrame()
        hero_card.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border: 1px solid {self.accent};
                border-radius: {RADIUS_XL}px;
            }}
        """)
        hero_lay = QVBoxLayout(hero_card)
        hero_lay.setContentsMargins(PAD_XL, PAD_LG, PAD_XL, PAD_LG)
        hero_lay.setSpacing(10)

        # Title + class badge row
        title_row = QHBoxLayout()
        title_row.setSpacing(PAD_MD)

        title_lbl = QLabel(exp["name"])
        title_lbl.setFont(QFont(FONT_FAMILY_HEADING, FONT_SIZE_H1, QFont.Bold))
        title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        title_row.addWidget(title_lbl)

        class_badge = TagBadge(f"  Class {self.class_num}  ",
                               self.accent, BG_PRIMARY)
        title_row.addWidget(class_badge)
        title_row.addStretch()
        hero_lay.addLayout(title_row)

        # Aim
        aim_row = QHBoxLayout()
        aim_row.setSpacing(8)
        aim_icon = QLabel("🎯")
        aim_icon.setFont(QFont("Segoe UI Emoji", 14))
        aim_icon.setStyleSheet("background: transparent;")
        aim_row.addWidget(aim_icon)

        aim_txt = QLabel(exp["aim"])
        aim_txt.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_BODY))
        aim_txt.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        aim_txt.setWordWrap(True)
        aim_row.addWidget(aim_txt, 1)
        hero_lay.addLayout(aim_row)
        body_lay.addWidget(hero_card)

        # ── TWO-COLUMN ROW: apparatus + chemicals ────
        two_col = QHBoxLayout()
        two_col.setSpacing(PAD_LG)
        self._two_col_layout = two_col

        # Apparatus
        ap_card = SectionCard("Apparatus Required", self.accent)
        ap_card.add_widget(ChipFlow(exp["apparatus"], self.accent))
        two_col.addWidget(ap_card, 1)

        # Chemicals
        ch_card = SectionCard("Chemicals Required", ACCENT_ORANGE)
        ch_card.add_widget(ChipFlow(exp["chemicals"], ACCENT_ORANGE))
        two_col.addWidget(ch_card, 1)
        body_lay.addLayout(two_col)

        # ── THEORY ────────────────────────────────────
        theory_card = SectionCard("Theory", ACCENT_TEAL)
        theory_lbl = _body(exp["theory"], TEXT_PRIMARY)
        theory_lbl.setWordWrap(True)
        theory_card.add_widget(theory_lbl)
        body_lay.addWidget(theory_card)

        # ── PROCEDURE ─────────────────────────────────
        proc_card = SectionCard("Procedure", self.accent)
        proc_card.add_widget(BulletList(exp["steps"], numbered=True, accent=self.accent))
        body_lay.addWidget(proc_card)

        # ── SAFETY ────────────────────────────────────
        safety_card = SectionCard("Safety Precautions", ACCENT_ORANGE)
        safety_card.add_widget(BulletList(exp["safety"], numbered=False, accent=ACCENT_ORANGE))
        body_lay.addWidget(safety_card)

        body_lay.addStretch()
        scroll.setWidget(body)
        root.addWidget(scroll, 1)

        # ── STICKY BOTTOM ACTION BAR ─────────────────
        bar = QFrame()
        bar.setStyleSheet(f"""
            QFrame {{
                background: {BG_SECONDARY};
                border-top: 1px solid {BORDER_COLOR};
            }}
        """)
        bar_lay = QHBoxLayout(bar)
        bar_lay.setContentsMargins(PAD_XL, 0, PAD_XL, 0)
        bar_lay.setSpacing(PAD_LG)
        self._action_bar = bar
        self._action_layout = bar_lay

        info_txt = QLabel(
           f"✅ All details reviewed? Click below to launch the interactive simulation for {exp['name']}."
        )
        info_txt.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_BODY))
        info_txt.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        info_txt.setWordWrap(True)
        bar_lay.addWidget(info_txt, 1)
        self._info_txt = info_txt

        start_btn = GlowButton(
            "▶  Start Simulation",
            accent=ACCENT_TEAL,
            height=BTN_HEIGHT_LG
        )
        start_btn.setMinimumWidth(220)
        start_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        start_btn.clicked.connect(self.on_start)
        bar_lay.addWidget(start_btn)
        self._start_btn = start_btn

        root.addWidget(bar)
        self._update_responsive_layout()

    def resizeEvent(self, e):
        self._update_responsive_layout()
        super().resizeEvent(e)

    def _update_responsive_layout(self):
        width = self.width() if self.width() > 0 else 1280

        if width < 1100:
            self._body_layout.setContentsMargins(PAD_LG, PAD_LG, PAD_LG, PAD_LG)
        else:
            self._body_layout.setContentsMargins(PAD_XXL, PAD_XL, PAD_XXL, PAD_XL)

        if width < 980:
            self._two_col_layout.setDirection(QBoxLayout.TopToBottom)
        else:
            self._two_col_layout.setDirection(QBoxLayout.LeftToRight)

        if width < 1180:
            self._action_bar.setFixedHeight(124)
            self._action_layout.setDirection(QBoxLayout.TopToBottom)
            self._action_layout.setContentsMargins(PAD_LG, PAD_SM, PAD_LG, PAD_SM)
            self._start_btn.setMinimumWidth(0)
            self._start_btn.setMaximumWidth(16777215)
        else:
            self._action_bar.setFixedHeight(80)
            self._action_layout.setDirection(QBoxLayout.LeftToRight)
            self._action_layout.setContentsMargins(PAD_XL, 0, PAD_XL, 0)
            self._start_btn.setMinimumWidth(220)
            self._start_btn.setMaximumWidth(320)

    def paintEvent(self, e):
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0, QColor("#0A0E1A"))
        grad.setColorAt(1, QColor("#080C18"))
        painter.fillRect(self.rect(), QBrush(grad))
        painter.end()
