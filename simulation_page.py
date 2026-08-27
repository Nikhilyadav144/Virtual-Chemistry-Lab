"""
pages/simulation_page.py  (v5 — right panel fully visible)
"""

import numpy as np
import re

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QSizePolicy, QSpinBox, QButtonGroup, QComboBox, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui  import QImage, QPixmap, QFont, QCursor

from data.experiments             import (
    get_experiment, get_chemical_options, get_simulation_apparatus
)
from simulation.experiment_runner import ExperimentRunner
from simulation.apparatus         import ApparatusRegistry, LIQUID_BGR
from voice_assistant.command_registry import CommandRegistry, normalize as normalize_voice
from utils.theme                  import *


# ══════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════
def _panel_label(text, color=ACCENT_CYAN, size=FONT_SIZE_SMALL, bold=True):
    lbl = QLabel(text)
    lbl.setFont(QFont(FONT_FAMILY_BODY, size,
                      QFont.Bold if bold else QFont.Normal))
    lbl.setStyleSheet(f"color: {color}; background: transparent;")
    return lbl


def _divider():
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(f"background: {BORDER_COLOR}; border: none;")
    return f


def _chip(text, fg=TEXT_PRIMARY, bg=BG_CARD, border=BORDER_COLOR):
    lbl = QLabel(text)
    lbl.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_TINY, QFont.Bold))
    lbl.setStyleSheet(f"""
        color: {fg};
        background: {bg};
        border: 1px solid {border};
        border-radius: 10px;
        padding: 4px 10px;
    """)
    return lbl


