"""Настройки генерации провинций."""
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ProvinceGenerationConfig:
    """Конфигурация для генерации провинций."""
    # Базовые ограничения
    min_province_size: int = 4  # Минимальный размер не меняем
    max_province_size: int = 10  # Немного увеличиваем максимальный размер
    min_province_count: int = 3
    max_province_count: int = 15  # Уменьшаем для лучшего контроля
    
    # Настройки генерации
    max_generation_attempts: int = 100  # Увеличиваем количество попыток
    max_province_attempts: int = 150
    min_total_coverage: float = 0.95  # Увеличиваем минимальное покрытие
    allow_diagonal_growth: bool = True
    check_plus_intersection: bool = True  # Включаем проверку плюсов
    
    # Вероятности размеров провинций
    size_probabilities: Dict[int, float] = field(default_factory=lambda: {
        4: 0.10,  # Уменьшаем вероятность маленьких провинций
        5: 0.20,
        6: 0.30,  # Увеличиваем вероятность средних провинций
        7: 0.25,
        8: 0.10,
        9: 0.03,
        10: 0.02
    })
    
    # Веса для выбора следующей клетки
    weights: Dict[str, float] = field(default_factory=lambda: {
        'neighbor_count': 0.6,    # Увеличиваем вес соседей
        'compactness': 0.3,
        'center_distance': 0.05,  # Уменьшаем влияние расстояния
        'border_length': 0.05     # Уменьшаем влияние границ
    })
    
    # Параметры качества генерации
    quality_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'min_compactness': 0.7,      # Увеличиваем требования к компактности
        'max_border_ratio': 0.4,     # Уменьшаем допустимую длину границ
        'min_province_ratio': 0.95,   # Увеличиваем требования к размеру
        'max_size_variance': 0.15     # Уменьшаем допустимую разницу размеров
    })