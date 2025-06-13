"""Конфигурация игры."""

# Настройки окна
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
WINDOW_TITLE = "Procedural Generation Game"
FPS = 60

# Размеры тайлов и сетки
TILE_SIZE = 32
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# Настройки границ
BORDER_THICKNESS = 4  # Толстая граница острова
PROVINCE_BORDER_THICKNESS = 2  # Тонкая граница провинций
PROVINCE_BORDER_DASH_LENGTH = 5  # Длина штриха
PROVINCE_BORDER_GAP_LENGTH = 5  # Длина промежутка
# Слои рендеринга (порядок отрисовки)
# Слои рендеринга (порядок отрисовки)
RENDER_LAYERS = {
    'background': 0,    # Фон
    'terrain': 1,       # Местность (вода и суша)
    'grid': 2,         # Сетка
    'provinces': 3,    # Провинции
    'resources': 4,    # Ресурсы
    'buildings': 5,    # Здания
    'units': 6,        # Юниты
    'fx': 7,          # Эффекты
    'ui': 8           # Интерфейс
}

COLORS = {
    # Основные цвета
    'background': (0, 0, 0),          # Черный фон
    'text': (255, 255, 255),          # Белый текст
    'text_highlighted': (255, 255, 0), # Желтый текст для выделения
    'text_disabled': (128, 128, 128),  # Серый текст для неактивных элементов
    'highlight': (255, 255, 0),        # Желтый для выделения
    'highlight_hover': (255, 255, 128), # Светло-желтый для выделения при наведении
    
    # Цвета интерфейса
    'ui_background': (40, 40, 40),     # Темно-серый фон UI
    'ui_border': (100, 100, 100),      # Серая граница UI
    'ui_button': (60, 60, 60),         # Кнопка
    'ui_button_hover': (80, 80, 80),   # Кнопка при наведении
    'ui_button_pressed': (30, 30, 30), # Кнопка при нажатии
    
     # Обновить цвета для воды
    'water': (65, 105, 225),           # Синий для воды
    'water_grid': (45, 85, 205),       # Темно-синий для сетки воды
    
    # Обновить цвета для ресурсов и их сеток
    'food': (124, 252, 0),             # Светло-зеленый для лугов
    'food_grid': (94, 192, 0),         # Темнее на 30%
    'wood': (34, 139, 34),             # Зеленый для леса
    'wood_grid': (24, 99, 24),         # Темнее на 30%
    'gold': (218, 165, 32),            # Золотой
    'gold_grid': (158, 125, 22),       # Темнее на 30%
    'stone': (128, 128, 128),          # Серый
    'stone_grid': (98, 98, 98),        # Темнее на 30%
    
    # Обновить цвета границ
    'border_thick': (60, 60, 60),      # Почти черный для границы острова
    'province_border': (60, 60, 60),    # Темно-серый для границ провинций
    
    # Цвета игроков
    'player_one': (255, 0, 0),         # Красный для первого игрока
    'player_two': (0, 0, 255),         # Синий для второго игрока
    'province_neutral': (150, 150, 150),# Серый для нейтральных провинций

    # Цвета сетки и границ
    
    'grid_lines': (50, 50, 50),             # Общий цвет сетки
    'grid_lines_land': (85, 170, 0),
    'province_border_internal': (150, 150, 150),  # Светло-серый для границ между провинциями  
    'grid_lines_water': (45, 85, 205),      # Цвет сетки для воды
    
}
# Настройки игры
GAME_CONFIG = {
    'starting_gold': 100,
    'province_income': 10,
    'max_players': 2,
    'turn_timeout': 60,  # секунды
    'building_costs': {
        'farm': 50,
        'mine': 100,
        'barracks': 150,
        'town_hall': 200
    },
    'resource_generation': {
        'farm': {'food': 5},
        'mine': {'gold': 3},
        'quarry': {'stone': 2},
        'lumber_mill': {'wood': 4}
    }
}

# Настройки UI
UI_CONFIG = {
    'button_width': 200,
    'button_height': 50,
    'button_spacing': 20,
    'panel_padding': 10,
    'tooltip_delay': 0.5,
    'message_duration': 3.0
}

# Настройки производительности
PERFORMANCE_CONFIG = {
    'max_fps': FPS,
    'vsync': True,
    'particle_limit': 1000,
    'max_messages': 5
}

# Пути к ресурсам
RESOURCE_PATHS = {
    'fonts': 'assets/fonts',
    'images': 'assets/images',
    'sounds': 'assets/sounds',
    'music': 'assets/music'
}

# Отладочные настройки
DEBUG = {
    'show_fps': True,
    'show_grid': True,
    'show_collisions': False,
    'log_level': 'INFO'
}
# Параметры генерации провинций
PROVINCE_GENERATION = {
    'MIN_PROVINCE_SIZE': 100,        # Минимальный размер провинции в пикселях
    'MIN_DISTANCE': 30,              # Минимальное расстояние между центрами провинций
    'BORDER_SMOOTHING': 2,           # Уровень сглаживания границ
    'MAX_GENERATION_ATTEMPTS': 5     # Максимальное количество попыток генерации
}