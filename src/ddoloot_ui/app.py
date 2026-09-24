"""Application entry point."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ddoloot_ui.main_window import MainWindow
from ddoloot_ui.theme import STYLESHEET


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("DDOLoot")
    app.setOrganizationName("DDOLoot")
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
