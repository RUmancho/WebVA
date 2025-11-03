# -*- coding: utf-8 -*-
"""
Асинхронные помощники для оптимизации операций
"""
import asyncio
import aiofiles
from typing import List, Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime
from config_manager import log_info, log_error, get_config_value

# Максимальное количество одновременных задач
MAX_CONCURRENT_TASKS = 5

def run_async(func: Callable) -> Callable:
    """
    Декоратор для запуска синхронных функций асинхронно
    
    Args:
        func: Функция для выполнения
        
    Returns:
        Callable: Обернутая функция
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    return wrapper

async def batch_process(items: List[Any], process_func: Callable, 
                       batch_size: int = 100) -> List[Any]:
    """
    Обработка элементов пакетами асинхронно
    
    Args:
        items: Список элементов для обработки
        process_func: Функция обработки
        batch_size: Размер батча
        
    Returns:
        List[Any]: Результаты обработки
    """
    try:
        results = []
        max_concurrent = get_config_value("scheduler.max_concurrent_tasks", MAX_CONCURRENT_TASKS)
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # Создаем задачи для батча
            tasks = []
            for item in batch:
                if asyncio.iscoroutinefunction(process_func):
                    task = process_func(item)
                else:
                    task = asyncio.get_event_loop().run_in_executor(None, process_func, item)
                tasks.append(task)
            
            # Выполняем задачи с ограничением параллелизма
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def bounded_task(task):
                async with semaphore:
                    return await task
            
            batch_results = await asyncio.gather(*[bounded_task(task) for task in tasks], 
                                                return_exceptions=True)
            results.extend(batch_results)
        
        return results
        
    except Exception as e:
        log_error("async_helpers.py", f"Ошибка пакетной обработки: {e}")
        return []

async def read_file_async(file_path: str, encoding: str = "utf-8") -> Optional[str]:
    """
    Асинхронное чтение файла
    
    Args:
        file_path: Путь к файлу
        encoding: Кодировка файла
        
    Returns:
        Optional[str]: Содержимое файла или None при ошибке
    """
    try:
        async with aiofiles.open(file_path, mode='r', encoding=encoding) as f:
            content = await f.read()
        return content
    except Exception as e:
        log_error("async_helpers.py", f"Ошибка чтения файла {file_path}: {e}")
        return None

async def write_file_async(file_path: str, content: str, encoding: str = "utf-8") -> bool:
    """
    Асинхронная запись в файл
    
    Args:
        file_path: Путь к файлу
        content: Содержимое для записи
        encoding: Кодировка файла
        
    Returns:
        bool: True если успешно
    """
    try:
        async with aiofiles.open(file_path, mode='w', encoding=encoding) as f:
            await f.write(content)
        return True
    except Exception as e:
        log_error("async_helpers.py", f"Ошибка записи файла {file_path}: {e}")
        return False

async def parallel_db_operations(operations: List[Callable]) -> List[Any]:
    """
    Выполнение нескольких операций БД параллельно
    
    Args:
        operations: Список функций для выполнения
        
    Returns:
        List[Any]: Результаты операций
    """
    try:
        max_concurrent = get_config_value("database_advanced.max_db_requests_per_minute", 100)
        semaphore = asyncio.Semaphore(min(max_concurrent // 10, MAX_CONCURRENT_TASKS))
        
        async def bounded_operation(op):
            async with semaphore:
                if asyncio.iscoroutinefunction(op):
                    return await op()
                else:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, op)
        
        results = await asyncio.gather(*[bounded_operation(op) for op in operations],
                                      return_exceptions=True)
        return results
        
    except Exception as e:
        log_error("async_helpers.py", f"Ошибка параллельных операций БД: {e}")
        return []

def run_async_task(coro) -> Any:
    """
    Запуск асинхронной задачи в синхронном коде
    
    Args:
        coro: Корутина для выполнения
        
    Returns:
        Any: Результат выполнения
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Если цикл уже запущен, создаем новый
            return asyncio.run(coro)
        else:
            return loop.run_until_complete(coro)
    except Exception as e:
        log_error("async_helpers.py", f"Ошибка выполнения async задачи: {e}")
        return None

class AsyncRateLimiter:
    """Ограничитель скорости для асинхронных операций"""
    
    def __init__(self, max_calls: int, time_window: int):
        """
        Инициализация ограничителя
        
        Args:
            max_calls: Максимальное количество вызовов
            time_window: Временное окно в секундах
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: List[float] = []
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Ожидание разрешения на выполнение"""
        async with self._lock:
            now = datetime.now().timestamp()
            
            # Удаляем старые вызовы
            self.calls = [call_time for call_time in self.calls 
                         if now - call_time < self.time_window]
            
            # Проверяем лимит
            if len(self.calls) >= self.max_calls:
                # Вычисляем время ожидания
                oldest_call = min(self.calls)
                wait_time = self.time_window - (now - oldest_call)
                
                if wait_time > 0:
                    log_info("async_helpers.py", 
                            f"Rate limit reached, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    
                    # Повторяем проверку
                    now = datetime.now().timestamp()
                    self.calls = [call_time for call_time in self.calls 
                                 if now - call_time < self.time_window]
            
            # Добавляем текущий вызов
            self.calls.append(now)

# Глобальный ограничитель для операций БД
db_rate_limiter = AsyncRateLimiter(
    max_calls=get_config_value("database_advanced.max_db_requests_per_minute", 100),
    time_window=60
)

async def rate_limited_db_call(func: Callable, *args, **kwargs) -> Any:
    """
    Вызов функции БД с ограничением скорости
    
    Args:
        func: Функция для вызова
        *args: Позиционные аргументы
        **kwargs: Именованные аргументы
        
    Returns:
        Any: Результат вызова
    """
    try:
        await db_rate_limiter.acquire()
        
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)
            
    except Exception as e:
        log_error("async_helpers.py", f"Ошибка rate-limited вызова: {e}")
        return None

