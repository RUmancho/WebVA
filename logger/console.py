import functools
import time
import colorama
from typing import Callable, Any, Optional, Dict, List, Tuple
import atexit
import os
from collections import defaultdict
from dataclasses import dataclass
import json
from datetime import datetime
import threading

from rich.console import Console as RichConsole
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

# Инициализация colorama и rich
colorama.init()
rich_console = RichConsole()


@dataclass
class FunctionProfile:
    """Данные профилирования для одной функции"""
    name: str
    total_time: float = 0.0
    call_count: int = 0
    min_time: float = float('inf')
    max_time: float = 0.0
    
    def add_call(self, execution_time: float):
        """Добавляет данные о вызове функции"""
        self.total_time += execution_time
        self.call_count += 1
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)
    
    @property
    def avg_time(self) -> float:
        """Среднее время выполнения"""
        return self.total_time / self.call_count if self.call_count > 0 else 0.0
    
    def to_dict(self) -> dict:
        """Преобразует в словарь для сериализации"""
        return {
            'name': self.name,
            'total_time': self.total_time,
            'call_count': self.call_count,
            'avg_time': self.avg_time,
            'min_time': self.min_time if self.min_time != float('inf') else 0.0,
            'max_time': self.max_time
        }


class Profiler:
    """Класс для управления профилированием и сохранением данных"""
    
    _instance = None
    _lock = threading.Lock()
    
    # Директория tracing в корне проекта
    TRACING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tracing")
    
    def __new__(cls):
        """Реализация синглтона"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Инициализация профайлера"""
        if not hasattr(self, '_initialized') or not self._initialized:
            self._data = defaultdict(lambda: defaultdict(FunctionProfile))
            self._global_lock = threading.Lock()
            self._save_registered = False
            self._enabled = True
            self._save_directory = self.TRACING_DIR
            self._call_count = 0
            self._save_interval = 10  # Сохранять каждые N вызовов
            self._last_save_time = time.time()
            self._save_time_interval = 30  # Или каждые N секунд
            os.makedirs(self._save_directory, exist_ok=True)
            self._initialized = True
            # Автоматически регистрируем сохранение при выходе
            self.register_exit_handler()
    
    def enable(self) -> None:
        """Включает сбор статистики"""
        self._enabled = True
    
    def disable(self) -> None:
        """Выключает сбор статистики"""
        self._enabled = False
    
    def is_enabled(self) -> bool:
        """Проверяет, включен ли сбор статистики"""
        return self._enabled
    
    def set_save_directory(self, directory: str) -> None:
        """Устанавливает директорию для сохранения файлов"""
        os.makedirs(directory, exist_ok=True)
        self._save_directory = directory
    
    def record(self, module: str, func_name: str, execution_time: float) -> None:
        """
        Записывает данные о выполнении функции
        
        Args:
            module: Имя модуля
            func_name: Имя функции
            execution_time: Время выполнения
        """
        if not self._enabled:
            return
            
        with self._global_lock:
            if func_name not in self._data[module]:
                self._data[module][func_name] = FunctionProfile(name=func_name)
            self._data[module][func_name].add_call(execution_time)
            self._call_count += 1
        
        # Автосохранение по количеству вызовов или времени
        current_time = time.time()
        if (self._call_count >= self._save_interval or 
            current_time - self._last_save_time >= self._save_time_interval):
            self._auto_save()
    
    def write(self, module: str = None, 
              filename: str = None, 
              format: str = "txt",
              sort_by: str = "total_time",
              reverse: bool = True) -> str:
        """
        Записывает данные профилирования в файл
        
        Args:
            module: Имя модуля (если None - все модули)
            filename: Имя файла (если None - генерируется автоматически)
            format: Формат файла (txt, json, csv)
            sort_by: Поле для сортировки (total_time, avg_time, call_count)
            reverse: Сортировка по убыванию
            
        Returns:
            Путь к созданному файлу
        """
        with self._global_lock:
            # Получаем данные для сохранения
            if module is not None:
                data_to_save = {module: dict(self._data.get(module, {}))}
            else:
                data_to_save = {m: dict(funcs) for m, funcs in self._data.items()}
        
        if not data_to_save:
            print(f"{colorama.Fore.YELLOW}Нет данных для сохранения{colorama.Style.RESET_ALL}")
            return ""
        
        # Генерируем имя файла
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if module is not None:
                safe_module = module.replace(".", "_").replace("\\", "_").replace("/", "_")
                filename = f"{safe_module}_{timestamp}.{format}"
            else:
                filename = f"profiling_all_{timestamp}.{format}"
        
        filepath = os.path.join(self._save_directory, filename)
        
        try:
            if format.lower() == "txt":
                self._write_txt(filepath, data_to_save, sort_by, reverse)
            elif format.lower() == "json":
                self._write_json(filepath, data_to_save)
            elif format.lower() == "csv":
                self._write_csv(filepath, data_to_save, sort_by, reverse)
            else:
                raise ValueError(f"Неподдерживаемый формат: {format}")
            
            print(f"{colorama.Fore.GREEN}Данные профилирования сохранены в: {filepath}{colorama.Style.RESET_ALL}")
            return filepath
            
        except Exception as e:
            print(f"{colorama.Fore.RED}Ошибка при сохранении файла {filepath}: {e}{colorama.Style.RESET_ALL}")
            return ""
    
    def _write_txt(self, filepath: str, data: Dict, sort_by: str, reverse: bool) -> None:
        """Записывает данные в текстовый файл"""
        with open(filepath, 'w', encoding='utf-8') as f:
            for module_name, functions in data.items():
                if not functions:
                    continue
                
                # Записываем заголовок модуля
                f.write(f"{'='*60}\n")
                f.write(f"МОДУЛЬ: {module_name}\n")
                f.write(f"{'='*60}\n\n")
                
                # Преобразуем в список и сортируем
                func_list = list(functions.values())
                func_list.sort(key=lambda x: getattr(x, sort_by, x.total_time), reverse=reverse)
                
                # Заголовок таблицы
                header = f"{'Функция':<30} {'Вызовов':<8} {'Общее время':<12} {'Среднее':<12} {'Мин':<10} {'Макс':<10}"
                f.write(header + "\n")
                f.write("-" * 92 + "\n")
                
                # Данные функций
                for func_profile in func_list:
                    row = (f"{func_profile.name:<30} "
                           f"{func_profile.call_count:<8} "
                           f"{func_profile.total_time:<12.6f} "
                           f"{func_profile.avg_time:<12.6f} "
                           f"{func_profile.min_time:<10.6f} "
                           f"{func_profile.max_time:<10.6f}")
                    f.write(row + "\n")
                
                # Итоги по модулю
                total_calls = sum(f.call_count for f in func_list)
                total_time = sum(f.total_time for f in func_list)
                f.write("\n" + "-" * 92 + "\n")
                f.write(f"ИТОГО: {len(func_list)} функций, {total_calls} вызовов, общее время: {total_time:.6f} сек\n\n")
            
            # Глобальная статистика (если несколько модулей)
            if len(data) > 1:
                f.write(f"\n{'='*60}\n")
                f.write(f"ГЛОБАЛЬНАЯ СТАТИСТИКА\n")
                f.write(f"{'='*60}\n\n")
                
                total_funcs = sum(len(funcs) for funcs in data.values())
                total_calls = 0
                total_time = 0.0
                
                for module_name, functions in data.items():
                    module_calls = sum(f.call_count for f in functions.values())
                    module_time = sum(f.total_time for f in functions.values())
                    total_calls += module_calls
                    total_time += module_time
                    
                    f.write(f"{module_name:<20}: {len(functions):<3} функций, "
                           f"{module_calls:<5} вызовов, {module_time:<10.6f} сек\n")
                
                f.write("\n" + "-" * 60 + "\n")
                f.write(f"ВСЕГО: {total_funcs} функций, {total_calls} вызовов, {total_time:.6f} сек\n")
            
            # Метаданные
            f.write(f"\n{'='*60}\n")
            f.write(f"МЕТАДАННЫЕ\n")
            f.write(f"{'='*60}\n")
            f.write(f"Файл создан: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Формат: txt\n")
            f.write(f"Сортировка: {sort_by} ({'по убыванию' if reverse else 'по возрастанию'})\n")
    
    def _write_json(self, filepath: str, data: Dict) -> None:
        """Записывает данные в JSON файл"""
        # Преобразуем данные для сериализации
        serializable_data = {}
        for module_name, functions in data.items():
            serializable_data[module_name] = {
                func_name: func_profile.to_dict()
                for func_name, func_profile in functions.items()
            }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'format': 'json',
                    'modules_count': len(data)
                },
                'data': serializable_data
            }, f, indent=2, ensure_ascii=False)
    
    def _write_csv(self, filepath: str, data: Dict, sort_by: str, reverse: bool) -> None:
        """Записывает данные в CSV файл"""
        with open(filepath, 'w', encoding='utf-8') as f:
            # Записываем заголовок
            f.write("module,function,call_count,total_time,avg_time,min_time,max_time\n")
            
            for module_name, functions in data.items():
                # Сортируем функции
                func_list = list(functions.values())
                func_list.sort(key=lambda x: getattr(x, sort_by, x.total_time), reverse=reverse)
                
                # Записываем данные
                for func_profile in func_list:
                    row = (f"{module_name},"
                           f"{func_profile.name},"
                           f"{func_profile.call_count},"
                           f"{func_profile.total_time:.6f},"
                           f"{func_profile.avg_time:.6f},"
                           f"{func_profile.min_time:.6f},"
                           f"{func_profile.max_time:.6f}")
                    f.write(row + "\n")
    
    def get_summary(self, module: str = None) -> Dict:
        """
        Возвращает сводную статистику
        
        Args:
            module: Имя модуля (если None - по всем модулям)
            
        Returns:
            Словарь со статистикой
        """
        with self._global_lock:
            if module is not None:
                functions = self._data.get(module, {})
            else:
                functions = {}
                for mod_funcs in self._data.values():
                    functions.update(mod_funcs)
        
        if not functions:
            return {}
        
        total_calls = sum(f.call_count for f in functions.values())
        total_time = sum(f.total_time for f in functions.values())
        
        return {
            'functions_count': len(functions),
            'total_calls': total_calls,
            'total_time': total_time,
            'avg_time_per_call': total_time / total_calls if total_calls > 0 else 0,
            'modules': list(self._data.keys()) if module is None else [module]
        }
    
    def clear(self, module: str = None) -> None:
        """
        Очищает данные профилирования
        
        Args:
            module: Имя модуля (если None - все модули)
        """
        with self._global_lock:
            if module is not None:
                if module in self._data:
                    del self._data[module]
            else:
                self._data.clear()
    
    def register_exit_handler(self) -> None:
        """Регистрирует сохранение при выходе из программы"""
        if not self._save_registered:
            atexit.register(self._save_on_exit)
            self._save_registered = True
    
    def _auto_save(self) -> None:
        """Автоматическое сохранение в фоне"""
        self._call_count = 0
        self._last_save_time = time.time()
        # Сохраняем в отдельном потоке чтобы не блокировать
        threading.Thread(target=self.save_table, daemon=True).start()
    
    def _save_on_exit(self) -> None:
        """Сохраняет данные профилирования при выходе"""
        self.save_table()
    
    def save_table(self) -> None:
        """Сохраняет таблицу профилирования в tracing/"""
        if not self._data:
            return
        
        # Генерируем имя файла с датой
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}_cpu_profiling.txt"
        filepath = os.path.join(self._save_directory, filename)
        
        try:
            # Собираем данные
            with self._global_lock:
                data_to_save = {m: dict(funcs) for m, funcs in self._data.items()}
            
            if not data_to_save:
                return
            
            # Записываем в файл
            with open(filepath, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"\n[{timestamp}] ПРОФИЛИРОВАНИЕ ЦП\n")
                f.write(f"{'─'*70}\n")
                
                total_cpu_time = 0.0
                
                for module_name, functions in data_to_save.items():
                    if not functions:
                        continue
                    
                    f.write(f"\n[{module_name}]\n")
                    f.write(f"┌{'─'*30}┬{'─'*18}┬{'─'*16}┐\n")
                    f.write(f"│ {'Функция':<28} │ {'Среднее время':<16} │ {'Время ЦП':<14} │\n")
                    f.write(f"├{'─'*30}┼{'─'*18}┼{'─'*16}┤\n")
                    
                    # Сортируем по времени ЦП
                    func_list = sorted(functions.values(), key=lambda x: x.total_time, reverse=True)
                    
                    for fp in func_list:
                        f.write(f"│ {fp.name:<28} │ {fp.avg_time:>14.4f}s │ {fp.total_time:>12.4f}s │\n")
                        total_cpu_time += fp.total_time
                    
                    f.write(f"└{'─'*30}┴{'─'*18}┴{'─'*16}┘\n")
                
                f.write(f"\nОБЩЕЕ ВРЕМЯ ЦП: {total_cpu_time:.4f}s\n")
                f.write(f"{'─'*70}\n")
                
        except Exception as e:
            print(f"{colorama.Fore.RED}Ошибка сохранения профилирования: {e}{colorama.Style.RESET_ALL}")
    
    def print_table(self, module: str = None, sort_by: str = "total_time", reverse: bool = True) -> None:
        """
        Выводит красивую таблицу с данными профилирования в консоль
        
        Args:
            module: Имя модуля (если None - все модули)
            sort_by: Поле для сортировки (total_time, avg_time, call_count)
            reverse: Сортировка по убыванию
        """
        with self._global_lock:
            if module is not None:
                data = {module: dict(self._data.get(module, {}))}
            else:
                data = {m: dict(funcs) for m, funcs in self._data.items()}
        
        if not data or all(len(funcs) == 0 for funcs in data.values()):
            rich_console.print("[yellow]⚠ Нет данных профилирования[/yellow]")
            return
        
        # Общая статистика
        total_funcs = 0
        total_calls = 0
        total_time = 0.0
        
        for module_name, functions in data.items():
            if not functions:
                continue
            
            # Создаём таблицу для модуля
            table = Table(
                title=f"⚡ Профилирование: {module_name}",
                box=box.ROUNDED,
                header_style="bold cyan",
                title_style="bold magenta",
                border_style="blue"
            )
            
            table.add_column("Функция", style="white", no_wrap=True)
            table.add_column("Вызовов", justify="right", style="green")
            table.add_column("Общее время", justify="right", style="yellow")
            table.add_column("Среднее", justify="right", style="cyan")
            table.add_column("Мин", justify="right", style="dim")
            table.add_column("Макс", justify="right", style="red")
            table.add_column("% от общего", justify="right", style="magenta")
            
            # Сортируем функции
            func_list = list(functions.values())
            func_list.sort(key=lambda x: getattr(x, sort_by, x.total_time), reverse=reverse)
            
            # Вычисляем общее время модуля для процентов
            module_total_time = sum(f.total_time for f in func_list)
            
            for func_profile in func_list:
                percent = (func_profile.total_time / module_total_time * 100) if module_total_time > 0 else 0
                
                # Цветовая индикация для процента
                if percent >= 50:
                    percent_style = "[bold red]"
                elif percent >= 25:
                    percent_style = "[yellow]"
                else:
                    percent_style = "[green]"
                
                table.add_row(
                    func_profile.name,
                    str(func_profile.call_count),
                    f"{func_profile.total_time:.4f}s",
                    f"{func_profile.avg_time:.4f}s",
                    f"{func_profile.min_time:.4f}s" if func_profile.min_time != float('inf') else "-",
                    f"{func_profile.max_time:.4f}s",
                    f"{percent_style}{percent:.1f}%[/]"
                )
            
            # Итоговая строка
            table.add_section()
            table.add_row(
                f"[bold]ИТОГО ({len(func_list)} функций)[/bold]",
                f"[bold]{sum(f.call_count for f in func_list)}[/bold]",
                f"[bold]{module_total_time:.4f}s[/bold]",
                "-", "-", "-",
                "[bold]100%[/bold]"
            )
            
            rich_console.print(table)
            rich_console.print()
            
            # Обновляем общую статистику
            total_funcs += len(func_list)
            total_calls += sum(f.call_count for f in func_list)
            total_time += module_total_time
        
        # Если несколько модулей - выводим сводную таблицу
        if len(data) > 1:
            summary_table = Table(
                title="📊 Сводная статистика по модулям",
                box=box.DOUBLE,
                header_style="bold white on blue",
                title_style="bold yellow"
            )
            
            summary_table.add_column("Модуль", style="cyan")
            summary_table.add_column("Функций", justify="right", style="white")
            summary_table.add_column("Вызовов", justify="right", style="green")
            summary_table.add_column("Время ЦП", justify="right", style="yellow")
            summary_table.add_column("% времени", justify="right", style="magenta")
            
            for module_name, functions in data.items():
                if not functions:
                    continue
                module_calls = sum(f.call_count for f in functions.values())
                module_time = sum(f.total_time for f in functions.values())
                percent = (module_time / total_time * 100) if total_time > 0 else 0
                
                summary_table.add_row(
                    module_name,
                    str(len(functions)),
                    str(module_calls),
                    f"{module_time:.4f}s",
                    f"{percent:.1f}%"
                )
            
            summary_table.add_section()
            summary_table.add_row(
                "[bold]ВСЕГО[/bold]",
                f"[bold]{total_funcs}[/bold]",
                f"[bold]{total_calls}[/bold]",
                f"[bold]{total_time:.4f}s[/bold]",
                "[bold]100%[/bold]"
            )
            
            rich_console.print(summary_table)
        
        # Время генерации отчёта
        rich_console.print(
            f"\n[dim]Отчёт сформирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]"
        )


