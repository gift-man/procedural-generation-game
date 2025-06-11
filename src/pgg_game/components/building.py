"""Компоненты для зданий."""
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from .resource import ResourceType  # Добавляем импорт ResourceType

class BuildingType(Enum):
    """Типы зданий."""
    TOWN_HALL = auto()    # Ратуша
    FARM = auto()         # Ферма
    SAWMILL = auto()      # Лесопилка
    QUARRY = auto()       # Каменоломня
    GOLD_MINE = auto()    # Золотая шахта

@dataclass
class BuildingComponent:
    """Компонент здания."""
    building_type: BuildingType
    owner: int  # ID игрока
    position: Tuple[int, int]
    production_per_turn: Dict[ResourceType, int]
    resource_requirement: Optional[ResourceType] = None  # Требуемый ресурс для постройки