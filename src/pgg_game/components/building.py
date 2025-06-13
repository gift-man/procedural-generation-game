"""Компоненты для зданий."""
from enum import Enum, auto
from dataclasses import dataclass
from typing import Tuple

class BuildingType(Enum):
    """Типы зданий."""
    TOWN_HALL = auto()    # Ратуша

@dataclass
class BuildingComponent:
    """Компонент здания."""
    building_type: BuildingType
    owner: int  # ID игрока
    position: Tuple[int, int]   