"""Данные о провинции."""
from dataclasses import dataclass, field
from typing import Set, Tuple, Optional

@dataclass
class ProvinceData:
    """Данные о провинции."""
    cells: Set[Tuple[int, int]] = field(default_factory=set)
    target_size: Optional[int] = None
    border_cells: Set[Tuple[int, int]] = field(default_factory=set)