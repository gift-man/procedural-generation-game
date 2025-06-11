"""Система обработки событий."""
from typing import Dict, Callable, List
import pygame

class EventSystem:
    """
    Система обработки событий.
    Позволяет подписываться на события и обрабатывать их.
    """
    
    def __init__(self):
        """Инициализация системы событий."""
        # Словарь подписчиков на события
        # event_type -> list of callbacks
        self._subscribers: Dict[str, List[Callable]] = {}
        
        # Маппинг pygame событий в наши события
        self._pygame_event_mapping = {
            pygame.MOUSEMOTION: self._handle_mouse_motion,
            pygame.MOUSEBUTTONDOWN: self._handle_mouse_click,
            pygame.KEYDOWN: self._handle_key_down,
            pygame.KEYUP: self._handle_key_up
        }
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Подписка на событие.
        
        Args:
            event_type: Тип события
            callback: Функция обработчик
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """
        Отписка от события.
        
        Args:
            event_type: Тип события
            callback: Функция обработчик
        """
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
    
    def emit(self, event_type: str, event_data: Dict) -> None:
        """
        Вызов события.
        
        Args:
            event_type: Тип события
            event_data: Данные события
        """
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(event_data)
    
    def handle_pygame_event(self, event: pygame.event.Event) -> None:
        """
        Обработка pygame события.
        
        Args:
            event: Событие pygame
        """
        # Проверяем, есть ли обработчик для данного типа события
        if event.type in self._pygame_event_mapping:
            self._pygame_event_mapping[event.type](event)
    
    def _handle_mouse_motion(self, event: pygame.event.Event) -> None:
        """
        Обработка движения мыши.
        
        Args:
            event: Событие pygame
        """
        self.emit('mouse_motion', {
            'pos': event.pos,
            'rel': event.rel if hasattr(event, 'rel') else (0, 0),
            'buttons': event.buttons if hasattr(event, 'buttons') else (0, 0, 0)
        })
    
    def _handle_mouse_click(self, event: pygame.event.Event) -> None:
        """
        Обработка клика мыши.
        
        Args:
            event: Событие pygame
        """
        self.emit('mouse_click', {
            'pos': event.pos,
            'button': event.button,
            'touch': event.touch if hasattr(event, 'touch') else False
        })
    
    def _handle_key_down(self, event: pygame.event.Event) -> None:
        """
        Обработка нажатия клавиши.
        
        Args:
            event: Событие pygame
        """
        self.emit('key_down', {
            'key': event.key,
            'mod': event.mod,
            'unicode': event.unicode if hasattr(event, 'unicode') else '',
            'scancode': event.scancode if hasattr(event, 'scancode') else 0
        })
        
        # Специальные события для часто используемых клавиш
        if event.key == pygame.K_ESCAPE:
            self.emit('escape_pressed', {})
        elif event.key == pygame.K_RETURN:
            self.emit('enter_pressed', {})
        elif event.key == pygame.K_SPACE:
            self.emit('space_pressed', {})
    
    def _handle_key_up(self, event: pygame.event.Event) -> None:
        """
        Обработка отпускания клавиши.
        
        Args:
            event: Событие pygame
        """
        self.emit('key_up', {
            'key': event.key,
            'mod': event.mod
        })