"""Настройки генерации провинций."""
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class ProvinceGenerationConfig:
    """Конфигурация для генерации провинций."""
    min_province_size: int = 4  # Минимальный размер провинции
    max_province_size: int = 8  # Максимальный размер провинции
    allow_diagonal_growth: bool = False  # Рост только по основным направлениям
    check_plus_intersection: bool = True  # Проверка на плюсовые пересечения
    
    # Вероятности размеров провинций (должны в сумме давать 1.0)
    size_probabilities: Dict[int, float] = field(default_factory=lambda: {
        4: 0.15,  # 15% шанс для провинций размером 4
        5: 0.20,  # 20% шанс для провинций размером 5
        6: 0.30,  # 30% шанс для провинций размером 6
        7: 0.20,  # 20% шанс для провинций размером 7
        8: 0.15   # 15% шанс для провинций размером 8
    })