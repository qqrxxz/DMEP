from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from exchange_parser import parse_exchange_file
from exchange_specs import load_specs
from models import FormatSpec


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DataMobile Exchange Parser")
        self.resize(1080, 760)

        self._settings = QSettings("DataMobile", "DataMobile Exchange Parser")
        self._specs = load_specs()
        self._selected_file: Path | None = None

        self._format_combo = QComboBox()
        for spec in self._specs:
            self._format_combo.addItem(spec.display_name, spec)
        self._restore_selected_format()

        self._file_label = QLabel("Файл не выбран")
        self._file_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._file_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        choose_button = QPushButton("Выбрать .dm / .dmU")
        choose_button.clicked.connect(self._choose_file)

        self._parse_button = QPushButton("Расшифровать")
        self._parse_button.setEnabled(False)
        self._parse_button.clicked.connect(self._parse_file)

        self._output = QPlainTextEdit()
        self._output.setReadOnly(True)
        self._output.setPlaceholderText(
            "Выберите формат обмена и файл, затем нажмите «Расшифровать»."
        )
        mono_font = QFont("Menlo")
        mono_font.setStyleHint(QFont.Monospace)
        mono_font.setPointSize(12)
        self._output.setFont(mono_font)

        format_row = QHBoxLayout()
        format_row.addWidget(QLabel("Формат обмена:"))
        format_row.addWidget(self._format_combo, 1)

        file_row = QHBoxLayout()
        file_row.addWidget(QLabel("Файл:"))
        file_row.addWidget(self._file_label, 1)
        file_row.addWidget(choose_button)

        actions_row = QHBoxLayout()
        actions_row.addStretch(1)
        actions_row.addWidget(self._parse_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addLayout(format_row)
        layout.addLayout(file_row)
        layout.addLayout(actions_row)
        layout.addWidget(QLabel("Результат:"))
        layout.addWidget(self._output, 1)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _current_spec(self) -> FormatSpec:
        return self._format_combo.currentData()

    def _restore_selected_format(self) -> None:
        saved_key = self._settings.value("selected_format", "")
        for index in range(self._format_combo.count()):
            spec = self._format_combo.itemData(index)
            if spec.key == saved_key:
                self._format_combo.setCurrentIndex(index)
                return

    def _choose_file(self) -> None:
        initial_directory = self._settings.value("last_directory", "")
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл DataMobile",
            initial_directory,
            "Файлы DataMobile (*.dm *.dmu *.dmU *.DM *.DMU);;Все файлы (*)",
        )
        if not file_name:
            return

        self._selected_file = Path(file_name)
        self._file_label.setText(str(self._selected_file))
        self._file_label.setToolTip(str(self._selected_file))
        self._parse_button.setEnabled(True)
        self._settings.setValue("last_directory", str(self._selected_file.parent))

    def _parse_file(self) -> None:
        if self._selected_file is None:
            return

        spec = self._current_spec()
        self._settings.setValue("selected_format", spec.key)
        try:
            result = parse_exchange_file(self._selected_file, spec)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка разбора", str(exc))
            return

        self._output.setPlainText(result)
        self._output.moveCursor(QTextCursor.Start)
