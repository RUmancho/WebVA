import colorama
import time
import functools
from typing import Any, Callable, Optional

colorama.init()


import sys
import inspect
from typing import Dict, Any
import pympler.asizeof

# Глобальный словарь для хранения результатов по модулям
_module_memory_usage: Dict[str, int] = {}

def track_global_memory(func):
    """
    Декоратор для отслеживания памяти глобальных переменных модуля, 
    где используется декорируемая функция.
    """
    def wrapper(*args, **kwargs):
        # Получаем модуль, в котором определена функция
        module_name = func.__module__
        module = sys.modules.get(module_name)
        
        if module:
            # Считаем общую память глобальных переменных модуля
            module_globals = module.__dict__
            
            # Фильтруем только "пользовательские" глобальные переменные
            # Исключаем служебные переменные (начинающиеся с _)
            user_globals = {
                k: v for k, v in module_globals.items() 
                if not k.startswith('_') or k == '__name__'
            }
            
            # Рекурсивно вычисляем общий размер памяти
            total_memory = 0
            seen_ids = set()  # Для отслеживания уже посчитанных объектов
            
            for var_name, var_value in user_globals.items():
                # Исключаем сам декоратор и модули из подсчета
                if (var_name == 'track_global_memory' or 
                    var_name == '__file__' or 
                    isinstance(var_value, type(sys))):
                    continue
                
                # Используем pympler.asizeof для рекурсивного подсчета
                total_memory += pympler.asizeof.asizeof(var_value)
            
            # Обновляем глобальный словарь
            _module_memory_usage[module_name] = total_memory
            
            # Выводим информацию
            print(f"\nМодуль: {module_name}")
            print(f"Память глобальных переменных: {total_memory:,} байт")
            print(f"Общая память всех отслеживаемых модулей: {sum(_module_memory_usage.values()):,} байт")
            
            # Сохраняем в глобальную переменную модуля для доступа извне
            module._module_memory = total_memory
        
        # Вызываем оригинальную функцию
        return func(*args, **kwargs)
    
    return wrapper

def get_total_memory() -> int:
    """Возвращает общее потребление памяти всеми отслеживаемыми модулями."""
    return sum(_module_memory_usage.values())

def get_module_memory(module_name: str) -> int:
    """Возвращает потребление памяти конкретного модуля."""
    return _module_memory_usage.get(module_name, 0)

def get_all_modules_memory() -> Dict[str, int]:
    """Возвращает словарь с памятью всех отслеживаемых модулей."""
    return _module_memory_usage.copy()




def debug(
    module: Optional[str] = None,
    slow_threshold: float = 1.0,
    show_args: bool = True,
    show_time: bool = True,
    show_return: bool = False
) -> Callable:
    """
    Декоратор для отладки функций с замером времени выполнения
    
    Args:
        module: Префикс модуля для вывода
        slow_threshold: Порог времени (сек) для предупреждения о медленном выполнении
        show_args: Показывать аргументы функции
        show_time: Показывать время выполнения
        show_return: Показывать возвращаемое значение
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            func_name = f"{module}.{func.__name__}" if module else func.__name__
            
            if show_args:
                args_str = ", ".join(repr(a) for a in args)
                kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
                all_args = ", ".join(filter(None, [args_str, kwargs_str]))
                calling_str = f"{func_name}({all_args})"
            else:
                calling_str = func_name
            
            colored_calling = f"{colorama.Fore.CYAN}{calling_str}"
            
            try:
                start_time = time.perf_counter() if show_time else None
                result = func(*args, **kwargs)
                
                if show_time and start_time:
                    execution_time = time.perf_counter() - start_time
                    
                    if execution_time >= slow_threshold:
                        time_color = colorama.Fore.YELLOW
                    else:
                        time_color = colorama.Fore.GREEN
                    
                    time_str = f" за {time_color}{execution_time:.6f}{colorama.Fore.GREEN} секунд"
                else:
                    time_str = ""
                
                return_info = ""
                if show_return and result is not None:
                    result_preview = str(result)
                    if len(result_preview) > 50:
                        result_preview = result_preview[:47] + "..."
                    return_info = f" --> {colorama.Fore.MAGENTA}{result_preview}"
                
                success_msg = f"{colored_calling}{colorama.Fore.GREEN} выполнена{time_str}{return_info}"
                print(f"{success_msg}{colorama.Style.RESET_ALL}")
                
                return result
                
            except Exception as e:
                error_msg = f"{colored_calling}{colorama.Fore.RED} ошибка: {e}"
                print(f"{error_msg}{colorama.Style.RESET_ALL}")
                raise
        
        return wrapper
    return decorator

