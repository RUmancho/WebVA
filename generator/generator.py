import os
import sys

# Настройка путей
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from LibraryManager import loader

GENERATOR_DIR = os.path.dirname(os.path.abspath(__file__))
ALGEBRA_DLL = loader.Library("algebra", os.path.join(GENERATOR_DIR, "algebra.h"), GENERATOR_DIR)

def string_handler(method):
    def wrapper(cls, *args, **kwargs):
        char_ptr = method(cls, *args, **kwargs)
        if char_ptr == cls.FFI.NULL:
            return ""
        
        try:
            return cls.FFI.string(char_ptr).decode("utf-8")
        finally:
            cls.library.free_string(char_ptr)
    return wrapper


class Algebra:
    library = ALGEBRA_DLL.lib
    FFI = ALGEBRA_DLL.ffi

    @classmethod
    @string_handler
    def linear_equation(cls, difficulty):
        return cls.library.linear_equation(difficulty)

    @classmethod
    @string_handler
    def quadratic_equation(cls, difficulty):
        return cls.library.quadratic_equation(difficulty)

    @classmethod
    @string_handler
    def exponential_equation(cls, difficulty):
        return cls.library.exponential_equation(difficulty)

    @classmethod
    @string_handler
    def linear_inequality(cls, difficulty):
        return cls.library.linear_inequality(difficulty)

    @classmethod
    @string_handler
    def quadratic_inequality(cls, difficulty):
        return cls.library.quadratic_inequality(difficulty)