# Глобальный экземпляр профайлера
profiler = Profiler()


# ========================== ФУНКЦИИ ЛОГИРОВАНИЯ ==========================

def info(message: str, module: Optional[str] = None) -> None:
    """Информационное сообщение"""
    prefix = f"[{module}] " if module else ""
    print(f"{colorama.Fore.BLUE}[INFO]{colorama.Style.RESET_ALL} {prefix}{message}")


def warning(message: str, module: Optional[str] = None) -> None:
    """Предупреждение"""
    prefix = f"[{module}] " if module else ""
    print(f"{colorama.Fore.YELLOW}[WARNING]{colorama.Style.RESET_ALL} {prefix}{message}")


def error(message: str, module: Optional[str] = None) -> None:
    """Ошибка"""
    prefix = f"[{module}] " if module else ""
    print(f"{colorama.Fore.RED}[ERROR]{colorama.Style.RESET_ALL} {prefix}{message}")


def debug_log(message: str, module: Optional[str] = None) -> None:
    """Отладочное сообщение"""
    prefix = f"[{module}] " if module else ""
    print(f"{colorama.Fore.CYAN}[DEBUG]{colorama.Style.RESET_ALL} {prefix}{message}")


def success(message: str, module: Optional[str] = None) -> None:
    """Успешное сообщение"""
    prefix = f"[{module}] " if module else ""
    print(f"{colorama.Fore.GREEN}[SUCCESS]{colorama.Style.RESET_ALL} {prefix}{message}")


