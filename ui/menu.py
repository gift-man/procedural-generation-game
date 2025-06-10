"""Главное меню игры"""
import pygame
from core.settings import *

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_button = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.buttons = []
        self.create_buttons()
    
    def create_buttons(self):
        """Создаёт кнопки меню"""
        screen_width, screen_height = self.screen.get_size()
        
        # Кнопка "Сгенерировать карту"
        button_width = 300
        button_height = 80
        button_x = (screen_width - button_width) // 2
        button_y = screen_height // 2
        
        self.buttons.append({
            'rect': pygame.Rect(button_x, button_y, button_width, button_height),
            'text': 'Сгенерировать карту',
            'action': 'generate_map',
            'color': (70, 130, 180),
            'hover_color': (100, 160, 210)
        })
        
        # Кнопка "Выход"
        exit_y = button_y + 120
        self.buttons.append({
            'rect': pygame.Rect(button_x, exit_y, button_width, button_height),
            'text': 'Выход',
            'action': 'exit',
            'color': (180, 70, 70),
            'hover_color': (210, 100, 100)
        })
    
    def draw(self):
        """Отрисовывает меню"""
        # Фон
        self.screen.fill((30, 40, 50))
        
        # Заголовок
        title_text = self.font_title.render("ГЕНЕРАТОР ПРОВИНЦИЙ", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Подзаголовок
        subtitle_text = self.font_small.render("Создание идеальных территорий", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(self.screen.get_width() // 2, 200))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Кнопки
        mouse_pos = pygame.mouse.get_pos()
        
        for button in self.buttons:
            # Определяем цвет кнопки (hover эффект)
            if button['rect'].collidepoint(mouse_pos):
                color = button['hover_color']
            else:
                color = button['color']
            
            # Рисуем кнопку
            pygame.draw.rect(self.screen, color, button['rect'])
            pygame.draw.rect(self.screen, (255, 255, 255), button['rect'], 3)
            
            # Текст кнопки
            text_surf = self.font_button.render(button['text'], True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=button['rect'].center)
            self.screen.blit(text_surf, text_rect)
        
        # Информация внизу
        info_text = self.font_small.render("Алгоритм создаёт идеальные провинции без плюсовых пересечений", True, (150, 150, 150))
        info_rect = info_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 50))
        self.screen.blit(info_text, info_rect)
    
    def handle_event(self, event):
        """Обрабатывает события меню"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            for button in self.buttons:
                if button['rect'].collidepoint(mouse_pos):
                    return button['action']
        
        return None
