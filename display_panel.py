"""
Панель отображения карт и информации
"""

import tkinter as tk
from tkinter import ttk
import numpy as np


class DisplayPanel:
    """
    Панель отображения - правая часть интерфейса
    """
    
    def __init__(self, parent, app, status_bar):
        self.parent = parent
        self.app = app
        self.status_bar = status_bar
        
        self.notebook = None
        self.terrain_canvas = None
        self.height_canvas = None
        self.temp_canvas = None
        self.stats_text = None
        self.ml_text = None
        
        self.setup_panel()
    
    def setup_panel(self):
        """Настройка панели отображения"""
        # Вкладки для разных отображений
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Создание вкладок
        self.create_terrain_tab()
        self.create_height_tab()
        self.create_temperature_tab()
        self.create_stats_tab()
        self.create_ml_tab()
    
    def create_terrain_tab(self):
        """Создание вкладки с картой местности"""
        terrain_tab = ttk.Frame(self.notebook)
        self.notebook.add(terrain_tab, text="Карта местности")
        
        self.terrain_canvas = tk.Canvas(terrain_tab, bg='white', 
                                       highlightthickness=0)
        self.terrain_canvas.pack(fill=tk.BOTH, expand=True)
    
    def create_height_tab(self):
        """Создание вкладки с картой высот"""
        height_tab = ttk.Frame(self.notebook)
        self.notebook.add(height_tab, text="Карта высот")
        
        self.height_canvas = tk.Canvas(height_tab, bg='white',
                                      highlightthickness=0)
        self.height_canvas.pack(fill=tk.BOTH, expand=True)
    
    def create_temperature_tab(self):
        """Создание вкладки с картой температуры"""
        temp_tab = ttk.Frame(self.notebook)
        self.notebook.add(temp_tab, text="Карта температуры")
        
        self.temp_canvas = tk.Canvas(temp_tab, bg='white',
                                    highlightthickness=0)
        self.temp_canvas.pack(fill=tk.BOTH, expand=True)
    
    def create_stats_tab(self):
        """Создание вкладки со статистикой"""
        stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(stats_tab, text="Статистика")
        
        # Frame для статистики
        stats_frame = ttk.Frame(stats_tab)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # Текстовое поле для статистики
        self.stats_text = tk.Text(stats_frame, font=('Courier', 9), wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(stats_frame, command=self.stats_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stats_text.configure(yscrollcommand=scrollbar.set)
        
        self.stats_text.insert(1.0, "Статистика будет отображена после генерации карты...")
        self.stats_text.configure(state='disabled')
    
    def create_ml_tab(self):
        """Создание вкладки с ML информацией"""
        ml_tab = ttk.Frame(self.notebook)
        self.notebook.add(ml_tab, text="ML информация")
        
        # Frame для ML информации
        ml_frame = ttk.Frame(ml_tab)
        ml_frame.pack(fill=tk.BOTH, expand=True)
        
        # Текстовое поле для ML информации
        self.ml_text = tk.Text(ml_frame, font=('Arial', 9), wrap=tk.WORD)
        self.ml_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(ml_frame, command=self.ml_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ml_text.configure(yscrollcommand=scrollbar.set)
        
        self.ml_text.insert(1.0, "Информация о машинном обучении...")
        self.ml_text.configure(state='disabled')
    
    def draw_terrain_map(self, terrain_data, map_gen):
        """Отрисовка карты местности"""
        if terrain_data is None or map_gen is None:
            return
        
        self._draw_map(
            self.terrain_canvas,
            terrain_data,
            map_gen,
            lambda x, y, elevation, gen: gen.get_terrain_color(
                gen.classify_terrain(elevation, x, y, terrain_data)
            )
        )
    
    def draw_height_map(self, terrain_data, map_gen):
        """Отрисовка карты высот"""
        if terrain_data is None:
            return
        
        self._draw_map(
            self.height_canvas,
            terrain_data,
            map_gen,
            lambda x, y, elevation, gen: self._height_to_color(elevation, terrain_data)
        )
    
    def draw_temperature_map(self, temperature_data, map_gen):
        """Отрисовка карты температуры"""
        if temperature_data is None:
            return
        
        self._draw_map(
            self.temp_canvas,
            temperature_data,
            map_gen,
            lambda x, y, temperature, gen: self._temperature_to_color(temperature)
        )
    
    def _draw_map(self, canvas, data, map_gen, color_func):
        """Общий метод отрисовки карты"""
        if data is None or map_gen is None:
            return
        
        canvas.delete("all")
        
        # Размеры канваса
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 600
            canvas_height = 400
        
        # Размер клетки
        cell_width = canvas_width / map_gen.width
        cell_height = canvas_height / map_gen.height
        cell_size = min(cell_width, cell_height)
        
        # Смещение для центрирования
        offset_x = (canvas_width - cell_size * map_gen.width) / 2
        offset_y = (canvas_height - cell_size * map_gen.height) / 2
        
        # Отрисовка клеток (оптимизированная - без сетки)
        for y in range(map_gen.height):
            for x in range(map_gen.width):
                value = data[y][x]
                color = color_func(x, y, value, map_gen)
                
                # Координаты клетки
                x1 = offset_x + x * cell_size
                y1 = offset_y + y * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                # Рисуем клетку без обводки для скорости
                canvas.create_rectangle(x1, y1, x2, y2, 
                                      fill=color, outline="", width=0)
    
    def _height_to_color(self, elevation, terrain_data):
        """Преобразование высоты в цвет (градации серого)"""
        min_height = np.min(terrain_data)
        max_height = np.max(terrain_data)
        height_range = max_height - min_height
        
        if height_range > 0:
            normalized = (elevation - min_height) / height_range
        else:
            normalized = 0.5
        
        gray_value = int(normalized * 255)
        return f'#{gray_value:02x}{gray_value:02x}{gray_value:02x}'
    
    def _temperature_to_color(self, temperature):
        """Преобразование температуры в цвет (упрощенная версия)"""
        # Упрощенный градиент для производительности
        if temperature < 0.3:
            # От синего к голубому
            blue = 255
            green = int(255 * temperature / 0.3)
            red = 0
        elif temperature < 0.7:
            # От голубого к желтому
            normalized = (temperature - 0.3) / 0.4
            red = int(255 * normalized)
            green = 255
            blue = int(255 * (1 - normalized))
        else:
            # От желтого к красному
            normalized = (temperature - 0.7) / 0.3
            red = 255
            green = int(255 * (1 - normalized))
            blue = 0
        
        # Ограничиваем значения
        red = max(0, min(255, red))
        green = max(0, min(255, green))
        blue = max(0, min(255, blue))
        
        return f'#{red:02x}{green:02x}{blue:02x}'
    
    def update_stats(self, stats):
        """Обновление статистики"""
        if self.stats_text is None:
            return
        
        text = self._format_stats(stats)
        
        self.stats_text.configure(state='normal')
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, text)
        self.stats_text.see(1.0)  # Прокручиваем к началу
        self.stats_text.configure(state='disabled')
    
    def _format_stats(self, stats):
        """Упрощенное форматирование статистики"""
        if not stats:
            return "Статистика недоступна\n"
        
        text = f"Размер: {stats['width']} × {stats['height']}\n"
        text += f"Seed: {stats['seed']}\n"
        text += f"Всего клеток: {stats['total_cells']}\n\n"
        
        # Основная статистика биомов
        text += "Распределение биомов:\n"
        biome_counts = stats['biome_counts']
        total_cells = stats['total_cells']
        
        # Показываем только биомы с ненулевым количеством
        for biome, count in sorted(biome_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / total_cells) * 100
                biome_name = str(biome).replace('BiomeType.', '').replace('_', ' ')
                text += f"  {biome_name}: {percentage:.1f}%\n"
        
        text += f"\nВысота: {stats['min_height']:.2f} - {stats['max_height']:.2f}\n"
        text += f"Средняя: {stats['avg_height']:.2f}\n"
        
        ml_stats = stats.get('ml_stats', {})
        if ml_stats.get('enabled'):
            text += f"\nML: {ml_stats.get('ml_percent', 0):.1f}%\n"
        
        return text
    
    def update_ml_info(self, info_text):
        """Обновление информации о ML"""
        if self.ml_text is None:
            return
        
        self.ml_text.configure(state='normal')
        self.ml_text.delete(1.0, tk.END)
        self.ml_text.insert(1.0, info_text)
        self.ml_text.see(1.0)
        self.ml_text.configure(state='disabled')