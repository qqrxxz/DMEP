from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtGui import QGuiApplication, QKeySequence, QShortcut, QTextDocument
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from exchange_parser import ParseResult, parse_exchange, render_text
from exchange_specs import load_specs
from models import FormatSpec
from result_view import (
    build_document,
    render_empty_file,
    render_error,
    render_placeholder,
    summary_text,
)
from theme import current_theme, monospace_family, output_font


def _label(text: str, object_name: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName(object_name)
    return label


def _shortcut(key: QKeySequence.StandardKey) -> str:
    return QKeySequence(key).toString(QKeySequence.NativeText)


def _card() -> QFrame:
    card = QFrame()
    card.setObjectName("card")
    return card


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DataMobile Exchange Parser")
        self.resize(1080, 760)
        self.setMinimumSize(720, 520)

        self._settings = QSettings("DataMobile", "DataMobile Exchange Parser")
        self._theme = current_theme()
        self._mono = monospace_family()
        self._specs = load_specs()
        self._selected_file: Path | None = None
        self._result: ParseResult | None = None
        self._document: QTextDocument | None = None

        self._format_combo = QComboBox()
        self._format_combo.setMaxVisibleItems(24)
        for spec in self._specs:
            self._format_combo.addItem(spec.display_name, spec)
        self._restore_selected_format()
        self._format_combo.currentIndexChanged.connect(self._on_format_changed)

        self._file_field = QLineEdit()
        self._file_field.setReadOnly(True)
        self._file_field.setPlaceholderText("Файл не выбран")

        choose_button = QPushButton("Выбрать файл…")
        choose_button.setObjectName("primary")
        choose_button.setToolTip(f"Выбрать файл .dm или .dmU ({_shortcut(QKeySequence.Open)})")
        choose_button.clicked.connect(self._choose_file)

        self._reload_button = QPushButton("Обновить")
        self._reload_button.setToolTip(
            f"Перечитать файл с диска ({_shortcut(QKeySequence.Refresh)})"
        )
        self._reload_button.setEnabled(False)
        self._reload_button.clicked.connect(self._parse_file)

        self._status = _label("", "status")
        self._hide_empty = QCheckBox("Скрыть пустые поля")
        self._hide_empty.setChecked(self._settings.value("hide_empty", False, type=bool))
        self._hide_empty.toggled.connect(self._on_hide_empty_toggled)

        self._copy_button = QPushButton("Копировать")
        self._copy_button.setToolTip("Скопировать результат как текст")
        self._copy_button.setEnabled(False)
        self._copy_button.clicked.connect(self._copy_result)

        self._output = QTextBrowser()
        self._output.setOpenLinks(False)
        self._output.setFont(output_font(self.font()))
        self._show_html(render_placeholder(self._theme))

        QShortcut(QKeySequence.Open, self, activated=self._choose_file)
        QShortcut(QKeySequence.Refresh, self, activated=self._parse_file)

        self.setCentralWidget(self._build_layout(choose_button))
        choose_button.setFocus()

    def _build_layout(self, choose_button: QPushButton) -> QWidget:
        header = QVBoxLayout()
        header.setSpacing(4)
        header.addWidget(_label("DataMobile Exchange Parser", "title"))
        header.addWidget(
            _label("Расшифровка файлов обмена DataMobile .dm и .dmU", "subtitle")
        )

        controls = _card()
        grid = QGridLayout(controls)
        grid.setContentsMargins(16, 16, 16, 16)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(8)
        grid.addWidget(_label("Формат обмена", "caption"), 0, 0)
        grid.addWidget(_label("Файл", "caption"), 0, 1)
        grid.addWidget(self._format_combo, 1, 0)
        grid.addWidget(self._file_field, 1, 1)
        grid.addWidget(choose_button, 1, 2)
        grid.addWidget(self._reload_button, 1, 3)
        grid.setColumnStretch(0, 2)
        grid.setColumnStretch(1, 3)

        result_header = QHBoxLayout()
        result_header.setContentsMargins(16, 12, 16, 12)
        result_header.setSpacing(12)
        result_header.addWidget(_label("Результат", "cardTitle"))
        result_header.addWidget(self._status, 1)
        result_header.addWidget(self._hide_empty)
        result_header.addWidget(self._copy_button)

        results = _card()
        results_layout = QVBoxLayout(results)
        results_layout.setContentsMargins(1, 1, 1, 1)
        results_layout.setSpacing(0)
        results_layout.addLayout(result_header)
        results_layout.addWidget(self._output, 1)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addLayout(header)
        layout.addSpacing(8)
        layout.addWidget(controls)
        layout.addWidget(results, 1)

        container = QWidget()
        container.setObjectName("central")
        container.setLayout(layout)
        return container

    def _current_spec(self) -> FormatSpec:
        return self._format_combo.currentData()

    def _restore_selected_format(self) -> None:
        saved_key = self._settings.value("selected_format", "")
        for index in range(self._format_combo.count()):
            spec = self._format_combo.itemData(index)
            if spec.key == saved_key:
                self._format_combo.setCurrentIndex(index)
                return

    def _on_format_changed(self) -> None:
        self._settings.setValue("selected_format", self._current_spec().key)
        self._parse_file()

    def _on_hide_empty_toggled(self, checked: bool) -> None:
        self._settings.setValue("hide_empty", checked)
        self._show_result(keep_scroll=True)

    def _choose_file(self) -> None:
        initial_directory = self._settings.value("last_directory", "")
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл DataMobile",
            initial_directory,
            "Файлы DataMobile (*.dm *.dmu *.dmU *.DM *.DMU);;Все файлы (*)",
        )
        if file_name:
            self.open_file(Path(file_name))

    def open_file(self, path: Path) -> None:
        """Remember the file and decode it right away."""
        self._selected_file = path
        self._file_field.setText(str(path))
        self._file_field.setCursorPosition(len(str(path)))
        self._file_field.setToolTip(str(path))
        self._reload_button.setEnabled(True)
        self._settings.setValue("last_directory", str(path.parent))
        self._parse_file()

    def _parse_file(self) -> None:
        if self._selected_file is None:
            return

        QGuiApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self._result = parse_exchange(self._selected_file, self._current_spec())
        except Exception as exc:
            self._result = None
            self._copy_button.setEnabled(False)
            self._set_status("")
            self._show_html(render_error(self._theme, str(exc)))
            return
        else:
            self._show_result()
        finally:
            QGuiApplication.restoreOverrideCursor()

    def _show_result(self, keep_scroll: bool = False) -> None:
        if self._result is None:
            return

        self._copy_button.setEnabled(True)
        self._set_status(summary_text(self._result))
        if self._result.is_empty:
            self._show_html(render_empty_file(self._theme))
            return

        scrollbar = self._output.verticalScrollBar()
        position = scrollbar.value() if keep_scroll else 0
        self._set_document(
            build_document(
                self._result,
                self._theme,
                self._output.font(),
                self._mono,
                self._hide_empty.isChecked(),
            )
        )
        scrollbar.setValue(position)

    def _show_html(self, html: str) -> None:
        document = QTextDocument()
        document.setDefaultFont(self._output.font())
        document.setHtml(html)
        self._set_document(document)

    def _set_document(self, document: QTextDocument) -> None:
        # QTextBrowser does not own documents set from outside: keep a reference.
        document.setParent(self._output)
        self._output.setDocument(document)
        if self._document is not None:
            self._document.deleteLater()
        self._document = document

    def _set_status(self, text: str) -> None:
        self._status.setText(text)
        self._status.setToolTip(text)

    def _copy_result(self) -> None:
        if self._result is not None:
            QGuiApplication.clipboard().setText(render_text(self._result))
            self._copy_button.setText("Скопировано")
            self._copy_button.setEnabled(False)
            QTimer.singleShot(1500, self._reset_copy_button)

    def _reset_copy_button(self) -> None:
        self._copy_button.setText("Копировать")
        self._copy_button.setEnabled(self._result is not None)
