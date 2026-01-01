"""
Файловый логгер для записи статистики работы программы.
Все логи записываются в файлы в папку tracing/.
"""

import os
import threading
from datetime import datetime
from typing import Optional
from enum import Enum


class LogLevel(Enum):
    """Уровни логирования"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class StatsLogger:
    """Менеджер статистики и логирования в файлы"""
    
    _instance = None
    _lock = threading.Lock()
    
    # Директория для логов - папка tracing в корне проекта
    STATS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tracing")
    
    def __new__(cls):
        """Реализация синглтона"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Инициализация логгера"""
        if not hasattr(self, '_initialized') or not self._initialized:
            self._file_lock = threading.Lock()
            self._ensure_log_dir()
            self._current_date = datetime.now().strftime("%Y-%m-%d")
            self._initialized = True
    
    def _ensure_log_dir(self):
        """Создаёт директорию для логов если не существует"""
        os.makedirs(self.STATS_DIR, exist_ok=True)
    
    def _get_log_file(self, module: str = None) -> str:
        """Получить путь к файлу лога"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        if module:
            safe_module = module.replace(".", "_").replace("\\", "_").replace("/", "_")
            filename = f"логи_{safe_module}_{date_str}.txt"
        else:
            filename = f"логи_общие_{date_str}.txt"
        return os.path.join(self.STATS_DIR, filename)
    
    def _write_log(self, level: LogLevel, message: str, module: Optional[str] = None):
        """Записывает лог в файл"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        module_str = f"[{module}]" if module else ""
        log_line = f"[{timestamp}] [{level.value}] {module_str} {message}\n"
        
        with self._file_lock:
            try:
                filepath = self._get_log_file(module)
                with open(filepath, 'a', encoding='utf-8') as f:
                    f.write(log_line)
            except Exception:
                # Если не удалось записать в файл модуля, пишем в общий
                try:
                    filepath = self._get_log_file()
                    with open(filepath, 'a', encoding='utf-8') as f:
                        f.write(log_line)
                except Exception:
                    pass  # Игнорируем ошибки записи
    
    def info(self, message: str, module: Optional[str] = None):
        """Информационное сообщение"""
        self._write_log(LogLevel.INFO, message, module)
    
    def warning(self, message: str, module: Optional[str] = None):
        """Предупреждение"""
        self._write_log(LogLevel.WARNING, message, module)
    
    def error(self, message: str, module: Optional[str] = None):
        """Ошибка"""
        self._write_log(LogLevel.ERROR, message, module)
    
    def debug(self, message: str, module: Optional[str] = None):
        """Отладочное сообщение"""
        self._write_log(LogLevel.DEBUG, message, module)
    
    def get_logs(self, module: str = None, date: str = None, level: LogLevel = None) -> list:
        """
        Получить логи из файла.
        
        Args:
            module: Фильтр по модулю
            date: Дата в формате YYYY-MM-DD (по умолчанию сегодня)
            level: Фильтр по уровню
        
        Returns:
            Список строк логов
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        logs = []
        
        # Определяем файлы для чтения
        if module:
            files = [self._get_log_file(module)]
        else:
            # Читаем все файлы за дату
            files = []
            for filename in os.listdir(self.STATS_DIR):
                if filename.startswith(date) and filename.endswith('.txt'):
                    files.append(os.path.join(self.STATS_DIR, filename))
        
        for filepath in files:
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            if level is None or f"[{level.value}]" in line:
                                logs.append(line.strip())
                except Exception:
                    pass
        
        return logs
    
    def clear_old_logs(self, days: int = 7):
        """
        Удаляет логи старше указанного количества дней.
        
        Args:
            days: Количество дней для хранения логов
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            for filename in os.listdir(self.STATS_DIR):
                if filename.endswith('.txt'):
                    # Извлекаем дату из имени файла
                    try:
                        date_str = filename[:10]  # YYYY-MM-DD
                        file_date = datetime.strptime(date_str, "%Y-%m-%d")
                        if file_date < cutoff_date:
                            filepath = os.path.join(self.STATS_DIR, filename)
                            os.remove(filepath)
                    except Exception:
                        pass
        except Exception:
            pass


# Глобальный экземпляр логгера
stats_logger = StatsLogger()


# Удобные функции для быстрого доступа
def log_info(message: str, module: Optional[str] = None):
    """Записать информационное сообщение"""
    stats_logger.info(message, module)


def log_warning(message: str, module: Optional[str] = None):
    """Записать предупреждение"""
    stats_logger.warning(message, module)


def log_error(message: str, module: Optional[str] = None):
    """Записать ошибку"""
    stats_logger.error(message, module)


def log_debug(message: str, module: Optional[str] = None):
    """Записать отладочное сообщение"""
    stats_logger.debug(message, module)

