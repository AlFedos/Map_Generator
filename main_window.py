"""
Основное окно приложения - координатор всех компонентов
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import threading

from .control_panel import ControlPanel
from .display_panel import DisplayPanel
from .status_bar import StatusBar
from .utils.export_utils import export_map_to_png
from enhanced_map_generator import EnhancedMapGenerator
from biomes import BiomeType


class MapGeneratorGUI:
    """
    Главный класс графического интерфейса
    Координирует работу всех компонентов
    """
    
    def __init__(self, root):
        self.root = root
        self.map_gen = None
        self.current_terrain = None
        self.current_moisture = None
        self.current_temperature = None
        
        # Флаг состояния
        self.is_generating = False
        
        self.setup_window()
        self.setup_components()
        
        # Инициализируем статус
        self.update_status()
    
    def setup_window(self):
        """Настройка главного окна"""
        self.root.title("Интеллектуальная система генерации карт местности (с ML)")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Главный контейнер
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Разделитель для левой и правой панели
        self.paned_window = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Создаем контейнеры для панелей
        self.left_container = ttk.Frame(self.paned_window, width=400)
        self.right_container = ttk.Frame(self.paned_window)
        
        self.paned_window.add(self.left_container, weight=1)
        self.paned_window.add(self.right_container, weight=2)
    
    def setup_components(self):
        """Инициализация и настройка компонентов"""
        # Создаем статусную строку
        self.status_bar = StatusBar(self.root)
        
        # Создаем панель управления
        self.control_panel = ControlPanel(
            self.left_container, 
            self,
            self.status_bar
        )
        
        # Создаем панель отображения
        self.display_panel = DisplayPanel(
            self.right_container,
            self,
            self.status_bar
        )
    
    def generate_map(self):
        """Синхронная генерация карты (простейшая версия для отладки)"""
        if self.is_generating:
            return
            
        try:
            self.is_generating = True
            self.status_bar.set_status("Генерация карты...")
            
            # Получаем параметры
            params = self.control_panel.get_generation_params()
            biome_params = self.control_panel.get_biome_params()
            
            # Создаем генератор
            self.map_gen = EnhancedMapGenerator(
                width=params['width'],
                height=params['height'],
                use_ml=params['use_ml']
            )
            
            # Применяем настройки биомов
            self.map_gen.adjust_water_amount(biome_params['water'])
            self.map_gen.adjust_mountain_amount(biome_params['mountain'])
            self.map_gen.adjust_desert_amount(biome_params['desert'])
            self.map_gen.adjust_forest_amount(biome_params['forest'])
            self.map_gen.adjust_temperature_amount(biome_params['temperature'])
            
            # Генерируем карты
            self.current_terrain = self.map_gen.generate_terrain(
                scale=params['scale'],
                roughness=params['roughness'],
                seed=params['seed']
            )
            
            self.current_moisture, self.current_temperature = self.map_gen.generate_climate_maps(
                scale=params['scale']
            )
            
            # Генерируем карту биомов
            self.map_gen.generate_biome_map()
            
            # Отображаем карты
            self.redraw_all_maps()
            self.update_stats()
            self.update_ml_info()
            self.update_status()
            
            self.status_bar.set_status("Карта сгенерирована успешно!")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status_bar.set_error(f"Ошибка при генерации карты: {str(e)}")
        finally:
            self.is_generating = False
    
    def redraw_all_maps(self):
        """Перерисовка всех карт"""
        if self.current_terrain is None or self.map_gen is None:
            return
        
        # Отрисовываем карту местности
        self.display_panel.draw_terrain_map(
            self.current_terrain,
            self.map_gen
        )
        
        # Отрисовываем карту высот
        self.display_panel.draw_height_map(
            self.current_terrain,
            self.map_gen
        )
        
        # Отрисовываем карту температуры
        if self.current_temperature is not None:
            self.display_panel.draw_temperature_map(
                self.current_temperature,
                self.map_gen
            )
    
    def update_stats(self):
        """Обновление статистики"""
        if self.map_gen is None:
            return
        
        # Вычисляем статистику
        stats = self.calculate_stats()
        self.display_panel.update_stats(stats)
    
    def calculate_stats(self):
        """Вычисление статистики карты"""
        if (self.map_gen is None or self.current_terrain is None):
            return {}
        
        total_cells = self.map_gen.width * self.map_gen.height
        
        # Подсчет биомов
        biome_counts = {}
        if self.map_gen.biome_data is not None:
            # Простой подсчет
            for biome_type in BiomeType:
                biome_counts[biome_type] = 0
            
            for y in range(self.map_gen.height):
                for x in range(self.map_gen.width):
                    biome = self.map_gen.biome_data[y][x]
                    if biome in biome_counts:
                        biome_counts[biome] += 1
        
        # Характеристики высот
        min_height = float(np.min(self.current_terrain))
        max_height = float(np.max(self.current_terrain))
        avg_height = float(np.mean(self.current_terrain))
        
        # Влажность и температура
        avg_moisture = None
        avg_temperature = None
        
        if self.current_moisture is not None:
            avg_moisture = float(np.mean(self.current_moisture))
        
        if self.current_temperature is not None:
            avg_temperature = float(np.mean(self.current_temperature))
        
        # ML статистика
        ml_stats = {}
        if hasattr(self.map_gen, 'get_ml_stats'):
            ml_stats = self.map_gen.get_ml_stats()
        
        return {
            'width': self.map_gen.width,
            'height': self.map_gen.height,
            'seed': self.map_gen.seed,
            'total_cells': total_cells,
            'biome_counts': biome_counts,
            'min_height': min_height,
            'max_height': max_height,
            'avg_height': avg_height,
            'avg_moisture': avg_moisture,
            'avg_temperature': avg_temperature,
            'ml_stats': ml_stats,
            'biome_params': self.control_panel.get_biome_params()
        }
    
    def update_ml_info(self):
        """Обновление информации о ML"""
        if self.map_gen is None:
            return
        
        ml_stats = self.map_gen.get_ml_stats()
        
        if ml_stats["enabled"] and ml_stats["model_loaded"]:
            info = f"""ML активен:
