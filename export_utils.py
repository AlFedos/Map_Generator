"""
Утилиты для экспорта карт
"""

import time
from tkinter import messagebox


def export_map_to_png(terrain_data, map_gen):
    """
    Экспорт карты в PNG файл
    
    Args:
        terrain_data: данные карты
        map_gen: генератор карты
    
    Returns:
        str: имя файла
    """
    try:
        from PIL import Image, ImageDraw
        
        # Создаем изображение
        img_width = map_gen.width * 10
        img_height = map_gen.height * 10
        image = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Рисуем клетки
        for y in range(map_gen.height):
            for x in range(map_gen.width):
                elevation = terrain_data[y][x]
                
                # Определяем тип местности
                terrain_type = map_gen.classify_terrain(elevation, x, y, terrain_data)
                color = map_gen.get_terrain_color(terrain_type)
                
                # Преобразуем HEX в RGB
                if color.startswith('#'):
                    color_rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
                else:
                    color_rgb = (255, 255, 255)  # Белый по умолчанию
                
                # Координаты
                x1 = x * 10
                y1 = y * 10
                x2 = x1 + 10
                y2 = y1 + 10
                
                draw.rectangle([x1, y1, x2, y2], fill=color_rgb, outline=None)
        
        # Сохраняем файл
        filename = f"map_{int(time.time())}.png"
        image.save(filename)
        
        return filename
        
    except ImportError:
        raise ImportError(
            "Для экспорта в PNG требуется библиотека Pillow\n"
            "Установите: pip install Pillow"
        )
    except Exception as e:
        raise Exception(f"Ошибка при экспорте: {str(e)}")