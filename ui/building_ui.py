"""UI для строительства зданий"""
import pygame
from world.buildings import BuildingType
from ui.building_icons import BuildingIcons

class BuildingUI:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Состояние UI
        self.selected_building_type = None
        self.show_building_menu = False
        
        # Доступные здания для строительства
        self.buildable_types = [
            BuildingType.FARM,
            BuildingType.SAWMILL,
            BuildingType.QUARRY,
            BuildingType.GOLD_MINE
        ]

    def handle_event(self, event):
        """Обрабатывает события UI строительства"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:  # Клавиша B - открыть меню строительства
                self.show_building_menu = not self.show_building_menu
                return f"building_menu_{'opened' if self.show_building_menu else 'closed'}"
            
            # Горячие клавиши для зданий
            if event.key == pygame.K_1:
                self.selected_building_type = BuildingType.FARM
                return "building_selected"
            elif event.key == pygame.K_2:
                self.selected_building_type = BuildingType.SAWMILL
                return "building_selected"
            elif event.key == pygame.K_3:
                self.selected_building_type = BuildingType.QUARRY
                return "building_selected"
            elif event.key == pygame.K_4:
                self.selected_building_type = BuildingType.GOLD_MINE
                return "building_selected"
            elif event.key == pygame.K_ESCAPE:
                self.selected_building_type = None
                self.show_building_menu = False
                return "building_cancelled"
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левый клик
                if self.selected_building_type:
                    # Попытка строительства
                    mouse_x, mouse_y = event.pos
                    grid_x = mouse_x // self.game.CELL_SIZE if hasattr(self.game, 'CELL_SIZE') else mouse_x // 20
                    grid_y = mouse_y // self.game.CELL_SIZE if hasattr(self.game, 'CELL_SIZE') else mouse_y // 20
                    
                    return f"build_attempt_{grid_x}_{grid_y}"
            
            elif event.button == 3:  # Правый клик - отмена
                self.selected_building_type = None
                return "building_cancelled"
        
        return None

    def draw(self):
        """Отрисовывает UI строительства"""
        if self.show_building_menu:
            self.draw_building_menu()
        
        if self.selected_building_type:
            self.draw_selected_building_indicator()
        
        # Отрисовка зданий на карте
        self.draw_buildings_on_map()

    def draw_building_menu(self):
        """Отрисовывает меню выбора зданий"""
        menu_width = 300
        menu_height = 200
        menu_x = 20
        menu_y = 100
        
        # Фон меню
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        overlay = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (menu_x, menu_y))
        pygame.draw.rect(self.screen, (255, 255, 255), menu_rect, 2)
        
        # Заголовок
        title_text = self.font.render("Строительство (B)", True, (255, 255, 255))
        self.screen.blit(title_text, (menu_x + 10, menu_y + 10))
        
        # Список зданий
        y_offset = menu_y + 40
        building_names = {
            BuildingType.FARM: "1. Ферма (любая суша)",
            BuildingType.SAWMILL: "2. Лесопилка (лес)",
            BuildingType.QUARRY: "3. Каменоломня (камень)", 
            BuildingType.GOLD_MINE: "4. Шахта (золото)"
        }
        
        for building_type in self.buildable_types:
            name = building_names[building_type]
            color = (255, 255, 100) if building_type == self.selected_building_type else (255, 255, 255)
            
            text = self.small_font.render(name, True, color)
            self.screen.blit(text, (menu_x + 10, y_offset))
            
            # Рисуем иконку здания
            icon_rect = pygame.Rect(menu_x + 250, y_offset, 20, 15)
            BuildingIcons.draw_building_icon(self.screen, icon_rect, building_type, color)
            
            y_offset += 25
        
        # Инструкции
        instructions = [
            "ESC - отмена",
            "ПКМ - отмена", 
            "ЛКМ - построить"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, (200, 200, 200))
            self.screen.blit(text, (menu_x + 10, y_offset + 10 + i * 15))

    def draw_selected_building_indicator(self):
        """Показывает индикатор выбранного здания"""
        if not self.selected_building_type:
            return
        
        # Получаем позицию мыши
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Рисуем превью здания под курсором
        preview_rect = pygame.Rect(mouse_x - 10, mouse_y - 10, 20, 20)
        
        # Полупрозрачный фон
        preview_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        preview_surface.fill((255, 255, 255, 100))
        self.screen.blit(preview_surface, (mouse_x - 10, mouse_y - 10))
        
        # Иконка здания
        BuildingIcons.draw_building_icon(self.screen, preview_rect, self.selected_building_type, (255, 255, 255))
        
        # Информация о выбранном здании
        building_names = {
            BuildingType.FARM: "Ферма",
            BuildingType.SAWMILL: "Лесопилка",
            BuildingType.QUARRY: "Каменоломня",
            BuildingType.GOLD_MINE: "Шахта золота"
        }
        
        name = building_names.get(self.selected_building_type, "Неизвестно")
        text = self.small_font.render(f"Строим: {name}", True, (255, 255, 255))
        text_rect = text.get_rect()
        
        # Фон для текста
        bg_rect = pygame.Rect(10, 10, text_rect.width + 10, text_rect.height + 5)
        pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 1)
        
        self.screen.blit(text, (15, 12))

    def draw_buildings_on_map(self):
        """ИСПРАВЛЕННАЯ отрисовка зданий с учетом центрирования"""
        if not hasattr(self.game, 'building_system') or not hasattr(self.game, 'map_offset_x'):
            return
        
        cell_size = getattr(self.game, 'CELL_SIZE', 20)
        
        for (x, y), building in self.game.building_system.buildings.items():
            # ИСПРАВЛЕНО: Преобразуем координаты сетки в экранные с учетом центрирования
            screen_x = self.game.map_offset_x + (x - self.game.map_min_x) * cell_size
            screen_y = self.game.map_offset_y + (y - self.game.map_min_y) * cell_size
            
            # Прямоугольник для иконки
            margin = cell_size * 0.15
            icon_rect = pygame.Rect(
                screen_x + margin,
                screen_y + margin, 
                cell_size - 2 * margin,
                cell_size - 2 * margin
            )
            
            if icon_rect.width <= 0 or icon_rect.height <= 0:
                continue
            
            player_color = self.get_correct_player_color(building.owner_id)
            
            # Рисуем иконку здания
            BuildingIcons.draw_building_icon(self.screen, icon_rect, building.type, player_color)



    def get_correct_player_color(self, player_id):
        """ИСПРАВЛЕННАЯ функция получения цвета БЕЗ спама"""
        # Ищем игрока по ID в системе выбора
        if hasattr(self.game, 'player_selection') and self.game.player_selection:
            for player in self.game.player_selection.players:
                if player.player_id == player_id:
                    # УБИРАЕМ print - он вызывается 60 раз в секунду!
                    # print(f"🎨 Цвет для игрока {player_id} ({player.name}): {player.color}")
                    return player.color
        
        # Цвета по умолчанию если не найден игрок
        default_colors = {1: (255, 50, 50), 2: (50, 50, 255)}
        color = default_colors.get(player_id, (255, 255, 255))
        
        # УБИРАЕМ и этот print тоже
        # print(f"⚠️ Использован цвет по умолчанию для игрока {player_id}: {color}")
        return color



    def get_player_color(self, player_id):
        """Возвращает цвет игрока"""
        if hasattr(self.game, 'player_selection'):
            for player in self.game.player_selection.players:
                if player.player_id == player_id:
                    return player.color
        
        # Цвета по умолчанию
        colors = {1: (255, 50, 50), 2: (50, 50, 255)}
        return colors.get(player_id, (255, 255, 255))

    def try_build(self, grid_x, grid_y):
        """ИСПРАВЛЕННАЯ попытка строительства с правильным игроком"""
        if not self.selected_building_type:
            return False, "Не выбран тип здания"
        
        if not hasattr(self.game, 'building_system'):
            return False, "Система строительства не инициализирована"
        
        # ИСПРАВЛЕНО: Получаем ТЕКУЩЕГО игрока (чей сейчас ход)
        if hasattr(self.game, 'get_current_player'):
            current_player = self.game.get_current_player()
            current_player_id = current_player.player_id
            print(f"🔨 Строит игрок: {current_player.name} (ID: {current_player_id})")
        else:
            current_player_id = 1  # По умолчанию первый игрок
            print(f"⚠️ Используется игрок по умолчанию: {current_player_id}")
        
        # Пытаемся построить
        success, message = self.game.building_system.build(
            grid_x, grid_y, self.selected_building_type, current_player_id,
            self.game.island, self.game.province_map
        )
        
        if success:
            print(f"✅ {message}")
            self.selected_building_type = None  # Сбрасываем выбор после успешного строительства
        else:
            print(f"❌ {message}")
        
        return success, message

