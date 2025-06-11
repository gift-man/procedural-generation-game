"""Компонент для позиционирования объектов."""
from typing import Tuple

class TransformComponent:
    """Компонент для хранения позиции и размера объекта."""
    
    def __init__(self, x: float, y: float, scale_x: float = 1.0, scale_y: float = 1.0):
        """
        Инициализация компонента трансформации.

        Args:
            x: Позиция по X
            y: Позиция по Y
            scale_x: Масштаб по X
            scale_y: Масштаб по Y
        """
        self.x = x
        self.y = y
        self.scale_x = scale_x
        self.scale_y = scale_y
    
    def set_position(self, x: float, y: float) -> None:
        """
        Устанавливает позицию объекта.

        Args:
            x: Новая позиция по X
            y: Новая позиция по Y
        """
        self.x = x
        self.y = y
    
    def move(self, dx: float, dy: float) -> None:
        """
        Перемещает объект на заданное расстояние.

        Args:
            dx: Смещение по X
            dy: Смещение по Y
        """
        self.x += dx
        self.y += dy
    
    def set_scale(self, scale_x: float, scale_y: float) -> None:
        """
        Устанавливает масштаб объекта.

        Args:
            scale_x: Новый масштаб по X
            scale_y: Новый масштаб по Y
        """
        self.scale_x = scale_x
        self.scale_y = scale_y
    
    def get_position(self) -> Tuple[float, float]:
        """
        Получает текущую позицию объекта.

        Returns:
            Tuple[float, float]: Позиция (x, y)
        """
        return self.x, self.y
    
    def get_scale(self) -> Tuple[float, float]:
        """
        Получает текущий масштаб объекта.

        Returns:
            Tuple[float, float]: Масштаб (scale_x, scale_y)
        """
        return self.scale_x, self.scale_y