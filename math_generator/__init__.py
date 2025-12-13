"""
Модуль math_generator для генерации математических задач.
Использует DLL библиотеку algebra.dll для создания алгебраических примеров.
"""

from math_generator.math_generator_wrapper import (
    MathGeneratorWrapper,
    get_math_generator,
    generate_math_problem,
    is_math_generator_available,
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    DIFFICULTY_HARD,
    DIFFICULTY_MAP,
    TOPIC_TO_PROBLEM_TYPE,
    SUPPORTED_PROBLEM_TYPES
)

__all__ = [
    'MathGeneratorWrapper',
    'get_math_generator',
    'generate_math_problem',
    'is_math_generator_available',
    'DIFFICULTY_EASY',
    'DIFFICULTY_MEDIUM',
    'DIFFICULTY_HARD',
    'DIFFICULTY_MAP',
    'TOPIC_TO_PROBLEM_TYPE',
    'SUPPORTED_PROBLEM_TYPES'
]
