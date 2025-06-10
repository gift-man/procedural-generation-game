"""UI элементы внутри игры"""
import pygame
from core.settings import *

class GameUI:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.font = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 20)
        
        # Состояния UI
        self.show_confirmation = False
        self.show_info = False  # Скрыто по умолчанию
        self.show_popup_menu = False  # ВАЖНО: инициализируем всплывающее меню
        
        # Инициализация элементов
        self.confirmation_action = None
        
        self.create_ui_elements()
    def create_ui_elements(self):
            """Создание элементов UI включая всплывающее меню"""
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            
            # НОВОЕ: Всплывающее меню в центре экрана
            menu_width = 400
            menu_height = 300
            menu_x = (screen_width - menu_width) // 2
            menu_y = (screen_height - menu_height) // 2
            
            self.popup_menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
            
            # Кнопки всплывающего меню
            button_width = 300
            button_height = 50
            button_x = menu_x + (menu_width - button_width) // 2
            
            # Кнопка "Главное меню"
            self.main_menu_button = pygame.Rect(button_x, menu_y + 60, button_width, button_height)
            
            # Кнопка "Новая карта"
            self.new_map_button = pygame.Rect(button_x, menu_y + 120, button_width, button_height)
            
            # Кнопка "Вернуться"
            self.return_button = pygame.Rect(button_x, menu_y + 180, button_width, button_height)
            
            # Диалог подтверждения (адаптируем к размеру экрана)
            dialog_width = min(400, screen_width - 40)
            dialog_height = min(200, screen_height - 40)
            dialog_x = (screen_width - dialog_width) // 2
            dialog_y = (screen_height - dialog_height) // 2
            
            self.confirmation_dialog = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
            
            button_y = dialog_y + dialog_height - 60
            button_spacing = dialog_width // 4
            
            self.yes_button = pygame.Rect(dialog_x + button_spacing - 50, button_y, 100, 40)
            self.no_button = pygame.Rect(dialog_x + 3 * button_spacing - 50, button_y, 100, 40)
    
    def draw(self):
        """ОБНОВЛЕННАЯ отрисовка с всплывающим меню"""
        
        # Информация об острове (если включена И если нет всплывающего меню)
        if self.show_info and not self.show_popup_menu:
            self.draw_province_info()
        
        # НОВОЕ: Всплывающее меню
        if self.show_popup_menu:
            self.draw_popup_menu()
        
        # Окно подтверждения (всегда поверх всего)
        if self.show_confirmation:
            self.draw_confirmation_dialog()

 
    def draw_popup_menu(self):
        """НОВАЯ функция: Отрисовка всплывающего меню"""
        # Затемнение всего экрана
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Фон меню
        pygame.draw.rect(self.screen, (50, 50, 50), self.popup_menu_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.popup_menu_rect, 3)
        
        # Заголовок меню
        title_text = self.font.render("МЕНЮ ИГРЫ", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.popup_menu_rect.centerx, self.popup_menu_rect.y + 30))
        self.screen.blit(title_text, title_rect)
        
        # Кнопки меню с hover эффектом
        mouse_pos = pygame.mouse.get_pos()
        
        # Кнопка "Главное меню"
        main_menu_color = (200, 100, 100) if self.main_menu_button.collidepoint(mouse_pos) else (170, 70, 70)
        pygame.draw.rect(self.screen, main_menu_color, self.main_menu_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.main_menu_button, 2)
        
        main_text = self.font_small.render("Главное меню", True, (255, 255, 255))
        main_rect = main_text.get_rect(center=self.main_menu_button.center)
        self.screen.blit(main_text, main_rect)
        
        # Кнопка "Новая карта"
        new_map_color = (200, 150, 100) if self.new_map_button.collidepoint(mouse_pos) else (170, 120, 70)
        pygame.draw.rect(self.screen, new_map_color, self.new_map_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.new_map_button, 2)
        
        new_text = self.font_small.render("Создать новую карту", True, (255, 255, 255))
        new_rect = new_text.get_rect(center=self.new_map_button.center)
        self.screen.blit(new_text, new_rect)
        
        # Кнопка "Вернуться"
        return_color = (100, 150, 200) if self.return_button.collidepoint(mouse_pos) else (70, 120, 170)
        pygame.draw.rect(self.screen, return_color, self.return_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.return_button, 2)
        
        return_text = self.font_small.render("Вернуться", True, (255, 255, 255))
        return_rect = return_text.get_rect(center=self.return_button.center)
        self.screen.blit(return_text, return_rect)
        
        # НОВОЕ: Подсказка про клавишу I
        hint_text = self.font_small.render("Нажмите (I) для дополнительной информации", True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(self.popup_menu_rect.centerx, self.popup_menu_rect.bottom - 30))
        self.screen.blit(hint_text, hint_rect)

    def draw_control_buttons(self):
        """ИСПРАВЛЕННАЯ отрисовка кнопок управления БЕЗ пересечений"""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Кнопка "В меню" (слева вверху, ПОД информацией о ходе)
        menu_width = min(120, screen_width - 40)
        menu_height = 35
        menu_x = 20
        menu_y = 120  # ИСПРАВЛЕНО: увеличено с 75 до 120 (больше места под информацией о ходе)
        
        self.menu_button = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        
        # Кнопка "Перегенерировать карту" (справа вверху, НАД кнопкой конца хода)  
        regen_width = min(160, screen_width - 40)
        regen_height = 35
        regen_x = screen_width - regen_width - 20  # ИСПРАВЛЕНО: убираем -220, размещаем в самом правом углу
        regen_y = 80  # ИСПРАВЛЕНО: размещаем выше кнопки конца хода
        
        self.regenerate_button = pygame.Rect(regen_x, regen_y, regen_width, regen_height)
        
        # Цвета с hover эффектом
        mouse_pos = pygame.mouse.get_pos()
        
        # Отрисовка кнопки "В меню"
        if self.menu_button.collidepoint(mouse_pos):
            menu_color = (100, 100, 180)
        else:
            menu_color = (70, 70, 150)
        
        pygame.draw.rect(self.screen, menu_color, self.menu_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.menu_button, 2)
        
        menu_text = self.font_small.render("В меню", True, (255, 255, 255))
        menu_rect = menu_text.get_rect(center=self.menu_button.center)
        self.screen.blit(menu_text, menu_rect)
        
        # Отрисовка кнопки "Перегенерировать"
        if self.regenerate_button.collidepoint(mouse_pos):
            regen_color = (200, 80, 80)
        else:
            regen_color = (170, 60, 60)
        
        pygame.draw.rect(self.screen, regen_color, self.regenerate_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.regenerate_button, 2)
        
        regen_text = self.font_small.render("Новая карта", True, (255, 255, 255))
        regen_rect = regen_text.get_rect(center=self.regenerate_button.center)
        self.screen.blit(regen_text, regen_rect)


    def draw_info_toggle_hint(self):
        """Показывает подсказку о клавише I"""
        hint_text = f"I - {'скрыть' if self.show_info else 'показать'} информацию"
        hint_surface = self.font_small.render(hint_text, True, (150, 150, 150))
        
        # Позиционируем в правом нижнем углу
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        hint_rect = hint_surface.get_rect()
        hint_rect.bottomright = (screen_width - 10, screen_height - 10)
        
        # Полупрозрачный фон
        bg_rect = hint_rect.inflate(10, 5)
        overlay = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, bg_rect)
        
        self.screen.blit(hint_surface, hint_rect)

    def draw_province_info(self):
            """ОБНОВЛЕННАЯ информация об острове с подсказками"""
            if not (hasattr(self.game, 'provinces') and self.game.provinces):
                return
            
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            
            # Панель информации (больше места для подсказок)
            max_panel_width = min(400, screen_width - 40)
            max_panel_height = min(280, screen_height - 100)
            
            panel_x = 20
            panel_y = max(20, screen_height - max_panel_height - 20)
            
            info_rect = pygame.Rect(panel_x, panel_y, max_panel_width, max_panel_height)
            
            # Проверяем границы
            if info_rect.bottom > screen_height - 20:
                info_rect.bottom = screen_height - 20
            if info_rect.right > screen_width - 20:
                info_rect.right = screen_width - 20
            
            # Полупрозрачный фон
            overlay = pygame.Surface((info_rect.width, info_rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (info_rect.x, info_rect.y))
            
            # Белая рамка
            pygame.draw.rect(self.screen, (255, 255, 255), info_rect, 2)
            
            # Контент
            content_x = info_rect.x + 10
            content_y = info_rect.y + 10
            content_width = info_rect.width - 20
            line_height = 18
            
            current_y = content_y
            
            # Заголовок
            title = self.font_small.render("ИНФОРМАЦИЯ ОБ ОСТРОВЕ", True, (255, 255, 255))
            self.screen.blit(title, (content_x, current_y))
            current_y += 25
            
            # Статистика провинций
            if hasattr(self.game, 'provinces'):
                total_provinces = len(self.game.provinces)
                sizes = [len(prov['cells']) for prov in self.game.provinces]
                
                province_info = [
                    f"Провинций: {total_provinces}",
                    f"Размеры: {min(sizes)}-{max(sizes)} клеток",
                    f"Всего клеток: {sum(sizes)}"
                ]
                
                for text in province_info:
                    if current_y + line_height > info_rect.bottom - 80:  # Оставляем место для подсказок
                        break
                    
                    text_surf = self.font_small.render(text, True, (255, 255, 255))
                    self.screen.blit(text_surf, (content_x, current_y))
                    current_y += line_height
            
            # Разделитель
            current_y += 10
            pygame.draw.line(self.screen, (255, 255, 255), 
                            (content_x, current_y), 
                            (content_x + content_width - 10, current_y), 1)
            current_y += 15
            
            # НОВОЕ: Подсказки управления
            hints = [
                "УПРАВЛЕНИЕ:",
                "B - строительство зданий",
                "Enter - конец хода",
                "I - показать/скрыть информацию",
                "Меню - дополнительные опции"
            ]
            
            for hint in hints:
                if current_y + line_height > info_rect.bottom - 10:
                    break
                
                if hint == "УПРАВЛЕНИЕ:":
                    text_surf = self.font_small.render(hint, True, (255, 255, 100))  # Желтый заголовок
                else:
                    text_surf = self.font_small.render(hint, True, (200, 200, 200))  # Серые подсказки
                
                self.screen.blit(text_surf, (content_x, current_y))
                current_y += line_height
    
    def draw_confirmation_dialog(self):
        """ИСПРАВЛЕННЫЙ диалог подтверждения"""
        # Затемнение фона
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Диалоговое окно
        pygame.draw.rect(self.screen, (50, 50, 50), self.confirmation_dialog)
        pygame.draw.rect(self.screen, (200, 200, 200), self.confirmation_dialog, 3)
        
        # ИСПРАВЛЕНО: Текст с проверкой размеров
        title_text = self.font.render("Подтверждение", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.confirmation_dialog.centerx, self.confirmation_dialog.top + 40))
        
        # Проверяем что заголовок помещается
        if title_rect.width > self.confirmation_dialog.width - 20:
            title_text = self.font_small.render("Подтверждение", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(self.confirmation_dialog.centerx, self.confirmation_dialog.top + 40))
        
        self.screen.blit(title_text, title_rect)
        
        # Текст вопроса
        question_text = self.font_small.render("Перегенерировать карту?", True, (255, 255, 255))
        question_rect = question_text.get_rect(center=(self.confirmation_dialog.centerx, self.confirmation_dialog.centery - 10))
        self.screen.blit(question_text, question_rect)
        
        warning_text = self.font_small.render("Текущая карта будет утеряна!", True, (255, 200, 200))
        warning_rect = warning_text.get_rect(center=(self.confirmation_dialog.centerx, self.confirmation_dialog.centery + 15))
        self.screen.blit(warning_text, warning_rect)
        
        # Кнопки с hover эффектом
        mouse_pos = pygame.mouse.get_pos()
        
        # Кнопка "Да"
        yes_color = (100, 180, 100) if self.yes_button.collidepoint(mouse_pos) else (70, 150, 70)
        pygame.draw.rect(self.screen, yes_color, self.yes_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.yes_button, 2)
        
        yes_text = self.font.render("Да", True, (255, 255, 255))
        yes_rect = yes_text.get_rect(center=self.yes_button.center)
        self.screen.blit(yes_text, yes_rect)
        
        # Кнопка "Нет"
        no_color = (200, 100, 100) if self.no_button.collidepoint(mouse_pos) else (170, 70, 70)
        pygame.draw.rect(self.screen, no_color, self.no_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.no_button, 2)
        
        no_text = self.font.render("Нет", True, (255, 255, 255))
        no_rect = no_text.get_rect(center=self.no_button.center)
        self.screen.blit(no_text, no_rect)
    
    def handle_event(self, event):
        """ИСПРАВЛЕННАЯ обработка событий всплывающего меню"""
        
        # Закрытие всплывающего меню по ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if getattr(self, 'show_popup_menu', False):
                self.show_popup_menu = False
                print("📋 ESC - закрываем всплывающее меню")
                return 'popup_menu_closed'
        
        # Клавиша I для показа/скрытия информации
        if event.type == pygame.KEYDOWN and not getattr(self, 'show_popup_menu', False):
            if event.key == pygame.K_i:
                self.show_info = not self.show_info
                print(f"ℹ️ Клавиша I - информация {'показана' if self.show_info else 'скрыта'}")
                return f"info_{'shown' if self.show_info else 'hidden'}"
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            print(f"🖱️ GameUI получил клик на {mouse_pos}")
            
            if getattr(self, 'show_confirmation', False):
                print("📋 Обрабатываем клик в диалоге подтверждения")
                # Обработка диалога подтверждения
                if hasattr(self, 'yes_button') and self.yes_button.collidepoint(mouse_pos):
                    self.show_confirmation = False
                    action = getattr(self, 'confirmation_action', 'regenerate_confirmed')
                    print(f"✅ Подтверждение: {action}")
                    return action
                elif hasattr(self, 'no_button') and self.no_button.collidepoint(mouse_pos):
                    self.show_confirmation = False
                    print("❌ Отмена подтверждения")
                    return 'confirmation_cancelled'
                elif hasattr(self, 'confirmation_dialog') and not self.confirmation_dialog.collidepoint(mouse_pos):
                    self.show_confirmation = False
                    print("❌ Клик вне диалога - отмена")
                    return 'confirmation_cancelled'
            
            elif getattr(self, 'show_popup_menu', False):
                print("📋 Обрабатываем клик во всплывающем меню")
                # Обработка всплывающего меню
                if hasattr(self, 'main_menu_button') and self.main_menu_button.collidepoint(mouse_pos):
                    print("🏠 Клик по кнопке 'Главное меню'")
                    self.show_confirmation = True
                    self.confirmation_action = 'main_menu_confirmed'
                    return 'main_menu_requested'
                
                elif hasattr(self, 'new_map_button') and self.new_map_button.collidepoint(mouse_pos):
                    print("🗺️ Клик по кнопке 'Новая карта'")
                    self.show_confirmation = True
                    self.confirmation_action = 'regenerate_confirmed'
                    # ИСПРАВЛЕНО: Закрываем всплывающее меню
                    self.show_popup_menu = False
                    return 'regenerate_requested'
                
                elif hasattr(self, 'return_button') and self.return_button.collidepoint(mouse_pos):
                    print("🔙 Клик по кнопке 'Вернуться'")
                    self.show_popup_menu = False
                    return 'popup_menu_closed'
                
                # Клик вне меню закрывает его
                elif hasattr(self, 'popup_menu_rect') and not self.popup_menu_rect.collidepoint(mouse_pos):
                    print("📋 Клик вне всплывающего меню - закрываем")
                    self.show_popup_menu = False
                    return 'popup_menu_closed'
        
        return None
