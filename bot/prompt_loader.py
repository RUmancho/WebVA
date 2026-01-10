"""
Сервис загрузки промптов из файлов.
Отвечает только за чтение файлов и кэширование.
"""

import os
import sys
from typing import Optional, Dict
from functools import lru_cache

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from logger import console
from logger.tracer import trace

PYTHON_FILENAME = "prompt_loader"


class PromptLoaderError(Exception):
    """Ошибка загрузки промпта."""
    pass


class PromptLoader:
    """
    Сервис загрузки промптов из файлов.
    
    Обеспечивает:
    - Чтение файлов с промптами
    - Кэширование загруженных промптов
    - Обработку ошибок
    """
    
    _cache: Dict[str, str] = {}
    
    @classmethod
    @trace
    def load(cls, filepath: str) -> str:
        """
        Загружает содержимое файла промпта.
        
        Args:
            filepath: Путь к файлу
            
        Returns:
            str: Содержимое файла
            
        Raises:
            PromptLoaderError: Если файл не найден или не читается
        """
        # Проверяем кэш
        if filepath in cls._cache:
            return cls._cache[filepath]
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                cls._cache[filepath] = content
                return content
        except FileNotFoundError:
            print(f"[ERROR] Файл промпта не найден: {filepath}")
            raise PromptLoaderError(f"Файл не найден: {filepath}")
        except PermissionError:
            print(f"[ERROR] Нет доступа к файлу: {filepath}")
            raise PromptLoaderError(f"Нет доступа к файлу: {filepath}")
        except Exception as e:
            print(f"[ERROR] Ошибка чтения файла {filepath}: {e}")
            raise PromptLoaderError(f"Ошибка чтения: {e}")
    
    @classmethod
    @trace
    def load_safe(cls, filepath: str, default: str = "") -> str:
        """
        Безопасная загрузка промпта (без исключений).
        
        Args:
            filepath: Путь к файлу
            default: Значение по умолчанию при ошибке
            
        Returns:
            str: Содержимое файла или default
        """
        try:
            return cls.load(filepath)
        except PromptLoaderError:
            return default
    
    @classmethod
    @trace
    def load_with_params(cls, filepath: str, **kwargs) -> str:
        """
        Загружает промпт и подставляет параметры.
        
        Args:
            filepath: Путь к файлу
            **kwargs: Параметры для подстановки
            
        Returns:
            str: Промпт с подставленными параметрами
        """
        template = cls.load(filepath)
        
        if kwargs and "{" in template and "}" in template:
            try:
                return template.format(**kwargs)
            except KeyError as e:
                print(f"[WARN] Отсутствует параметр в {filepath}: {e}")
                return template
        
        return template
    
    @classmethod
    def clear_cache(cls) -> None:
        """Очищает кэш загруженных промптов."""
        cls._cache.clear()
    
    @classmethod
    def preload(cls, filepaths: list) -> Dict[str, str]:
        """
        Предзагрузка нескольких промптов.
        
        Args:
            filepaths: Список путей к файлам
            
        Returns:
            Dict[str, str]: Словарь {путь: содержимое}
        """
        result = {}
        for path in filepaths:
            try:
                result[path] = cls.load(path)
            except PromptLoaderError:
                result[path] = ""
        return result
    
    @classmethod
    def exists(cls, filepath: str) -> bool:
        """Проверяет существование файла промпта."""
        return os.path.isfile(filepath)


# Удобные функции-обёртки для прямого импорта
def load_prompt(filepath: str) -> str:
    """Загружает промпт из файла."""
    return PromptLoader.load(filepath)


def load_prompt_safe(filepath: str, default: str = "") -> str:
    """Безопасно загружает промпт из файла."""
    return PromptLoader.load_safe(filepath, default)


def load_prompt_with_params(filepath: str, **kwargs) -> str:
    """Загружает промпт с подстановкой параметров."""
    return PromptLoader.load_with_params(filepath, **kwargs)
