"""Настройки генерации провинций."""
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ProvinceGenerationConfig:
    """Конфигурация для генерации провинций."""
    # Базовые ограничения
    min_province_size: int = 4
    max_province_size: int = 8
    min_province_count: int = 3
    max_province_count: int = 20
    
    # Настройки генерации
    max_generation_attempts: int = 50  # Увеличено с 5
    max_province_attempts: int = 100   # Увеличено с 50
    allow_diagonal_growth: bool = True # Изменено на True
    check_plus_intersection: bool = False # Изменено на False для упрощения
    
    # Вероятности размеров провинций
    size_probabilities: Dict[int, float] = field(default_factory=lambda: {
        4: 0.20,  # 20% шанс для провинций размером 4
        5: 0.25,  # 25% шанс для провинций размером 5
        6: 0.25,  # 25% шанс для провинций размером 6
        7: 0.20,  # 20% шанс для провинций размером 7
        8: 0.10   # 10% шанс для провинций размером 8
    })
    
    # Веса для выбора следующей клетки
    weights: Dict[str, float] = field(default_factory=lambda: {
        'neighbor_count': 0.5,    # Увеличен вес соседей
        'compactness': 0.3,
        'center_distance': 0.1,   # Уменьшен вес расстояния
        'border_length': 0.1
    })
    
    # Параметры качества генерации
    quality_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'min_compactness': 0.6,      # Минимальная компактность провинции
        'max_border_ratio': 0.5,     # Максимальное отношение границы к площади
        'min_province_ratio': 0.9,   # Минимальное отношение размера к целевому
        'max_size_variance': 0.2     # Максимальное отклонение размеров провинций
    })