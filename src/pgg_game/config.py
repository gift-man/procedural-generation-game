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
    'background': (30, 40, 50),      # Темно-синий фон
    'water': (65, 105, 225),         # Более светлый синий для воды
    'water_grid': (45, 85, 205),     # Чуть темнее воды для сетки на воде
    # Базовые цвета
    'water': (65, 105, 225),         # Более светлый синий для воды
    'water_grid': (45, 85, 205),     # Чуть темнее воды для сетки на воде
    
    # Цвета ресурсов и их сетки
    'food': (124, 252, 0),           # Светло-зеленый для лугов
    'food_grid': (85, 170, 0),       # Более темный зеленый для сетки лугов
    
    'wood': (34, 139, 34),          # Темно-зеленый для леса
    'wood_grid': (25, 100, 25),     # Еще более темный зеленый для сетки леса
    
    'gold': (218, 165, 32),         # Золотой
    'gold_grid': (184, 134, 11),    # Темно-золотой для сетки
    
    'stone': (128, 128, 128),       # Серый
    'stone_grid': (105, 105, 105),  # Темно-серый для сетки
    
    'text_highlighted': (255, 255, 0),# Желтый текст для выделения
    'ui_button': (70, 130, 180),     # Синяя кнопка
    'ui_button_hover': (100, 160, 210),# Светло-синяя кнопка при наведении
    'ui_border': (255, 255, 255),    # Белая граница
    'ui_background': (0, 0, 0, 180), # Полупрозрачный черный фон UI
    'province_neutral': (150, 150, 150),# Серый для нейтральных провинций
    'grid_lines': (50, 50, 50),      # Темно-серый для сетки

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