class _IconButton(QPushButton):
    def __init__(self, text, accent=ACCENT_CYAN, parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD};
                color: {accent};
                border: 1px solid {accent};
                border-radius: 8px;
                padding: 6px 10px;
                font-size: {FONT_SIZE_SMALL}pt;
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background: {accent};
                color: {BG_PRIMARY};
            }}
        """)


# ══════════════════════════════════════════════════════════════════
#  LEFT PANEL — Apparatus
# ══════════════════════════════════════════════════════════════════
class ApparatusPanel(QFrame):
    apparatus_requested = pyqtSignal(str)

    ICONS = {
        "beaker":    "",
        "test_tube": "",
        "flask":     "",
        "dropper":   "",
        "cylinder":  "",
        "burette":   "",
        "bunsen":    "",
        "water_bath": "",
    }
    LABELS = {
        "test_tube": "Test Tube",
        "burette": "Burette",
        "cylinder": "Cylinder",
        "dropper": "Dropper",
        "beaker": "Beaker",
        "flask": "Flask",
        "bunsen": "Bunsen",
        "water_bath": "Water Bath",
    }

    def __init__(self, available=None, parent=None):
        super().__init__(parent)
        self._available = available or ApparatusRegistry.AVAILABLE
        self.setFixedWidth(112)
        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_SECONDARY};
                border-right: 1px solid {BORDER_COLOR};
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(PAD_SM, PAD_MD, PAD_SM, PAD_MD)
        lay.setSpacing(6)

        lay.addWidget(_panel_label("⚗  Apparatus", ACCENT_CYAN, FONT_SIZE_SMALL))
        lay.addWidget(_divider())
        lay.addSpacing(4)

        for atype in self._available:
            icon = self.ICONS.get(atype, "🧪")
            label = self.LABELS.get(atype, atype.replace("_", " ").title())
            btn_text = f"{icon} {label}".strip()
            btn  = _IconButton(btn_text, ACCENT_CYAN)
            btn.setFixedHeight(34)
            btn.setStyleSheet(btn.styleSheet() + f"""
                QPushButton {{
                    font-size: {FONT_SIZE_TINY}pt;
                    padding: 4px 6px;
                }}
            """)
            btn.clicked.connect(
                lambda _, t=atype: self.apparatus_requested.emit(t))
            lay.addWidget(btn)

        lay.addStretch()
        hint = QLabel("Click to add\nto the desk")
        hint.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_TINY))
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        lay.addWidget(hint)


# ══════════════════════════════════════════════════════════════════
#  RIGHT PANEL — Mode + Chemicals + Quantity
# ══════════════════════════════════════════════════════════════════
class ChemicalPanel(QFrame):
    fill_requested  = pyqtSignal(str, str, float)
    rinse_requested = pyqtSignal(str, str)
    mode_changed    = pyqtSignal(str)

    CHEM_COLORS = {
        "water":     "#00BFFF",
        "acid":      "#7FFF00",
        "base":      "#FF69B4",
        "salt":      "#FFD700",
        "indicator": "#FF8C00",
        "alcohol":   "#98FF98",
    }

    def __init__(self, chemical_options=None, parent=None):
        super().__init__(parent)
        # FIX: wider panel so nothing gets cut off
        self.setFixedWidth(186)
        self._chemical_options = chemical_options or {}
        self._selected_liquid = "water"
        self._selected_formula = "Water"
        self._selected_ml     = 20.0
        self._option_buttons  = {}

        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_SECONDARY};
                border-left: 1px solid {BORDER_COLOR};
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(7, PAD_MD, 7, PAD_MD)
        lay.setSpacing(4)

        # ── MODE TOGGLE (moved here from top bar) ──
        lay.addWidget(_panel_label("Mode", TEXT_MUTED, FONT_SIZE_TINY))
        mode_row = QHBoxLayout()
        mode_row.setSpacing(6)
        self._guided_btn = QPushButton("Guided")
        self._free_btn   = QPushButton("Free")
        for btn, active in [(self._guided_btn, True),
                            (self._free_btn,   False)]:
            btn.setFixedHeight(32)
            btn.setCheckable(True)
            btn.setChecked(active)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {BG_CARD};
                    color: {TEXT_SECONDARY};
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 6px;
                    font-size: {FONT_SIZE_SMALL}pt;
                    font-weight: bold;
                }}
                QPushButton:checked {{
                    background: {ACCENT_CYAN};
                    color: {BG_PRIMARY};
                    border-color: {ACCENT_CYAN};
                }}
                QPushButton:hover {{
                    background: {BG_HOVER};
                    color: {TEXT_PRIMARY};
                }}
            """)
        self._guided_btn.clicked.connect(
            lambda: self.mode_changed.emit("guided"))
        self._free_btn.clicked.connect(
            lambda: self.mode_changed.emit("free"))
        mode_row.addWidget(self._guided_btn)
        mode_row.addWidget(self._free_btn)
        lay.addLayout(mode_row)

        lay.addWidget(_divider())
        lay.addSpacing(2)

        # ── CHEMICALS ──────────────────────────────
        lay.addWidget(_panel_label("⚗  Chemicals", ACCENT_TEAL, FONT_SIZE_SMALL))
        lay.addWidget(_divider())
        lay.addSpacing(2)

        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        available_keys = [
            key for key in self.CHEM_COLORS
            if self._chemical_options.get(key)
        ] or list(self.CHEM_COLORS.keys())

        for i, name in enumerate(available_keys):
            color = self.CHEM_COLORS[name]
            option_count = len(self._chemical_options.get(name) or [])
            if option_count == 1:
                sample = (self._chemical_options.get(name) or [name.title()])[0]
                short_sample = sample.replace(" solution", "").replace(" Solution", "")
                btn_text = f"● {name.title()}: {short_sample}"
            else:
                btn_text = f"● {name.title()} ({option_count})"
            btn = QPushButton(btn_text)
            btn.setCheckable(True)
            btn.setFixedHeight(42)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {BG_CARD};
                    color: {color};
                    border: 1px solid {color};
                    border-radius: 7px;
                    padding: 2px 6px;
                    font-size: {FONT_SIZE_TINY}pt;
                    font-weight: bold;
                    text-align: left;
                }}
                QPushButton:checked {{
                    background: {color};
                    color: {BG_PRIMARY};
                }}
                QPushButton:hover {{
                    background: {BG_HOVER};
                }}
            """)
            btn.setToolTip(", ".join(self._chemical_options.get(name) or [name.title()]))
            btn.clicked.connect(
                lambda _, n=name: self._on_chemical_selected(n))
            self._btn_group.addButton(btn, i)
            lay.addWidget(btn)
            self._option_buttons[name] = btn
            if i == 0:
                btn.setChecked(True)
                self._selected_liquid = name

        lay.addSpacing(6)
        lay.addWidget(_panel_label("Formula / Chemical", TEXT_MUTED, FONT_SIZE_TINY))

        self._formula_combo = QComboBox()
        self._formula_combo.setStyleSheet(f"""
            QComboBox {{
                background: {BG_CARD};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 4px 8px;
                font-size: {FONT_SIZE_SMALL}pt;
            }}
            QComboBox:focus {{ border-color: {ACCENT_CYAN}; }}
            QComboBox::drop-down {{
                border: none;
                width: 22px;
            }}
        """)
        self._formula_combo.currentTextChanged.connect(self._on_formula_changed)
        lay.addWidget(self._formula_combo)
        self._refresh_formula_options()

        lay.addSpacing(6)
        lay.addWidget(_divider())
        lay.addSpacing(2)

        # ── QUANTITY ───────────────────────────────
        lay.addWidget(
            _panel_label("📏  Quantity (ml)", ACCENT_YELLOW, FONT_SIZE_SMALL))

        self._ml_spin = QSpinBox()
        self._ml_spin.setRange(1, 250)
        self._ml_spin.setValue(20)
        self._ml_spin.setSingleStep(1)
        self._ml_spin.setSuffix(" ml")
        self._ml_spin.setStyleSheet(f"""
            QSpinBox {{
                background: {BG_CARD};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 4px 6px;
                font-size: {FONT_SIZE_BODY}pt;
            }}
            QSpinBox:focus {{ border-color: {ACCENT_CYAN}; }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background: {BG_HOVER};
                width: 22px;
            }}
        """)
        self._ml_spin.valueChanged.connect(self._on_ml_changed)
        lay.addWidget(self._ml_spin)

        # Quick buttons
        quick_row = QHBoxLayout()
        quick_row.setSpacing(4)
        for ml in [2, 5, 10]:
            qb = QPushButton(f"+{ml}")
            qb.setFixedHeight(28)
            qb.setCursor(QCursor(Qt.PointingHandCursor))
            qb.setStyleSheet(f"""
                QPushButton {{
                    background: {BG_HOVER};
                    color: {ACCENT_YELLOW};
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 5px;
                    font-size: {FONT_SIZE_TINY}pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: {ACCENT_YELLOW};
                    color: {BG_PRIMARY};
                }}
            """)
            qb.clicked.connect(lambda _, m=ml: self._quick_add(m))
            quick_row.addWidget(qb)
        lay.addLayout(quick_row)

        lay.addSpacing(6)

        # Add button
        self._add_btn = QPushButton("➕  Add to Selected")
        self._add_btn.setFixedHeight(42)
        self._add_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_TEAL};
                color: {BG_PRIMARY};
                border: none;
                border-radius: 8px;
                font-size: {FONT_SIZE_BODY}pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {ACCENT_CYAN}; }}
        """)
        self._add_btn.clicked.connect(self._on_add_clicked)
        lay.addWidget(self._add_btn)

        self._rinse_btn = QPushButton("🚿  Rinse Selected")
        self._rinse_btn.setFixedHeight(38)
        self._rinse_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._rinse_btn.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD};
                color: {ACCENT_CYAN};
                border: 1px solid {ACCENT_CYAN};
                border-radius: 8px;
                font-size: {FONT_SIZE_SMALL}pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {ACCENT_CYAN};
                color: {BG_PRIMARY};
            }}
        """)
        self._rinse_btn.clicked.connect(self._on_rinse_clicked)
        lay.addWidget(self._rinse_btn)

        lay.addStretch()

        # Selected label at bottom
        self._sel_lbl = _panel_label(
            f"Selected:\n{self._selected_liquid.title()}"
            f" / {int(self._selected_ml)} ml",
            ACCENT_TEAL, FONT_SIZE_TINY
        )
        self._sel_lbl.setWordWrap(True)
        lay.addWidget(self._sel_lbl)

    def set_mode_buttons(self, mode):
        self._guided_btn.setChecked(mode == "guided")
        self._free_btn.setChecked(mode == "free")

    def _on_chemical_selected(self, name):
        self._selected_liquid = name
        self._refresh_formula_options()
        self._update_sel_label()

    def _on_formula_changed(self, text):
        self._selected_formula = text or self._selected_liquid.title()
        self._update_sel_label()

    def _on_ml_changed(self, val):
        self._selected_ml = float(val)
        self._update_sel_label()

    def _quick_add(self, ml):
        self._ml_spin.setValue(self._ml_spin.value() + ml)

    def _on_add_clicked(self):
        self.fill_requested.emit(
            self._selected_liquid,
            self._selected_formula,
            self._selected_ml,
        )

    def _on_rinse_clicked(self):
        self.rinse_requested.emit(self._selected_liquid, self._selected_formula)

    def _refresh_formula_options(self):
        options = self._chemical_options.get(self._selected_liquid) or [
            self._selected_liquid.title()
        ]
        self._formula_combo.blockSignals(True)
        self._formula_combo.clear()
        self._formula_combo.addItems(options)
        self._formula_combo.blockSignals(False)
        self._selected_formula = self._formula_combo.currentText() or options[0]

    def _update_sel_label(self):
        self._sel_lbl.setText(
            f"Selected:\n{self._selected_formula}"
            f" / {int(self._selected_ml)} ml"
        )

    def get_selected(self):
        return self._selected_liquid, self._selected_formula, self._selected_ml


# ══════════════════════════════════════════════════════════════════
#  SIMULATION CANVAS
# ══════════════════════════════════════════════════════════════════
class SimCanvas(QLabel):
    mouse_pressed  = pyqtSignal(int, int)
    mouse_moved    = pyqtSignal(int, int)
    mouse_released = pyqtSignal(int, int)
    tilt_pressed   = pyqtSignal(int, int)
    tilt_moved     = pyqtSignal(int, int)
    tilt_released  = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(360, 240)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setStyleSheet("background: #000;")
        self.setMouseTracking(True)

    def set_scale(self, fw, fh):
        self._fw = fw
        self._fh = fh

    def _map(self, qx, qy):
        if not hasattr(self, "_fw"):
            return qx, qy
        sx = self._fw / max(self.width(),  1)
        sy = self._fh / max(self.height(), 1)
        return int(qx * sx), int(qy * sy)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.mouse_pressed.emit(*self._map(e.x(), e.y()))
        elif e.button() == Qt.RightButton:
            self.tilt_pressed.emit(*self._map(e.x(), e.y()))

    def mouseMoveEvent(self, e):
        mx, my = self._map(e.x(), e.y())
        if e.buttons() & Qt.RightButton:
            self.tilt_moved.emit(mx, my)
        else:
            self.mouse_moved.emit(mx, my)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.mouse_released.emit(*self._map(e.x(), e.y()))
        elif e.button() == Qt.RightButton:
            self.tilt_released.emit(*self._map(e.x(), e.y()))


# ══════════════════════════════════════════════════════════════════
#  SIMULATION PAGE
# ══════════════════════════════════════════════════════════════════
class SimulationPage(QWidget):
    def __init__(self, exp_id, class_num, on_back, parent=None):
        super().__init__(parent)
        self.exp                 = get_experiment(exp_id)
        self.class_num           = class_num
        self._on_back            = on_back
        self._runner             = None
        self._selected_apparatus = None
        self._chemical_options   = get_chemical_options(self.exp)
        self._available_apparatus = get_simulation_apparatus(self.exp)
        self._voice_registry     = CommandRegistry()
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_top_bar())
        root.addWidget(self._build_lab_strip())

        # Middle row
        mid = QHBoxLayout()
        mid.setContentsMargins(0, 0, 0, 0)
        mid.setSpacing(0)

        self._ap_panel   = ApparatusPanel(self._available_apparatus)
        self._canvas     = SimCanvas()
        self._chem_panel = ChemicalPanel(self._chemical_options)

        ap_scroll = QScrollArea()
        ap_scroll.setWidgetResizable(True)
        ap_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        ap_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        ap_scroll.setWidget(self._ap_panel)

        chem_scroll = QScrollArea()
        chem_scroll.setWidgetResizable(True)
        chem_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        chem_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        chem_scroll.setWidget(self._chem_panel)

        mid.addWidget(ap_scroll)
        mid.addWidget(self._canvas, 1)
        mid.addWidget(chem_scroll)

        mid_w = QWidget()
        mid_w.setStyleSheet("background: transparent;")
        mid_w.setLayout(mid)
        root.addWidget(mid_w, 1)

        root.addWidget(self._build_bottom_bar())

        # Wire signals
        self._ap_panel.apparatus_requested.connect(self._on_apparatus_add)
        self._chem_panel.fill_requested.connect(self._on_fill)
        self._chem_panel.rinse_requested.connect(self._on_rinse)
        self._chem_panel.mode_changed.connect(self._set_mode)
        self._canvas.mouse_pressed.connect(self._on_mouse_press)
        self._canvas.mouse_moved.connect(self._on_mouse_move)
        self._canvas.mouse_released.connect(self._on_mouse_release)
        self._canvas.tilt_pressed.connect(self._on_tilt_press)
        self._canvas.tilt_moved.connect(self._on_tilt_move)
        self._canvas.tilt_released.connect(self._on_tilt_release)

    def _build_top_bar(self):
        bar = QFrame()
        bar.setFixedHeight(64)
        bar.setStyleSheet(f"""
            QFrame {{
                background: {BG_SECONDARY};
                border-bottom: 1px solid {BORDER_COLOR};
            }}
        """)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(PAD_MD, 0, PAD_MD, 0)
        lay.setSpacing(PAD_MD)

        # Exit button
        back = QPushButton("← Exit")
        back.setFixedSize(92, 36)
        back.setCursor(QCursor(Qt.PointingHandCursor))
        back.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SECONDARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background: {BG_HOVER};
                color: white;
                border-color: {ACCENT_ORANGE};
            }}
        """)
        back.clicked.connect(self._stop_and_back)
        lay.addWidget(back)

        # Experiment name
        exp_lbl = QLabel(f"⚗  {self.exp['name']}")
        exp_lbl.setFont(QFont(FONT_FAMILY_HEADING, 13, QFont.Bold))
        exp_lbl.setStyleSheet(f"color: {ACCENT_CYAN}; background: transparent;")
        exp_lbl.setMaximumWidth(180)
        lay.addWidget(exp_lbl)

        class_chip = _chip(
            f"Class {self.class_num}",
            fg=BG_PRIMARY,
            bg=CLASS_COLORS.get(self.class_num, ACCENT_CYAN),
            border=CLASS_COLORS.get(self.class_num, ACCENT_CYAN),
        )
        lay.addWidget(class_chip)

        demo_chip = _chip(
            "Live Lab",
            fg=ACCENT_TEAL,
            bg=BG_CARD,
            border=ACCENT_TEAL,
        )
        lay.addWidget(demo_chip)

        lay.addStretch()

        # Step info — centre of top bar
        step_col = QVBoxLayout()
        step_col.setSpacing(2)
        self._step_lbl = QLabel("Loading experiment…")
        self._step_lbl.setFont(
            QFont(FONT_FAMILY_BODY, FONT_SIZE_BODY, QFont.Bold))
        self._step_lbl.setStyleSheet(
            f"color: {TEXT_PRIMARY}; background: transparent;")
        self._step_lbl.setAlignment(Qt.AlignCenter)
        self._step_lbl.setWordWrap(True)
        self._step_lbl.setMaximumWidth(360)

        self._prog_lbl = QLabel("")
        self._prog_lbl.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL))
        self._prog_lbl.setStyleSheet(
            f"color: {ACCENT_TEAL}; background: transparent;")
        self._prog_lbl.setAlignment(Qt.AlignCenter)

        step_col.addWidget(self._step_lbl)
        step_col.addWidget(self._prog_lbl)
        lay.addLayout(step_col)

        lay.addStretch()

        self._delete_btn = QPushButton("Delete")
        self._delete_btn.setFixedHeight(36)
        self._delete_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._delete_btn.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD};
                color: {ACCENT_ORANGE};
                border: 1px solid {ACCENT_ORANGE};
                border-radius: 8px;
                padding: 0 12px;
                font-size: {FONT_SIZE_SMALL}pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {ACCENT_ORANGE}; color: {BG_PRIMARY}; }}
        """)
        self._delete_btn.clicked.connect(self._delete_selected)
        lay.addWidget(self._delete_btn)

        self._undo_btn = QPushButton("Undo")
        self._undo_btn.setFixedHeight(36)
        self._undo_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._undo_btn.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD};
                color: {ACCENT_CYAN};
                border: 1px solid {ACCENT_CYAN};
                border-radius: 8px;
                padding: 0 12px;
                font-size: {FONT_SIZE_SMALL}pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {ACCENT_CYAN}; color: {BG_PRIMARY}; }}
        """)
        self._undo_btn.clicked.connect(self._undo_action)
        lay.addWidget(self._undo_btn)

        self._redo_btn = QPushButton("Redo")
        self._redo_btn.setFixedHeight(36)
        self._redo_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._redo_btn.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD};
                color: {ACCENT_YELLOW};
                border: 1px solid {ACCENT_YELLOW};
                border-radius: 8px;
                padding: 0 12px;
                font-size: {FONT_SIZE_SMALL}pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {ACCENT_YELLOW}; color: {BG_PRIMARY}; }}
        """)
        self._redo_btn.clicked.connect(self._redo_action)
        lay.addWidget(self._redo_btn)

        self._next_step_btn = QPushButton("Next Step")
        self._next_step_btn.setFixedHeight(36)
        self._next_step_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._next_step_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_TEAL};
                color: {BG_PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 0 14px;
                font-size: {FONT_SIZE_SMALL}pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {ACCENT_CYAN}; }}
            QPushButton:disabled {{
                background: {BG_HOVER};
                color: {TEXT_MUTED};
            }}
        """)
        self._next_step_btn.clicked.connect(self._advance_step)
        lay.addWidget(self._next_step_btn)

        return bar

    def _build_lab_strip(self):
        bar = QFrame()
        bar.setFixedHeight(46)
        bar.setStyleSheet(f"""
            QFrame {{
                background: {BG_PRIMARY};
                border-bottom: 1px solid {BORDER_COLOR};
            }}
        """)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(PAD_MD, 6, PAD_MD, 6)
        lay.setSpacing(8)

        label = QLabel("Reagent Shelf")
        label.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL, QFont.Bold))
        label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        lay.addWidget(label)

        chemical_colors = {
            "water": ACCENT_CYAN,
            "acid": ACCENT_GREEN,
            "base": ACCENT_PINK,
            "salt": ACCENT_YELLOW,
            "indicator": ACCENT_ORANGE,
            "alcohol": ACCENT_TEAL,
        }
        for category, items in self._chemical_options.items():
            if not items:
                continue
            names = ", ".join(items[:2])
            if len(items) > 2:
                names += f" +{len(items) - 2}"
            lay.addWidget(
                _chip(
                    names,
                    fg=chemical_colors.get(category, TEXT_PRIMARY),
                    bg=BG_CARD,
                    border=chemical_colors.get(category, BORDER_COLOR),
                )
            )

        lay.addStretch()
        return bar

    def _build_bottom_bar(self):
        bar = QFrame()
        bar.setFixedHeight(64)
        bar.setStyleSheet(f"""
            QFrame {{
                background: {BG_SECONDARY};
                border-top: 1px solid {BORDER_COLOR};
            }}
        """)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(PAD_LG, 0, PAD_LG, 0)
        lay.setSpacing(PAD_MD)

        self._selected_card = QLabel("No apparatus selected")
        self._selected_card.setMinimumWidth(290)
        self._selected_card.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL, QFont.Bold))
        self._selected_card.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            background: {BG_CARD};
            border: 1px solid {BORDER_COLOR};
            border-radius: 10px;
            padding: 8px 12px;
        """)
        lay.addWidget(self._selected_card)

        hint = QLabel(
            "🟢 Pinch to grab  ·  Hold above container to pour  ·  Right-click = manual tilt")
        hint.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_SMALL))
        hint.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        lay.addWidget(hint)

        lay.addStretch()

        self._ml_lbl = QLabel("")
        self._ml_lbl.setMaximumWidth(360)
        self._ml_lbl.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self._ml_lbl.setFont(
            QFont(FONT_FAMILY_BODY, FONT_SIZE_BODY, QFont.Bold))
        self._ml_lbl.setStyleSheet(
            f"color: {ACCENT_TEAL}; background: transparent;")
        lay.addWidget(self._ml_lbl)

        lay.addStretch()

        self._status_lbl = QLabel(
            "Select apparatus from the left panel to begin")
        self._status_lbl.setMaximumWidth(420)
        self._status_lbl.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self._status_lbl.setFont(QFont(FONT_FAMILY_BODY, FONT_SIZE_BODY))
        self._status_lbl.setStyleSheet(
            f"color: {TEXT_PRIMARY}; background: transparent;")
        lay.addWidget(self._status_lbl)

        return bar

    # ── LIFECYCLE ─────────────────────────────────
    def showEvent(self, e):
        self._start_runner()
        super().showEvent(e)

    def hideEvent(self, e):
        self._stop_runner()
        super().hideEvent(e)

    def resizeEvent(self, e):
        width = self.width()
        if width < 1350:
            self._ap_panel.setFixedWidth(102)
            self._chem_panel.setFixedWidth(168)
        elif width < 1500:
            self._ap_panel.setFixedWidth(108)
            self._chem_panel.setFixedWidth(174)
        else:
            self._ap_panel.setFixedWidth(112)
            self._chem_panel.setFixedWidth(182)
        super().resizeEvent(e)

    # ── RUNNER CONTROL ────────────────────────────
    def _start_runner(self):
        if self._runner and self._runner.isRunning():
            return
        scr = self.screen()
        fw  = scr.size().width()
        fh  = scr.size().height()
        self._canvas.set_scale(fw, fh)

        self._runner = ExperimentRunner(self.exp, fw, fh, mode="guided")
        self._runner.frame_ready.connect(self._on_frame)
        self._runner.status_update.connect(self._on_status)
        self._runner.step_update.connect(self._on_step)
        self._runner.ml_update.connect(self._on_ml)
        self._runner.start()

    def _stop_runner(self):
        if self._runner:
            self._runner.stop()
            self._runner.wait(3000)
            self._runner = None

    def _stop_and_back(self):
        self._stop_runner()
        self._on_back()

    # ── SIGNAL HANDLERS ───────────────────────────
    def _on_frame(self, rgb):
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img).scaled(
            max(1, self._canvas.width()), max(1, self._canvas.height()),
            Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self._canvas.setPixmap(pix)
        self._sync_selection_from_gesture()
        self._refresh_selected_card()

    def _on_status(self, msg):
        self._status_lbl.setText(msg)

    def _on_step(self, desc, prog):
        self._step_lbl.setText(desc)
        self._prog_lbl.setText(prog)
        if self._runner and self._runner.step_mgr.completed:
            self._next_step_btn.setDisabled(True)
            self._next_step_btn.setText("Completed")
        else:
            self._next_step_btn.setDisabled(False)
            self._next_step_btn.setText("Next Step")

    def _on_ml(self, txt):
        self._ml_lbl.setText(txt)

    def _on_apparatus_add(self, atype):
        if self._runner:
            a = self._runner.add_apparatus(atype)
            self._selected_apparatus = a
            self._refresh_selected_card()

    def _on_fill(self, liquid_name, formula_name, amount_ml):
        if self._runner:
            if self._selected_apparatus:
                self._runner.fill_apparatus(
                    self._selected_apparatus, liquid_name, amount_ml,
                    display_name=formula_name)
            elif self._runner.apparatus_list:
                a = self._runner.apparatus_list[-1]
                self._runner.fill_apparatus(
                    a, liquid_name, amount_ml, display_name=formula_name)
            self._runner.set_selected_liquid(liquid_name)
            self._runner.set_selected_ml(amount_ml)

    def _on_rinse(self, liquid_name, formula_name):
        if self._runner and self._selected_apparatus:
            self._runner.rinse_apparatus(
                self._selected_apparatus,
                liquid_name=liquid_name,
                display_name=formula_name,
            )
        else:
            self._on_status("Select an apparatus first to rinse it")

    def _on_mouse_press(self, mx, my):
        if self._runner:
            self._runner.mouse_press(mx, my)
            for a in reversed(self._runner.apparatus_list):
                if a.near_enough(mx, my):
                    self._selected_apparatus = a
                    self._on_status(f"Selected: {a.atype.title()}")
                    self._refresh_selected_card()
                    break

    def _on_mouse_move(self, mx, my):
        if self._runner:
            self._runner.mouse_move(mx, my)

    def _on_mouse_release(self, mx, my):
        if self._runner:
            self._runner.mouse_release(mx, my)
            if self._selected_apparatus and self._selected_apparatus not in self._runner.apparatus_list:
                self._selected_apparatus = None
            self._refresh_selected_card()

    def _on_tilt_press(self, mx, my):
        if self._runner:
            self._runner.mouse_tilt_press(mx, my)
            for a in reversed(self._runner.apparatus_list):
                if a.near_enough(mx, my):
                    self._selected_apparatus = a
                    self._refresh_selected_card()
                    break

    def _on_tilt_move(self, mx, my):
        if self._runner:
            self._runner.mouse_tilt_move(mx, my)

    def _on_tilt_release(self, mx, my):
        if self._runner:
            self._runner.mouse_tilt_release(mx, my)
            self._refresh_selected_card()

    def _set_mode(self, mode):
        if self._runner:
            self._runner.set_mode(mode)
        self._chem_panel.set_mode_buttons(mode)
        self._next_step_btn.setVisible(mode == "guided")
        self._on_status(f"Mode: {mode.title()}")

    def _advance_step(self):
        if self._runner:
            self._runner.next_step()
            step = self._runner.step_mgr.current_step()
            if step:
                self._on_step(step.description(), self._runner.step_mgr.progress_text())
            else:
                self._on_step("Experiment complete", self._runner.step_mgr.progress_text())

    def _delete_selected(self):
        if not self._runner or not self._selected_apparatus:
            self._on_status("Select an apparatus first to delete it")
            return
        removed = self._runner.remove_apparatus(self._selected_apparatus)
        if removed:
            self._selected_apparatus = self._runner.apparatus_list[-1] if self._runner.apparatus_list else None
            self._refresh_selected_card()

    def _undo_action(self):
        if not self._runner:
            return
        if self._runner.undo():
            self._selected_apparatus = self._runner.apparatus_list[-1] if self._runner.apparatus_list else None
            self._refresh_selected_card()

    def _redo_action(self):
        if not self._runner:
            return
        if self._runner.redo():
            self._selected_apparatus = self._runner.apparatus_list[-1] if self._runner.apparatus_list else None
            self._refresh_selected_card()

    def _refresh_selected_card(self):
        if not self._selected_apparatus:
            self._selected_card.setText("No apparatus selected")
            return

        apparatus = self._selected_apparatus
        liquid = apparatus.liquid
        if liquid.is_empty():
            liquid_text = "Empty"
        else:
            liquid_text = (
                f"{liquid.display_name} · {liquid.amount_ml:.0f} ml · "
                f"pH {apparatus.mixture.pH:.1f} · {apparatus.mixture.temperature:.0f}°C"
            )

        self._selected_card.setText(
            f"Selected: {apparatus.atype.replace('_', ' ').title()}    |    {liquid_text}"
        )

    def _sync_selection_from_gesture(self):
        if not self._runner:
            return
        for apparatus in reversed(self._runner.apparatus_list):
            if apparatus.grabbed in ("Left", "Right"):
                self._selected_apparatus = apparatus
                return

    def handle_voice_command(self, command):
        intent = command.intent
        target = command.target
        if intent == "select":
            return self._voice_select(target)
        if intent == "add":
            return self._voice_add(target)
        if intent == "remove":
            return self._voice_remove(target)
        if intent == "set_mode":
            self._set_mode(target)
            return f"{target.title()} mode enabled."
        if intent == "reset":
            self._stop_runner()
            self._selected_apparatus = None
            self._start_runner()
            return "Experiment reset."
        if intent == "pause":
            self._stop_runner()
            return "Simulation paused."
        if intent == "resume":
            self._start_runner()
            return "Simulation resumed."
        if intent == "next_step":
            self._advance_step()
            return "Moving to the next guided step."
        if intent == "undo":
            self._undo_action()
            return "Undo applied."
        if intent == "redo":
            self._redo_action()
            return "Redo applied."
        if intent == "rinse_selected":
            liquid, formula, _amount = self._chem_panel.get_selected()
            self._on_rinse(liquid, formula)
            return "Selected apparatus rinsed."
        if intent == "heat_selected":
            return self._voice_heat_selected()
        if intent == "tutor":
            return self._voice_tutor(target)
        return "I did not understand that simulation command."

    def _voice_select(self, target):
        if self._voice_select_apparatus(target):
            return f"{target.title()} selected."
        if self._voice_select_chemical(target):
            return f"{self._chem_panel.get_selected()[1]} selected."
        return f"I could not find {target} here."

    def _voice_add(self, target):
        apparatus_key = self._match_apparatus_key(target)
        if apparatus_key:
            self._on_apparatus_add(apparatus_key)
            return f"{apparatus_key.replace('_', ' ').title()} added to workspace."
        if self._voice_select_chemical(target):
            liquid, formula, amount = self._chem_panel.get_selected()
            self._on_fill(liquid, formula, amount)
            return f"Added {formula}."
        return f"I could not add {target}."

    def _voice_remove(self, target):
        if not self._runner:
            return "Simulation is not running."
        key = self._match_apparatus_key(target)
        for apparatus in reversed(self._runner.apparatus_list):
            if key == apparatus.atype or target.lower() in apparatus.atype.replace("_", " "):
                self._selected_apparatus = apparatus
                self._delete_selected()
                return f"Removed {apparatus.atype.replace('_', ' ')}."
        return f"I could not find {target} to remove."

    def _voice_select_apparatus(self, target):
        if not self._runner:
            return False
        key = self._match_apparatus_key(target)
        for apparatus in reversed(self._runner.apparatus_list):
            label = apparatus.atype.replace("_", " ")
            if key == apparatus.atype or target.lower() in label:
                self._selected_apparatus = apparatus
                self._refresh_selected_card()
                self._on_status(f"Selected: {apparatus.atype.title()}")
                return True
        return False

    def _voice_select_chemical(self, target):
        target_norm = normalize_voice(target)
        alias_match = self._voice_registry.match_chemical_alias(target)
        alias_terms = [alias_match.canonical] if alias_match else []
        alias_terms.append(target_norm)
        for category, options in self._chemical_options.items():
            for option in options:
                option_norm = normalize_voice(option)
                if any(term and (term in option_norm or option_norm in term) for term in alias_terms):
                    self._chem_panel._on_chemical_selected(category)
                    index = self._chem_panel._formula_combo.findText(option)
                    if index >= 0:
                        self._chem_panel._formula_combo.setCurrentIndex(index)
                    return True
        aliases = {
            "hydrochloric acid": "hcl",
            "hcl": "hcl",
            "sodium hydroxide": "naoh",
            "naoh": "naoh",
            "phenolphthalein": "phenolphthalein",
            "water": "water",
        }
        alias = aliases.get(target_norm)
        if alias:
            for category, options in self._chemical_options.items():
                for option in options:
                    if alias in self._norm(option):
                        self._chem_panel._on_chemical_selected(category)
                        index = self._chem_panel._formula_combo.findText(option)
                        if index >= 0:
                            self._chem_panel._formula_combo.setCurrentIndex(index)
                        return True
        return False

    def _voice_heat_selected(self):
        self._sync_selection_from_gesture()
        if not self._selected_apparatus:
            return "Select an apparatus first."
        self._selected_apparatus.mixture.temperature += 5.0
        if self._runner:
            self._runner.step_mgr.notify_heat(self._selected_apparatus.atype)
        self._refresh_selected_card()
        return f"Heating {self._selected_apparatus.atype.replace('_', ' ')}."

    def _voice_tutor(self, target):
        text = target.lower()
        if "pink" in text:
            return "Phenolphthalein is pink in base and colorless after neutralization."
        if "neutralization" in text:
            return "Neutralization forms salt and water when acid and base react."
        if "titration" in text:
            return "Titration uses a known solution from the burette to find an unknown concentration."
        step = self._step_lbl.text()
        return step or "I can explain the current guided step."

    def _match_apparatus_key(self, target):
        metadata_key = None
        if hasattr(target, "metadata") and target.metadata:
            metadata_key = target.metadata.get("apparatus")
        match = self._voice_registry.match_apparatus(str(target))
        if metadata_key:
            return metadata_key
        if match:
            return match.canonical
        return None

    def _norm(self, text):
        return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
