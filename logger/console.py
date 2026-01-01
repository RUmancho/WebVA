from typing import Callable, Any, Optional
from table import *
import time


tracer = Table("reports/tracer.db",
            Unique("Function"),
               Summation("Calls"),
               Summation("Errors"),
               Minimal("Min_exe_time_sec"),
               Maximal("Max_exe_time_sec"),
               Mean("Medium_exe_time_sec"),
               Summation("CPU_time_sec"))


def debug(module: Optional[str] = None, show_args: bool = False, 
          show_time: bool = True, show_return: bool = False, tracing: bool = True) -> Callable:
    """Декоратор для отладки функций с замером времени"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            func_name = f"{module}.{func.__name__}" if module else func.__name__
            
            if show_args:
                args_str = ", ".join(repr(a) for a in args)
                kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
                calling_str = f"{func_name}({', '.join(filter(None, [args_str, kwargs_str]))})"
            else:
                calling_str = func_name
            
            try:
                start = time.perf_counter() if show_time else None
                result = func(*args, **kwargs)
                
                if show_time and start:
                    CPU_TIME = time.perf_counter() - start
                    
                    time_str = f" за {CPU_TIME:.4f} секунд"
                else:
                    time_str = ""
                
                return_str = ""
                if show_return and result is not None:
                    preview = str(result)[:47] + "..." if len(str(result)) > 50 else str(result)
                    return_str = f" --> {preview}"
                
                print(f"{calling_str} выполнена{time_str}{return_str}")
                if tracing:
                    tracer.write(Function=func_name, Calls=1, Errors=0, Min_exe_time_sec=CPU_TIME, Max_exe_time_sec=CPU_TIME, Medium_exe_time_sec=CPU_TIME, CPU_time_sec=CPU_TIME)
                return result
                
            except Exception as e:
                print(f"{calling_str} ошибка: {e}")
                if tracing:
                    tracer.write(Function=func_name, Calls=1, Errors=1, Min_exe_time_sec=CPU_TIME, Max_exe_time_sec=CPU_TIME, Medium_exe_time_sec=CPU_TIME, CPU_time_sec=CPU_TIME)
                raise

        return wrapper
    return decorator
