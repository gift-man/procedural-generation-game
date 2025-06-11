from dataclasses import dataclass, field
import pygame
from typing import Dict

@dataclass
class PlayerInfoComponent:
    """Информация об игроке."""
    name: str
    color: pygame.Color
    turn_order: int
    gold: int = 100
    income: int = 0
    provinces: Dict[int, str] = field(default_factory=dict)  # id провинции -> имя
    
    def add_province(self, province_id: int, province_name: str) -> None:
        """Добавляет провинцию под контроль игрока."""
        self.provinces[province_id] = province_name
    
    def remove_province(self, province_id: int) -> None:
        """Удаляет провинцию из-под контроля игрока."""
        self.provinces.pop(province_id, None)