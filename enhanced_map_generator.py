# enhanced_map_generator.py
"""
Расширенный генератор карт с дополнительными параметрами и ML поддержкой
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any

from map_generator import MapGenerator
from biomes import BiomeType
from noise_generator import ImprovedNoiseGenerator
from ml_biome_classifier import MLBiomeClassifier  # <-- ИМПОРТ МЛ МОДУЛЯ


class EnhancedMapGenerator(MapGenerator):
    """
    Расширенный генератор с дополнительными параметрами и ML классификацией
    """
    
    def __init__(self, width=60, height=40, use_ml: bool = True):
        super().__init__(width, height)
        self.moisture_data = None
        self.temperature_data = None
        self.biome_data = None
        self.ml_predictions = None
        
        # Дополнительные параметры для усиления биомов
        self.water_amount = 0.5
        self.mountain_amount = 0.5
        self.desert_amount = 0.3
        self.forest_amount = 0.6
        self.temperature_amount = 0.5
        
        # ML классификатор
        self.use_ml = use_ml
        self.ml_classifier = MLBiomeClassifier(use_ml=use_ml, auto_train=True)
        self.ml_accuracy = None
        self.ml_enabled = use_ml and self.ml_classifier.is_trained
    
    def adjust_water_amount(self, amount: float):
        """Переопределяем для сохранения значения water_amount"""
        self.water_amount = amount
        super().adjust_water_amount(amount)
    
    def adjust_mountain_amount(self, amount: float):
        """Переопределяем для сохранения значения mountain_amount"""
        self.mountain_amount = amount
        super().adjust_mountain_amount(amount)
    
    def adjust_desert_amount(self, amount: float):
        """Переопределяем для сохранения значения desert_amount"""
        self.desert_amount = amount
        super().adjust_desert_amount(amount)
    
    def adjust_forest_amount(self, amount: float):
        """Переопределяем для сохранения значения forest_amount"""
        self.forest_amount = amount
        super().adjust_forest_amount(amount)
    
    def adjust_temperature_amount(self, amount: float):
        """Настройка общей температуры (0 = холодно, 1 = жарко)"""
        self.temperature_amount = amount
    
    def set_ml_enabled(self, enabled: bool):
        """Включить/выключить ML классификацию"""
        self.use_ml = enabled
        self.ml_enabled = enabled and self.ml_classifier.is_trained
        if enabled and not self.ml_classifier.is_trained:
            print("Предупреждение: ML модель не обучена. Используются правила.")
    
    def generate_climate_maps(self, scale=8.0) -> Tuple[np.ndarray, np.ndarray]:
        """Генерация карт влажности и температуры"""
        moisture_seed = self.seed + 1000
        moisture_map = ImprovedNoiseGenerator.perlin_noise(
            width=self.width,
            height=self.height,
            scale=scale * 0.7,
            octaves=3,
            persistence=0.5,
            lacunarity=2.0,
            seed=moisture_seed
        )
        
        # Корректируем влажность на основе настроек биомов
        for y in range(self.height):
            for x in range(self.width):
                elevation = self.map_data[y][x] if self.map_data is not None else 0
                
                # Увеличиваем влажность в лесах
                if self.forest_amount > 0.7 and 0.1 < elevation < 0.4:
                    moisture_map[y][x] = min(1.0, moisture_map[y][x] * 1.3)
                elif self.forest_amount < 0.3 and 0.1 < elevation < 0.4:
                    moisture_map[y][x] = max(0.0, moisture_map[y][x] * 0.7)
                
                # Уменьшаем влажность для песка/пустынь
                if self.desert_amount > 0.7 and elevation < 0.2:
                    moisture_map[y][x] = max(0.0, moisture_map[y][x] * 0.5)
                elif self.desert_amount < 0.3 and elevation < 0.2:
                    moisture_map[y][x] = min(1.0, moisture_map[y][x] * 1.2)
        
        temperature_seed = self.seed + 2000
        temp_base = ImprovedNoiseGenerator.perlin_noise(
            width=self.width,
            height=self.height,
            scale=scale * 0.5,
            octaves=2,
            persistence=0.4,
            lacunarity=2.0,
            seed=temperature_seed
        )
        
        temperature_map = np.zeros((self.height, self.width))
        for y in range(self.height):
            lat_factor = 1.0 - abs(y / self.height - 0.5) * 1.5
            lat_factor = max(0.0, min(1.0, lat_factor))
            
            for x in range(self.width):
                if self.map_data is not None:
                    height_factor = 1.0 - max(0, self.map_data[y][x]) * 0.8
                else:
                    height_factor = 1.0
                
                # Базовая температура с учетом настройки пользователя
                base_temp = (temp_base[y][x] * 0.4 + 
                            lat_factor * 0.5 + 
                            height_factor * 0.1)
                
                # Применяем глобальную настройку температуры
                temp_adjustment = (self.temperature_amount - 0.5) * 0.5
                adjusted_temp = base_temp + temp_adjustment
                
                temperature_map[y][x] = max(0.0, min(1.0, adjusted_temp))
        
        # Нормализация
        if np.max(moisture_map) - np.min(moisture_map) > 0:
            moisture_map = (moisture_map - np.min(moisture_map)) / (np.max(moisture_map) - np.min(moisture_map))
        else:
            moisture_map = np.ones_like(moisture_map) * 0.5
            
        if np.max(temperature_map) - np.min(temperature_map) > 0:
            temperature_map = (temperature_map - np.min(temperature_map)) / (np.max(temperature_map) - np.min(temperature_map))
        else:
            temperature_map = np.ones_like(temperature_map) * 0.5
        
        self.moisture_data = moisture_map
        self.temperature_data = temperature_map
        
        return moisture_map, temperature_map
    
    def generate_biome_map(self, use_ml: bool = None) -> np.ndarray:
        """
        Генерация карты биомов с возможностью использования ML
        
        Args:
            use_ml: Использовать ML классификатор (None - использовать настройку по умолчанию)
        """
        if self.map_data is None:
            self.generate_terrain()
        
        if self.moisture_data is None or self.temperature_data is None:
            self.generate_climate_maps()
        
        # Определяем, использовать ли ML
        use_ml_final = use_ml if use_ml is not None else self.ml_enabled
        
        biome_map = np.empty((self.height, self.width), dtype=object)
        ml_predictions = np.zeros((self.height, self.width), dtype=bool)
        
        # Счетчики для статистики
        ml_count = 0
        rule_count = 0
        
        for y in range(self.height):
            for x in range(self.width):
                elevation = self.map_data[y][x]
                moisture = self.moisture_data[y][x]
                temperature = self.temperature_data[y][x]
                
                # Дополнительные корректировки на основе настроек
                adjusted_elevation = elevation
                adjusted_moisture = moisture
                adjusted_temperature = temperature
                
                # Корректировка для воды
                if self.water_amount > 0.7 and elevation < -0.1:
                    adjusted_elevation -= 0.15
                elif self.water_amount < 0.3 and elevation < -0.1:
                    adjusted_elevation += 0.15
                
                # Корректировка для гор
                if self.mountain_amount > 0.7 and elevation > 0.2:
                    adjusted_elevation += 0.15
                elif self.mountain_amount < 0.3 and elevation > 0.2:
                    adjusted_elevation -= 0.15
                
                # Корректировка для пустынь/песка
                if self.desert_amount > 0.7 and elevation < 0.3:
                    adjusted_moisture *= 0.6
                    adjusted_temperature = min(1.0, adjusted_temperature * 1.2)
                elif self.desert_amount < 0.3 and elevation < 0.3:
                    adjusted_moisture = min(1.0, adjusted_moisture * 1.3)
                
                # Корректировка для лесов
                if self.forest_amount > 0.7 and 0.1 < elevation < 0.5:
                    adjusted_moisture = min(1.0, adjusted_moisture * 1.3)
                elif self.forest_amount < 0.3 and 0.1 < elevation < 0.5:
                    adjusted_moisture *= 0.7
                
                # Корректировка температуры на основе общего параметра температуры
                temp_adjustment = (self.temperature_amount - 0.5) * 0.3
                adjusted_temperature = max(0.0, min(1.0, adjusted_temperature + temp_adjustment))
                
                # Пробуем ML классификацию
                ml_biome = None
                if use_ml_final:
                    ml_biome = self.ml_classifier.predict_biome(
                        adjusted_elevation, 
                        adjusted_moisture, 
                        adjusted_temperature,
                        self.water_level,
                        self.mountain_level,
                        self.desert_moisture,
                        self.forest_moisture
                    )
                
                if ml_biome is not None:
                    biome_map[y][x] = ml_biome
                    ml_predictions[y][x] = True
                    ml_count += 1
                else:
                    # Используем классификацию по правилам
                    biome = self.biome_system.classify_biome(
                        adjusted_elevation, 
                        adjusted_moisture, 
                        adjusted_temperature,
                        self.water_level,
                        self.mountain_level,
                        self.desert_moisture,
                        self.forest_moisture
                    )
                    biome_map[y][x] = biome
                    rule_count += 1
        
        self.biome_data = biome_map
        self.ml_predictions = ml_predictions
        
        # Статистика использования ML
        total_cells = self.width * self.height
        ml_percent = (ml_count / total_cells) * 100 if total_cells > 0 else 0
        
        if use_ml_final and ml_count > 0:
            print(f"ML классификация: {ml_count}/{total_cells} клеток ({ml_percent:.1f}%)")
        
        return biome_map
    
    def classify_terrain(self, elevation, x=None, y=None, terrain_map=None):
        """Классификация типа местности с поддержкой ML"""
        # Если доступны ML предсказания, используем их
        if (self.biome_data is not None and x is not None and y is not None 
            and 0 <= y < self.height and 0 <= x < self.width):
            
            biome = self.biome_data[y][x]
            
            # Конвертируем в старый формат для совместимости
            if biome == BiomeType.DEEP_OCEAN:
                return "deep_water"
            elif biome == BiomeType.COAST:
                return "water"
            elif biome == BiomeType.BEACH:
                return "sand"
            elif biome == BiomeType.PLAINS:
                return "grass"
            elif biome == BiomeType.FOREST:
                return "forest"
            elif biome == BiomeType.MOUNTAINS:
                return "mountain"
            elif biome == BiomeType.SNOWY_MOUNTAINS:
                return "snow"
        
        # Резервная классификация
        if elevation < -0.5:
            return "deep_water"
        elif elevation < -0.15:
            return "water"
        elif elevation < 0.0:
            return "sand"
        elif elevation < 0.25:
            return "grass"
        elif elevation < 0.45:
            return "forest"
        elif elevation < 0.7:
            return "mountain"
        else:
            return "snow"
    
    def get_all_biomes(self):
        """Возвращает все типы биомов с их цветами и названиями"""
        return [
            (BiomeType.DEEP_OCEAN, self.get_biome_color(BiomeType.DEEP_OCEAN), "Глубоководье"),
            (BiomeType.COAST, self.get_biome_color(BiomeType.COAST), "Побережье"),
            (BiomeType.BEACH, self.get_biome_color(BiomeType.BEACH), "Песок"),
            (BiomeType.PLAINS, self.get_biome_color(BiomeType.PLAINS), "Равнины"),
            (BiomeType.FOREST, self.get_biome_color(BiomeType.FOREST), "Лес"),
            (BiomeType.MOUNTAINS, self.get_biome_color(BiomeType.MOUNTAINS), "Горы"),
            (BiomeType.SNOWY_MOUNTAINS, self.get_biome_color(BiomeType.SNOWY_MOUNTAINS), "Заснеженные горы"),
        ]
    
    def apply_preset(self, preset_name: str):
        """Применение пресета биомов"""
        presets = {
            "Архипелаг": (0.9, 0.2, 0.1, 0.3, 0.6),
            "Пустыня": (0.1, 0.2, 0.9, 0.1, 0.8),
            "Леса": (0.3, 0.2, 0.1, 0.9, 0.5),
            "Горы": (0.3, 0.9, 0.2, 0.3, 0.3),
            "Континент": (0.5, 0.5, 0.3, 0.6, 0.5),
            "Джунгли": (0.6, 0.1, 0.1, 0.8, 0.8),
        }
        
        if preset_name in presets:
            water, mountain, desert, forest, temperature = presets[preset_name]
            self.adjust_water_amount(water)
            self.adjust_mountain_amount(mountain)
            self.adjust_desert_amount(desert)
            self.adjust_forest_amount(forest)
            self.adjust_temperature_amount(temperature)
            return True
        return False
    
    def get_ml_stats(self) -> Dict[str, Any]:
        """Получить статистику по использованию ML"""
        if self.ml_predictions is None:
            return {"enabled": False, "message": "ML не использовался"}
        
        ml_count = np.sum(self.ml_predictions)
        total_cells = self.width * self.height
        ml_percent = (ml_count / total_cells) * 100 if total_cells > 0 else 0
        
        return {
            "enabled": self.ml_enabled,
            "ml_cells": int(ml_count),
            "total_cells": total_cells,
            "ml_percent": ml_percent,
            "model_loaded": self.ml_classifier.is_trained,
            "use_ml": self.use_ml
        }