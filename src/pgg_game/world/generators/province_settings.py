"""Настройки генерации провинций."""
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ProvinceGenerationConfig:
    """Настройки генерации провинций."""
    # Базовые параметры
    min_size: int = 15           # Увеличиваем минимальный размер для лучшей видимости
    max_size: int = 25           # Увеличиваем максимальный размер
    min_provinces: int = 5       # Уменьшаем минимум провинций
    max_provinces: int = 8       # Уменьшаем максимум провинций
    
    # Параметры расположения
    spacing: int = 1            # Уменьшаем расстояние для более плотного размещения
    initial_radius: int = 6     # Увеличиваем начальный радиус
    max_radius: int = 12       # Увеличиваем максимальный радиус
    edge_distance: int = 3     # Отступ от края карты
    
    # Параметры роста
    growth_steps: int = 8      # Увеличиваем количество шагов роста
    growth_chance: float = 0.9 # Увеличиваем шанс роста
    min_neighbors: int = 1     # Минимум соседей для роста
    max_neighbors: int = 4     # Максимум соседей для роста
    
    # Параметры генерации
    border_smoothing: int = 2  # Сглаживание границ
    max_attempts: int = 100    # Увеличиваем количество попыток
    max_generation_attempts: int = 50  # Добавляем пропущенный параметр
    check_plus_intersection: bool = False # Отключаем проверку плюсовых пересечений
    min_total_coverage: float = 0.8  # Добавляем минимальное покрытие
    
    # Веса для оценки клеток
    weights: Dict[str, float] = field(default_factory=lambda: {
        'neighbor_count': 0.5,     # Повышаем вес соседей
        'center_distance': 0.3,    # Вес расстояния до центра
        'edge_penalty': 0.1,       # Уменьшаем штраф за края
        'direction': 0.1,          # Вес направления роста
        'compactness': 0.4,        # Добавляем вес компактности
        'border_length': 0.2       # Добавляем вес длины границы
    })