from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from resources import resource_path


def _load_config(path: Path | None = None) -> dict:
    config_path = path or resource_path("config/decoders.json")
    return json.loads(Path(config_path).read_text(encoding="utf-8"))


_CONFIG = _load_config()
FIELD_DECODERS: Dict[str, Dict[str, str]] = _CONFIG["field_decoders"]
BOOLEAN_PREFIXES = tuple(_CONFIG["boolean_prefixes"])
BOOLEAN_FIELDS = set(_CONFIG["boolean_fields"])


def decode_value(field_name: str, value: str) -> Optional[str]:
    field_name = field_name.strip()
    value = value.strip()
    if value == "":
        return None

    decoder = FIELD_DECODERS.get(field_name)
    if decoder and value in decoder:
        return decoder[value]

    lowered = value.lower()
    if lowered in {"true", "false"}:
        return "да" if lowered == "true" else "нет"

    if field_name in BOOLEAN_FIELDS or field_name.startswith(BOOLEAN_PREFIXES):
        if value == "0":
            return "нет / не использовать"
        if value == "1":
            return "да / использовать"

    return None
