"""Компонент провинции."""
import random
from typing import Set, List, Tuple, Dict, Optional
from dataclasses import dataclass, field
from ..world.generators.province_settings import ProvinceGenerationConfig

@dataclass
class ProvinceData:
    """Класс для хранения данных о провинции."""
    cells: Set[Tuple[int, int]] = field(default_factory=set)  # Клетки провинции
    neighbors: Set[int] = field(default_factory=set)          # ID соседних провинций
    border_cells: Set[Tuple[int, int]] = field(default_factory=set)  # Граничные клетки
    target_size: Optional[int] = None  # Целевой размер провинции

