"""Настройки и константы игры с адаптивным разрешением"""
import pygame

# АДАПТИВНЫЕ настройки экрана
# УВЕЛИЧИВАЕМ размер для 3 островов
DEFAULT_WIDTH = 1600  # Было 1200
DEFAULT_HEIGHT = 900  # Было 800
CELL_SIZE = 22        # Немного меньше для большего количества клеток


# Определяем реальное разрешение монитора
pygame.init()
desktop_sizes = pygame.display.get_desktop_sizes()
if desktop_sizes:
    DESKTOP_WIDTH, DESKTOP_HEIGHT = desktop_sizes[0]
    print(f"🖥️ Разрешение монитора: {DESKTOP_WIDTH}x{DESKTOP_HEIGHT}")
    
    # Адаптируем размер окна к монитору (80% от размера экрана)
    SCREEN_WIDTH = min(DEFAULT_WIDTH, int(DESKTOP_WIDTH * 0.8))
    SCREEN_HEIGHT = min(DEFAULT_HEIGHT, int(DESKTOP_HEIGHT * 0.8))
    
    # Для больших мониторов увеличиваем окно
    if DESKTOP_WIDTH >= 1920:
        SCREEN_WIDTH = min(1600, int(DESKTOP_WIDTH * 0.75))
    if DESKTOP_HEIGHT >= 1080:
        SCREEN_HEIGHT = min(1000, int(DESKTOP_HEIGHT * 0.75))
else:
    SCREEN_WIDTH = DEFAULT_WIDTH
    SCREEN_HEIGHT = DEFAULT_HEIGHT

# Вычисляем количество клеток
COLS = SCREEN_WIDTH // CELL_SIZE
ROWS = SCREEN_HEIGHT // CELL_SIZE

print(f"📊 Адаптивное окно: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
print(f"📏 Клеток: {COLS}x{ROWS}")

# Для совместимости с существующим кодом
WIDTH = SCREEN_WIDTH
HEIGHT = SCREEN_HEIGHT

# Настройки провинций
MIN_PROVINCE_SIZE = 4
MAX_PROVINCE_SIZE = 8

# Смещение острова
ISLAND_OFFSET_X = 4
ISLAND_OFFSET_Y = 2

# Матрица основного острова (статическая)
ISLAND_MATRIX = [
    [0,1,0,0,0,0,0,0,0],
    [0,1,1,1,0,1,1,0,0],
    [1,1,1,1,1,1,1,0,0],
    [0,1,1,1,1,1,1,0,0],
    [0,1,1,1,1,1,1,1,0],
    [0,0,1,1,1,1,1,1,0],
    [0,0,1,1,1,1,1,1,0],
    [0,0,1,1,1,1,1,1,1],
    [0,1,1,1,1,1,1,1,1],
    [0,1,1,1,1,1,1,0,0],
    [0,1,1,1,1,1,1,0,0],
    [1,1,1,1,1,1,1,0,0],
    [1,1,1,1,1,1,1,1,0],
    [0,1,1,1,1,1,1,1,0],
    [0,0,0,0,1,1,1,0,0]
]

# FPS
FPS = 60

# === НАСТРОЙКИ UI ===

# Настройки отрисовки карты
MAP_OFFSET_X = 100
MAP_OFFSET_Y = 100

# Цвета базовой карты
BACKGROUND_COLOR = (200, 230, 255)   # Светло-голубой фон
WATER_COLOR = (173, 216, 230)        # Светло-голубое море  
LAND_COLOR = (144, 238, 144)         # Светло-зеленая суша

# Цвета провинций для игроков
PROVINCE_COLORS = [
    (255, 100, 100), (100, 255, 100), (100, 100, 255),
    (255, 255, 100), (255, 100, 255), (100, 255, 255),
    (255, 200, 100), (200, 255, 100), (200, 100, 255),
    (255, 150, 150), (150, 255, 150), (150, 150, 255),
    (200, 200, 100), (200, 100, 200), (100, 200, 200),
    (180, 180, 180), (120, 120, 120), (80, 80, 80),
    (160, 100, 200), (100, 200, 160), (200, 160, 100)
]

# UI цвета кнопок
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 160, 210)
BUTTON_DANGER_COLOR = (180, 70, 70)
BUTTON_DANGER_HOVER_COLOR = (210, 100, 100)

