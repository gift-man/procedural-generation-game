"""Настройки генерации провинций."""
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class ProvinceGenerationConfig:
    """Конфигурация для генерации провинций."""
    # Базовые ограничения
    min_province_size: int = 4
    max_province_size: int = 8
    min_provinces: int = 3
    max_provinces: int = 20
    
    # Настройки генерации
    max_generation_attempts: int = 5
    max_province_attempts: int = 50
    allow_diagonal_growth: bool = False
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
    
    # Веса для выбора следующей клетки
    weights: Dict[str, float] = field(default_factory=lambda: {
        'neighbor_count': 0.4,    # Вес количества соседей
        'compactness': 0.3,       # Вес компактности формы
        'center_distance': 0.2,   # Вес расстояния от центра провинции
        'border_length': 0.1      # Вес длины общей границы
    })
    
    # Параметры качества генерации
    quality_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'min_compactness': 0.5,     # Минимальная компактность провинции
        'max_border_ratio': 0.6,     # Максимальное отношение границы к площади
        'min_province_ratio': 0.8,   # Минимальное отношение размера к целевому
        'max_size_variance': 0.3     # Максимальное отклонение размеров провинций
    })