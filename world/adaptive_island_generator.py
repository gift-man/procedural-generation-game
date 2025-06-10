"""Адаптер для использования адаптивного генератора с островами"""
from world.generator import ProvinceGenerator

class AdaptiveIslandProvinceGenerator:
    def __init__(self, island_cells):
        self.island_cells = set(island_cells)
        
        # Создаем временный объект острова
        self.temp_island = self._create_temp_island()
        
        # Инициализируем ваш адаптивный генератор
        self.province_generator = ProvinceGenerator(self.temp_island)
    
    def _create_temp_island(self):
        """Создает объект совместимый с вашим генератором"""
        class TempIsland:
            def __init__(self, cells):
                self.cells = set(cells)
        
        return TempIsland(self.island_cells)
    
    def generate_provinces(self, target_count=None):
        """Генерирует провинции используя ваш адаптивный алгоритм"""
        print(f"🎯 Использование адаптивного генератора для {len(self.island_cells)} клеток")
        
        # Если задано целевое количество, модифицируем настройки
        if target_count:
            # Временно изменяем параметры генератора
            original_min = getattr(self.province_generator, 'MIN_PROVINCE_SIZE', 4)
            original_max = getattr(self.province_generator, 'MAX_PROVINCE_SIZE', 8)
            
            # Подстраиваем под целевое количество
            avg_size = len(self.island_cells) / target_count
            self.province_generator.MIN_PROVINCE_SIZE = max(3, int(avg_size * 0.7))
            self.province_generator.MAX_PROVINCE_SIZE = min(12, int(avg_size * 1.5))
            
            print(f"   📊 Целевое количество: {target_count}")
            print(f"   📏 Адаптированные размеры: {self.province_generator.MIN_PROVINCE_SIZE}-{self.province_generator.MAX_PROVINCE_SIZE}")
        
        # Используем ваш генератор
        provinces, province_map = self.province_generator.generate_provinces()
        
        # Восстанавливаем настройки если изменяли
        if target_count:
            self.province_generator.MIN_PROVINCE_SIZE = original_min
            self.province_generator.MAX_PROVINCE_SIZE = original_max
        
        return provinces, province_map
