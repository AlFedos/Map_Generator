"""
Модуль машинного обучения для классификации биомов
"""

import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import time
from typing import List, Tuple, Optional
import os

from biomes import BiomeType, BiomeSystem


class MLBiomeClassifier:
    """
    Классификатор биомов на основе машинного обучения
    """
    
    def __init__(self, use_ml: bool = True, auto_train: bool = False):
        """
        Инициализация ML классификатора
        
        Args:
            use_ml: Использовать ML для классификации
            auto_train: Автоматически обучать модель, если не найдена
        """
        self.use_ml = use_ml
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.biome_system = BiomeSystem()
        self.is_trained = False
        
        if use_ml:
            self.load_model()
            if not self.is_trained and auto_train:
                print("Автоматическое обучение модели...")
                self.train_model(samples=50000, save=True)
    
    def load_model(self):
        """Загрузка обученной модели"""
        try:
            self.model = joblib.load('models/biome_rf_model.pkl')
            self.scaler = joblib.load('models/biome_scaler.pkl')
            self.label_encoder = joblib.load('models/biome_label_encoder.pkl')
            self.is_trained = True
            print("ML модель успешно загружена")
        except Exception as e:
            print(f"Не удалось загрузить модель: {e}")
            self.is_trained = False
    
    def save_model(self):
        """Сохранение обученной модели"""
        import os
        os.makedirs('models', exist_ok=True)
        
        if self.model and self.scaler and self.label_encoder:
            joblib.dump(self.model, 'models/biome_rf_model.pkl')
            joblib.dump(self.scaler, 'models/biome_scaler.pkl')
            joblib.dump(self.label_encoder, 'models/biome_label_encoder.pkl')
            print("ML модель сохранена")
    
    def generate_training_data(self, num_samples: int = 100000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Генерация тренировочных данных на основе правил
        
        Args:
            num_samples: Количество примеров для генерации
            
        Returns:
            X: Признаки (elevation, moisture, temperature, water_level, mountain_level, desert_moisture, forest_moisture)
            y: Метки классов (биомы)
        """
        print(f"Генерация {num_samples} тренировочных примеров...")
        
        X = []
        y = []
        
        # Генерируем случайные параметры
        np.random.seed(42)
        
        for i in range(num_samples):
            # Случайные параметры карты
            elevation = np.random.uniform(-1.0, 1.0)
            moisture = np.random.uniform(0.0, 1.0)
            temperature = np.random.uniform(0.0, 1.0)
            water_level = np.random.uniform(-0.8, 0.0)
            mountain_level = np.random.uniform(0.2, 0.8)
            desert_moisture = np.random.uniform(0.1, 0.5)
            forest_moisture = np.random.uniform(0.4, 0.9)
            
            # Классификация по правилам (ground truth)
            biome = self.biome_system.classify_biome(
                elevation, moisture, temperature,
                water_level, mountain_level,
                desert_moisture, forest_moisture
            )
            
            X.append([elevation, moisture, temperature,
                     water_level, mountain_level,
                     desert_moisture, forest_moisture])
            y.append(biome.value)
            
            # Прогресс
            if (i + 1) % 10000 == 0:
                print(f"  Сгенерировано {i + 1}/{num_samples} примеров")
        
        return np.array(X), np.array(y)
    
    def train_model(self, samples: int = 50000, save: bool = True, 
                   test_size: float = 0.2, random_state: int = 42):
        """
        Обучение модели классификации биомов
        
        Args:
            samples: Количество тренировочных примеров
            save: Сохранять ли модель после обучения
            test_size: Доля тестовых данных
            random_state: Seed для воспроизводимости
        """
        print("=" * 60)
        print("ОБУЧЕНИЕ МОДЕЛИ КЛАССИФИКАЦИИ БИОМОВ")
        print("=" * 60)
        
        start_time = time.time()
        
        # Генерация данных
        X, y = self.generate_training_data(num_samples=samples)
        
        # Кодирование меток
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Нормализация признаков
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Разделение на тренировочную и тестовую выборки
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded, test_size=test_size, 
            random_state=random_state, stratify=y_encoded
        )
        
        print(f"\nРазмеры данных:")
        print(f"  Всего: {len(X)} примеров")
        print(f"  Обучающая выборка: {len(X_train)} примеров")
        print(f"  Тестовая выборка: {len(X_test)} примеров")
        
        # Обучение Random Forest
        print("\nОбучение Random Forest классификатора...")
        
        # Быстрая модель для начала
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1  # Использовать все ядра
        )
        
        self.model.fit(X_train, y_train)
        
        # Оценка модели
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ ОБУЧЕНИЯ")
        print("=" * 60)
        print(f"Точность на обучающей выборке: {train_score:.4f}")
        print(f"Точность на тестовой выборке:  {test_score:.4f}")
        
        # Детальная классификация
        y_pred = self.model.predict(X_test)
        report = classification_report(y_test, y_pred, 
                                      target_names=self.label_encoder.classes_,
                                      zero_division=0)
        print("\nОтчет по классификации:\n")
        print(report)
        
        # Анализ важности признаков
        feature_names = ['Высота', 'Влажность', 'Температура', 
                        'Уровень воды', 'Уровень гор', 
                        'Пустынная влажность', 'Лесная влажность']
        
        importances = self.model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        print("\nВажность признаков:")
        for i, idx in enumerate(indices):
            print(f"  {i+1:2}. {feature_names[idx]:25} {importances[idx]:.4f}")
        
        # Время обучения
        training_time = time.time() - start_time
        print(f"\nВремя обучения: {training_time:.2f} секунд")
        
        self.is_trained = True
        
        # Сохранение модели
        if save:
            self.save_model()
    
    def predict_biome(self, elevation: float, moisture: float, temperature: float,
                     water_level: float, mountain_level: float,
                     desert_moisture: float, forest_moisture: float) -> Optional[BiomeType]:
        """
        Предсказание биома с помощью ML модели
        
        Args:
            elevation: Высота (-1.0 до 1.0)
            moisture: Влажность (0.0 до 1.0)
            temperature: Температура (0.0 до 1.0)
            water_level: Уровень воды (-0.8 до 0.0)
            mountain_level: Уровень гор (0.2 до 0.8)
            desert_moisture: Пустынная влажность (0.1 до 0.5)
            forest_moisture: Лесная влажность (0.4 до 0.9)
            
        Returns:
            BiomeType или None если модель не обучена
        """
        if not self.use_ml or not self.is_trained:
            return None
        
        try:
            # Подготовка признаков
            features = np.array([[elevation, moisture, temperature,
                                water_level, mountain_level,
                                desert_moisture, forest_moisture]])
            
            # Масштабирование
            features_scaled = self.scaler.transform(features)
            
            # Предсказание
            prediction = self.model.predict(features_scaled)[0]
            
            # Декодирование
            biome_str = self.label_encoder.inverse_transform([prediction])[0]
            
            # Преобразование в BiomeType
            for biome in BiomeType:
                if biome.value == biome_str:
                    return biome
            
            return None
            
        except Exception as e:
            print(f"Ошибка при предсказании: {e}")
            return None
        
    
    def predict_proba(self, elevation: float, moisture: float, temperature: float,
                     water_level: float, mountain_level: float,
                     desert_moisture: float, forest_moisture: float) -> Optional[np.ndarray]:
        """
        Предсказание вероятностей для каждого класса
        
        Returns:
            Массив вероятностей для каждого биома
        """
        if not self.use_ml or not self.is_trained:
            return None
        
        try:
            features = np.array([[elevation, moisture, temperature,
                                water_level, mountain_level,
                                desert_moisture, forest_moisture]])
            
            features_scaled = self.scaler.transform(features)
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            return probabilities
            
        except Exception as e:
            print(f"Ошибка при предсказании вероятностей: {e}")
            return None
    
    def evaluate_on_map(self, terrain_map: np.ndarray, moisture_map: np.ndarray,
                       temperature_map: np.ndarray, biome_map: np.ndarray,
                       water_level: float, mountain_level: float,
                       desert_moisture: float, forest_moisture: float) -> dict:
        """
        Оценка модели на сгенерированной карте
        
        Returns:
            Словарь с метриками оценки
        """
        if not self.use_ml or not self.is_trained:
            return {}
        
        height, width = terrain_map.shape
        correct = 0
        total = 0
        
        for y in range(height):
            for x in range(width):
                ml_biome = self.predict_biome(
                    terrain_map[y][x], moisture_map[y][x], temperature_map[y][x],
                    water_level, mountain_level, desert_moisture, forest_moisture
                )
                
                if ml_biome == biome_map[y][x]:
                    correct += 1
                total += 1
        
        accuracy = correct / total if total > 0 else 0
        
        return {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'percent': accuracy * 100
        }


# Функции для обучения из командной строки
def train_main():
    """Основная функция для обучения модели"""
    classifier = MLBiomeClassifier(use_ml=True, auto_train=False)
    
    print("\nВыберите действие:")
    print("1. Быстрое обучение (50k примеров)")
    print("2. Полное обучение (200k примеров)")
    print("3. Обучение с настройкой гиперпараметров")
    
    choice = input("\nВаш выбор (1-3): ").strip()
    
    if choice == '1':
        classifier.train_model(samples=50000, save=True)
    elif choice == '2':
        classifier.train_model(samples=200000, save=True)
    elif choice == '3':
        classifier.train_model(samples=100000, save=True)
        # Здесь можно добавить GridSearchCV для оптимизации
    else:
        print("Неверный выбор. Запуск быстрого обучения...")
        classifier.train_model(samples=50000, save=True)
    
    print("\nОбучение завершено!")


if __name__ == "__main__":
    train_main()