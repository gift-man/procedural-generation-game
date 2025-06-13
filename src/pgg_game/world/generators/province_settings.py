"""Настройки генерации провинций."""
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ProvinceGenerationConfig:
    """Настройки генерации провинций."""
    # Базовые параметры
    min_size: int = 4          # Минимальный размер провинции
    max_size: int = 8          # Максимальный размер провинции
    min_provinces: int = 8     # Минимальное количество провинций
    max_provinces: int = 15    # Максимальное количество провинций
    
    # Параметры расположения
    spacing: int = 2           # Минимальное расстояние между провинциями
    initial_radius: int = 4    # Начальный радиус размещения провинций (в клетках)
    max_radius: int = 10      # Максимальный радиус для роста
    
    # Параметры роста
    growth_steps: int = 5      # Количество шагов роста провинции
    growth_chance: float = 0.8 # Шанс роста на каждом шаге
    min_neighbors: int = 1     # Минимальное число соседей для роста
    max_neighbors: int = 3     # Максимальное число соседей для роста
    
    # Параметры генерации
    border_smoothing: int = 2  # Количество проходов сглаживания
    max_attempts: int = 50     # Максимальное число попыток на провинцию
    edge_distance: int = 2     # Минимальное расстояние до края карты
    
    # Веса для оценки клеток при росте
    weights: Dict[str, float] = field(default_factory=lambda: {
        'neighbor_count': 0.4,    # Вес количества соседей
        'center_distance': 0.3,   # Вес расстояния до центра
        'edge_penalty': 0.2,      # Штраф за близость к краю
        'direction': 0.1          # Вес сохранения направления роста
    })