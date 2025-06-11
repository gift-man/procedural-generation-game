from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from collections import deque

@dataclass
class Event:
    """
    Структура события в игре.
    
    Attributes:
        type: Тип события (например, 'province_selected', 'turn_ended')
        data: Дополнительные данные события
    """
    type: str
    data: Dict[str, Any]

class EventQueue:
    """
    Очередь событий с поддержкой подписки и асинхронной обработки.
    Реализует паттерн Observer для событийно-ориентированной архитектуры.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_queue = deque()
        
    def subscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Подписывает обработчик на определенный тип события.
        
        Args:
            event_type: Тип события для подписки
            handler: Функция-обработчик события
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """
        Отписывает обработчик от события.
        
        Args:
            event_type: Тип события
            handler: Функция-обработчик для отписки
        """
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)
            if not self._subscribers[event_type]:
                del self._subscribers[event_type]
    
    def emit(self, event: Event) -> None:
        """
        Добавляет событие в очередь для последующей обработки.
        
        Args:
            event: Событие для обработки
        """
        self._event_queue.append(event)
    
    def process_events(self) -> None:
        """Обрабатывает все события в очереди."""
        while self._event_queue:
            event = self._event_queue.popleft()
            if event.type in self._subscribers:
                for handler in self._subscribers[event.type]:
                    try:
                        handler(event.data)
                    except Exception as e:
                        print(f"Ошибка при обработке события {event.type}: {e}")

    def clear(self) -> None:
        """Очищает очередь событий."""
        self._event_queue.clear()