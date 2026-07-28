from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List, Tuple

from decoders import decode_value
from models import FormatSpec, LineSpec


ALLOWED_EXTENSIONS = {".dm", ".dmu"}
MISSING = "значение не передано"


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


def parse_fields(fields: List[str], values: List[str]) -> List[str]:
    values = normalize_values(values, len(fields))
    result: List[str] = []

    for index, field_name in enumerate(fields):
        value = values[index] if index < len(values) else ""
        result.append(f"{field_name}: {format_value(field_name, value)}")

    if len(values) > len(fields):
        for index, value in enumerate(values[len(fields) :], start=1):
            result.append(
                f"Дополнительное значение {index}: "
                f"{format_value('Дополнительное значение', value)}"
            )

    return result


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


def parse_exchange_file(path: Path, spec: FormatSpec) -> str:
    path = Path(path)
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("Можно выбрать только файл .dm или .dmU/.dmu")

    text, encoding = read_data_file(path)
    lines, skipped_empty = non_empty_lines(text)

    output = [
        "DataMobile Exchange Parser",
        f"Формат обмена: {spec.display_name}",
        f"Файл: {path.name}",
        f"Кодировка: {encoding}",
        f"Непустых строк в файле: {len(lines)}",
    ]
    if skipped_empty:
        output.append(f"Пустых строк пропущено: {skipped_empty}")
    output.append("=" * 80)

    if not lines:
        output.append("Файл пустой или содержит только пустые строки.")
        return "\n".join(output)

    line_index = 0
    for line_spec in spec.line_specs:
        if line_spec.repeat:
            remaining = lines[line_index:]
            if not remaining:
                output.extend(("", f"{line_spec.title}: строки не переданы"))
                continue

            if len(spec.line_specs) == 1 and len(remaining) == 1:
                flat_values = split_line(remaining[0])
                rows = chunk_flat_values(flat_values, len(line_spec.fields))
            else:
                rows = [split_line(row) for row in remaining]

            for row_number, values in enumerate(rows, start=1):
                fields = choose_fields(line_spec, values)
                output.extend(
                    (
                        "",
                        f"{line_spec.title} {row_number}",
                        "-" * 80,
                        *parse_fields(fields, values),
                    )
                )
            line_index = len(lines)
            continue

        output.extend(("", line_spec.title, "-" * 80))
        if line_index < len(lines):
            output.extend(parse_fields(line_spec.fields, split_line(lines[line_index])))
            line_index += 1
        else:
            output.extend(parse_fields(line_spec.fields, []))

    if line_index < len(lines):
        output.extend(("", "Необработанные строки", "-" * 80))
        for index, row in enumerate(lines[line_index:], start=1):
            output.append(f"Строка {index}: {row}")

    return "\n".join(output)
