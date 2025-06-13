"""Настройки генерации карты."""
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class MapGenerationSettings:
    """Настройки генерации острова из провинций."""
    # Настройки размеров
    min_province_size: int = 4
    max_province_size: int = 8
    target_provinces: int = 10
    min_total_size: int = 40
    
    # Настройки генерации
    initial_provinces: int = 3      # Стартовое количество провинций
    growth_steps: int = 5           # Количество шагов роста
    smoothing_passes: int = 2       # Количество проходов сглаживания
    connection_range: int = 2       # Диапазон для соединения провинций
    
    # Параметры роста
    growth_chance: float = 0.7      # Шанс роста провинции за шаг
    max_growth_attempts: int = 50   # Максимум попыток роста за шаг
    merge_threshold: float = 0.3    # Порог для объединения мелких провинций
    
    # Веса для оценки клеток
    weights: Dict[str, float] = field(default_factory=lambda: {
        'center_distance': 0.4,     # Вес расстояния до центра
        'neighbor_count': 0.3,      # Вес количества соседей
        'border_length': 0.2,       # Вес длины границы
        'compactness': 0.1          # Вес компактности формы
    })