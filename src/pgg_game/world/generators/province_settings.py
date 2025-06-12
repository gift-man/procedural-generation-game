"""Настройки генерации провинций."""
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ProvinceGenerationConfig:
    """Конфигурация для генерации провинций."""
    # Базовые ограничения - будут заполнены из анализа острова
    min_province_size: int = 4
    max_province_size: int = 8
    min_province_count: int = 3
    max_province_count: int = 15
    
    # Настройки генерации
    max_generation_attempts: int = 50
    max_province_attempts: int = 100
    check_plus_intersection: bool = True
    
  # Вероятности размеров провинций (будут заполнены из анализа острова)
    size_probabilities: Dict[int, float] = field(default_factory=lambda: {
        4: 0.0,
        5: 0.0,
        6: 0.0,
        7: 0.0,
        8: 0.0
    })
    
    # Веса для выбора следующей клетки
    weights: Dict[str, float] = field(default_factory=lambda: {
        'neighbor_count': 0.6,    # Увеличиваем вес соседей
        'compactness': 0.3,       # Сохраняем важность компактности
        'center_distance': 0.1    # Немного увеличиваем влияние расстояния
    })
    
    # Параметры качества генерации
    quality_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'min_compactness': 0.6,
        'max_border_ratio': 0.4,
        'min_province_ratio': 0.9,
        'max_size_variance': 0.2
    })