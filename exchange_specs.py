from __future__ import annotations

import json
from pathlib import Path
from typing import List

from models import FormatSpec, LineSpec
from resources import resource_path


def load_specs(config_path: Path | None = None) -> List[FormatSpec]:
    path = config_path or resource_path("config/exchange_specs.json")
    raw_specs = json.loads(Path(path).read_text(encoding="utf-8"))
    result: List[FormatSpec] = []

    for raw_spec in raw_specs:
        line_specs = [LineSpec(**line_spec) for line_spec in raw_spec["line_specs"]]
        result.append(
            FormatSpec(
                key=raw_spec["key"],
                display_name=raw_spec["display_name"],
                source_file=raw_spec["source_file"],
                line_specs=line_specs,
            )
        )

    return result
