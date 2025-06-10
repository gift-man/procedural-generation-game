"""Обработка событий"""
import pygame

class EventHandler:
    def __init__(self, game):
        self.game = game
    
    def handle(self, event):
        """Обрабатывает событие"""
        if event.type == pygame.QUIT:
            self.game.running = False
        elif event.type == pygame.KEYDOWN:
            self.handle_keydown(event)
    
    def handle_keydown(self, event):
        """Обрабатывает нажатие клавиш"""
        if event.key == pygame.K_SPACE:
            self.game.regenerate_provinces()
        elif event.key == pygame.K_ESCAPE:
            self.game.running = False
