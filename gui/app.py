"""Desktop GUI entry point."""

from __future__ import annotations

import sys

import gui.bootstrap  # noqa: F401 — adds prog/ to sys.path

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("E7 Gear Selector")
    app.setOrganizationName("E7 Py Gear Selector")

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
