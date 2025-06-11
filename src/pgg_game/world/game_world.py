"""Игровой мир."""
from typing import Dict, Any, Type, TypeVar, Optional, Set, List
from ..components.transform import TransformComponent

T = TypeVar('T')

class GameWorld:
    """
    Класс игрового мира.
    Управляет сущностями и их компонентами.
    """
    
    def __init__(self):
        """Инициализация игрового мира."""
        self._next_entity_id = 0
        self._entities: Dict[int, Dict[Type, Any]] = {}
        self._components: Dict[Type, Dict[int, Any]] = {}
        self._entities_with_components: Dict[Type, Set[int]] = {}
    
    def create_entity(self) -> int:
        """
        Создает новую сущность.
        
        Returns:
            int: ID новой сущности
        """
        entity_id = self._next_entity_id
        self._next_entity_id += 1
        self._entities[entity_id] = {}
        return entity_id
    
    def add_component(self, entity_id: int, component: Any) -> None:
        """
        Добавляет компонент к сущности.
        
        Args:
            entity_id: ID сущности
            component: Компонент для добавления
        """
        component_type = type(component)
        
        # Создаем словарь для типа компонента, если его еще нет
        if component_type not in self._components:
            self._components[component_type] = {}
        
        # Создаем множество для типа компонента, если его еще нет
        if component_type not in self._entities_with_components:
            self._entities_with_components[component_type] = set()
        
        # Добавляем компонент
        self._components[component_type][entity_id] = component
        self._entities[entity_id][component_type] = component
        self._entities_with_components[component_type].add(entity_id)
    
    def get_component(self, entity_id: int, component_type: Type[T]) -> Optional[T]:
        """
        Получает компонент сущности по типу.
        
        Args:
            entity_id: ID сущности
            component_type: Тип компонента

        Returns:
            Optional[T]: Компонент или None, если не найден
        """
        if entity_id in self._entities:
            return self._entities[entity_id].get(component_type)
        return None
    
    def get_entities_with_component(self, component_type: Type[T]) -> List[int]:
        """
        Получает список ID сущностей, имеющих указанный компонент.
        
        Args:
            component_type: Тип компонента

        Returns:
            List[int]: Список ID сущностей
        """
        return list(self._entities_with_components.get(component_type, set()))
    
    def get_all_components(self, component_type: Type[T]) -> Dict[int, T]:
        """
        Получает все компоненты определенного типа.
        
        Args:
            component_type: Тип компонента

        Returns:
            Dict[int, T]: Словарь {entity_id: component}
        """
        return self._components.get(component_type, {})
    
    def remove_component(self, entity_id: int, component_type: Type) -> None:
        """
        Удаляет компонент у сущности.
        
        Args:
            entity_id: ID сущности
            component_type: Тип компонента для удаления
        """
        if entity_id in self._entities:
            if component_type in self._entities[entity_id]:
                del self._entities[entity_id][component_type]
            
            if component_type in self._components:
                if entity_id in self._components[component_type]:
                    del self._components[component_type][entity_id]
            
            if component_type in self._entities_with_components:
                self._entities_with_components[component_type].discard(entity_id)
    
    def remove_entity(self, entity_id: int) -> None:
        """
        Удаляет сущность и все её компоненты.
        
        Args:
            entity_id: ID сущности для удаления
        """
        if entity_id in self._entities:
            # Удаляем все компоненты сущности
            for component_type in list(self._entities[entity_id].keys()):
                self.remove_component(entity_id, component_type)
            # Удаляем саму сущность
            del self._entities[entity_id]
    
    def has_component(self, entity_id: int, component_type: Type) -> bool:
        """
        Проверяет наличие компонента у сущности.
        
        Args:
            entity_id: ID сущности
            component_type: Тип компонента

        Returns:
            bool: True если компонент есть, иначе False
        """
        return (
            entity_id in self._entities and
            component_type in self._entities[entity_id]
        )
    
    def get_entity_components(self, entity_id: int) -> Dict[Type, Any]:
        """
        Получает все компоненты сущности.
        
        Args:
            entity_id: ID сущности

        Returns:
            Dict[Type, Any]: Словарь {тип_компонента: компонент}
        """
        return self._entities.get(entity_id, {})