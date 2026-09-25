from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtCore import QCoreApplication, QMimeData, QPoint, QSettings, Qt, QUrl
    from PySide6.QtGui import QDragEnterEvent, QDropEvent
    from PySide6.QtWidgets import QApplication
except ImportError:  # pragma: no cover - GUI tests need PySide6
    QApplication = None


@unittest.skipIf(QApplication is None, "PySide6 is not installed")
class MainWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._settings_dir = tempfile.TemporaryDirectory()
        QSettings.setDefaultFormat(QSettings.IniFormat)
        QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, cls._settings_dir.name)
        cls.app = QApplication.instance() or QApplication([])
        QCoreApplication.setOrganizationName("DataMobileTests")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._settings_dir.cleanup()

    def setUp(self) -> None:
        from app_window import MainWindow

        self.window = MainWindow()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.select_format("Склады")

    def select_format(self, display_name: str) -> None:
        combo = self.window._format_combo
        combo.setCurrentIndex(combo.findText(display_name))

    def write_file(self, text: str, name: str = "example.dm") -> Path:
        path = Path(self.temp_dir.name) / name
        path.write_text(text, encoding="utf-8")
        return path

    def output_text(self) -> str:
        return self.window._output.toPlainText()

    def test_file_is_decoded_right_after_selection(self) -> None:
        self.window.open_file(self.write_file("1\n+\n1;+;Основной склад"))

        self.assertIn("Основной склад", self.output_text())
        self.assertIn("добавить / обновить", self.output_text())
        self.assertTrue(self.window._copy_button.isEnabled())

    def test_changing_format_decodes_again(self) -> None:
        self.window.open_file(self.write_file("1\n+\n1;+;Основной склад"))
        self.select_format("Ячейки")

        self.assertIn("Ячейки", self.window._result.format_name)

    def test_hide_empty_fields(self) -> None:
        self.window.open_file(self.write_file("1\n+\n1;+;Основной склад"))
        self.assertIn("не передано", self.output_text())

        self.window._hide_empty.setChecked(True)
        self.assertNotIn("не передано", self.output_text())
        self.window._hide_empty.setChecked(False)

    def test_error_is_shown_inline(self) -> None:
        self.window.open_file(self.write_file("x", name="example.txt"))

        self.assertIn("Не удалось расшифровать файл", self.output_text())
        self.assertFalse(self.window._copy_button.isEnabled())

    def mime_for(self, path: Path) -> QMimeData:
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(str(path))])
        return mime

    def test_dropped_file_is_decoded(self) -> None:
        path = self.write_file("1\n+\n1;+;Основной склад", name="example.dmU")
        mime = self.mime_for(path)
        args = (QPoint(10, 10), Qt.CopyAction, mime, Qt.LeftButton, Qt.NoModifier)

        enter = QDragEnterEvent(*args)
        self.window.dragEnterEvent(enter)
        self.assertTrue(enter.isAccepted())

        drop = QDropEvent(*args)
        self.window.dropEvent(drop)
        self.assertIn("Основной склад", self.output_text())
        self.assertEqual(str(path), self.window._file_field.text())

    def test_drop_of_unsupported_file_is_rejected(self) -> None:
        mime = self.mime_for(self.write_file("x", name="example.txt"))
        enter = QDragEnterEvent(
            QPoint(10, 10), Qt.CopyAction, mime, Qt.LeftButton, Qt.NoModifier
        )
        self.window.dragEnterEvent(enter)
        self.assertFalse(enter.isAccepted())


if __name__ == "__main__":
    unittest.main()
