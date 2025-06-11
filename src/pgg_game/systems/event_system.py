"""Система обработки событий."""
from typing import Dict, List, Callable, Any
import pygame

class EventSystem:
    """Система обработки игровых событий."""
    
    def __init__(self):
        """Инициализация системы событий."""
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Подписка на событие.
        
        Args:
            event_type: Тип события
            callback: Функция обратного вызова
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """
        Отписка от события.
        
        Args:
            event_type: Тип события
            callback: Функция обратного вызова
        """
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
            if not self._subscribers[event_type]:
                del self._subscribers[event_type]
    
    def emit(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Генерация события.
        
        Args:
            event_type: Тип события
            event_data: Данные события
        """
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(event_data)
    
    def handle_pygame_event(self, pygame_event: pygame.event.Event) -> None:
        """
        Обработка событий Pygame.
        
        Args:
            pygame_event: Событие Pygame
        """
        # Обработка движения мыши
        if pygame_event.type == pygame.MOUSEMOTION:
            self.emit('mouse_motion', {'pos': pygame_event.pos})
        
        # Обработка кликов мыши
        elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
            event_data = {
                'pos': pygame_event.pos,
                'button': pygame_event.button
            }
            self.emit('mouse_click', event_data)
        
        # Обработка отпускания кнопок мыши
        elif pygame_event.type == pygame.MOUSEBUTTONUP:
            event_data = {
                'pos': pygame_event.pos,
                'button': pygame_event.button
            }
            self.emit('mouse_up', event_data)
        
        # Обработка нажатий клавиш
        elif pygame_event.type == pygame.KEYDOWN:
            event_data = {
                'key': pygame_event.key,
                'mod': pygame_event.mod,
                'unicode': pygame_event.unicode
            }
            self.emit('key_down', event_data)
        
        # Обработка отпускания клавиш
        elif pygame_event.type == pygame.KEYUP:
            event_data = {
                'key': pygame_event.key,
                'mod': pygame_event.mod
            }
            self.emit('key_up', event_data)