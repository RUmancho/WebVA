"""
Обёртка для математического генератора.
Использует DLL библиотеку algebra.dll для создания алгебраических примеров.
"""

import os
import sys
import random
from typing import Optional, Dict, Any
from math import gcd

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from logger import console

PYTHON_FILENAME = "math_generator"

# Константы сложности
DIFFICULTY_EASY = 1
DIFFICULTY_MEDIUM = 2
DIFFICULTY_HARD = 3

DIFFICULTY_MAP = {
    "Лёгкий": DIFFICULTY_EASY,
    "Средний": DIFFICULTY_MEDIUM,
    "Хардкор": DIFFICULTY_HARD,
    "easy": DIFFICULTY_EASY,
    "medium": DIFFICULTY_MEDIUM,
    "hard": DIFFICULTY_HARD,
}

# Поддерживаемые типы задач
SUPPORTED_PROBLEM_TYPES = [
    "linear_equation",
    "quadratic_equation",
    "fraction_addition",
    "fraction_multiplication",
    "power_calculation",
    "root_calculation",
]

# Маппинг тем к типам задач
TOPIC_TO_PROBLEM_TYPE = {
    "Линейные уравнения": "linear_equation",
    "Квадратные уравнения": "quadratic_equation",
    "Дроби": "fraction_addition",
    "Степени": "power_calculation",
    "Корни": "root_calculation",
}


