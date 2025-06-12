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
    max_generation_attempts: int = 5  # Уменьшаем количество попыток для более быстрой обратной связи
    max_province_attempts: int = 50   # Уменьшаем для оптимизации
    min_total_coverage: float = 1.0   # Требуем полное покрытие
    check_plus_intersection: bool = True
    allow_uneven_sizes: bool = True   # Разрешаем неравномерные размеры
    
   # Вероятности размеров провинций
    size_probabilities: Dict[int, float] = field(default_factory=lambda: {
        4: 0.2,
        5: 0.3,
        6: 0.3,
        7: 0.15,
        8: 0.05
    })
    
    # Веса для выбора следующей клетки
    weights: Dict[str, float] = field(default_factory=lambda: {
        'neighbor_count': 0.7,    # Увеличиваем важность соседей
        'compactness': 0.2,       # Уменьшаем важность компактности
        'center_distance': 0.1    # Уменьшаем влияние расстояния
    })
    
    # Параметры качества генерации
    quality_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'min_compactness': 0.6,
        'max_border_ratio': 0.4,
        'min_province_ratio': 0.9,
        'max_size_variance': 0.2
    })