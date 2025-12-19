"""
Основной модуль генерации карт местности
"""

import numpy as np
import random
import math
from typing import Optional

from noise_generator import ImprovedNoiseGenerator
from biomes import BiomeType, BiomeSystem


class MapGenerator:
    """
    Основной класс для генерации карт местности с системой биомов
    """
    
    def __init__(self, width=60, height=40):
        self.width = width
        self.height = height
        self.map_data = None
        self.seed = random.randint(1, 1000000)
        self.biome_system = BiomeSystem()
        
        # Параметры биомов с нормальными значениями
        self.water_level = -0.3
        self.mountain_level = 0.4
        self.desert_moisture = 0.3
        self.forest_moisture = 0.6
    
    def set_seed(self, seed=None):
        if seed is None:
            self.seed = random.randint(1, 1000000)
        else:
            self.seed = seed
    
    def adjust_water_amount(self, amount: float):
        """Настройка количества воды (0-1)"""
        self.water_level = -0.8 + (amount * 0.7)
    
    def adjust_mountain_amount(self, amount: float):
        """Настройка количества гор (0-1)"""
        self.mountain_level = 0.2 + (amount * 0.6)
    
    def adjust_desert_amount(self, amount: float):
        """Настройка количества пустынь (0-1)"""
        self.desert_moisture = 0.1 + (amount * 0.4)
    
    def adjust_forest_amount(self, amount: float):
        """Настройка количества лесов (0-1)"""
        self.forest_moisture = 0.4 + (amount * 0.5)
    
    def adjust_temperature_amount(self, amount: float):
        """Настройка общей температуры (0 = холодно, 1 = жарко) - базовый метод для совместимости"""
        # Этот метод будет переопределен в EnhancedMapGenerator
        pass
    
    def generate_terrain(self, scale=8.0, roughness=0.5, octaves=4, seed=None,
                         island_mode=True, smooth_iterations=2):
        if seed is not None:
            self.set_seed(seed)
        
        adjusted_octaves = max(1, min(6, int(roughness * 6)))
        persistence = 0.4 + roughness * 0.3
        
        noise_map = ImprovedNoiseGenerator.perlin_noise(
            width=self.width,
            height=self.height,
            scale=scale,
            octaves=adjusted_octaves,
            persistence=persistence,
            lacunarity=2.0,
            seed=self.seed
        )
        
        terrain = (noise_map * 2) - 1
        
        if island_mode:
            terrain = self.apply_island_effect(terrain, strength=0.7)
        
        for _ in range(smooth_iterations):
            terrain = self.smooth_terrain(terrain)
        
        terrain = self.normalize_terrain(terrain)
        terrain = self.smooth_coastlines(terrain)
        
        self.map_data = terrain
        return terrain
    
    def apply_island_effect(self, terrain, strength=0.7):
        height, width = terrain.shape
        
        for y in range(height):
            for x in range(width):
                dx = (x / width - 0.5) * 2
                dy = (y / height - 0.5) * 2
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < 0.7:
                    terrain[y][x] += (1 - distance) * strength * 0.3
                else:
                    falloff = (1 - distance) * strength
                    terrain[y][x] -= abs(falloff) * 0.5
        
        return terrain
    
    def smooth_terrain(self, terrain):
        height, width = terrain.shape
        smoothed = terrain.copy()
        
        for y in range(1, height-1):
            for x in range(1, width-1):
                neighbors = [
                    terrain[y-1][x-1], terrain[y-1][x], terrain[y-1][x+1],
                    terrain[y][x-1], terrain[y][x], terrain[y][x+1],
                    terrain[y+1][x-1], terrain[y+1][x], terrain[y+1][x+1]
                ]
                smoothed[y][x] = np.mean(neighbors) * 0.7 + terrain[y][x] * 0.3
        
        return smoothed
    
    def smooth_coastlines(self, terrain):
        height, width = terrain.shape
        smoothed = terrain.copy()
        
        for y in range(1, height-1):
            for x in range(1, width-1):
                current = terrain[y][x]
                is_water = current < self.water_level
                
                water_neighbors = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < height and 0 <= nx < width:
                            if terrain[ny][nx] < self.water_level:
                                water_neighbors += 1
                
                if is_water and water_neighbors < 4:
                    smoothed[y][x] = max(self.water_level + 0.1, current)
                elif not is_water and water_neighbors > 4:
                    smoothed[y][x] = min(self.water_level + 0.05, current)
        
        return smoothed
    
    def normalize_terrain(self, terrain):
        min_val = np.min(terrain)
        max_val = np.max(terrain)
        
        if max_val > min_val:
            normalized = (terrain - min_val) / (max_val - min_val)
            return normalized * 2 - 1
        else:
            return terrain
    
    def get_terrain_color(self, terrain_type):
        """Для обратной совместимости с GUI"""
        if isinstance(terrain_type, BiomeType):
            return self.biome_system.get_biome_color(terrain_type)
        elif isinstance(terrain_type, str):
            # Для обратной совместимости
            if terrain_type == "deep_water":
                return self.biome_system.get_biome_color(BiomeType.DEEP_OCEAN)
            elif terrain_type == "water":
                return self.biome_system.get_biome_color(BiomeType.COAST)
            elif terrain_type == "sand":
                return self.biome_system.get_biome_color(BiomeType.BEACH)
            elif terrain_type == "grass":
                return self.biome_system.get_biome_color(BiomeType.PLAINS)
            elif terrain_type == "forest":
                return self.biome_system.get_biome_color(BiomeType.FOREST)
            elif terrain_type == "mountain":
                return self.biome_system.get_biome_color(BiomeType.MOUNTAINS)
            elif terrain_type == "snow":
                return self.biome_system.get_biome_color(BiomeType.SNOWY_MOUNTAINS)
            else:
                return "#FFFFFF"
        else:
            return "#FFFFFF"
    
    def get_biome_color(self, biome_type: BiomeType) -> str:
        return self.biome_system.get_biome_color(biome_type)
    
    def get_biome_name(self, biome_type: BiomeType) -> str:
        return self.biome_system.get_biome_name(biome_type)