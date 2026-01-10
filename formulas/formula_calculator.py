# -*- coding: utf-8 -*-
"""
Калькулятор формул по математике и физике
"""

import math
import inspect

# Структура формул: категория -> подкатегория -> формулы
FORMULAS_DATABASE = {
    "Геометрия": {
        "Планиметрия и стереометрия": [
            {
                "name": "Площадь прямоугольника",
                "formula": "S = a × b",
                "fields": [
                    ("S", "Площадь", "м²"),
                    ("a", "Длина", "м"),
                    ("b", "Ширина", "м")
                ],
                "calculate": {
                    "S": lambda a, b: a * b,
                    "a": lambda S, b: S / b,
                    "b": lambda S, a: S / a
                }
            },
            {
                "name": "Площадь треугольника",
                "formula": "S = (a × h) / 2",
                "fields": [
                    ("S", "Площадь", "м²"),
                    ("a", "Основание", "м"),
                    ("h", "Высота", "м")
                ],
                "calculate": {
                    "S": lambda a, h: (a * h) / 2,
                    "a": lambda S, h: (2 * S) / h,
                    "h": lambda S, a: (2 * S) / a
                }
            },
            {
                "name": "Площадь круга",
                "formula": "S = π × r²",
                "fields": [
                    ("S", "Площадь", "м²"),
                    ("r", "Радиус", "м")
                ],
                "calculate": {
                    "S": lambda r: math.pi * r ** 2,
                    "r": lambda S: math.sqrt(S / math.pi)
                }
            },
            {
                "name": "Площадь трапеции",
                "formula": "S = ((a + b) × h) / 2",
                "fields": [
                    ("S", "Площадь", "м²"),
                    ("a", "Основание a", "м"),
                    ("b", "Основание b", "м"),
                    ("h", "Высота", "м")
                ],
                "calculate": {
                    "S": lambda a, b, h: ((a + b) * h) / 2,
                    "a": lambda S, b, h: (2 * S) / h - b,
                    "b": lambda S, a, h: (2 * S) / h - a,
                    "h": lambda S, a, b: (2 * S) / (a + b)
                }
            },
            {
                "name": "Объём куба",
                "formula": "V = a³",
                "fields": [
                    ("V", "Объём", "м³"),
                    ("a", "Ребро", "м")
                ],
                "calculate": {
                    "V": lambda a: a ** 3,
                    "a": lambda V: V ** (1/3)
                }
            },
            {
                "name": "Объём параллелепипеда",
                "formula": "V = a × b × c",
                "fields": [
                    ("V", "Объём", "м³"),
                    ("a", "Длина", "м"),
                    ("b", "Ширина", "м"),
                    ("c", "Высота", "м")
                ],
                "calculate": {
                    "V": lambda a, b, c: a * b * c,
                    "a": lambda V, b, c: V / (b * c),
                    "b": lambda V, a, c: V / (a * c),
                    "c": lambda V, a, b: V / (a * b)
                }
            },
            {
                "name": "Объём цилиндра",
                "formula": "V = π × r² × h",
                "fields": [
                    ("V", "Объём", "м³"),
                    ("r", "Радиус", "м"),
                    ("h", "Высота", "м")
                ],
                "calculate": {
                    "V": lambda r, h: math.pi * r ** 2 * h,
                    "r": lambda V, h: math.sqrt(V / (math.pi * h)),
                    "h": lambda V, r: V / (math.pi * r ** 2)
                }
            },
            {
                "name": "Объём шара",
                "formula": "V = (4/3) × π × r³",
                "fields": [
                    ("V", "Объём", "м³"),
                    ("r", "Радиус", "м")
                ],
                "calculate": {
                    "V": lambda r: (4/3) * math.pi * r ** 3,
                    "r": lambda V: ((3 * V) / (4 * math.pi)) ** (1/3)
                }
            },
            {
                "name": "Площадь поверхности куба",
                "formula": "S = 6 × a²",
                "fields": [
                    ("S", "Площадь", "м²"),
                    ("a", "Ребро", "м")
                ],
                "calculate": {
                    "S": lambda a: 6 * a ** 2,
                    "a": lambda S: math.sqrt(S / 6)
                }
            },
            {
                "name": "Площадь поверхности цилиндра",
                "formula": "S = 2πr(r + h)",
                "fields": [
                    ("S", "Площадь", "м²"),
                    ("r", "Радиус", "м"),
                    ("h", "Высота", "м")
                ],
                "calculate": {
                    "S": lambda r, h: 2 * math.pi * r * (r + h),
                    "r": lambda S, h: (math.sqrt(h**2 + S/math.pi) - h) / 2,
                    "h": lambda S, r: (S / (2 * math.pi * r)) - r
                }
            }
        ]
    },
    "Алгебра": {
        "Основы алгебры": [
            {
                "name": "Процент от числа",
                "formula": "A = (N × P) / 100",
                "fields": [
                    ("A", "Результат", ""),
                    ("N", "Число", ""),
                    ("P", "Процент", "%")
                ],
                "calculate": {
                    "A": lambda N, P: (N * P) / 100,
                    "N": lambda A, P: (A * 100) / P,
                    "P": lambda A, N: (A * 100) / N
                }
            },
            {
                "name": "Квадрат суммы",
                "formula": "(a + b)² = a² + 2ab + b²",
                "fields": [
                    ("result", "Результат", ""),
                    ("a", "Первое число", ""),
                    ("b", "Второе число", "")
                ],
                "calculate": {
                    "result": lambda a, b: a**2 + 2*a*b + b**2
                }
            },
            {
                "name": "Квадрат разности",
                "formula": "(a - b)² = a² - 2ab + b²",
                "fields": [
                    ("result", "Результат", ""),
                    ("a", "Первое число", ""),
                    ("b", "Второе число", "")
                ],
                "calculate": {
                    "result": lambda a, b: a**2 - 2*a*b + b**2
                }
            },
            {
                "name": "Разность квадратов",
                "formula": "a² - b² = (a - b)(a + b)",
                "fields": [
                    ("result", "Результат", ""),
                    ("a", "Первое число", ""),
                    ("b", "Второе число", "")
                ],
                "calculate": {
                    "result": lambda a, b: a**2 - b**2
                }
            },
            {
                "name": "Среднее арифметическое",
                "formula": "Средняя = (a + b) / 2",
                "fields": [
                    ("avg", "Среднее", ""),
                    ("a", "Первое число", ""),
                    ("b", "Второе число", "")
                ],
                "calculate": {
                    "avg": lambda a, b: (a + b) / 2,
                    "a": lambda avg, b: 2 * avg - b,
                    "b": lambda avg, a: 2 * avg - a
                }
            },
            {
                "name": "Линейное уравнение",
                "formula": "y = kx + b",
                "fields": [
                    ("y", "Значение y", ""),
                    ("k", "Коэффициент k", ""),
                    ("x", "Значение x", ""),
                    ("b", "Свободный член", "")
                ],
                "calculate": {
                    "y": lambda k, x, b: k * x + b,
                    "k": lambda y, x, b: (y - b) / x,
                    "x": lambda y, k, b: (y - b) / k,
                    "b": lambda y, k, x: y - k * x
                }
            },
            {
                "name": "Степень числа",
                "formula": "result = a^n",
                "fields": [
                    ("result", "Результат", ""),
                    ("a", "Основание", ""),
                    ("n", "Степень", "")
                ],
                "calculate": {
                    "result": lambda a, n: a ** n,
                    "a": lambda result, n: result ** (1/n)
                }
            },
            {
                "name": "Корень квадратный",
                "formula": "x = √a",
                "fields": [
                    ("x", "Корень", ""),
                    ("a", "Число", "")
                ],
                "calculate": {
                    "x": lambda a: math.sqrt(a),
                    "a": lambda x: x ** 2
                }
            }
        ]
    },
    "Физика": {
        "Механика": [
            {
                "name": "Скорость",
                "formula": "v = S / t",
                "fields": [
                    ("v", "Скорость", "м/с"),
                    ("S", "Путь", "м"),
                    ("t", "Время", "с")
                ],
                "calculate": {
                    "v": lambda S, t: S / t,
                    "S": lambda v, t: v * t,
                    "t": lambda S, v: S / v
                }
            },
            {
                "name": "Ускорение",
                "formula": "a = (v - v₀) / t",
                "fields": [
                    ("a", "Ускорение", "м/с²"),
                    ("v", "Конечная скорость", "м/с"),
                    ("v0", "Начальная скорость", "м/с"),
                    ("t", "Время", "с")
                ],
                "calculate": {
                    "a": lambda v, v0, t: (v - v0) / t,
                    "v": lambda a, v0, t: v0 + a * t,
                    "v0": lambda v, a, t: v - a * t,
                    "t": lambda v, v0, a: (v - v0) / a
                }
            },
            {
                "name": "Второй закон Ньютона",
                "formula": "F = m × a",
                "fields": [
                    ("F", "Сила", "Н"),
                    ("m", "Масса", "кг"),
                    ("a", "Ускорение", "м/с²")
                ],
                "calculate": {
                    "F": lambda m, a: m * a,
                    "m": lambda F, a: F / a,
                    "a": lambda F, m: F / m
                }
            },
            {
                "name": "Импульс",
                "formula": "p = m × v",
                "fields": [
                    ("p", "Импульс", "кг·м/с"),
                    ("m", "Масса", "кг"),
                    ("v", "Скорость", "м/с")
                ],
                "calculate": {
                    "p": lambda m, v: m * v,
                    "m": lambda p, v: p / v,
                    "v": lambda p, m: p / m
                }
            },
            {
                "name": "Кинетическая энергия",
                "formula": "E = (m × v²) / 2",
                "fields": [
                    ("E", "Энергия", "Дж"),
                    ("m", "Масса", "кг"),
                    ("v", "Скорость", "м/с")
                ],
                "calculate": {
                    "E": lambda m, v: (m * v ** 2) / 2,
                    "m": lambda E, v: (2 * E) / (v ** 2),
                    "v": lambda E, m: math.sqrt((2 * E) / m)
                }
            },
            {
                "name": "Потенциальная энергия",
                "formula": "E = m × g × h",
                "fields": [
                    ("E", "Энергия", "Дж"),
                    ("m", "Масса", "кг"),
                    ("g", "Ускорение свободного падения", "м/с²"),
                    ("h", "Высота", "м")
                ],
                "calculate": {
                    "E": lambda m, g, h: m * g * h,
                    "m": lambda E, g, h: E / (g * h),
                    "g": lambda E, m, h: E / (m * h),
                    "h": lambda E, m, g: E / (m * g)
                }
            }
        ],
        "Электричество": [
            {
                "name": "Закон Ома",
                "formula": "I = U / R",
                "fields": [
                    ("I", "Сила тока", "А"),
                    ("U", "Напряжение", "В"),
                    ("R", "Сопротивление", "Ом")
                ],
                "calculate": {
                    "I": lambda U, R: U / R,
                    "U": lambda I, R: I * R,
                    "R": lambda U, I: U / I
                }
            },
            {
                "name": "Мощность электрического тока",
                "formula": "P = U × I",
                "fields": [
                    ("P", "Мощность", "Вт"),
                    ("U", "Напряжение", "В"),
                    ("I", "Сила тока", "А")
                ],
                "calculate": {
                    "P": lambda U, I: U * I,
                    "U": lambda P, I: P / I,
                    "I": lambda P, U: P / U
                }
            },
            {
                "name": "Работа электрического тока",
                "formula": "A = P × t",
                "fields": [
                    ("A", "Работа", "Дж"),
                    ("P", "Мощность", "Вт"),
                    ("t", "Время", "с")
                ],
                "calculate": {
                    "A": lambda P, t: P * t,
                    "P": lambda A, t: A / t,
                    "t": lambda A, P: A / P
                }
            },
            {
                "name": "Закон Джоуля-Ленца",
                "formula": "Q = I² × R × t",
                "fields": [
                    ("Q", "Количество теплоты", "Дж"),
                    ("I", "Сила тока", "А"),
                    ("R", "Сопротивление", "Ом"),
                    ("t", "Время", "с")
                ],
                "calculate": {
                    "Q": lambda I, R, t: I ** 2 * R * t,
                    "I": lambda Q, R, t: math.sqrt(Q / (R * t)),
                    "R": lambda Q, I, t: Q / (I ** 2 * t),
                    "t": lambda Q, I, R: Q / (I ** 2 * R)
                }
            }
        ],
        "Оптика": [
            {
                "name": "Формула тонкой линзы",
                "formula": "1/F = 1/d + 1/f",
                "fields": [
                    ("F", "Фокусное расстояние", "м"),
                    ("d", "Расстояние до предмета", "м"),
                    ("f", "Расстояние до изображения", "м")
                ],
                "calculate": {
                    "F": lambda d, f: (d * f) / (d + f),
                    "d": lambda F, f: (F * f) / (f - F),
                    "f": lambda F, d: (F * d) / (d - F)
                }
            }
        ]
    }
}


