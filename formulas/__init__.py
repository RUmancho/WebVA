"""
Пакет формул для физических и математических расчетов
"""

from .formula_calculator import (
    FORMULAS_DATABASE,
    get_categories,
    get_subcategories,
    get_formulas,
    calculate
)

__all__ = [
    'FORMULAS_DATABASE',
    'get_categories',
    'get_subcategories',
    'get_formulas',
    'calculate'
]

