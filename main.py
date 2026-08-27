"""
main.py
──────────────────────────────────────────────────────────────────
Application entry point.
"""

import sys
import os
from pathlib import Path

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"

try:
    import PyQt5
    _pyqt_root = Path(PyQt5.__file__).resolve().parent
    _platforms = _pyqt_root / "Qt5" / "plugins" / "platforms"
    if _platforms.exists():
        os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", str(_platforms))
except Exception:
    pass

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QShortcut, QWidget, QVBoxLayout,
    QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui  import QFont, QKeySequence, QCursor

from utils.theme                     import *
from pages.splash_page               import SplashPage
from pages.home_page                 import HomePage
from pages.class_page                import ClassPage
from pages.experiment_list_page      import ExperimentListPage
from pages.experiment_details_page   import ExperimentDetailsPage
from pages.simulation_page           import SimulationPage
from voice_assistant.assistant       import AtomAssistant
from voice_assistant.atom_panel      import AtomPanel
from voice_assistant.atom_overlay    import AtomOverlay


IDX_SPLASH   = 0
IDX_HOME     = 1
IDX_CLASS    = 2
IDX_EXP_LIST = 3
IDX_EXP_DET  = 4
IDX_SIM      = 5


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virtual Chemistry Lab")

        self._atom_overlay = None
        self._atom_launcher = None

        # ── Maximize to fill screen, keep macOS menu bar ──
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen)
        self.setMinimumSize(1024, 700)
        self.setMaximumSize(screen.width(), screen.height())
        self.showMaximized()

        self._chosen_class  = None
        self._chosen_exp_id = None

        self.stack = QStackedWidget()
        self._atom_panel = AtomPanel()
        shell = QWidget()
        shell_lay = QVBoxLayout(shell)
        shell_lay.setContentsMargins(0, 0, 0, 0)
        shell_lay.setSpacing(0)
        shell_lay.addWidget(self.stack, 1)
        shell_lay.addWidget(self._atom_panel)
        self.setCentralWidget(shell)
        self._atom_overlay = AtomOverlay(self)
        self._atom_launcher = self._build_atom_launcher()
        self._position_atom_overlay()

        self._splash = SplashPage(on_done=self._go_home)
        self._home   = HomePage(on_start=self._go_class)
        self._class  = ClassPage(
            on_select=self._go_exp_list,
            on_back=self._go_home
        )

        self.stack.insertWidget(IDX_SPLASH,   self._splash)
        self.stack.insertWidget(IDX_HOME,     self._home)
        self.stack.insertWidget(IDX_CLASS,    self._class)
        self.stack.insertWidget(IDX_EXP_LIST, QStackedWidget())
        self.stack.insertWidget(IDX_EXP_DET,  QStackedWidget())
        self.stack.insertWidget(IDX_SIM,      QStackedWidget())

        self.stack.setCurrentIndex(IDX_SPLASH)

        # Keyboard shortcuts
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.close)
        QShortcut(QKeySequence(Qt.Key_F11),    self, self._toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+Q"),      self, self.close)

        self._atom = AtomAssistant(self, self)
        self._atom.activated.connect(self._atom_overlay.wake)
        self._atom.transcript.connect(self._atom_panel.set_transcript)
        self._atom.transcript.connect(self._atom_overlay.set_transcript)
        self._atom.response.connect(self._atom_panel.set_response)
        self._atom.response.connect(self._atom_overlay.set_response)
        self._atom.status.connect(self._atom_panel.set_status)
        self._atom.status.connect(self._atom_overlay.set_status)
        self._atom_panel.typed_command.connect(self._atom.handle_text)
        self._atom_panel.atom_requested.connect(self._atom.activate)
        self._atom_launcher.clicked.connect(self._atom.activate)
        self._atom_overlay.listen_requested.connect(self._atom.activate)
        self._atom.start()

    def _build_atom_launcher(self):
        btn = QPushButton("🎙  Atom", self)
        btn.setFixedSize(118, 42)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setToolTip("Open Atom assistant")
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_TEAL};
                color: {BG_PRIMARY};
                border: 1px solid {ACCENT_CYAN};
                border-radius: 21px;
                font-size: {FONT_SIZE_SMALL}pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {ACCENT_CYAN};
                border-color: {ACCENT_TEAL};
            }}
        """)
        btn.raise_()
        btn.show()
        return btn

    def _toggle_fullscreen(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self._position_atom_overlay()

    def resizeEvent(self, event):
        self._position_atom_overlay()
        super().resizeEvent(event)

    def _position_atom_overlay(self):
        overlay = getattr(self, "_atom_overlay", None)
        launcher = getattr(self, "_atom_launcher", None)
        if overlay:
            x = max(20, (self.width() - self._atom_overlay.width()) // 2)
            y = max(60, int(self.height() * 0.16))
            self._atom_overlay.move(x, y)
        if launcher:
            x = max(20, self.width() - launcher.width() - 24)
            y = max(92, min(self.height() - launcher.height() - 96, int(self.height() * 0.28)))
            launcher.move(x, y)
            launcher.raise_()

    def _go_home(self):
        self.stack.setCurrentIndex(IDX_HOME)

    def _go_class(self):
        self.stack.setCurrentIndex(IDX_CLASS)

    def _go_exp_list(self, class_num: int):
        self._chosen_class = class_num
        page = ExperimentListPage(
            class_num=class_num,
            on_select=self._go_exp_details,
            on_back=self._go_class
        )
        old = self.stack.widget(IDX_EXP_LIST)
        self.stack.removeWidget(old)
        old.deleteLater()
        self.stack.insertWidget(IDX_EXP_LIST, page)
        self.stack.setCurrentIndex(IDX_EXP_LIST)

    def _go_exp_details(self, exp_id: str):
        self._chosen_exp_id = exp_id
        page = ExperimentDetailsPage(
            exp_id=exp_id,
            class_num=self._chosen_class,
            on_start=self._go_simulation,
            on_back=lambda: self.stack.setCurrentIndex(IDX_EXP_LIST)
        )
        old = self.stack.widget(IDX_EXP_DET)
        self.stack.removeWidget(old)
        old.deleteLater()
        self.stack.insertWidget(IDX_EXP_DET, page)
        self.stack.setCurrentIndex(IDX_EXP_DET)

    def _go_simulation(self):
        page = SimulationPage(
            exp_id=self._chosen_exp_id,
            class_num=self._chosen_class,
            on_back=lambda: self.stack.setCurrentIndex(IDX_EXP_DET)
        )
        old = self.stack.widget(IDX_SIM)
        self.stack.removeWidget(old)
        old.deleteLater()
        self.stack.insertWidget(IDX_SIM, page)
        self.stack.setCurrentIndex(IDX_SIM)

    def current_simulation_page(self):
        if self.stack.currentIndex() != IDX_SIM:
            return None
        page = self.stack.widget(IDX_SIM)
        return page if isinstance(page, SimulationPage) else None

    def closeEvent(self, event):
        if hasattr(self, "_atom"):
            self._atom.stop()
        super().closeEvent(event)


def main():
    # Must be set before QApplication is created
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Virtual Chemistry Lab")
    app.setOrganizationName("BTech CS Project")

    app.setStyleSheet(f"""
        * {{
            font-family: "{FONT_FAMILY_BODY}";
            font-size: {FONT_SIZE_BODY}pt;
            color: {TEXT_PRIMARY};
        }}
        QMainWindow {{
            background: {BG_PRIMARY};
        }}
        QStackedWidget {{
            background: {BG_PRIMARY};
        }}
        {TOOLTIP_STYLE}
        {SCROLLBAR_STYLE}
    """)

    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
