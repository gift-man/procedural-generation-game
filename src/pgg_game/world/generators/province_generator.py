"""Генератор провинций."""
import random
import math
from typing import Set, Dict, List, Tuple, Optional
from collections import deque

from .province_settings import ProvinceGenerationConfig
from .province_metrics import ProvinceAnalyzer, ProvinceMetrics
from ...components.province import Province
from ...config import GRID_WIDTH, GRID_HEIGHT

class ProvinceGenerator:
    """Улучшенный генератор провинций."""
    
    def __init__(self, config: Optional[ProvinceGenerationConfig] = None):
        """
        Инициализация генератора.
        
        Args:
            config: Настройки генерации
        """
        self.config = config or ProvinceGenerationConfig()
        self.analyzer = ProvinceAnalyzer()
        self.island_analysis = None
    
    def generate_provinces(self, island_cells: Set[Tuple[int, int]]) -> List[Province]:
        """
        Генерирует провинции для острова.
        
        Args:
            island_cells: Множество клеток острова
            
        Returns:
            List[Province]: Список созданных провинций
        """
        try:
            # Анализируем остров
            self.island_analysis = self._analyze_island(island_cells)
            
            # Пытаемся выполнить умную генерацию
            provinces = self._smart_generation(island_cells)
            if self._is_generation_acceptable(provinces):
                return provinces
            
            # Если не получилось, используем экстренную генерацию
            return self._emergency_generation(island_cells)
            
        except Exception as e:
            print(f"Ошибка при генерации провинций: {e}")
            return self._emergency_generation(island_cells)