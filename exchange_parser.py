from __future__ import annotations

import csv
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from decoders import decode_value
from models import FormatSpec, LineSpec


ALLOWED_EXTENSIONS = {".dm", ".dmu"}
MISSING = "значение не передано"


@dataclass(frozen=True)
class FieldValue:
    name: str
    value: str
    decoded: Optional[str] = None

    @property
    def missing(self) -> bool:
        return self.value.strip() == ""

    def as_text(self) -> str:
        if self.missing:
            return f"{self.name}: {MISSING}"
        value = self.value.strip()
        shown = f"{value} — {self.decoded}" if self.decoded else value
        return f"{self.name}: {shown}"


@dataclass
class Section:
    title: str
    fields: List[FieldValue] = field(default_factory=list)
    raw_lines: List[str] = field(default_factory=list)
    note: Optional[str] = None


@dataclass
class ParseResult:
    format_name: str
    file_name: str
    encoding: str
    line_count: int
    skipped_empty: int = 0
    sections: List[Section] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return self.line_count == 0


def read_data_file(path: Path) -> Tuple[str, str]:
    last_error: UnicodeDecodeError | None = None
    for encoding in ("utf-8-sig", "utf-8", "cp1251", "windows-1251"):
        try:
            return path.read_text(encoding=encoding), encoding
        except UnicodeDecodeError as exc:
            last_error = exc

    if last_error:
        return (
            path.read_text(encoding="utf-8", errors="replace"),
            "utf-8 с заменой нечитаемых символов",
        )
    return path.read_text(encoding="utf-8"), "utf-8"


def split_line(line: str) -> List[str]:
    line = line.strip().strip("\ufeff")
    return next(csv.reader([line], delimiter=";", quotechar='"'))


def normalize_values(values: List[str], field_count: int) -> List[str]:
    values = [value.strip() for value in values]
    while len(values) > field_count and values and values[-1] == "":
        values.pop()
    return values


def format_value(field_name: str, value: str | None) -> str:
    if value is None or value.strip() == "":
        return MISSING
    value = value.strip()
    decoded = decode_value(field_name, value)
    return f"{value} — {decoded}" if decoded else value


def parse_field_values(fields: List[str], values: List[str]) -> List[FieldValue]:
    values = normalize_values(values, len(fields))
    result: List[FieldValue] = []

    for index, field_name in enumerate(fields):
        value = values[index] if index < len(values) else ""
        result.append(FieldValue(field_name, value, decode_value(field_name, value)))

    if len(values) > len(fields):
        for index, value in enumerate(values[len(fields) :], start=1):
            result.append(
                FieldValue(
                    f"Дополнительное значение {index}",
                    value,
                    decode_value("Дополнительное значение", value),
                )
            )

    return result


def parse_fields(fields: List[str], values: List[str]) -> List[str]:
    return [field.as_text() for field in parse_field_values(fields, values)]


def chunk_flat_values(values: List[str], fields_count: int) -> List[List[str]]:
    values = [value.strip() for value in values]
    while values and values[-1] == "":
        values.pop()
    if fields_count <= 0:
        return [values]

    chunks: List[List[str]] = []
    for index in range(0, len(values), fields_count):
        chunk = values[index : index + fields_count]
        if any(value.strip() for value in chunk):
            chunks.append(chunk)
    return chunks


def choose_fields(line_spec: LineSpec, values: List[str]) -> List[str]:
    if not line_spec.variants:
        return line_spec.fields
    if len(values) > line_spec.variant_index:
        discriminator = values[line_spec.variant_index].strip()
        return line_spec.variants.get(discriminator, line_spec.fields)
    return line_spec.fields


def non_empty_lines(text: str) -> Tuple[List[str], int]:
    lines: List[str] = []
    skipped = 0
    for raw_line in text.splitlines():
        if raw_line.strip():
            lines.append(raw_line.strip())
        else:
            skipped += 1
    return lines, skipped


def parse_exchange(path: Path, spec: FormatSpec) -> ParseResult:
    path = Path(path)
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("Можно выбрать только файл .dm или .dmU/.dmu")

    text, encoding = read_data_file(path)
    lines, skipped_empty = non_empty_lines(text)
    result = ParseResult(
        format_name=spec.display_name,
        file_name=path.name,
        encoding=encoding,
        line_count=len(lines),
        skipped_empty=skipped_empty,
    )
    if not lines:
        return result

    sections = result.sections
    line_index = 0
    for line_spec in spec.line_specs:
        if line_spec.repeat:
            remaining = lines[line_index:]
            if not remaining:
                sections.append(Section(line_spec.title, note="строки не переданы"))
                continue

            if len(spec.line_specs) == 1 and len(remaining) == 1:
                flat_values = split_line(remaining[0])
                rows = chunk_flat_values(flat_values, len(line_spec.fields))
            else:
                rows = [split_line(row) for row in remaining]

            for row_number, values in enumerate(rows, start=1):
                fields = choose_fields(line_spec, values)
                sections.append(
                    Section(
                        f"{line_spec.title} {row_number}",
                        parse_field_values(fields, values),
                    )
                )
            line_index = len(lines)
            continue

        if line_index < len(lines):
            values = split_line(lines[line_index])
            line_index += 1
        else:
            values = []
        sections.append(
            Section(line_spec.title, parse_field_values(line_spec.fields, values))
        )

    if line_index < len(lines):
        sections.append(
            Section("Необработанные строки", raw_lines=lines[line_index:])
        )

    return result


def render_text(result: ParseResult) -> str:
    output = [
        "DataMobile Exchange Parser",
        f"Формат обмена: {result.format_name}",
        f"Файл: {result.file_name}",
        f"Кодировка: {result.encoding}",
        f"Непустых строк в файле: {result.line_count}",
    ]
    if result.skipped_empty:
        output.append(f"Пустых строк пропущено: {result.skipped_empty}")
    output.append("=" * 80)

    if result.is_empty:
        output.append("Файл пустой или содержит только пустые строки.")
        return "\n".join(output)

    for section in result.sections:
        if section.note:
            output.extend(("", f"{section.title}: {section.note}"))
            continue
        output.extend(("", section.title, "-" * 80))
        output.extend(field.as_text() for field in section.fields)
        output.extend(
            f"Строка {index}: {row}"
            for index, row in enumerate(section.raw_lines, start=1)
        )

    return "\n".join(output)


def parse_exchange_file(path: Path, spec: FormatSpec) -> str:
    return render_text(parse_exchange(path, spec))
