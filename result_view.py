from __future__ import annotations

from html import escape

from PySide6.QtGui import (
    QColor,
    QFont,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QTextLength,
    QTextTableFormat,
)

from exchange_parser import FieldValue, ParseResult, Section
from theme import Theme


def _plural(count: int, one: str, few: str, many: str) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return one
    if 2 <= count % 10 <= 4 and not 12 <= count % 100 <= 14:
        return few
    return many


def _message(theme: Theme, title: str, text: str, color: str | None = None) -> str:
    body = escape(text).replace("\n", "<br>")
    return (
        f'<div style="margin-top: 48px;" align="center">'
        f'<p style="font-size: large; font-weight: 600; color: {color or theme.text};">'
        f"{escape(title)}</p>"
        f'<p style="color: {theme.muted};">{body}</p>'
        f"</div>"
    )


def render_placeholder(theme: Theme) -> str:
    return _message(
        theme,
        "Файл пока не выбран",
        "Выберите формат обмена и перетащите файл .dm / .dmU в это окно\n"
        "или нажмите «Выбрать файл…». Расшифровка начнётся автоматически.",
    )


def render_error(theme: Theme, message: str) -> str:
    return _message(theme, "Не удалось расшифровать файл", message, theme.danger)


def render_empty_file(theme: Theme) -> str:
    return _message(theme, "Файл пустой", "В файле нет данных — только пустые строки.")


def summary_text(result: ParseResult) -> str:
    count = result.line_count
    parts = [
        result.encoding,
        f"{count} {_plural(count, 'непустая строка', 'непустые строки', 'непустых строк')}",
    ]
    if result.skipped_empty:
        parts.append(f"пустых пропущено: {result.skipped_empty}")
    return " · ".join(parts)


class _DocumentBuilder:
    """Builds the result with QTextCursor: much faster than HTML for big files."""

    def __init__(self, theme: Theme, base_font: QFont, mono: str) -> None:
        self._theme = theme
        self.document = QTextDocument()
        self.document.setDefaultFont(base_font)
        self.document.setDocumentMargin(8)
        self.document.setUndoRedoEnabled(False)
        self._cursor = QTextCursor(self.document)
        self._first_block = True

        size = base_font.pointSizeF()
        self._title = self._char(theme.text)
        self._title.setFontWeight(QFont.DemiBold)
        self._title.setFontPointSize(size * 1.25)
        self._title_danger = QTextCharFormat(self._title)
        self._title_danger.setForeground(QColor(theme.danger))
        self._meta = self._char(theme.faint)
        self._name = self._char(theme.muted)
        self._value = self._char(theme.text)
        self._value.setFontFamilies([mono])
        self._decoded = self._char(theme.accent)
        self._missing = self._char(theme.faint)
        self._stripe = QColor(theme.surface_alt)

        self._table = QTextTableFormat()
        self._table.setWidth(QTextLength(QTextLength.PercentageLength, 100))
        self._table.setColumnWidthConstraints(
            [
                QTextLength(QTextLength.PercentageLength, 38),
                QTextLength(QTextLength.PercentageLength, 62),
            ]
        )
        self._table.setCellPadding(6)
        self._table.setCellSpacing(0)
        self._table.setBorder(0)
        self._table.setBottomMargin(8)

    def begin(self) -> None:
        # One edit block keeps insertTable() from relaying out the whole document.
        self._cursor.beginEditBlock()

    def end(self) -> None:
        self._cursor.endEditBlock()

    @staticmethod
    def _char(color: str) -> QTextCharFormat:
        char_format = QTextCharFormat()
        char_format.setForeground(QColor(color))
        return char_format

    def _new_block(self, top_margin: int) -> None:
        block_format = self._cursor.blockFormat()
        block_format.setTopMargin(0 if self._first_block else top_margin)
        block_format.setBottomMargin(8)
        if self._first_block:
            self._cursor.setBlockFormat(block_format)
            self._first_block = False
        else:
            self._cursor.insertBlock(block_format)

    def heading(self, title: str, meta: str, danger: bool = False) -> None:
        self._new_block(top_margin=16)
        self._cursor.insertText(title, self._title_danger if danger else self._title)
        if meta:
            self._cursor.insertText(f"   {meta}", self._meta)

    def note(self, text: str) -> None:
        self._new_block(top_margin=0)
        self._cursor.insertText(text, self._missing)

    def fields(self, fields: list[FieldValue]) -> None:
        table = self._cursor.insertTable(len(fields), 2, self._table)
        for row, field in enumerate(fields):
            if row % 2:
                for column in range(2):
                    cell = table.cellAt(row, column)
                    cell_format = cell.format()
                    cell_format.setBackground(self._stripe)
                    cell.setFormat(cell_format)

            table.cellAt(row, 0).firstCursorPosition().insertText(field.name, self._name)
            cursor = table.cellAt(row, 1).firstCursorPosition()
            if field.missing:
                cursor.insertText("не передано", self._missing)
                continue
            cursor.insertText(field.value, self._value)
            if field.decoded:
                cursor.insertText(f"   {field.decoded}", self._decoded)
        self._cursor.movePosition(QTextCursor.End)


def _section_meta(section: Section) -> str:
    if section.note:
        return section.note
    if section.raw_lines:
        return "не описаны в выбранном формате — проверьте, верно ли он выбран"
    filled = sum(not field.missing for field in section.fields)
    return f"заполнено {filled} из {len(section.fields)}"


def build_document(
    result: ParseResult,
    theme: Theme,
    base_font: QFont,
    mono: str,
    hide_empty: bool = False,
) -> QTextDocument:
    builder = _DocumentBuilder(theme, base_font, mono)
    builder.begin()
    for section in result.sections:
        builder.heading(section.title, _section_meta(section), danger=bool(section.raw_lines))
        if section.raw_lines:
            builder.fields(
                [
                    FieldValue(f"Строка {index}", line)
                    for index, line in enumerate(section.raw_lines, start=1)
                ]
            )
            continue

        fields = [field for field in section.fields if not (hide_empty and field.missing)]
        if fields:
            builder.fields(fields)
        elif section.fields:
            builder.note("Все поля пустые.")
    builder.end()
    return builder.document
