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

# Слои рендеринга (порядок отрисовки)
RENDER_LAYERS = {
    'background': 0,
    'terrain': 1,
    'grid': 2,
    'resources': 3,
    'buildings': 4,
    'units': 5,
    'fx': 6,
    'ui': 7
}

# Цвета
COLORS = {
    # Основные цвета
    'background': (0, 0, 0),
    'text': (255, 255, 255),
    'text_highlighted': (255, 255, 0),
    'text_disabled': (128, 128, 128),
    
    # Цвета интерфейса
    'ui_background': (40, 40, 40),
    'ui_border': (100, 100, 100),
    'ui_button': (60, 60, 60),
    'ui_button_hover': (80, 80, 80),
    'ui_button_pressed': (30, 30, 30),
    
    # Цвета игрового поля
    'grid_lines': (50, 50, 50),
    'water': (0, 0, 139),
    'land': (34, 139, 34),
    'province_neutral': (150, 150, 150),
    'player_one': (255, 0, 0),
    'player_two': (0, 0, 255),
    
    # Цвета ресурсов
    'gold': (255, 215, 0),
    'stone': (128, 128, 128),
    'wood': (139, 69, 19),
    'food': (124, 252, 0)
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