• Модель загружена и используется
• Клеток классифицировано ML: {ml_stats.get('ml_cells', 0)}
• Процент ML классификации: {ml_stats.get('ml_percent', 0):.1f}%"""
        elif ml_stats["enabled"]:
            info = "ML включен, но модель не обучена.\nНажмите 'Обучить модель' для начала."
        else:
            info = "ML классификация отключена."
        
        self.display_panel.update_ml_info(info)
    
    def update_status(self):
        """Обновление статусной строки"""
        if self.map_gen is None:
            self.status_bar.set_status("Готов к генерации")
            self.status_bar.set_ml_status("❌ не обучена")
            self.status_bar.set_seed("-")
            return
        
        ml_stats = self.map_gen.get_ml_stats()
        
        if ml_stats["enabled"] and ml_stats["model_loaded"]:
            status = f"Карта сгенерирована | ML: {ml_stats.get('ml_percent', 0):.1f}%"
        elif ml_stats["enabled"]:
            status = "Карта сгенерирована (ML не обучен)"
        else:
            status = "Карта сгенерирована (без ML)"
        
        self.status_bar.set_status(status)
        self.status_bar.set_seed(self.map_gen.seed)
        
        if ml_stats["enabled"] and ml_stats["model_loaded"]:
            self.status_bar.set_ml_status("✅ обучена")
        elif ml_stats["enabled"]:
            self.status_bar.set_ml_status("❌ не обучена")
        else:
            self.status_bar.set_ml_status("⚪ выключена")
    
    def train_ml_model(self):
        """Обучение ML модели"""
        def training_thread():
            try:
                self.status_bar.set_status("Начало обучения ML модели...")
                
                from ml_biome_classifier import MLBiomeClassifier
                classifier = MLBiomeClassifier(use_ml=True, auto_train=False)
                classifier.train_model(samples=20000, save=True)
                
                # Обновляем модель в генераторе
                if self.map_gen:
                    self.map_gen.ml_classifier = classifier
                    self.map_gen.ml_enabled = True
                
                self.status_bar.set_status("ML модель обучена успешно!")
                self.status_bar.set_ml_status("✅ обучена")
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.status_bar.set_error(f"Ошибка при обучении модели: {str(e)}")
        
        # Запускаем обучение в отдельном потоке
        thread = threading.Thread(target=training_thread, daemon=True)
        thread.start()
    
    def apply_preset(self, preset_name):
        """Применение пресета биомов"""
        success = self.control_panel.apply_preset(preset_name)
        
        if success and self.map_gen and self.current_terrain is not None:
            # Обновляем генератор
            params = self.control_panel.get_biome_params()
            self.map_gen.adjust_water_amount(params['water'])
            self.map_gen.adjust_mountain_amount(params['mountain'])
            self.map_gen.adjust_desert_amount(params['desert'])
            self.map_gen.adjust_forest_amount(params['forest'])
            self.map_gen.adjust_temperature_amount(params['temperature'])
            
            # Перегенерируем карту биомов
            self.map_gen.generate_biome_map()
            self.redraw_all_maps()
            self.update_stats()
            self.update_ml_info()
            self.update_status()
    
    def export_current_map(self):
        """Экспорт текущей карты"""
        if self.current_terrain is None or self.map_gen is None:
            self.status_bar.set_status("Нет карты для экспорта")
            return
        
        try:
            filename = export_map_to_png(
                self.current_terrain,
                self.map_gen
            )
            self.status_bar.set_status(f"Карта сохранена: {filename}")
        except Exception as e:
            self.status_bar.set_error(f"Ошибка при экспорте: {str(e)}")
    
    def new_random_map(self):
        """Генерация новой случайной карты"""
        self.control_panel.generate_random_seed()
        self.generate_map()