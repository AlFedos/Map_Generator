"""
Модуль для определения типов биомов и системы биомов
"""

from enum import Enum
from typing import Dict


class BiomeType(Enum):
    """Типы биомов (упрощенный список)"""
    DEEP_OCEAN = "deep_ocean"
    COAST = "coast"
    BEACH = "beach"
    PLAINS = "plains"
    FOREST = "forest"
    MOUNTAINS = "mountains"
    SNOWY_MOUNTAINS = "snowy_mountains"


class BiomeSystem:
    """Система управления биомами"""
    
    def __init__(self):
        self.biome_colors = {
            BiomeType.DEEP_OCEAN: "#000066",        # Темно-синий (глубоководье)
            BiomeType.COAST: "#3399ff",             # Светло-голубой (побережье)
            BiomeType.BEACH: "#ffcc99",             # Светло-оранжевый (песок)
            BiomeType.PLAINS: "#99cc66",            # Светло-зеленый (равнины)
            BiomeType.FOREST: "#006600",            # Темно-зеленый (лес)
            BiomeType.MOUNTAINS: "#666666",         # Серый (горы)
            BiomeType.SNOWY_MOUNTAINS: "#ffffff",   # Белый (заснеженные горы)
        }
                
        self.biome_names = {
            BiomeType.DEEP_OCEAN: "Глубоководье",
            BiomeType.COAST: "Побережье",
            BiomeType.BEACH: "Песок",
            BiomeType.PLAINS: "Равнины",
            BiomeType.FOREST: "Лес",
            BiomeType.MOUNTAINS: "Горы",
            BiomeType.SNOWY_MOUNTAINS: "Заснеженные горы",
        }
    
    def get_biome_color(self, biome_type: BiomeType) -> str:
        return self.biome_colors.get(biome_type, "#FFFFFF")
    
    def get_biome_name(self, biome_type: BiomeType) -> str:
        return self.biome_names.get(biome_type, "Неизвестно")
    
    def classify_biome(self, elevation: float, moisture: float, temperature: float, 
                      water_level: float = -0.3, mountain_level: float = 0.4,
                      desert_moisture: float = 0.3, forest_moisture: float = 0.6) -> BiomeType:
        """
        Классификация биомов
        """
        # Водные биомы
        if elevation < water_level - 0.3:
            return BiomeType.DEEP_OCEAN
        elif elevation < water_level:
            return BiomeType.DEEP_OCEAN
        elif elevation < water_level + 0.15:
            return BiomeType.COAST
        elif elevation < water_level + 0.25:
            # Песок или пустынный берег
            if moisture < desert_moisture:
                return BiomeType.BEACH
            return BiomeType.BEACH
        
        # Сухопутные биомы
        if elevation < 0.1:
            # Низменности
            if moisture > 0.8:
                return BiomeType.FOREST
            elif moisture > 0.65:
                if temperature > 0.8:
                    return BiomeType.FOREST  # Джунгли заменены на лес
                elif temperature > 0.6:
                    return BiomeType.FOREST
                else:
                    return BiomeType.FOREST
            elif moisture < desert_moisture:
                if temperature > 0.7:
                    return BiomeType.BEACH  # Пустыня заменена на песок
                else:
                    return BiomeType.PLAINS
            elif temperature > 0.8:
                if moisture > 0.5:
                    return BiomeType.FOREST  # Джунгли заменены на лес
                else:
                    return BiomeType.PLAINS
            else:
                return BiomeType.PLAINS
        
        elif elevation < 0.3:
            # Средние высоты
            if moisture > forest_moisture:
                if temperature > 0.7:
                    return BiomeType.FOREST
                elif temperature < 0.4:
                    return BiomeType.FOREST
                else:
                    return BiomeType.FOREST
            elif moisture > desert_moisture + 0.1:
                if temperature > 0.6:
                    return BiomeType.PLAINS  # Холмы заменены на равнины
                elif temperature < 0.4:
                    return BiomeType.PLAINS
                else:
                    return BiomeType.PLAINS
            elif moisture < desert_moisture:
                if temperature > 0.6:
                    return BiomeType.BEACH  # Пустынные возвышенности заменены на песок
                else:
                    return BiomeType.PLAINS
            else:
                return BiomeType.PLAINS
        
        elif elevation < mountain_level:
            # Высокие горы
            if temperature < 0.4:
                # Холодные горы
                if elevation > mountain_level - 0.1:
                    return BiomeType.SNOWY_MOUNTAINS
                else:
                    return BiomeType.MOUNTAINS
            elif temperature < 0.6:
                if elevation > mountain_level - 0.15:
                    return BiomeType.MOUNTAINS
                else:
                    return BiomeType.PLAINS
            else:
                return BiomeType.MOUNTAINS
        
        else:
            # Очень высокие горы
            if temperature < 0.5:
                return BiomeType.SNOWY_MOUNTAINS
            else:
                return BiomeType.MOUNTAINS