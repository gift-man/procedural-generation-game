"""Настройки генерации провинций."""
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class ProvinceGenerationConfig:
    """Конфигурация для генерации провинций."""
    # Базовые ограничения размера
    min_province_size: int = 4
    max_province_size: int = 8
    
    # Вероятности размеров провинций (должны в сумме давать 1.0)
    size_probabilities: Dict[int, float] = field(default_factory=lambda: {
        4: 0.15,  # 15% шанс для провинций размером 4
        5: 0.20,  # 20% шанс для провинций размером 5
        6: 0.30,  # 30% шанс для провинций размером 6
        7: 0.20,  # 20% шанс для провинций размером 7
        8: 0.15   # 15% шанс для провинций размером 8
    })
    
    # Настройки генерации
    max_generation_attempts: int = 5  # Максимальное число попыток генерации карты
    max_province_attempts: int = 50   # Максимальное число попыток создания одной провинции
    allow_diagonal_growth: bool = False  # Рост только по основным направлениям
    check_plus_intersection: bool = True  # Проверка на плюсовые пересечения
    
    # Параметры проверки качества
    min_province_count: int = 3  # Минимальное количество провинций
    min_total_coverage: float = 0.95  # Минимальный процент занятых клеток суши
    quality_threshold: float = 0.8  # Минимальное качество для принятия результата