"""Компоненты для игроков."""
from dataclasses import dataclass, field
from typing import Set, Tuple

@dataclass
class PlayerComponent:
    """Компонент игрока."""
    player_id: int
    color: Tuple[int, int, int]
    gold: int = 100  # Начальное количество золота
    provinces: Set[int] = field(default_factory=set)  # ID провинций
    has_placed_town_hall: bool = False