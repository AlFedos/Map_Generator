"""
Главный модуль приложения
"""

import tkinter as tk
from gui.main_window import MapGeneratorGUI


def main():
    """
    Основная функция приложения
    """
    print("=" * 60)
    print("Интеллектуальная система процедурной генерации карт")
    print("Курсовая работа по предмету 'Интеллектуальные ИС'")
    print("=" * 60)
    print()
    
    try:
        # Создаем главное окно
        root = tk.Tk()
        
        # Создаем и настраиваем интерфейс
        app = MapGeneratorGUI(root)
        
        # Запускаем главный цикл
        root.mainloop()
        
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()