"""
Модуль генерации шума для процедурной генерации карты.
Использует собственную реализацию шума без внешних зависимостей.
"""
import random
import math
from typing import Optional, Protocol
from dataclasses import dataclass

@dataclass
class NoiseConfig:
    """Конфигурация для генерации шума."""
    seed: int = random.randint(0, 1000)
    octaves: int = 6
    persistence: float = 0.5
    lacunarity: float = 2.0
    scale: float = 50.0
    
    def __post_init__(self):
        """Инициализация значений по умолчанию."""
        random.seed(self.seed)

class NoiseGenerator(Protocol):
    """Интерфейс для генераторов шума."""
    def noise2d(self, x: float, y: float) -> float:
        """Генерирует 2D шум для заданных координат."""
        ...

class SimplexNoise:
    """Базовая реализация шума без внешних зависимостей."""
    def __init__(self, config: Optional[NoiseConfig] = None):
        self.config = config or NoiseConfig()
        self._init_gradients()
    
    def _init_gradients(self) -> None:
        """Инициализирует градиенты для генерации шума."""
        self._gradients = [(
            math.cos(angle),
            math.sin(angle)
        ) for angle in [
            i * math.pi * 2 / 8
            for i in range(8)
        ]]
        
        self._perm = list(range(256))
        random.seed(self.config.seed)
        random.shuffle(self._perm)
        self._perm += self._perm
    
    def noise2d(self, x: float, y: float) -> float:
        """Генерирует 2D шум."""
        value = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0
        
        # Суммируем октавы
        for _ in range(self.config.octaves):
            nx = x * frequency * self.config.scale
            ny = y * frequency * self.config.scale
            
            noise_val = self._generate_base_noise(nx, ny)
            
            value += noise_val * amplitude
            max_value += amplitude
            
            amplitude *= self.config.persistence
            frequency *= self.config.lacunarity
        
        # Нормализуем результат
        if max_value > 0:
            value /= max_value
        
        return value
    
    def _generate_base_noise(self, x: float, y: float) -> float:
        """Генерирует базовое значение шума для одной октавы."""
        x0 = math.floor(x)
        y0 = math.floor(y)
        
        dx = x - x0
        dy = y - y0
        
        dx = self._smooth(dx)
        dy = self._smooth(dy)
        
        v00 = self._gradient(x0, y0, dx, dy)
        v10 = self._gradient(x0 + 1, y0, dx - 1, dy)
        v01 = self._gradient(x0, y0 + 1, dx, dy - 1)
        v11 = self._gradient(x0 + 1, y0 + 1, dx - 1, dy - 1)
        
        return self._lerp(
            self._lerp(v00, v10, dx),
            self._lerp(v01, v11, dx),
            dy
        )
    
    def _gradient(self, ix: int, iy: int, dx: float, dy: float) -> float:
        """Вычисляет влияние градиента в точке."""
        idx = self._perm[(ix + self._perm[iy & 255]) & 255] & 7
        grad = self._gradients[idx]
        return dx * grad[0] + dy * grad[1]
    
    @staticmethod
    def _smooth(t: float) -> float:
        """Сглаживающая функция."""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    @staticmethod
    def _lerp(a: float, b: float, t: float) -> float:
        """Линейная интерполяция."""
        return a + t * (b - a)

def create_noise_generator(config: Optional[NoiseConfig] = None) -> NoiseGenerator:
    """
    Создает генератор шума.
    
    Args:
        config: Конфигурация генерации шума
    
    Returns:
        NoiseGenerator: Генератор шума
    """
    return SimplexNoise(config)