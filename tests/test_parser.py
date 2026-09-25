from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from exchange_parser import MISSING, format_value, parse_exchange, parse_exchange_file
from exchange_specs import load_specs


SPECS = load_specs()


def spec_by_name(display_name: str):
    return next(spec for spec in SPECS if spec.display_name == display_name)


class ParserTests(unittest.TestCase):
    def parse_text(self, text: str, display_name: str, suffix: str = ".dm") -> str:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / f"example{suffix}"
            path.write_text(text, encoding="utf-8")
            return parse_exchange_file(path, spec_by_name(display_name))

    def test_all_exchange_formats_are_loaded(self) -> None:
        self.assertEqual(22, len(SPECS))
        self.assertEqual(22, len({spec.display_name for spec in SPECS}))

    def test_loading_document_does_not_shift_first_line(self) -> None:
        result = self.parse_text(
            "\n".join(
                (
                    "3",
                    "+;document-id;ТД-001",
                    "1;Заказ;ЗаказКлиента",
                    "1;S;product-id",
                )
            ),
            "Загрузка документа",
        )

        self.assertIn("КоличествоСтрокВФайле: 3", result)
        self.assertIn("РежимЗагрузкиФайла: + — добавить / обновить", result)
        self.assertIn("ИдентификаторДокумента: document-id", result)
        self.assertIn("КодШаблона: 1", result)
        self.assertIn("ТипСтроки: S — подбор", result)

    def test_missing_values_are_reported(self) -> None:
        result = self.parse_text("1\n+\n1;+;Основной склад", "Склады")
        self.assertIn(f"Наименование: {MISSING}", result)

    def test_changed_products_can_be_flat_on_one_line(self) -> None:
        first = ["id-1", "Товар 1", "10"] + [""] * 10 + ["5"]
        second = ["id-2", "Товар 2", "20"] + [""] * 10 + ["8"]
        result = self.parse_text(
            ";".join(first + second) + ";",
            "Товары измененные",
            suffix=".dmU",
        )
        self.assertIn("Строка товара 1", result)
        self.assertIn("Строка товара 2", result)
        self.assertIn("ИдентификаторТовара: id-2", result)

    def test_common_values_are_decoded(self) -> None:
        self.assertEqual("+ — добавить / обновить", format_value("Операция", "+"))
        self.assertEqual("1 — да / использовать", format_value("ИспользоватьПодбор", "1"))
        self.assertEqual(MISSING, format_value("Поле", ""))

    def test_structured_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "example.dm"
            path.write_text("1\n+\n1;+;Основной склад\n\n2;-", encoding="utf-8")
            result = parse_exchange(path, spec_by_name("Склады"))

        self.assertEqual(4, result.line_count)
        self.assertEqual(1, result.skipped_empty)
        titles = [section.title for section in result.sections]
        self.assertEqual("Строка объекта 1", titles[2])
        self.assertEqual("Строка объекта 2", titles[3])

        first_row = {field.name: field for field in result.sections[2].fields}
        self.assertEqual("добавить / обновить", first_row["Операция"].decoded)
        self.assertFalse(first_row["Идентификатор"].missing)
        second_row = {field.name: field for field in result.sections[3].fields}
        self.assertTrue(second_row["Наименование"].missing)

    def test_empty_file(self) -> None:
        result = self.parse_text("\n\n", "Склады")
        self.assertIn("Файл пустой или содержит только пустые строки.", result)


if __name__ == "__main__":
    unittest.main()