def debug(
    module: Optional[str] = None,
    slow_threshold: float = 1.0,
    show_args: bool = False,
    show_time: bool = True,
    show_return: bool = False,
    enable_profiling: bool = True
) -> Callable:
    """
    Декоратор для отладки функций с замером времени выполнения
    
    Args:
        module: Префикс модуля для вывода
        slow_threshold: Порог времени (сек) для предупреждения о медленном выполнении
        show_args: Показывать аргументы функции
        show_time: Показывать время выполнения
        show_return: Показывать возвращаемое значение
        enable_profiling: Включить сбор статистики для сохранения в файл
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
                    
                    # Записываем данные в профайлер
                    if enable_profiling:
                        module_key = module if module else "global"
                        profiler.record(module_key, func.__name__, execution_time)
                    
                    if execution_time >= slow_threshold:
                        time_color = colorama.Fore.YELLOW
                    else:
                        time_color = colorama.Fore.GREEN
                    
                    time_str = f" за {time_color}{execution_time:.4f}{colorama.Fore.GREEN} секунд"
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


# Вспомогательные функции для удобства использования
def save_profiling(module: str = None, directory: str = ".", format: str = "txt") -> None:
    """
    Быстрое сохранение данных профилирования
    
    Args:
        module: Имя модуля (если None - все модули)
        directory: Директория для сохранения
        format: Формат файла
    """
    profiler.set_save_directory(directory)
    profiler.write(module=module, format=format)


def get_profiling_summary(module: str = None) -> Dict:
    """
    Получить сводную статистику профилирования
    
    Args:
        module: Имя модуля (если None - по всем модулям)
        
    Returns:
        Словарь со статистикой
    """
    return profiler.get_summary(module)


def clear_profiling(module: str = None) -> None:
    """
    Очистить данные профилирования
    
    Args:
        module: Имя модуля (если None - все модули)
    """
    profiler.clear(module)


def print_profiling_table(module: str = None, sort_by: str = "total_time") -> None:
    """
    Вывести красивую таблицу профилирования с временем ЦП
    
    Args:
        module: Имя модуля (если None - все модули)
        sort_by: Поле для сортировки (total_time, avg_time, call_count)
    """
    profiler.print_table(module=module, sort_by=sort_by)


def save_profiling_table() -> None:
    """Сохранить таблицу профилирования в tracing/"""
    profiler.save_table()


# Пример использования
if __name__ == "__main__":
    # Настраиваем профайлер
    profiler.set_save_directory("./profiling_results")
    profiler.register_exit_handler()
    
    # Пример 1: Декорирование функций
    @debug(module="main", show_args=True, enable_profiling=True)
    def calculate_sum(a: int, b: int) -> int:
        """Пример функции для тестирования"""
        time.sleep(0.05)
        return a + b
    
    @debug(module="utils", show_return=True, enable_profiling=True)
    def process_list(data: list) -> list:
        """Обработка списка"""
        time.sleep(0.1)
        return [x ** 2 for x in data]
    
    @debug(module="main", enable_profiling=True)
    def factorial(n: int) -> int:
        """Вычисление факториала"""
        if n <= 1:
            return 1
        time.sleep(0.01)
        return n * factorial(n - 1)
    
    # Тестовые вызовы
    print("Тестовый запуск функций:\n")
    
    for i in range(3):
        calculate_sum(i * 10, i * 20)
    
    process_list([1, 2, 3, 4, 5])
    process_list([10, 20, 30])
    
    factorial(5)
    factorial(7)
    
    # Промежуточное сохранение
    print("\n" + "="*50)
    print("Промежуточное сохранение...\n")
    
    # Сохраняем в разных форматах
    profiler.write(module="main", format="txt")
    profiler.write(module="utils", format="json")
    
    # Красивая таблица с временем ЦП
    print("\n")
    print_profiling_table()
    
    # Еще несколько вызовов
    calculate_sum(100, 200)
    process_list([100, 200, 300])
    
    print("\n" + "="*50)
    print("Сохранение всех данных в CSV...")
    
    # Сохраняем все данные в CSV
    profiler.write(filename="all_profiling.csv", format="csv")
    
    # Таблица только для одного модуля
    print("\nТаблица только для модуля 'main':")
    print_profiling_table(module="main")
    
    # Очистка данных конкретного модуля
    print("\nОчистка данных модуля 'utils'...")
    clear_profiling(module="utils")
    
    # Проверяем, что данные utils удалены
    print_profiling_table()