# Размеры шрифтов
FONT_SIZE_TITLE = 72
FONT_SIZE_BUTTON = 48
FONT_SIZE_TEXT = 32
FONT_SIZE_SMALL = 24

# === НАСТРОЙКИ ПРОЦЕДУРНОЙ ГЕНЕРАЦИИ ===
ENABLE_PROCEDURAL_ISLANDS = True
MAX_ADDITIONAL_ISLANDS = 2
PROCEDURAL_ISLAND_MIN_SIZE = 12
PROCEDURAL_ISLAND_MAX_SIZE = 50

# === ОТЛАДОЧНЫЕ НАСТРОЙКИ ===
DEBUG_ISLAND_POSITIONING = True   # Показывать отладку позиционирования
ENABLE_SECOND_ISLAND = True       # Включить/выключить второй остров

# === НАСТРОЙКИ ГЕНЕРАЦИИ (для совместимости) ===
ISLAND_WIDTH = 15
ISLAND_HEIGHT = 12
ISLAND_DENSITY = 0.75  # Плотность заполнения острова

# === ПРОВЕРОЧНЫЕ ВЫЧИСЛЕНИЯ ===
print(f"📊 ПРОВЕРКА НАСТРОЕК ЭКРАНА:")
print(f"   Размер экрана: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
print(f"   Размер клетки: {CELL_SIZE}")
print(f"   Клеток помещается: {SCREEN_WIDTH // CELL_SIZE}x{SCREEN_HEIGHT // CELL_SIZE}")
print(f"   Основной остров: ширина {len(ISLAND_MATRIX[0])}, высота {len(ISLAND_MATRIX)}")
print(f"   Основной остров заканчивается примерно на X = {ISLAND_OFFSET_X + len(ISLAND_MATRIX[0])}")

# Проверка места для дополнительных островов
available_width = (SCREEN_WIDTH // CELL_SIZE) - (ISLAND_OFFSET_X + len(ISLAND_MATRIX[0]) + 2)
print(f"   Место для второго острова: X = {available_width}")

if available_width < 10:
    print(f"   ⚠️ ВНИМАНИЕ: Мало места для второго острова ({available_width} клеток)")
    print(f"   💡 Рекомендуется увеличить SCREEN_WIDTH или уменьшить CELL_SIZE")
else:
    print(f"   ✅ Достаточно места для дополнительных островов")

print(f"🏝️ Процедурная генерация островов: {'включена' if ENABLE_PROCEDURAL_ISLANDS else 'отключена'}")

# === АДАПТИВНЫЕ НАСТРОЙКИ ПО РАЗМЕРУ ЭКРАНА ===

# Корректируем настройки в зависимости от размера экрана
if SCREEN_WIDTH >= 1600:
    # Для больших экранов - больше клетки
    CELL_SIZE = 30
    print(f"📏 Большой экран - увеличен размер клетки до {CELL_SIZE}")
elif SCREEN_WIDTH <= 1000:
    # Для маленьких экранов - меньше клетки  
    CELL_SIZE = 20
    print(f"📏 Маленький экран - уменьшен размер клетки до {CELL_SIZE}")

# Пересчитываем количество клеток после корректировки
COLS = SCREEN_WIDTH // CELL_SIZE
ROWS = SCREEN_HEIGHT // CELL_SIZE

print(f"📐 Финальные параметры: {SCREEN_WIDTH}x{SCREEN_HEIGHT}, клетка {CELL_SIZE}px, сетка {COLS}x{ROWS}")
