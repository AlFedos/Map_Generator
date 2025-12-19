"""
Статусная строка приложения
"""

import tkinter as tk
from tkinter import ttk


class StatusBar:
    """
    Класс для управления статусной строкой
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.status_label = None
        self.ml_status_label = None
        self.seed_label = None
        
        self.setup_status_bar()
    
    def setup_status_bar(self):
        """Настройка статусной строки"""
        self.frame = ttk.Frame(self.parent, height=25)
        self.frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.frame.pack_propagate(False)
        
        # Статус
        self.status_label = ttk.Label(self.frame, text="Готов к генерации...")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # ML статус
        self.ml_status_label = ttk.Label(self.frame, text="ML: ❌ не обучена")
        self.ml_status_label.pack(side=tk.LEFT, padx=10)
        
        # Seed
        self.seed_label = ttk.Label(self.frame, text="Seed: -")
        self.seed_label.pack(side=tk.RIGHT, padx=10)
    
    def set_status(self, message):
        """Установка основного статуса"""
        if self.status_label:
            self.status_label.config(text=message)
    
    def set_ml_status(self, status):
        """Установка статуса ML"""
        if self.ml_status_label:
            self.ml_status_label.config(text=f"ML: {status}")
    
    def set_seed(self, seed):
        """Установка значения seed"""
        if self.seed_label:
            self.seed_label.config(text=f"Seed: {seed}")
    
    def set_error(self, error_message):
        """Установка сообщения об ошибке"""
        if self.status_label:
            self.status_label.config(text=f"Ошибка: {error_message}")
    
    def clear(self):
        """Очистка статусной строки"""
        self.set_status("Готов к генерации...")
        self.set_ml_status("❌ не обучена")
        self.set_seed("-")