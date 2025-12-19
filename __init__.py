"""
Пакет для процедурной генерации карт
"""

from .biomes import BiomeType, BiomeSystem
from .noise_generator import ImprovedNoiseGenerator
from .map_generator import MapGenerator
from .enhanced_map_generator import EnhancedMapGenerator

__version__ = "1.0.0"
__all__ = [
    "BiomeType",
    "BiomeSystem",
    "ImprovedNoiseGenerator",
    "MapGenerator",
    "EnhancedMapGenerator",
]