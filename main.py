from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app_window import MainWindow
from theme import apply_theme, current_theme
from version import APP_NAME, APP_VERSION


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("DataMobile")
    apply_theme(app, current_theme())
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
