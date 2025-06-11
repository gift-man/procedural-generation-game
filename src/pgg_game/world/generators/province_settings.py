"""Настройки генерации провинций."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProvinceGenerationConfig:
    """Конфигурация для генерации провинций."""
    # Базовые ограничения
    min_province_size: int = 4
    max_province_size: int = 12
    min_provinces: int = 8
    max_provinces: int = 20
    
    # Параметры адаптивной генерации
    optimal_size: int = 6
    target_count: Optional[int] = None
    
    # Настройки размещения семян
    min_seed_distance: int = 3
    prefer_central_seeds: bool = True
    seed_random_offset: float = 0.2
    
    # Параметры роста провинций
    growth_balance: float = 0.7  # Баланс между компактностью и равномерностью роста
    allow_diagonal_growth: bool = False  # Рост только по основным направлениям
    
    # Ограничения генерации
    max_attempts: int = 1000
    quality_threshold: float = 0.8  # Минимальное качество для принятия результата
    
    # Веса для оценки качества
    weights = {
        'compactness': 0.4,    # Насколько компактна форма провинции
        'connectivity': 0.3,    # Насколько хорошо соединены клетки
        'size_balance': 0.3,   # Насколько равномерно распределены размеры
    }