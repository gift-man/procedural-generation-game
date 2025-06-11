"""Компонент ресурсов."""
from enum import Enum
from typing import Dict

class ResourceType(Enum):
    """Типы ресурсов."""
    FOOD = "food"     # Еда (луга)
    WOOD = "wood"     # Дерево (лес)
    STONE = "stone"   # Камень
    GOLD = "gold"     # Золото

class ResourceComponent:
    """Компонент для хранения ресурсов."""
    
    def __init__(self):
        """Инициализация компонента ресурсов."""
        self.resources: Dict[ResourceType, int] = {}
    
    def add_resource(self, resource_type: ResourceType, amount: int) -> None:
        """
        Добавляет ресурс.
        
        Args:
            resource_type: Тип ресурса
            amount: Количество
        """
        if resource_type not in self.resources:
            self.resources[resource_type] = 0
        self.resources[resource_type] += amount
    
    def remove_resource(self, resource_type: ResourceType, amount: int) -> bool:
        """
        Удаляет ресурс.
        
        Args:
            resource_type: Тип ресурса
            amount: Количество
            
        Returns:
            bool: True если удаление успешно, False если недостаточно ресурса
        """
        if resource_type not in self.resources or self.resources[resource_type] < amount:
            return False
            
        self.resources[resource_type] -= amount
        return True
    
    def get_resource(self, resource_type: ResourceType) -> int:
        """
        Получает количество ресурса.
        
        Args:
            resource_type: Тип ресурса
            
        Returns:
            int: Количество ресурса
        """
        return self.resources.get(resource_type, 0)