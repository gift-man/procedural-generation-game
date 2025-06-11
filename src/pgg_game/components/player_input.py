from dataclasses import dataclass , field
from enum import Enum, auto
from typing import Optional, Set

class InputAction(Enum):
    """Возможные действия игрока."""
    SELECT = auto()         # Выбор провинции/юнита
    MOVE = auto()          # Перемещение
    ATTACK = auto()        # Атака
    BUILD = auto()         # Строительство
    UPGRADE = auto()       # Улучшение
    CANCEL = auto()        # Отмена действия
    END_TURN = auto()      # Завершение хода

@dataclass
class PlayerInputComponent:
    """
    Компонент, определяющий способность сущности
    получать команды от игрока.
    """
    # ID игрока, которому принадлежит сущность
    player_id: int
    
    # Текущее выполняемое действие
    current_action: Optional[InputAction] = None
    
    # Доступные действия для данной сущности
    available_actions: Set[InputAction] = field(default_factory=set)
    
    # Цель действия (например, ID провинции для атаки)
    target_entity_id: Optional[int] = None
    
    def can_perform(self, action: InputAction) -> bool:
        """
        Проверяет, может ли сущность выполнить действие.
        
        Args:
            action: Проверяемое действие
            
        Returns:
            bool: True если действие доступно
        """
        return action in self.available_actions
    
    def start_action(self, action: InputAction) -> bool:
        """
        Начинает выполнение действия.
        
        Args:
            action: Действие для выполнения
            
        Returns:
            bool: True если действие начато успешно
        """
        if not self.can_perform(action):
            return False
        
        self.current_action = action
        return True
    
    def cancel_action(self) -> None:
        """Отменяет текущее действие."""
        self.current_action = None
        self.target_entity_id = None
    
    def set_target(self, target_id: int) -> None:
        """
        Устанавливает цель для текущего действия.
        
        Args:
            target_id: ID целевой сущности
        """
        self.target_entity_id = target_id
    
    def add_available_action(self, action: InputAction) -> None:
        """
        Добавляет действие в список доступных.
        
        Args:
            action: Действие для добавления
        """
        self.available_actions.add(action)
    
    def remove_available_action(self, action: InputAction) -> None:
        """
        Удаляет действие из списка доступных.
        
        Args:
            action: Действие для удаления
        """
        self.available_actions.discard(action)
        if self.current_action == action:
            self.cancel_action()