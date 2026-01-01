"""
Модуль тестирования - генерация заданий по разным предметам.
Использует DLL генераторы для математических тем и AI для остальных.
"""

from testing.config import GENERATORS, GeneratorType
from testing.generator_manager import GeneratorManager

__all__ = ['GENERATORS', 'GeneratorType', 'GeneratorManager']

