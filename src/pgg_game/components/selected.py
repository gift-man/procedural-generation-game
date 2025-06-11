from dataclasses import dataclass
from typing import Optional

@dataclass
class SelectedComponent:
    """
    Компонент-маркер для выбранных сущностей.
    Используется для отслеживания выделенных провинций,
    юнитов и других игровых объектов.
    """
    # Время выделения (для анимации)
    selection_time: float = 0.0
    
    # ID игрока, который выделил сущность
    selector_id: Optional[int] = None
    
    # Флаг множественного выделения
    is_multi_select: bool = False
    
    def __bool__(self) -> bool:
        """
        Позволяет использовать компонент в условных выражениях.
        
        Returns:
            bool: True если сущность выделена
        """
        return True
