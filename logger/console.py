import colorama
import time
import functools
from typing import Any, Callable, Optional

colorama.init()

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

