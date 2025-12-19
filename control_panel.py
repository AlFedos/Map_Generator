"""
Панель управления с настройками генерации карт
"""

import tkinter as tk
from tkinter import ttk
import random


class ControlPanel:
    """
    Панель управления - левая часть интерфейса
    """
    
    def __init__(self, parent, app, status_bar):
        self.parent = parent
        self.app = app
        self.status_bar = status_bar
        
        # Переменные для настроек
        self.water_var = tk.DoubleVar(value=0.5)
        self.mountain_var = tk.DoubleVar(value=0.5)
        self.desert_var = tk.DoubleVar(value=0.3)
        self.forest_var = tk.DoubleVar(value=0.6)
        self.temperature_var = tk.DoubleVar(value=0.5)
        self.use_ml_var = tk.BooleanVar(value=True)
        
        self.width_var = tk.IntVar(value=90)
        self.height_var = tk.IntVar(value=60)
        self.scale_var = tk.DoubleVar(value=10.0)
        self.roughness_var = tk.DoubleVar(value=0.6)
        self.seed_var = tk.StringVar(value="0")
        
        # Пресеты
        self.presets = {
            "Архипелаг": (0.9, 0.2, 0.1, 0.3, 0.6),
            "Пустыня": (0.1, 0.2, 0.9, 0.1, 0.8),
            "Леса": (0.3, 0.2, 0.1, 0.9, 0.5),
            "Горы": (0.3, 0.9, 0.2, 0.3, 0.3),
            "Континент": (0.5, 0.5, 0.3, 0.6, 0.5),
            "Джунгли": (0.6, 0.1, 0.1, 0.8, 0.8),
        }
        
        self.setup_panel()
    
    def setup_panel(self):
        """Настройка панели управления"""
        # Canvas для прокрутки
        self.canvas = tk.Canvas(self.parent, highlightthickness=0, bg='#f0f0f0')
        self.scrollbar = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.canvas.yview)
        self.content_frame = ttk.Frame(self.canvas)
        
        self.content_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Создание компонентов
        self.create_title()
        self.create_map_params_section()
        self.create_gen_params_section()
        self.create_biome_settings_section()
        self.create_presets_section()
        self.create_buttons_section()
        self.create_legend_section()
    
    def create_title(self):
        """Создание заголовка"""
        title_label = ttk.Label(self.content_frame, text="Управление генерацией", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 15))
    
    def create_map_params_section(self):
        """Создание секции параметров карты"""
        map_frame = ttk.LabelFrame(self.content_frame, text="Параметры карты", padding=10)
        map_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Сетка для параметров
        grid = ttk.Frame(map_frame)
        grid.pack(fill=tk.X)
        
        # Ширина
        ttk.Label(grid, text="Ширина:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Spinbox(grid, from_=20, to=300, textvariable=self.width_var, width=10
                   ).grid(row=0, column=1, padx=5, pady=3, sticky=tk.W)
        
        # Высота
        ttk.Label(grid, text="Высота:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Spinbox(grid, from_=20, to=200, textvariable=self.height_var, width=10
                   ).grid(row=1, column=1, padx=5, pady=3, sticky=tk.W)
    
    def create_gen_params_section(self):
        """Создание секции параметров генерации"""
        gen_frame = ttk.LabelFrame(self.content_frame, text="Параметры генерации", padding=10)
        gen_frame.pack(fill=tk.X, pady=(0, 10))
        
        grid = ttk.Frame(gen_frame)
        grid.pack(fill=tk.X)
        
        # Масштаб
        ttk.Label(grid, text="Масштаб:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        scale_scale = ttk.Scale(grid, from_=2, to=20, variable=self.scale_var, 
                               orient=tk.HORIZONTAL, length=180)
        scale_scale.grid(row=0, column=1, padx=5, pady=3, sticky=tk.W)
        self.scale_label = ttk.Label(grid, text="10.0", width=5)
        self.scale_label.grid(row=0, column=2, padx=5, pady=3)
        
        # Шероховатость
        ttk.Label(grid, text="Шероховатость:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        roughness_scale = ttk.Scale(grid, from_=0.1, to=1.0, variable=self.roughness_var,
                                   orient=tk.HORIZONTAL, length=180)
        roughness_scale.grid(row=1, column=1, padx=5, pady=3, sticky=tk.W)
        self.roughness_label = ttk.Label(grid, text="0.6", width=5)
        self.roughness_label.grid(row=1, column=2, padx=5, pady=3)
        
        # Seed
        ttk.Label(grid, text="Seed:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        seed_entry = ttk.Entry(grid, textvariable=self.seed_var, width=15)
        seed_entry.grid(row=2, column=1, padx=5, pady=3, sticky=tk.W)
        ttk.Button(grid, text="Случайный", command=self.generate_random_seed, width=10
                  ).grid(row=2, column=2, padx=5, pady=3)
        
        # ML классификация
        ttk.Label(grid, text="ML классификация:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Checkbutton(grid, variable=self.use_ml_var).grid(row=3, column=1, padx=5, pady=3, sticky=tk.W)
        
        # Кнопка обучения модели
        ttk.Button(grid, text="Обучить модель", command=self.app.train_ml_model, width=12
                  ).grid(row=3, column=2, padx=5, pady=3)
        
        # Привязка обновления меток
        self.scale_var.trace('w', lambda *args: self.update_scale_label())
        self.roughness_var.trace('w', lambda *args: self.update_roughness_label())
    
    def create_biome_settings_section(self):
        """Создание секции настройки биомов"""
        biome_frame = ttk.LabelFrame(self.content_frame, text="Настройка биомов", padding=10)
        biome_frame.pack(fill=tk.X, pady=(0, 10))
        
        grid = ttk.Frame(biome_frame)
        grid.pack(fill=tk.X)
        
        # Вода
        ttk.Label(grid, text="Вода:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        water_scale = ttk.Scale(grid, from_=0.0, to=1.0, variable=self.water_var,
                               orient=tk.HORIZONTAL, length=180)
        water_scale.grid(row=0, column=1, padx=5, pady=3, sticky=tk.W)
        self.water_label = ttk.Label(grid, text="0.5", width=5)
        self.water_label.grid(row=0, column=2, padx=5, pady=3)
        
        # Горы
        ttk.Label(grid, text="Горы:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        mountain_scale = ttk.Scale(grid, from_=0.0, to=1.0, variable=self.mountain_var,
                                  orient=tk.HORIZONTAL, length=180)
        mountain_scale.grid(row=1, column=1, padx=5, pady=3, sticky=tk.W)
        self.mountain_label = ttk.Label(grid, text="0.5", width=5)
        self.mountain_label.grid(row=1, column=2, padx=5, pady=3)
        
        # Пустыни
        ttk.Label(grid, text="Пустыни:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        desert_scale = ttk.Scale(grid, from_=0.0, to=1.0, variable=self.desert_var,
                                orient=tk.HORIZONTAL, length=180)
        desert_scale.grid(row=2, column=1, padx=5, pady=3, sticky=tk.W)
        self.desert_label = ttk.Label(grid, text="0.3", width=5)
        self.desert_label.grid(row=2, column=2, padx=5, pady=3)
        
        # Леса
        ttk.Label(grid, text="Леса:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=3)
        forest_scale = ttk.Scale(grid, from_=0.0, to=1.0, variable=self.forest_var,
                                orient=tk.HORIZONTAL, length=180)
        forest_scale.grid(row=3, column=1, padx=5, pady=3, sticky=tk.W)
        self.forest_label = ttk.Label(grid, text="0.6", width=5)
        self.forest_label.grid(row=3, column=2, padx=5, pady=3)
        
        # Температура
        ttk.Label(grid, text="Температура:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=3)
        temperature_scale = ttk.Scale(grid, from_=0.0, to=1.0, variable=self.temperature_var,
                                     orient=tk.HORIZONTAL, length=180)
        temperature_scale.grid(row=4, column=1, padx=5, pady=3, sticky=tk.W)
        self.temperature_label = ttk.Label(grid, text="0.5", width=5)
        self.temperature_label.grid(row=4, column=2, padx=5, pady=3)
        
        # Привязка обновления меток
        self.water_var.trace('w', lambda *args: self.update_water_label())
        self.mountain_var.trace('w', lambda *args: self.update_mountain_label())
        self.desert_var.trace('w', lambda *args: self.update_desert_label())
        self.forest_var.trace('w', lambda *args: self.update_forest_label())
        self.temperature_var.trace('w', lambda *args: self.update_temperature_label())
    
    def create_presets_section(self):
        """Создание секции пресетов"""
        preset_frame = ttk.LabelFrame(self.content_frame, text="Пресеты биомов", padding=10)
        preset_frame.pack(fill=tk.X, pady=(0, 10))
        
        grid = ttk.Frame(preset_frame)
        grid.pack(fill=tk.X)
        
        # Создаем кнопки для каждого пресета
        row = 0
        col = 0
        for preset_name, values in self.presets.items():
            btn = ttk.Button(
                grid, 
                text=preset_name,
                command=lambda n=preset_name: self.app.apply_preset(n)
            )
            btn.grid(row=row, column=col, padx=2, pady=2, sticky=tk.W+tk.E)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        # Настраиваем расширение колонок
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
    
    def create_buttons_section(self):
        """Создание секции кнопок управления"""
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(fill=tk.X, pady=15)
        
        ttk.Button(btn_frame, text="Сгенерировать карту", 
                  command=self.app.generate_map).pack(pady=5, fill=tk.X)
        
        ttk.Button(btn_frame, text="Новая случайная карта", 
                  command=self.app.new_random_map).pack(pady=5, fill=tk.X)
        
        ttk.Button(btn_frame, text="Экспорт в PNG", 
                  command=self.app.export_current_map).pack(pady=5, fill=tk.X)
    
    def create_legend_section(self):
        """Создание упрощенной секции легенды биомов"""
        legend_frame = ttk.LabelFrame(self.content_frame, text="Легенда биомов", padding=10)
        legend_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Используем compact grid (3 колонки)
        legend_content = ttk.Frame(legend_frame)
        legend_content.pack(fill=tk.X, padx=5, pady=5)
        
        # Компактный список биомов с цветами (из biomes.py)
        biomes_info = [
            ("#000066", "Глубоководье"),
            ("#3399ff", "Побережье"),
            ("#ffcc99", "Песок"),
            ("#99cc66", "Равнины"),
            ("#006600", "Лес"),
            ("#666666", "Горы"),
            ("#ffffff", "Снег"),
        ]
        
        # Размещаем в сетке 3x3
        row, col = 0, 0
        max_cols = 3
        
        for color, name in biomes_info:
            # Создаем мини-фрейм для одного биома
            item_frame = ttk.Frame(legend_content)
            item_frame.grid(row=row, column=col, padx=8, pady=4, sticky=tk.W)
            
            # Цветной индикатор (квадрат)
            color_indicator = tk.Canvas(item_frame, width=16, height=16, 
                                    bg=color, highlightthickness=0)
            color_indicator.pack(side=tk.LEFT, padx=(0, 5))
            
            # Название биома
            name_label = ttk.Label(item_frame, text=name, font=('Arial', 9))
            name_label.pack(side=tk.LEFT)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Информация о цветах температуры (компактная)
        temp_info_frame = ttk.Frame(legend_content)
        temp_info_frame.grid(row=row+1, column=0, columnspan=3, pady=(10, 5), sticky=tk.W)
        
        ttk.Label(temp_info_frame, text="Температура: ", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        # Мини-индикаторы температуры
        temp_colors = [
            ("#0000ff", "Холодно"),
            ("#00ff00", "Умеренно"),
            ("#ff0000", "Жарко")
        ]
        
        for color, label in temp_colors:
            temp_item = ttk.Frame(temp_info_frame)
            temp_item.pack(side=tk.LEFT, padx=(10, 5))
            
            tk.Canvas(temp_item, width=12, height=12, bg=color, 
                    highlightthickness=0).pack(side=tk.LEFT, padx=(0, 3))
            ttk.Label(temp_item, text=label, font=('Arial', 8)).pack(side=tk.LEFT)
    
    def update_scale_label(self):
        """Обновление метки масштаба"""
        self.scale_label.config(text=f"{self.scale_var.get():.1f}")
    
    def update_roughness_label(self):
        """Обновление метки шероховатости"""
        self.roughness_label.config(text=f"{self.roughness_var.get():.2f}")
    
    def update_water_label(self):
        """Обновление метки воды"""
        self.water_label.config(text=f"{self.water_var.get():.2f}")
    
    def update_mountain_label(self):
        """Обновление метки гор"""
        self.mountain_label.config(text=f"{self.mountain_var.get():.2f}")
    
    def update_desert_label(self):
        """Обновление метки пустынь"""
        self.desert_label.config(text=f"{self.desert_var.get():.2f}")
    
    def update_forest_label(self):
        """Обновление метки лесов"""
        self.forest_label.config(text=f"{self.forest_var.get():.2f}")
    
    def update_temperature_label(self):
        """Обновление метки температуры"""
        self.temperature_label.config(text=f"{self.temperature_var.get():.2f}")
    
    def generate_random_seed(self):
        """Генерация случайного seed"""
        seed = random.randint(1, 1000000)
        self.seed_var.set(str(seed))
    
    def get_generation_params(self):
        """Получение параметров генерации"""
        seed_str = self.seed_var.get().strip()
        seed = int(seed_str) if seed_str and seed_str != "0" else None
        
        return {
            'width': self.width_var.get(),
            'height': self.height_var.get(),
            'scale': self.scale_var.get(),
            'roughness': self.roughness_var.get(),
            'seed': seed,
            'use_ml': self.use_ml_var.get()
        }
    
    def get_biome_params(self):
        """Получение параметров биомов"""
        return {
            'water': self.water_var.get(),
            'mountain': self.mountain_var.get(),
            'desert': self.desert_var.get(),
            'forest': self.forest_var.get(),
            'temperature': self.temperature_var.get()
        }
    
    def apply_preset(self, preset_name):
        """Применение пресета биомов"""
        if preset_name in self.presets:
            water, mountain, desert, forest, temperature = self.presets[preset_name]
            
            self.water_var.set(water)
            self.mountain_var.set(mountain)
            self.desert_var.set(desert)
            self.forest_var.set(forest)
            self.temperature_var.set(temperature)
            
            # Обновляем метки
            self.update_water_label()
            self.update_mountain_label()
            self.update_desert_label()
            self.update_forest_label()
            self.update_temperature_label()
            
            self.status_bar.set_status(f"Применен пресет: {preset_name}")
            return True
        
        return False
    
    def set_buttons_state(self, enabled=True):
        """Включение/выключение кнопок управления"""
        # Находим все кнопки в content_frame
        for widget in self.content_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state=tk.NORMAL if enabled else tk.DISABLED)
            elif isinstance(widget, (ttk.Frame, ttk.LabelFrame)):
                # Рекурсивно ищем кнопки во вложенных фреймах
                self._set_buttons_state_recursive(widget, enabled)

    def _set_buttons_state_recursive(self, parent, enabled):
        """Рекурсивное изменение состояния кнопок"""
        for widget in parent.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state=tk.NORMAL if enabled else tk.DISABLED)
            elif isinstance(widget, (ttk.Frame, ttk.LabelFrame)):
                self._set_buttons_state_recursive(widget, enabled)