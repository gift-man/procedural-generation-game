"""Основной игровой класс с меню и выбором провинций"""
import pygame
import sys
from world.island import Island
from world.generator import ProvinceGenerator
from ui.menu import MainMenu
from ui.game_ui import GameUI
from core.player_selection import GameSelection
from core.settings import *


from world.buildings import BuildingSystem, BuildingType
from ui.building_ui import BuildingUI

class Game:
    def __init__(self):
        pygame.init()
        # self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Генератор Провинций")
        self.clock = pygame.time.Clock()
        # АДАПТИВНЫЙ экран с возможностью изменения размера
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Генератор Провинций")
        self.clock = pygame.time.Clock()
        
        # Добавляем обработку изменения размера
        self.current_screen_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        # Состояния игры
        self.state = 'menu'  # 'menu' или 'game'
        
        # UI
        self.menu = MainMenu(self.screen)
        self.game_ui = None
        # Система строительства
        self.building_system = BuildingSystem()
        self.building_ui = None

        # Система ходов
        self.current_player_index = 0
        self.town_hall_selection_player = None
        self.town_hall_province_id = None

        # UI кнопки конца хода
        self.end_turn_button_rect = None
        
        # Размер клетки для UI
        self.CELL_SIZE = CELL_SIZE
        # Игровые объекты
        self.island = None
        self.provinces = None
        self.province_map = None
        self.generator = None
        
        # Система выбора игроков
        self.player_selection = GameSelection()

    def handle_screen_resize(self, new_size):
        """ИСПРАВЛЕННАЯ обработка изменения размера экрана"""
        global SCREEN_WIDTH, SCREEN_HEIGHT, COLS, ROWS, CELL_SIZE
        
        SCREEN_WIDTH, SCREEN_HEIGHT = new_size
        
        # Адаптивный размер клетки
        if SCREEN_WIDTH >= 1600:
            CELL_SIZE = 30
        elif SCREEN_WIDTH <= 1000:
            CELL_SIZE = 20
        else:
            CELL_SIZE = 25
        
        COLS = SCREEN_WIDTH // CELL_SIZE
        ROWS = SCREEN_HEIGHT // CELL_SIZE
        
        self.current_screen_size = new_size
        
        # НОВОЕ: Пересоздаем UI элементы под новый размер
        if hasattr(self, 'game_ui') and self.game_ui:
            self.game_ui.create_ui_elements()
        
        print(f"🔄 Экран изменен: {SCREEN_WIDTH}x{SCREEN_HEIGHT}, клетка: {CELL_SIZE}px")

        
    def run(self):
        """ИСПРАВЛЕННЫЙ основной игровой цикл с блокировкой при открытом меню"""
        running = True
        
        while running:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                 # НОВОЕ: Обработка изменения размера окна
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_screen_resize(event.size)
                # Обработка событий в зависимости от состояния
                if self.state == 'menu':
                    action = self.menu.handle_event(event)
                    if action == 'generate_map':
                        self.generate_new_map()
                    elif action == 'exit':
                        running = False

                elif self.state in ['selection_province', 'selection_town_hall']:
                    print(f"🖱️ Событие в состоянии {self.state}: {event.type}")
                    
                    # ВСЕГДА сначала обрабатываем UI события
                    ui_action = None
                    if self.game_ui:
                        ui_action = self.game_ui.handle_event(event)
                        if ui_action == 'main_menu_confirmed':
                            self.state = 'menu'
                            print("🏠 Возврат в главное меню из стартовой фазы")
                            continue  # Прерываем обработку других событий
                        elif ui_action == 'regenerate_confirmed':
                            self.regenerate_provinces()
                            continue
                        elif ui_action == 'popup_menu_closed':
                            print("📋 Всплывающее меню закрыто")
                            continue
                    
                    # НОВОЕ: Проверяем блокировку меню
                    menu_is_open = (self.game_ui and 
                                getattr(self.game_ui, 'show_popup_menu', False) or
                                getattr(self.game_ui, 'show_confirmation', False))
                    
                    if menu_is_open:
                        print("🚫 Меню открыто - блокируем игровые действия")
                        continue  # Блокируем все остальные действия
                    
                    # ESC открывает меню (только если меню закрыто)
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        if self.game_ui:
                            self.game_ui.show_popup_menu = True
                            print("📋 ESC - открываем всплывающее меню")
                            continue
                    
                    # Клики по игровому полю (только если меню закрыто)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # Проверяем кнопку меню
                        if hasattr(self, 'menu_button_rect') and self.menu_button_rect.collidepoint(event.pos):
                            if self.game_ui:
                                self.game_ui.show_popup_menu = True
                                print("📋 Кнопка меню нажата - открываем всплывающее меню")
                        else:
                            # Игровые действия
                            if self.state == 'selection_province':
                                print(f"🔍 Левый клик в selection_province на {event.pos}")
                                self.handle_province_click(event.pos)
                            elif self.state == 'selection_town_hall':
                                print(f"🏛️ Левый клик в selection_town_hall на {event.pos}")
                                self.handle_town_hall_click(event.pos)

                elif self.state == 'game':
                    if self.game_ui:
                        action = self.game_ui.handle_event(event)
                        if action == 'regenerate_confirmed':
                            print("🔄 Перегенерация карты через всплывающее меню")
                            self.regenerate_provinces()
                            continue
                        elif action == 'main_menu_confirmed':
                            self.state = 'menu'
                            print("🏠 Возврат в главное меню")
                            continue
                        elif action == 'popup_menu_closed':
                            pass  # Просто закрываем меню
                        elif action == 'return_to_menu':
                            self.state = 'menu'
                            print("🏠 Возврат в главное меню")
                            continue
                    
                    # НОВОЕ: Проверяем блокировку меню
                    menu_is_open = (self.game_ui and 
                                getattr(self.game_ui, 'show_popup_menu', False) or
                                getattr(self.game_ui, 'show_confirmation', False))
                    
                    if menu_is_open:
                        print("🚫 Меню открыто - блокируем игровые действия")
                        continue  # Блокируем все остальные действия
                    
                    # Клавиши (только если меню закрыто)
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if self.game_ui:
                                self.game_ui.show_popup_menu = True
                                print("📋 ESC в игре - открываем всплывающее меню")
                        elif event.key == pygame.K_RETURN:
                            self.end_turn()
                    
                    # Клики по кнопкам (только если меню закрыто)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # Проверяем кнопку меню
                        if hasattr(self, 'menu_button_rect') and self.menu_button_rect.collidepoint(event.pos):
                            if self.game_ui:
                                self.game_ui.show_popup_menu = True
                                print("📋 Кнопка меню нажата в игре - открываем всплывающее меню")
                        
                        # Обработка кнопки конца хода
                        elif hasattr(self, 'end_turn_button_rect') and self.end_turn_button_rect.collidepoint(event.pos):
                            self.end_turn()
                    
                    # Обработка строительства (только если меню закрыто)
                    if self.building_ui:
                        building_action = self.building_ui.handle_event(event)
                        if building_action and building_action.startswith('build_attempt_'):
                            parts = building_action.split('_')
                            grid_x, grid_y = int(parts[2]), int(parts[3])
                            success, message = self.building_ui.try_build(grid_x, grid_y)
            
            # Отрисовка
            if self.state == 'menu':
                self.menu.draw()
            elif self.state in ['selection_province', 'selection_town_hall', 'game']:
                self.render_game()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

    
      
    def handle_province_click(self, mouse_pos):
        """ОТЛАДОЧНАЯ версия обработки выбора провинции"""
        print(f"🖱️ Клик на позиции {mouse_pos}")
        print(f"📊 Текущее состояние: {self.state}")
        print(f"👤 Текущий игрок: {self.current_player_index}")
        
        clicked_province = self.get_province_at_pos(mouse_pos)
        print(f"🗺️ Провинция под курсором: {clicked_province}")
        
        if clicked_province is not None:
            current_player = self.player_selection.players[self.current_player_index]
            print(f"👨‍💼 Игрок: {current_player.name} (ID: {current_player.player_id})")
            
            # Проверяем, не занята ли провинция
            if self.player_selection.is_province_selected(clicked_province):
                print("❌ Эта провинция уже выбрана!")
                return
            
            # Выбираем провинцию
            print(f"📝 Вызываем select_province_for_player({current_player.player_id}, {clicked_province})")
            success = self.player_selection.select_province_for_player(current_player.player_id, clicked_province)
            print(f"📋 Результат выбора: {success}")
            
            if success:
                # Переходим к выбору места для ратуши
                self.town_hall_selection_player = current_player
                self.town_hall_province_id = clicked_province
                self.state = 'selection_town_hall'
                
                print(f"✅ {current_player.name} выбрал провинцию {clicked_province + 1}")
                print(f"📍 Переход к состоянию: {self.state}")
            else:
                print("❌ Не удалось выбрать провинцию")
        else:
            print("❌ Клик вне провинций")
            
            # ОТЛАДКА: Показываем что есть в province_map
            if hasattr(self, 'province_map') and self.province_map:
                print(f"🔍 Размер province_map: {len(self.province_map)}")
                sample_keys = list(self.province_map.keys())[:5]
                print(f"📊 Примеры ключей: {sample_keys}")



    def get_province_at_pos(self, mouse_pos):
        """ИСПРАВЛЕННАЯ функция с учетом центрирования карты"""
        if not hasattr(self, 'map_offset_x'):
            return None
        
        mx, my = mouse_pos
        
        # Конвертируем экранные координаты в координаты сетки с учетом центрирования
        map_x = mx - self.map_offset_x
        map_y = my - self.map_offset_y
        
        # Проверяем что клик в пределах карты
        if map_x < 0 or map_y < 0:
            return None
        
        grid_x = map_x // CELL_SIZE + self.map_min_x
        grid_y = map_y // CELL_SIZE + self.map_min_y
        
        # Проверяем, есть ли клетка в этой позиции
        if (grid_x, grid_y) in self.province_map:
            return self.province_map[(grid_x, grid_y)]
        
        return None

    
    def generate_new_map(self):
        """ИСПРАВЛЕННАЯ генерация новой карты"""
        print("=== СОЗДАНИЕ НОВОЙ КАРТЫ ===")
        
        # Создаём остров с встроенной генерацией провинций
        self.island = Island()  
        print(f"Остров создан: {len(self.island.cells)} клеток")
        
        # Сбрасываем выбор игроков
        self.player_selection.reset_selection()
        
        # Создаём UI для игры
        self.game_ui = GameUI(self.screen, self)
        
        # Инициализируем системы строительства
        self.building_system = BuildingSystem()
        self.building_system.game = self
        
        # Создаём UI строительства
        self.building_ui = BuildingUI(self.screen, self)
        
        # Устанавливаем состояние
        self.current_player_index = 0
        self.state = 'selection_province'
        
        # ИСПРАВЛЕНО: Используем встроенную генерацию провинций острова
        if hasattr(self.island, 'generate_provinces_for_islands'):
            self.provinces, self.province_map = self.island.generate_provinces_for_islands()
            print(f"✅ Провинции сгенерированы через Island: {len(self.provinces)}")
        else:
            # Fallback к обычной генерации
            self.generator = ProvinceGenerator(self.island)
            self.provinces, self.province_map = self.generator.generate_provinces()
            print(f"✅ Провинции сгенерированы через Generator: {len(self.provinces)}")
        self.debug_island_positioning()
        print("=== КАРТА ГОТОВА ===")
        print(f"🔴 {self.player_selection.players[0].name} - выберите стартовую провинцию!")

    def debug_island_positioning(self):
        """Отладка позиционирования островов"""
        if not DEBUG_ISLAND_POSITIONING:
            return
        
        print(f"\n🔍 ОТЛАДКА ПОЗИЦИОНИРОВАНИЯ:")
        print(f"   Размер экрана: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        print(f"   Размер клетки: {CELL_SIZE}")
        print(f"   Видимая область: {COLS}x{ROWS} клеток")
        
        if hasattr(self, 'island') and self.island:
            for island_info in self.island.get_island_info():
                name = island_info['name']
                cells = island_info['cells']
                
                if cells:
                    min_x = min(cell[0] for cell in cells)
                    max_x = max(cell[0] for cell in cells)
                    min_y = min(cell[1] for cell in cells)
                    max_y = max(cell[1] for cell in cells)
                    
                    print(f"   {name}:")
                    print(f"     Координаты: X({min_x}-{max_x}), Y({min_y}-{max_y})")
                    print(f"     Пиксели: X({min_x*CELL_SIZE}-{max_x*CELL_SIZE}), Y({min_y*CELL_SIZE}-{max_y*CELL_SIZE})")
                    
                    if max_x * CELL_SIZE >= SCREEN_WIDTH:
                        print(f"     ❌ Выходит за правую границу!")
                    if max_y * CELL_SIZE >= SCREEN_HEIGHT:
                        print(f"     ❌ Выходит за нижнюю границу!")

    
    def regenerate_provinces(self):
        """ИСПРАВЛЕННАЯ перегенерация провинций"""
        if self.island:
            print("\n=== ПЕРЕГЕНЕРАЦИЯ КАРТЫ ===")
            
            # НОВОЕ: Полная перегенерация островов
            self.island.regenerate_islands()
            
            # Генерируем провинции заново
            if hasattr(self.island, 'generate_provinces_for_islands'):
                self.provinces, self.province_map = self.island.generate_provinces_for_islands()
            else:
                if not hasattr(self, 'generator'):
                    self.generator = ProvinceGenerator(self.island)
                self.provinces, self.province_map = self.generator.generate_provinces()
            
            # Сбрасываем игровое состояние
            self.player_selection.reset_selection()
            self.building_system = BuildingSystem()
            self.building_system.game = self
            self.current_player_index = 0
            self.state = 'selection_province'
            
            print("=== КАРТА ПЕРЕГЕНЕРИРОВАНА ===")
            print(f"🔴 {self.player_selection.players[0].name} - выберите стартовую провинцию!")


    
    def render_game(self):
        """ИСПРАВЛЕННАЯ отрисовка игры"""
        # Фон
        self.screen.fill((200, 230, 255))
        
        if self.island and self.provinces:
            # Отрисовка карты с выделением игроков
            self.render_map_with_players()
        
        # Отрисовка информации о состоянии игры
        self.render_game_state_info()
        
        # ИСПРАВЛЕНО: Кнопка меню во ВСЕХ состояниях кроме начального экрана
        if self.state in ['selection_province', 'selection_town_hall', 'game']:
            self.render_menu_button()
        
        # UI строительства (только в игровом режиме)
        if self.state == 'game' and self.building_ui:
            self.building_ui.draw()
        
        # Кнопка конца хода (только в игровом режиме)
        if self.state == 'game':
            self.render_end_turn_button()
        
        # UI игры (информация об острове и всплывающее меню)
        if self.game_ui:
            self.game_ui.draw()


     
    
    def render_player_info(self):
        """Отрисовывает информацию о текущем игроке"""
        if self.player_selection.selection_phase:
            current_player = self.player_selection.get_current_player()
            if current_player:
                font = pygame.font.Font(None, 48)
                text = font.render(f"{current_player.name} - выберите провинцию", True, current_player.color)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 50))
                
                # Фон для текста
                bg_rect = text_rect.inflate(20, 10)
                pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)
                pygame.draw.rect(self.screen, current_player.color, bg_rect, 3)
                
                self.screen.blit(text, text_rect)
        elif self.player_selection.selections_complete:
            font = pygame.font.Font(None, 36)
            text = font.render("Выбор завершен! Игра может начаться.", True, (0, 0, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (200, 255, 200), bg_rect)
            pygame.draw.rect(self.screen, (0, 150, 0), bg_rect, 3)
            
            self.screen.blit(text, text_rect)
    
    def render_map_with_players(self):
        """ИСПРАВЛЕННАЯ отрисовка карты с правильным порядком"""
        
        # 1. Рисуем базовую карту (сохраняет координаты центрирования)
        self.render_base_terrain()
        
        # 2. Рисуем сетку (использует координаты центрирования)
        self.render_grid()
        
        # 3. Сплошные границы острова (теперь с центрированием)
        self.render_island_outline_solid()
        
        # 4. Пунктирные границы между провинциями (теперь с центрированием)
        self.render_province_borders_dashed()
        
        # 5. Контуры выбранных провинций (теперь с центрированием)
        self.render_selected_provinces()
        
        # 6. Здания на карте
        if self.building_ui:
            self.building_ui.draw_buildings_on_map()



    def draw_solid_border_centered(self, x, y, side, color):
        """НОВАЯ функция: Рисует сплошную границу для одной стороны клетки С ЦЕНТРИРОВАНИЕМ"""
        if not hasattr(self, 'map_offset_x'):
            return
        
        # Преобразуем координаты в экранные с учетом центрирования
        screen_x = self.map_offset_x + (x - self.map_min_x) * CELL_SIZE
        screen_y = self.map_offset_y + (y - self.map_min_y) * CELL_SIZE
        
        if side == 'top':
            pygame.draw.line(self.screen, color, 
                        (screen_x, screen_y), 
                        (screen_x + CELL_SIZE, screen_y), 4)
        elif side == 'bottom':
            pygame.draw.line(self.screen, color, 
                        (screen_x, screen_y + CELL_SIZE), 
                        (screen_x + CELL_SIZE, screen_y + CELL_SIZE), 4)
        elif side == 'left':
            pygame.draw.line(self.screen, color, 
                        (screen_x, screen_y), 
                        (screen_x, screen_y + CELL_SIZE), 4)
        elif side == 'right':
            pygame.draw.line(self.screen, color, 
                        (screen_x + CELL_SIZE, screen_y), 
                        (screen_x + CELL_SIZE, screen_y + CELL_SIZE), 4)




                            
    def draw_province_outline(self, cells, color):
        """ИСПРАВЛЕННАЯ функция: Рисует внешний контур провинции С ЦЕНТРИРОВАНИЕМ"""
        if not hasattr(self, 'map_offset_x'):
            return
        
        cells_set = set(cells)
        
        for cell in cells:
            x, y = cell
            
            # Преобразуем координаты в экранные с учетом центрирования
            screen_x = self.map_offset_x + (x - self.map_min_x) * CELL_SIZE
            screen_y = self.map_offset_y + (y - self.map_min_y) * CELL_SIZE
            
            # Проверяем каждую сторону клетки
            sides = [
                ('top', (x, y-1), (screen_x, screen_y), (screen_x + CELL_SIZE, screen_y)),
                ('bottom', (x, y+1), (screen_x, screen_y + CELL_SIZE), (screen_x + CELL_SIZE, screen_y + CELL_SIZE)),
                ('left', (x-1, y), (screen_x, screen_y), (screen_x, screen_y + CELL_SIZE)),
                ('right', (x+1, y), (screen_x + CELL_SIZE, screen_y), (screen_x + CELL_SIZE, screen_y + CELL_SIZE))
            ]
            
            for side_name, neighbor_pos, line_start, line_end in sides:
                # Если соседняя клетка НЕ принадлежит этой провинции - рисуем границу
                if neighbor_pos not in cells_set:
                    pygame.draw.line(self.screen, color, line_start, line_end, 4)


    def render_selected_provinces(self):
        """Рисует ТОЛЬКО КОНТУР выбранных провинций"""
        for province_id, province in enumerate(self.provinces):
            owner = self.player_selection.get_province_owner(province_id)
            if owner:
                # Рисуем только внешний контур провинции
                self.draw_province_outline(province['cells'], owner.color)

    
    def render_province_borders_with_players(self):
        """Рисует границы провинций с учетом выбора игроков"""
        for province_id, province in enumerate(self.provinces):
            for cell in province['cells']:
                x, y = cell
                neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
                
                for nx, ny in neighbors:
                    if (nx, ny) in self.province_map:
                        neighbor_province = self.province_map[(nx, ny)]
                        if neighbor_province != province_id:
                            # Определяем цвет границы
                            border_color = (0, 0, 0)  # По умолчанию черный
                            
                            # Проверяем, принадлежат ли провинции игрокам
                            owner1 = self.player_selection.get_province_owner(province_id)
                            owner2 = self.player_selection.get_province_owner(neighbor_province)
                            
                            if owner1 or owner2:
                                # Если хотя бы одна провинция принадлежит игроку
                                if owner1:
                                    border_color = owner1.color
                                elif owner2:
                                    border_color = owner2.color
                            
                            # Рисуем пунктирную границу
                            self.draw_dashed_border_colored(x, y, nx, ny, border_color)
    

    
    def render_island_outline_with_players(self):
        """Рисует контур острова с учетом выбора игроков"""
        for row_idx, row in enumerate(ISLAND_MATRIX):
            for col_idx, cell in enumerate(row):
                if cell == 1:  # Суша
                    x = col_idx + ISLAND_OFFSET_X
                    y = row_idx + ISLAND_OFFSET_Y
                    
                    # Проверяем, принадлежит ли эта клетка игроку
                    province_id = self.province_map.get((x, y))
                    owner = None
                    if province_id is not None:
                        owner = self.player_selection.get_province_owner(province_id)
                    
                    # Определяем цвет границы
                    border_color = (0, 0, 0)  # По умолчанию черный
                    if owner:
                        border_color = owner.color
                    
                    # Проверяем соседей - если рядом море, рисуем границу
                    neighbors = [
                        (row_idx - 1, col_idx),     # Верх
                        (row_idx + 1, col_idx),     # Низ
                        (row_idx, col_idx - 1),     # Лево
                        (row_idx, col_idx + 1)      # Право
                    ]
                    
                    for nr, nc in neighbors:
                        # Если сосед за границами матрицы или это море
                        if (nr < 0 or nr >= len(ISLAND_MATRIX) or 
                            nc < 0 or nc >= len(ISLAND_MATRIX[0]) or 
                            ISLAND_MATRIX[nr][nc] == 0):
                            
                            # Рисуем границу острова в цвете игрока
                            self.draw_island_border_colored(x, y, nr - row_idx, nc - col_idx, border_color)
    
    def draw_island_border_colored(self, x, y, dr, dc, color):
        """Рисует цветную границу острова"""
        start_x = x * CELL_SIZE
        start_y = y * CELL_SIZE
        
        if dr == -1:  # Верхняя граница
            pygame.draw.line(self.screen, color, 
                           (start_x, start_y), 
                           (start_x + CELL_SIZE, start_y), 4)
        elif dr == 1:  # Нижняя граница
            pygame.draw.line(self.screen, color, 
                           (start_x, start_y + CELL_SIZE), 
                           (start_x + CELL_SIZE, start_y + CELL_SIZE), 4)
        elif dc == -1:  # Левая граница
            pygame.draw.line(self.screen, color, 
                           (start_x, start_y), 
                           (start_x, start_y + CELL_SIZE), 4)
        elif dc == 1:  # Правая граница
            pygame.draw.line(self.screen, color, 
                           (start_x + CELL_SIZE, start_y), 
                           (start_x + CELL_SIZE, start_y + CELL_SIZE), 4)
    
    
    



    
    def is_position_on_land(self, x, y):
        """ИСПРАВЛЕННАЯ проверка для двух островов"""
        if hasattr(self, 'island') and self.island:
            return self.island.is_land(x, y)
        
        # Fallback к старой логике
        matrix_x = x - ISLAND_OFFSET_X
        matrix_y = y - ISLAND_OFFSET_Y
        
        if (0 <= matrix_y < len(ISLAND_MATRIX) and 
            0 <= matrix_x < len(ISLAND_MATRIX[0])):
            return ISLAND_MATRIX[matrix_y][matrix_x] == 1
        
        return False
    def draw_dashed_border_colored_centered(self, x1, y1, x2, y2, color):
        """НОВАЯ функция: Рисует пунктирную границу С ЦЕНТРИРОВАНИЕМ"""
        if not hasattr(self, 'map_offset_x'):
            return
        
        # Преобразуем координаты в экранные с учетом центрирования
        screen_x1 = self.map_offset_x + (x1 - self.map_min_x) * CELL_SIZE
        screen_y1 = self.map_offset_y + (y1 - self.map_min_y) * CELL_SIZE
        
        if x2 > x1:  # Правая граница
            line_start = (screen_x1 + CELL_SIZE, screen_y1)
            line_end = (screen_x1 + CELL_SIZE, screen_y1 + CELL_SIZE)
        elif x2 < x1:  # Левая граница
            line_start = (screen_x1, screen_y1)
            line_end = (screen_x1, screen_y1 + CELL_SIZE)
        elif y2 > y1:  # Нижняя граница
            line_start = (screen_x1, screen_y1 + CELL_SIZE)
            line_end = (screen_x1 + CELL_SIZE, screen_y1 + CELL_SIZE)
        elif y2 < y1:  # Верхняя граница
            line_start = (screen_x1, screen_y1)
            line_end = (screen_x1 + CELL_SIZE, screen_y1)
        else:
            return
        
        self.draw_dashed_line(line_start, line_end, color, 3, 6)
    
    def draw_dashed_line(self, start, end, color, thickness, dash_length):
        """Рисует пунктирную линию"""
        x1, y1 = start
        x2, y2 = end
        
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        
        if length == 0:
            return
        
        dx = (x2 - x1) / length
        dy = (y2 - y1) / length
        
        current_pos = 0
        while current_pos < length:
            dash_start_x = x1 + dx * current_pos
            dash_start_y = y1 + dy * current_pos
            
            dash_end_pos = min(current_pos + dash_length, length)
            dash_end_x = x1 + dx * dash_end_pos
            dash_end_y = y1 + dy * dash_end_pos
            
            pygame.draw.line(self.screen, color, 
                        (dash_start_x, dash_start_y), 
                        (dash_end_x, dash_end_y), thickness)
            
            current_pos += dash_length * 2






    
    def handle_town_hall_click(self, mouse_pos):
        """ИСПРАВЛЕННАЯ обработка с центрированием"""
        if not hasattr(self, 'map_offset_x'):
            return
        
        mx, my = mouse_pos
        
        # Конвертируем с учетом центрирования
        map_x = mx - self.map_offset_x
        map_y = my - self.map_offset_y
        
        if map_x < 0 or map_y < 0:
            return
        
        grid_x = map_x // self.CELL_SIZE + self.map_min_x
        grid_y = map_y // self.CELL_SIZE + self.map_min_y
        
        # Проверяем, что клетка внутри выбранной провинции
        province_cells = self.provinces[self.town_hall_province_id]['cells']
        if (grid_x, grid_y) not in province_cells:
            print("❌ Выберите клетку внутри выбранной провинции")
            return
        
        # Остальная логика остается прежней...
        success, message = self.building_system.build(
            grid_x, grid_y, BuildingType.TOWN_HALL, self.town_hall_selection_player.player_id,
            self.island, self.province_map
        )
        
        if success:
            print(f"🏛️ Ратуша построена на клетке ({grid_x}, {grid_y})")
            
            self.current_player_index += 1
            
            if self.current_player_index >= len(self.player_selection.players):
                self.current_player_index = 0
                self.state = 'game'
                self.player_selection.selection_phase = False
                print("🎮 Начинается игровой процесс!")
            else:
                self.state = 'selection_province'
                next_player = self.player_selection.players[self.current_player_index]
                print(f"🔄 Ход игрока {next_player.name} - выберите территорию!")
        else:
            print(f"❌ Ошибка при строительстве ратуши: {message}")


    def end_turn(self):
        """Заканчивает ход текущего игрока"""
        if self.state != 'game':
            return
        
        current_player = self.get_current_player()
        print(f"⏭️ {current_player.name} закончил ход")
        
        # Переходим к следующему игроку
        self.current_player_index = (self.current_player_index + 1) % len(self.player_selection.players)
        next_player = self.get_current_player()
        
        print(f"🔄 Ход игрока {next_player.name}")
        
        # Сбрасываем выбор здания
        if self.building_ui:
            self.building_ui.selected_building_type = None

    def get_current_player(self):
        """Возвращает текущего игрока"""
        return self.player_selection.players[self.current_player_index]

    def render_game_state_info(self):
        """НОВОЕ расположение: Информация о игроке справа сверху"""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        if self.state == 'selection_province':
            current_player = self.player_selection.players[self.current_player_index]
            main_text = f"СТАРТОВЫЙ ВЫБОР: {current_player.name}"
            sub_text = "Выберите стартовую провинцию"
            
            # Центрируем для стартового выбора
            text = font.render(main_text, True, current_player.color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 30))
            
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)
            pygame.draw.rect(self.screen, current_player.color, bg_rect, 3)
            self.screen.blit(text, text_rect)
            
            sub_surface = small_font.render(sub_text, True, (100, 100, 100))
            sub_rect = sub_surface.get_rect(center=(SCREEN_WIDTH // 2, 65))
            self.screen.blit(sub_surface, sub_rect)
        
        elif self.state == 'selection_town_hall':
            current_player = self.town_hall_selection_player
            main_text = f"СТАРТОВЫЙ ВЫБОР: {current_player.name}"
            sub_text = "Выберите место для ратуши"
            
            text = font.render(main_text, True, current_player.color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 30))
            
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)
            pygame.draw.rect(self.screen, current_player.color, bg_rect, 3)
            self.screen.blit(text, text_rect)
            
            sub_surface = small_font.render(sub_text, True, (100, 100, 100))
            sub_rect = sub_surface.get_rect(center=(SCREEN_WIDTH // 2, 65))
            self.screen.blit(sub_surface, sub_rect)
        
        elif self.state == 'game':
            # НОВОЕ: Информация о игроке СПРАВА СВЕРХУ
            current_player = self.get_current_player()
            text = font.render(f"ХОД {current_player.name}", True, current_player.color)
            
            # Позиционируем справа сверху
            text_rect = text.get_rect()
            text_rect.topright = (SCREEN_WIDTH - 20, 20)
            
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)
            pygame.draw.rect(self.screen, current_player.color, bg_rect, 3)
            self.screen.blit(text, text_rect)


    def render_end_turn_button(self):
        """НОВОЕ расположение: Кнопка конца хода снизу справа БЕЗ текста Enter"""
        font = pygame.font.Font(None, 32)
        button_text = font.render('Конец хода', True, (255, 255, 255))  # Убран текст (Enter)
        
        # НОВОЕ: Позиционируем снизу справа
        button_width = button_text.get_width() + 40
        button_height = button_text.get_height() + 20
        button_x = SCREEN_WIDTH - button_width - 20
        button_y = SCREEN_HEIGHT - button_height - 20  # Снизу справа
        
        self.end_turn_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Фон кнопки
        pygame.draw.rect(self.screen, (70, 70, 70), self.end_turn_button_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.end_turn_button_rect, 2)
        
        # Текст кнопки
        text_rect = button_text.get_rect(center=self.end_turn_button_rect.center)
        self.screen.blit(button_text, text_rect)

    def render_menu_button(self):
        """ИСПРАВЛЕННАЯ функция: Кнопка меню слева сверху"""
        font = pygame.font.Font(None, 24)
        button_text = font.render('Меню', True, (255, 255, 255))
        
        # Позиционируем слева сверху
        button_width = button_text.get_width() + 30
        button_height = button_text.get_height() + 15
        button_x = 20
        button_y = 20
        
        self.menu_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Hover эффект
        mouse_pos = pygame.mouse.get_pos()
        if self.menu_button_rect.collidepoint(mouse_pos):
            color = (100, 100, 180)
        else:
            color = (70, 70, 150)
        
        # Фон кнопки
        pygame.draw.rect(self.screen, color, self.menu_button_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.menu_button_rect, 2)
        
        # Текст кнопки
        text_rect = button_text.get_rect(center=self.menu_button_rect.center)
        self.screen.blit(button_text, text_rect)




if __name__ == "__main__":
    game = Game()
    game.run()
