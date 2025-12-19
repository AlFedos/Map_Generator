"""
Скрипт для обучения модели машинного обучения
"""

import os
import sys
import time
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent))

def main():
    """Основная функция обучения"""
    print("=" * 60)
    print("ОБУЧЕНИЕ МОДЕЛИ КЛАССИФИКАЦИИ БИОМОВ")
    print("=" * 60)
    
    try:
        from ml_biome_classifier import MLBiomeClassifier
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        print("Убедитесь, что файл ml_biome_classifier.py находится в той же директории")
        input("Нажмите Enter для выхода...")
        return
    
    # Проверяем существование директории models
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Создаем классификатор
    print("\nИнициализация ML классификатора...")
    classifier = MLBiomeClassifier(use_ml=True, auto_train=False)
    
    print("\nВыберите режим обучения:")
    print("1. Быстрое обучение (50,000 примеров, ~10-20 секунд)")
    print("2. Стандартное обучение (100,000 примеров, ~20-40 секунд)")
    print("3. Полное обучение (200,000 примеров, ~40-80 секунд)")
    print("4. Экспертное обучение (500,000 примеров, ~2-3 минуты)")
    print("5. Выход")
    
    while True:
        try:
            choice = input("\nВаш выбор (1-5): ").strip()
            
            if choice == '1':
                print("\nЗапуск быстрого обучения...")
                start_time = time.time()
                classifier.train_model(samples=50000, save=True)
                elapsed = time.time() - start_time
                print(f"\nОбучение завершено за {elapsed:.1f} секунд")
                break
                
            elif choice == '2':
                print("\nЗапуск стандартного обучения...")
                start_time = time.time()
                classifier.train_model(samples=100000, save=True)
                elapsed = time.time() - start_time
                print(f"\nОбучение завершено за {elapsed:.1f} секунд")
                break
                
            elif choice == '3':
                print("\nЗапуск полного обучения...")
                start_time = time.time()
                classifier.train_model(samples=200000, save=True)
                elapsed = time.time() - start_time
                print(f"\nОбучение завершено за {elapsed:.1f} секунд")
                break
                
            elif choice == '4':
                print("\nЗапуск экспертного обучения...")
                start_time = time.time()
                classifier.train_model(samples=500000, save=True)
                elapsed = time.time() - start_time
                print(f"\nОбучение завершено за {elapsed:.1f} секунд")
                break
                
            elif choice == '5':
                print("\nВыход...")
                sys.exit(0)
                
            else:
                print("Пожалуйста, введите число от 1 до 5")
                
        except KeyboardInterrupt:
            print("\n\nОбучение прервано пользователем")
            sys.exit(1)
        except Exception as e:
            print(f"\nОшибка при обучении: {e}")
            sys.exit(1)
    
    # Проверяем сохранение модели
    if (models_dir / "biome_rf_model.pkl").exists():
        print(f"\nМодель успешно сохранена в папке 'models/'")
        print("Теперь вы можете использовать ML классификатор в генераторе карт!")
    else:
        print("\nМодель не была сохранена. Проверьте права доступа к файлам.")
    
    print("\n" + "=" * 60)
    print("ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ:")
    print("=" * 60)
    print("1. Запустите main.py для запуска генератора карт")
    print("2. В интерфейсе включите опцию 'ML классификация'")
    print("3. Сгенерируйте новую карту - ML модель будет использоваться автоматически")
    print("4. Вы можете сравнить результаты с классификацией по правилам")


if __name__ == "__main__":
    main()