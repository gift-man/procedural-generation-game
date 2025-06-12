"""Настройки генерации провинций."""
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class ProvinceGenerationConfig:
    """Конфигурация для генерации провинций."""
    # Базовые ограничения размеров
    min_province_size: int = 4
    max_province_size: int = 8
    min_province_count: int = 3
    max_province_count: int = 20
    
    # Параметры генерации
    max_attempts: int = 5
    check_plus_intersection: bool = True
    min_total_coverage: float = 0.95
    
    # Вероятности размеров провинций
    size_probabilities: Dict[int, float] = field(default_factory=lambda: {
        4: 0.15,  # 15% шанс для провинций размером 4
        5: 0.20,  # 20% шанс для провинций размером 5
        6: 0.30,  # 30% шанс для провинций размером 6
        7: 0.20,  # 20% шанс для провинций размером 7
        8: 0.15   # 15% шанс для провинций размером 8
    })