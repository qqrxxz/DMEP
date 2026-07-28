from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class LineSpec:
    title: str
    fields: List[str]
    repeat: bool = False
    variants: Optional[Dict[str, List[str]]] = None
    variant_index: int = 0


@dataclass(frozen=True)
class FormatSpec:
    key: str
    display_name: str
    source_file: str
    line_specs: List[LineSpec] = field(default_factory=list)
