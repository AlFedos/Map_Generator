"""
Модуль генерации шума Перлина для процедурной генерации
"""

import numpy as np
import random
import math
from typing import Optional, List, Tuple


class ImprovedNoiseGenerator:
    """
    Улучшенный генератор шума для более естественных карт
    """
    
    @staticmethod
    def perlin_noise(width: int, height: int, scale: float = 8.0, 
                     octaves: int = 4, persistence: float = 0.5, 
                     lacunarity: float = 2.0, seed: Optional[int] = None) -> np.ndarray:
        """
        Генерация шума Перлина с несколькими октавами
        """
        if scale <= 0:
            scale = 0.0001
        
        base_noise = np.zeros((height, width))
        
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        
        gradients = []
        for _ in range(256):
            angle = np.random.uniform(0, 2 * math.pi)
            gradients.append((math.cos(angle), math.sin(angle)))
        
        def noise(x: float, y: float) -> float:
            x0 = int(x)
            x1 = x0 + 1
            y0 = int(y)
            y1 = y0 + 1
            
            sx = x - x0
            sy = y - y0
            
            n0 = ImprovedNoiseGenerator.dot_grid_gradient(gradients, x0, y0, x, y)
            n1 = ImprovedNoiseGenerator.dot_grid_gradient(gradients, x1, y0, x, y)
            ix0 = ImprovedNoiseGenerator.interpolate(n0, n1, sx)
            
            n0 = ImprovedNoiseGenerator.dot_grid_gradient(gradients, x0, y1, x, y)
            n1 = ImprovedNoiseGenerator.dot_grid_gradient(gradients, x1, y1, x, y)
            ix1 = ImprovedNoiseGenerator.interpolate(n0, n1, sx)
            
            value = ImprovedNoiseGenerator.interpolate(ix0, ix1, sy)
            return value
        
        for y in range(height):
            for x in range(width):
                amplitude = 1.0
                frequency = 1.0
                value = 0.0
                max_value = 0.0
                
                for _ in range(octaves):
                    sample_x = x / scale * frequency
                    sample_y = y / scale * frequency
                    perlin_value = noise(sample_x, sample_y)
                    value += perlin_value * amplitude
                    
                    max_value += amplitude
                    amplitude *= persistence
                    frequency *= lacunarity
                
                if max_value > 0:
                    value /= max_value
                
                base_noise[y][x] = value
        
        min_val = np.min(base_noise)
        max_val = np.max(base_noise)
        if max_val > min_val:
            base_noise = (base_noise - min_val) / (max_val - min_val)
        
        return base_noise
    
    @staticmethod
    def dot_grid_gradient(gradients, ix: int, iy: int, x: float, y: float) -> float:
        gradient_idx = ImprovedNoiseGenerator.hash(ix, iy) % len(gradients)
        gradient = gradients[gradient_idx]
        dx = x - ix
        dy = y - iy
        return dx * gradient[0] + dy * gradient[1]
    
    @staticmethod
    def interpolate(a: float, b: float, t: float) -> float:
        ft = t * math.pi
        f = (1 - math.cos(ft)) * 0.5
        return a * (1 - f) + b * f
    
    @staticmethod
    def hash(x: int, y: int) -> int:
        return (x * 1836311903) ^ (y * 2971215073 + 123456789)