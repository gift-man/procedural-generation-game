"""Компоненты для игроков."""
from dataclasses import dataclass, field
from typing import Set, Dict, Tuple
from .resource import ResourceType  # Добавляем импорт ResourceType

@dataclass
class PlayerComponent:
    """Компонент игрока."""
    player_id: int
    color: Tuple[int, int, int]
    gold: int = 100  # Начальное количество золота
    provinces: Set[int] = field(default_factory=set)  # ID провинций
    resources: Dict[ResourceType, int] = field(default_factory=dict)
    buildings: Set[int] = field(default_factory=set)  # ID зданий
    has_placed_town_hall: bool = False