def get_categories():
    """Получить список категорий"""
    return list(FORMULAS_DATABASE.keys())


def get_subcategories(category):
    """Получить подкатегории для категории"""
    return list(FORMULAS_DATABASE.get(category, {}).keys())


def get_formulas(category, subcategory):
    """Получить формулы для подкатегории"""
    return FORMULAS_DATABASE.get(category, {}).get(subcategory, [])


def calculate(formula_name, category, subcategory, values, target):
    """
    Вычислить неизвестную величину
    
    Args:
        formula_name: Название формулы
        category: Категория
        subcategory: Подкатегория
        values: Словарь с известными значениями
        target: Неизвестная величина
    
    Returns:
        float: Результат вычисления
    """
    try:
        formulas = get_formulas(category, subcategory)
        formula = next((f for f in formulas if f["name"] == formula_name), None)
        
        if not formula:
            raise ValueError(f"Формула '{formula_name}' не найдена")
        
        if target not in formula["calculate"]:
            raise ValueError(f"Невозможно найти '{target}' для этой формулы")
        
        calc_func = formula["calculate"][target]
        
        # Получаем необходимые параметры функции
        params = inspect.signature(calc_func).parameters.keys()
        
        # Проверяем, что все параметры предоставлены
        missing = [p for p in params if p not in values]
        if missing:
            raise ValueError(f"Недостаточно данных. Отсутствуют: {', '.join(missing)}")
        
        # Вызываем функцию с нужными параметрами
        args = [values[p] for p in params]
        result = calc_func(*args)
        
        return result
    
    except ZeroDivisionError:
        raise ValueError("Деление на ноль! Проверьте введённые значения")
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise ValueError(f"Ошибка вычисления: {str(e)}")

