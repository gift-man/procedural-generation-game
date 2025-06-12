"""Настройки генерации провинций."""
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ProvinceGenerationConfig:
    """Конфигурация для генерации провинций."""
    # Базовые ограничения
    min_province_size: int = 4
    max_province_size: int = 8  # Возвращаем к 8
    min_province_count: int = 3
    max_province_count: int = 12  # Уменьшаем максимум
    
    # Настройки генерации
    max_generation_attempts: int = 50  # Уменьшаем количество попыток
    max_province_attempts: int = 100
    min_total_coverage: float = 0.90  # Уменьшаем требования к покрытию
    allow_diagonal_growth: bool = False  # Отключаем диагональный рост
    check_plus_intersection: bool = True
    
    # Вероятности размеров провинций (убираем большие размеры)
    size_probabilities: Dict[int, float] = field(default_factory=lambda: {
        4: 0.15,
        5: 0.25,
        6: 0.35,  # Увеличиваем вероятность среднего размера
        7: 0.15,
        8: 0.10
    })
    
    # Веса для выбора следующей клетки
    weights: Dict[str, float] = field(default_factory=lambda: {
        'neighbor_count': 0.7,    # Увеличиваем важность соседей
        'compactness': 0.2,       # Уменьшаем важность компактности
        'center_distance': 0.05,
        'border_length': 0.05
    })
    
    # Параметры качества генерации
    quality_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'min_compactness': 0.6,
        'max_border_ratio': 0.4,
        'min_province_ratio': 0.9,
        'max_size_variance': 0.2
    })