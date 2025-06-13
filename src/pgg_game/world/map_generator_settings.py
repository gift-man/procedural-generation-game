"""Настройки генерации карты."""
from dataclasses import dataclass
from typing import Dict, Optional
from ..world.noise_generator import NoiseConfig

@dataclass
class MapGenerationSettings:
    """Основные параметры генерации карты."""
    # Настройки шума
    noise_config: Optional[NoiseConfig] = None
    
    # Параметры острова
    min_island_size: int = 100  # Минимальный размер острова в клетках
    max_island_size: int = 200  # Максимальный размер острова
    edge_buffer: int = 3       # Отступ от края карты
    water_level: float = 0.4   # Уровень воды (0-1)
    
    # Параметры провинций
    min_province_size: int = 15  # Минимальный размер провинции
    max_province_size: int = 25  # Максимальный размер провинции
    min_provinces: int = 5      # Минимальное количество провинций 
    max_provinces: int = 8      # Максимальное количество провинций
    
    # Параметры генерации
    smoothing_passes: int = 2   # Количество проходов сглаживания
    connection_passes: int = 2  # Проходы соединения областей
    max_attempts: int = 50     # Максимум попыток генерации
    
    # Настройки ресурсов
    resource_clusters: Dict[str, Dict[str, float]] = None

    def __post_init__(self):
        """Инициализация значений по умолчанию."""
        if self.noise_config is None:
            self.noise_config = NoiseConfig()
            
        if self.resource_clusters is None:
            self.resource_clusters = {
                'GOLD': {'min_size': 1, 'chance': 0.15},
                'STONE': {'min_size': 2, 'chance': 0.25},
                'WOOD': {'min_size': 4, 'chance': 0.35},
                'FOOD': {'min_size': 1, 'chance': 1.0}
            }

    def validate(self) -> bool:
        """Проверяет корректность настроек."""
        if self.min_island_size > self.max_island_size:
            return False
            
        if self.min_province_size > self.max_province_size:
            return False
            
        if self.min_provinces > self.max_provinces:
            return False
            
        if self.water_level < 0 or self.water_level > 1:
            return False
            
        # Проверяем, что острова могут вместить минимальное число провинций
        if self.min_island_size < (self.min_provinces * self.min_province_size):
            return False
            
        if not self.resource_clusters:
            return False
            
        return True