class MathGeneratorWrapper:
    """Обёртка для математического генератора."""
    
    def __init__(self):
        self.dll = None
        self.ffi = None
        self.dll_available = False
        self._init_dll()
    
    @console.debug(PYTHON_FILENAME)
    def _init_dll(self):
        """Инициализация DLL библиотеки."""
        try:
            import cffi
            
            dll_path = os.path.join(os.path.dirname(__file__), "algebra.dll")
            header_path = os.path.join(os.path.dirname(__file__), "algebra.h")
            
            if not os.path.exists(dll_path):
                return
            
            if not os.path.exists(header_path):
                return
            
            self.ffi = cffi.FFI()
            
            with open(header_path, "r", encoding="utf-8") as f:
                self.ffi.cdef(f.read())
            
            self.dll = self.ffi.dlopen(dll_path)
            self.dll_available = True
            
        except ImportError:
            pass
        except Exception:
            pass
    
    @console.debug(PYTHON_FILENAME)
    def _string_from_c(self, c_string) -> str:
        """Преобразование C-строки в Python строку."""
        if not self.ffi or c_string == self.ffi.NULL:
            return ""
        
        try:
            py_string = self.ffi.string(c_string).decode('utf-8')
            
            if hasattr(self.dll, 'free_string'):
                self.dll.free_string(c_string)
            
            return py_string
        except Exception:
            return ""
    
    @console.debug(PYTHON_FILENAME)
    def is_topic_supported(self, topic: str) -> bool:
        """Проверка поддержки темы."""
        return topic in TOPIC_TO_PROBLEM_TYPE
    
    @console.debug(PYTHON_FILENAME)
    def generate_problem_by_topic(self, topic: str, difficulty: str = "Средний") -> Optional[Dict[str, Any]]:
        """
        Генерация задачи по теме.
        
        Args:
            topic: Название темы
            difficulty: Уровень сложности
        
        Returns:
            Dict с вопросом и ответом или None
        """
        problem_type = TOPIC_TO_PROBLEM_TYPE.get(topic)
        if not problem_type:
            return None
        
        diff_level = DIFFICULTY_MAP.get(difficulty, DIFFICULTY_MEDIUM)
        
        return self.generate_problem(problem_type, diff_level)
    
    @console.debug(PYTHON_FILENAME)
    def generate_problem(self, problem_type: str, difficulty: int = DIFFICULTY_MEDIUM) -> Optional[Dict[str, Any]]:
        """
        Генерация математической задачи.
        
        Args:
            problem_type: Тип задачи
            difficulty: Уровень сложности (1-3)
        
        Returns:
            Dict с вопросом и ответом
        """
        if self.dll_available:
            return self._generate_with_dll(problem_type, difficulty)
        
        return self._generate_fallback(problem_type, difficulty)
    
    @console.debug(PYTHON_FILENAME)
    def _generate_with_dll(self, problem_type: str, difficulty: int) -> Optional[Dict[str, Any]]:
        """Генерация через DLL."""
        try:
            if problem_type == "linear_equation":
                if hasattr(self.dll, 'equation_linear'):
                    result = self._string_from_c(self.dll.equation_linear(difficulty))
                    if result:
                        parts = result.split('|')
                        if len(parts) >= 2:
                            return {"question": f"Решите: {parts[0]}", "correct_answer": parts[1]}
            
            elif problem_type == "quadratic_equation":
                if hasattr(self.dll, 'equation_quadratic'):
                    result = self._string_from_c(self.dll.equation_quadratic(difficulty))
                    if result:
                        parts = result.split('|')
                        if len(parts) >= 2:
                            return {"question": f"Решите: {parts[0]}", "correct_answer": parts[1]}
            
        except Exception as e:
            print(f"[ERROR] Ошибка DLL генерации: {e}")
        
        return self._generate_fallback(problem_type, difficulty)
    
    @console.debug(PYTHON_FILENAME)
    def _generate_fallback(self, problem_type: str, difficulty: int) -> Dict[str, Any]:
        """Fallback генерация на Python."""
        if problem_type == "linear_equation":
            return self._generate_linear_equation(difficulty)
        elif problem_type == "quadratic_equation":
            return self._generate_quadratic_equation(difficulty)
        elif problem_type == "fraction_addition":
            return self._generate_fraction(difficulty)
        elif problem_type == "power_calculation":
            return self._generate_power(difficulty)
        elif problem_type == "root_calculation":
            return self._generate_root(difficulty)
        
        return self._generate_linear_equation(difficulty)
    
    @console.debug(PYTHON_FILENAME)
    def _generate_linear_equation(self, difficulty: int) -> Dict[str, Any]:
        """Генерация линейного уравнения."""
        if difficulty == DIFFICULTY_EASY:
            a = random.randint(1, 5)
            x = random.randint(1, 10)
            b = a * x
            return {"question": f"Решите: {a}x = {b}", "correct_answer": f"x = {x}"}
        elif difficulty == DIFFICULTY_MEDIUM:
            a = random.randint(2, 10)
            x = random.randint(-10, 10)
            b = random.randint(1, 20)
            c = a * x + b
            return {"question": f"Решите: {a}x + {b} = {c}", "correct_answer": f"x = {x}"}
        else:
            a = random.randint(2, 10)
            d = random.randint(2, 10)
            x = random.randint(-10, 10)
            b = random.randint(1, 20)
            c = random.randint(1, 20)
            return {"question": f"Решите: {a}x + {b} = {d}x + {c}", "correct_answer": f"x = {x}"}
    
    @console.debug(PYTHON_FILENAME)
    def _generate_quadratic_equation(self, difficulty: int) -> Dict[str, Any]:
        """Генерация квадратного уравнения."""
        x1 = random.randint(1, 5)
        x2 = random.randint(-5, 5)
        b = -(x1 + x2)
        c = x1 * x2
        
        equation = f"x² "
        if b > 0:
            equation += f"+ {b}x "
        elif b < 0:
            equation += f"- {-b}x "
        
        if c > 0:
            equation += f"+ {c} = 0"
        elif c < 0:
            equation += f"- {-c} = 0"
        else:
            equation += "= 0"
        
        if x1 == x2:
            answer = f"x = {x1}"
        else:
            answer = f"x₁ = {min(x1, x2)}, x₂ = {max(x1, x2)}"
        
        return {"question": f"Решите: {equation}", "correct_answer": answer}
    
    @console.debug(PYTHON_FILENAME)
    def _generate_fraction(self, difficulty: int) -> Dict[str, Any]:
        """Генерация задачи на дроби."""
        a = random.randint(1, 5)
        b = random.randint(2, 10)
        c = random.randint(1, 5)
        d = random.randint(2, 10)
        
        # a/b + c/d
        numerator = a * d + c * b
        denominator = b * d
        
        # Упрощаем
        g = gcd(numerator, denominator)
        numerator //= g
        denominator //= g
        
        if denominator == 1:
            answer = str(numerator)
        else:
            answer = f"{numerator}/{denominator}"
        
        return {"question": f"Вычислите: {a}/{b} + {c}/{d}", "correct_answer": answer}
    
    @console.debug(PYTHON_FILENAME)
    def _generate_power(self, difficulty: int) -> Dict[str, Any]:
        """Генерация задачи на степени."""
        base = random.randint(2, 5)
        exp = random.randint(2, 4)
        result = base ** exp
        
        return {"question": f"Вычислите: {base}^{exp}", "correct_answer": str(result)}
    
    @console.debug(PYTHON_FILENAME)
    def _generate_root(self, difficulty: int) -> Dict[str, Any]:
        """Генерация задачи на корни."""
        answer = random.randint(2, 12)
        number = answer ** 2
        
        return {"question": f"Вычислите: √{number}", "correct_answer": str(answer)}


# Глобальный экземпляр
_generator_instance = None


@console.debug(PYTHON_FILENAME)
def get_math_generator() -> MathGeneratorWrapper:
    """Получить экземпляр генератора."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = MathGeneratorWrapper()
    return _generator_instance


@console.debug(PYTHON_FILENAME)
def generate_math_problem(problem_type: str, difficulty: int = DIFFICULTY_MEDIUM) -> Optional[Dict[str, Any]]:
    """Сгенерировать математическую задачу."""
    return get_math_generator().generate_problem(problem_type, difficulty)


@console.debug(PYTHON_FILENAME)
def is_math_generator_available() -> bool:
    """Проверить доступность DLL генератора."""
    return get_math_generator().dll_available
