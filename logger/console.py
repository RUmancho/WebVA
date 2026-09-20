import tracemalloc
import time
import os
import threading
from functools import wraps
from datetime import datetime
from typing import Optional, Callable, Any, Dict, Union, Tuple
from contextlib import contextmanager
import psutil
import platform
from collections import defaultdict

from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import DatabaseError

Base = declarative_base()

class PerformanceMetric(Base):
    """Модель для хранения метрик производительности с CPU временем."""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    
    # Идентификация функции
    function_name = Column(String(255), nullable=False)
    module_name = Column(String(255))
    file_path = Column(String(500))
    
    # Время выполнения
    cpu_time_ms = Column(Float, nullable=False)      # Процессорное время
    wall_time_ms = Column(Float, nullable=False)     # Реальное время
    cpu_percent = Column(Float)                     # Процент использования CPU
    
    # Поток/процесс
    thread_id = Column(Integer)
    process_id = Column(Integer)
    
    # Память
    memory_peak_mb = Column(Float)
    memory_current_mb = Column(Float)
    memory_percent = Column(Float)
    
    # Дополнительная информация
    args_hash = Column(String(64))
    result_type = Column(String(100))
    success = Column(Integer, default=1)
    error_message = Column(Text)
    call_count = Column(Integer, default=1)
    
    # Системные метрики
    system_cpu_percent = Column(Float)
    system_memory_percent = Column(Float)
    
    def __repr__(self) -> str:
        status = "ERROR" if not self.success else "OK"
        return f"<Metric {self.function_name} [{status}] CPU:{self.cpu_time_ms:.2f}ms WALL:{self.wall_time_ms:.2f}ms>"

class FunctionStatistics(Base):
    """Агрегированная статистика по функциям."""
    __tablename__ = "function_statistics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Идентификация функции
    folder_name = Column(String(255))           # Папка (из пути к файлу)
    module_name = Column(String(255))           # Модуль
    function_name = Column(String(255), nullable=False, unique=True)  # Полное имя функции
    
    # Статистика вызовов
    total_calls = Column(Integer, default=0)    # Общее количество вызовов
    success_count = Column(Integer, default=0)  # Успешных вызовов
    error_count = Column(Integer, default=0)    # Ошибок
    
    # Статистика CPU времени
    total_cpu_time_ms = Column(Float, default=0.0)  # Общее CPU время
    avg_cpu_time_ms = Column(Float, default=0.0)    # Среднее CPU время
    min_cpu_time_ms = Column(Float)                 # Минимальное CPU время
    max_cpu_time_ms = Column(Float)                 # Максимальное CPU время
    
    # Статистика реального времени
    total_wall_time_ms = Column(Float, default=0.0)  # Общее реальное время
    avg_wall_time_ms = Column(Float, default=0.0)    # Среднее реальное время
    min_wall_time_ms = Column(Float)                 # Минимальное реальное время
    max_wall_time_ms = Column(Float)                 # Максимальное реальное время
    
    # Статистика процента CPU
    avg_cpu_percent = Column(Float, default=0.0)     # Средний процент CPU
    max_cpu_percent = Column(Float)                  # Максимальный процент CPU
    
    # Статистика памяти
    avg_memory_mb = Column(Float)                    # Средняя память
    max_memory_mb = Column(Float)                    # Максимальная память
    
    # Временные метки
    first_call = Column(DateTime)                    # Первый вызов
    last_call = Column(DateTime)                     # Последний вызов
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self) -> str:
        success_rate = (self.success_count / self.total_calls * 100) if self.total_calls > 0 else 0
        return (f"<FunctionStats {self.function_name} | "
                f"Calls: {self.total_calls} | "
                f"Success: {success_rate:.1f}% | "
                f"Avg CPU: {self.avg_cpu_time_ms:.2f}ms>")

class CPUTracer:
    """Трассировщик производительности с CPU временем."""
    
    def __init__(
        self, 
        db_path: str = "cpu_tracer.db",
        enable_cpu_tracking: bool = True,
        enable_memory_tracking: bool = True,
        track_system_metrics: bool = True,
        enable_db_logging: bool = True
    ):
        """
        Инициализация CPU трассировщика.
        
        Args:
            db_path: Путь к файлу базы данных
            enable_cpu_tracking: Включить отслеживание CPU времени
            enable_memory_tracking: Включить отслеживание памяти
            track_system_metrics: Включить отслеживание системных метрик
            enable_db_logging: Включить запись в базу данных
        """
        self.db_path = os.path.abspath(db_path)
        self.enable_cpu_tracking = enable_cpu_tracking
        self.enable_memory_tracking = enable_memory_tracking
        self.track_system_metrics = track_system_metrics
        self.enable_db_logging = enable_db_logging
        
        # Статистика вызовов в памяти
        self.call_stats = defaultdict(lambda: {
            'total_calls': 0,
            'total_cpu_time': 0.0,
            'total_wall_time': 0.0,
            'success_calls': 0,
            'error_calls': 0
        })
        
        self._setup_database()
        
        if enable_memory_tracking and not tracemalloc.is_tracing():
            tracemalloc.start(25)  # Сохраняем 25 фреймов для детальной трассировки
        
        # Процесс для отслеживания системных метрик
        self.process = psutil.Process()
    
    def _setup_database(self) -> None:
        """Настройка подключения к базе данных."""
        self.db_url = f"sqlite:///{self.db_path}"
        
        try:
            self.engine = create_engine(
                self.db_url,
                connect_args={"check_same_thread": False},
                echo=False,
                pool_pre_ping=True
            )
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
            
            # Создаем таблицы, если их нет
            Base.metadata.create_all(self.engine)
            
        except DatabaseError as e:
            if "file is not a database" in str(e).lower():
                print(f"⚠️ Обнаружен конфликт форматов. Пересоздаю БД: {self.db_path}")
                self._recreate_database()
            else:
                print(f"❌ Ошибка подключения к БД: {e}")
                self.enable_db_logging = False
    
    def _recreate_database(self) -> None:
        """Пересоздание базы данных."""
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            self.engine.dispose()
            self._setup_database()
        except Exception as e:
            print(f"❌ Не удалось пересоздать БД: {e}")
            self.enable_db_logging = False
    
    @contextmanager
    def get_session(self) -> Session:
        """Контекстный менеджер для получения сессии БД."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка в сессии БД: {e}")
            raise
        finally:
            session.close()
    
    def get_cpu_time(self) -> float:
        """
        Получение CPU времени процесса в миллисекундах.
        
        Returns:
            CPU время в миллисекундах
        """
        if not self.enable_cpu_tracking:
            return 0.0
        
        try:
            # Используем process_time() для CPU времени процесса
            # time.process_time() возвращает время CPU в секундах
            return time.process_time() * 1000  # Преобразуем в миллисекунды
        except AttributeError:
            # Для обратной совместимости с Python < 3.3
            return time.clock() * 1000
    
    def get_memory_stats(self) -> Dict[str, float]:
        """Получение статистики по памяти."""
        stats = {
            "peak_mb": 0.0,
            "current_mb": 0.0,
            "percent": 0.0
        }
        
        if not self.enable_memory_tracking:
            return stats
        
        try:
            # Трассировка памяти через tracemalloc
            if tracemalloc.is_tracing():
                current, peak = tracemalloc.get_traced_memory()
                stats["peak_mb"] = peak / (1024 * 1024)
                stats["current_mb"] = current / (1024 * 1024)
            
            # Использование памяти процесса через psutil
            process_memory = self.process.memory_info()
            stats["percent"] = self.process.memory_percent()
            
        except Exception as e:
            print(f"⚠️ Ошибка получения статистики памяти: {e}")
        
        return stats
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Получение системных метрик."""
        if not self.track_system_metrics:
            return {"cpu_percent": 0.0, "memory_percent": 0.0}
        
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.01),
                "memory_percent": psutil.virtual_memory().percent
            }
        except Exception:
            return {"cpu_percent": 0.0, "memory_percent": 0.0}
    
    def log_metric(
        self,
        function_name: str,
        cpu_time_ms: float,
        wall_time_ms: float,
        success: bool = True,
        memory_stats: Optional[Dict[str, float]] = None,
        system_metrics: Optional[Dict[str, float]] = None,
        module_name: Optional[str] = None,
        file_path: Optional[str] = None,
        args_hash: Optional[str] = None,
        result_type: Optional[str] = None,
        error_message: Optional[str] = None,
        thread_id: Optional[int] = None,
        call_count: int = 1
    ) -> None:
        """
        Логирование метрики производительности с CPU временем.
        
        Args:
            function_name: Имя функции
            cpu_time_ms: CPU время выполнения в миллисекундах
            wall_time_ms: Реальное время выполнения в миллисекундах
            success: Успешно ли выполнение
            memory_stats: Статистика памяти
            system_metrics: Системные метрики
            module_name: Имя модуля
            file_path: Путь к файлу
            args_hash: Хэш аргументов функции
            result_type: Тип возвращаемого значения
            error_message: Сообщение об ошибке
            thread_id: ID потока
            call_count: Количество вызовов
        """
        if not self.enable_db_logging:
            return
        
        # Обновляем статистику в памяти
        stats_key = f"{module_name}.{function_name}" if module_name else function_name
        self.call_stats[stats_key]['total_calls'] += call_count
        self.call_stats[stats_key]['total_cpu_time'] += cpu_time_ms
        self.call_stats[stats_key]['total_wall_time'] += wall_time_ms
        
        if success:
            self.call_stats[stats_key]['success_calls'] += call_count
        else:
            self.call_stats[stats_key]['error_calls'] += call_count
        
        try:
            # Рассчитываем процент CPU
            cpu_percent = 0.0
            if wall_time_ms > 0:
                cpu_percent = (cpu_time_ms / wall_time_ms) * 100
            
            metric = PerformanceMetric(
                function_name=function_name,
                module_name=module_name,
                file_path=file_path,
                cpu_time_ms=cpu_time_ms,
                wall_time_ms=wall_time_ms,
                cpu_percent=cpu_percent,
                thread_id=thread_id or threading.get_ident(),
                process_id=os.getpid(),
                memory_peak_mb=memory_stats.get("peak_mb") if memory_stats else None,
                memory_current_mb=memory_stats.get("current_mb") if memory_stats else None,
                memory_percent=memory_stats.get("percent") if memory_stats else None,
                args_hash=args_hash,
                result_type=result_type,
                success=1 if success else 0,
                error_message=error_message,
                call_count=call_count,
                system_cpu_percent=system_metrics.get("cpu_percent") if system_metrics else None,
                system_memory_percent=system_metrics.get("memory_percent") if system_metrics else None
            )
            
            with self.get_session() as session:
                session.add(metric)
                
        except Exception as e:
            print(f"⚠️ Не удалось записать метрику: {e}")
    
    def trace_function(
        self, 
        func: Optional[Callable] = None, 
        aggregate_calls: bool = False,
        **decorator_kwargs
    ):
        """
        Декоратор для трассировки функций с CPU временем.
        
        Args:
            func: Декорируемая функция
            aggregate_calls: Агрегировать несколько вызовов в одну запись
            **decorator_kwargs: Дополнительные параметры для логирования
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def wrapper(*args, **kwargs) -> Any:
                # Получаем информацию о функции
                module_name = f.__module__
                file_path = f.__code__.co_filename if hasattr(f, '__code__') else None
                
                # Сбрасываем статистику памяти перед выполнением
                if self.enable_memory_tracking:
                    tracemalloc.clear_traces()
                
                # Замеряем время
                start_wall_time = time.perf_counter()
                start_cpu_time = self.get_cpu_time()
                
                success = True
                result = None
                error_message = None
                call_count = 1
                
                try:
                    result = f(*args, **kwargs)
                    return result
                    
                except Exception as e:
                    success = False
                    error_message = f"{type(e).__name__}: {str(e)}"
                    raise
                    
                finally:
                    # Вычисляем время выполнения
                    end_wall_time = time.perf_counter()
                    end_cpu_time = self.get_cpu_time()
                    
                    wall_time_ms = (end_wall_time - start_wall_time) * 1000
                    cpu_time_ms = end_cpu_time - start_cpu_time
                    
                    # Получаем статистику
                    memory_stats = self.get_memory_stats()
                    system_metrics = self.get_system_metrics()
                    
                    # Подготавливаем дополнительные данные
                    args_hash = str(hash(str(args) + str(kwargs)))[:16] if args or kwargs else None
                    result_type = type(result).__name__ if result is not None else "None"
                    thread_id = threading.get_ident()
                    
                    # Логируем метрику
                    self.log_metric(
                        function_name=f.__name__,
                        cpu_time_ms=cpu_time_ms,
                        wall_time_ms=wall_time_ms,
                        success=success,
                        memory_stats=memory_stats,
                        system_metrics=system_metrics,
                        module_name=module_name,
                        file_path=file_path,
                        args_hash=args_hash,
                        result_type=result_type,
                        error_message=error_message,
                        thread_id=thread_id,
                        call_count=call_count,
                        **decorator_kwargs
                    )
                    
                    # Выводим в консоль (опционально)
                    status = "✅" if success else "❌"
                    cpu_color = "\033[92m" if cpu_time_ms < 10 else "\033[93m" if cpu_time_ms < 100 else "\033[91m"
                    wall_color = "\033[92m" if wall_time_ms < 10 else "\033[93m" if wall_time_ms < 100 else "\033[91m"
                    reset_color = "\033[0m"
                    
                    print(f"{status} {f.__name__} | "
                          f"{cpu_color}CPU: {cpu_time_ms:.2f}ms{reset_color} | "
                          f"{wall_color}WALL: {wall_time_ms:.2f}ms{reset_color} | "
                          f"CPU%: {(cpu_time_ms/wall_time_ms*100 if wall_time_ms > 0 else 0):.1f}% | "
                          f"Mem: {memory_stats.get('peak_mb', 0):.2f}MB")
            
            return wrapper
        
        # Позволяет использовать декоратор как с аргументами, так и без
        if func is None:
            return decorator
        return decorator(func)
    
    @contextmanager
    def trace_block(self, block_name: str, **kwargs):
        """
        Контекстный менеджер для трассировки блока кода.
        
        Args:
            block_name: Имя блока кода
            **kwargs: Дополнительные параметры
        """
        module_name = kwargs.get('module_name', 'block')
        file_path = kwargs.get('file_path', None)
        
        # Сбрасываем статистику памяти перед выполнением
        if self.enable_memory_tracking:
            tracemalloc.clear_traces()
        
        # Замеряем время
        start_wall_time = time.perf_counter()
        start_cpu_time = self.get_cpu_time()
        
        success = True
        error_message = None
        
        try:
            yield
        except Exception as e:
            success = False
            error_message = f"{type(e).__name__}: {str(e)}"
            raise
        finally:
            # Вычисляем время выполнения
            end_wall_time = time.perf_counter()
            end_cpu_time = self.get_cpu_time()
            
            wall_time_ms = (end_wall_time - start_wall_time) * 1000
            cpu_time_ms = end_cpu_time - start_cpu_time
            
            # Получаем статистику
            memory_stats = self.get_memory_stats()
            system_metrics = self.get_system_metrics()
            
            # Логируем метрику
            self.log_metric(
                function_name=block_name,
                cpu_time_ms=cpu_time_ms,
                wall_time_ms=wall_time_ms,
                success=success,
                memory_stats=memory_stats,
                system_metrics=system_metrics,
                module_name=module_name,
                file_path=file_path,
                error_message=error_message
            )
    
    def get_statistics(
        self, 
        function_name: Optional[str] = None, 
        limit: int = 100,
        group_by_function: bool = False
    ) -> list:
        """Получение статистики из базы данных."""
        try:
            with self.get_session() as session:
                if group_by_function:
                    from sqlalchemy import func
                    
                    query = session.query(
                        PerformanceMetric.function_name,
                        func.count(PerformanceMetric.id).label('call_count'),
                        func.avg(PerformanceMetric.cpu_time_ms).label('avg_cpu_time'),
                        func.avg(PerformanceMetric.wall_time_ms).label('avg_wall_time'),
                        func.avg(PerformanceMetric.cpu_percent).label('avg_cpu_percent'),
                        func.sum(PerformanceMetric.cpu_time_ms).label('total_cpu_time'),
                        func.sum(PerformanceMetric.wall_time_ms).label('total_wall_time'),
                        func.sum(PerformanceMetric.success).label('success_count'),
                        (func.count(PerformanceMetric.id) - func.sum(PerformanceMetric.success)).label('error_count')
                    )
                    
                    if function_name:
                        query = query.filter(PerformanceMetric.function_name == function_name)
                    
                    results = query.group_by(PerformanceMetric.function_name).all()
                    
                    stats = []
                    for r in results:
                        stats.append({
                            "function": r.function_name,
                            "calls": r.call_count,
                            "avg_cpu_ms": f"{r.avg_cpu_time:.2f}",
                            "avg_wall_ms": f"{r.avg_wall_time:.2f}",
                            "avg_cpu_percent": f"{r.avg_cpu_percent:.1f}",
                            "total_cpu_ms": f"{r.total_cpu_time:.2f}",
                            "total_wall_ms": f"{r.total_wall_time:.2f}",
                            "success_rate": f"{(r.success_count/r.call_count*100):.1f}%" if r.call_count > 0 else "0%"
                        })
                    
                    return stats
                
                else:
                    query = session.query(PerformanceMetric)
                    
                    if function_name:
                        query = query.filter(PerformanceMetric.function_name == function_name)
                    
                    metrics = query.order_by(PerformanceMetric.timestamp.desc()).limit(limit).all()
                    
                    # Форматируем вывод
                    stats = []
                    for m in metrics:
                        stats.append({
                            "id": m.id,
                            "timestamp": m.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                            "function": m.function_name,
                            "cpu_ms": f"{m.cpu_time_ms:.2f}",
                            "wall_ms": f"{m.wall_time_ms:.2f}",
                            "cpu_percent": f"{m.cpu_percent:.1f}",
                            "status": "✅" if m.success else "❌",
                            "memory_mb": f"{m.memory_peak_mb:.2f}" if m.memory_peak_mb else "N/A",
                            "thread": m.thread_id
                        })
                    
                    return stats
                
        except Exception as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return []
    
    def get_memory_statistics(self) -> Dict:
        """Получение статистики по использованию памяти."""
        if not self.enable_memory_tracking:
            return {}
        
        try:
            with self.get_session() as session:
                from sqlalchemy import func
                
                # Получаем топ функций по использованию памяти
                memory_stats = session.query(
                    PerformanceMetric.function_name,
                    func.max(PerformanceMetric.memory_peak_mb).label('max_memory'),
                    func.avg(PerformanceMetric.memory_peak_mb).label('avg_memory'),
                    func.count(PerformanceMetric.id).label('call_count')
                ).filter(PerformanceMetric.memory_peak_mb.isnot(None)) \
                 .group_by(PerformanceMetric.function_name) \
                 .order_by(func.max(PerformanceMetric.memory_peak_mb).desc()) \
                 .limit(10) \
                 .all()
                
                return {
                    "top_memory_consumers": [
                        {
                            "function": r.function_name,
                            "max_mb": f"{r.max_memory:.2f}",
                            "avg_mb": f"{r.avg_memory:.2f}",
                            "calls": r.call_count
                        }
                        for r in memory_stats
                    ]
                }
                
        except Exception as e:
            print(f"❌ Ошибка получения статистики памяти: {e}")
            return {}
    
    def get_call_statistics(self) -> Dict:
        """Получение статистики вызовов из памяти."""
        return dict(self.call_stats)
    
    def update_function_statistics(self) -> None:
        """Обновление агрегированной статистики по функциям на основе performance_metrics."""
        try:
            with self.get_session() as session:
                from sqlalchemy import func, case
                
                # Получаем агрегированные данные из performance_metrics
                stats_query = session.query(
                    PerformanceMetric.function_name,
                    PerformanceMetric.module_name,
                    PerformanceMetric.file_path,
                    func.count(PerformanceMetric.id).label('total_calls'),
                    func.sum(case((PerformanceMetric.success == 1, 1), else_=0)).label('success_count'),
                    func.sum(case((PerformanceMetric.success == 0, 1), else_=0)).label('error_count'),
                    func.sum(PerformanceMetric.cpu_time_ms).label('total_cpu_time'),
                    func.avg(PerformanceMetric.cpu_time_ms).label('avg_cpu_time'),
                    func.min(PerformanceMetric.cpu_time_ms).label('min_cpu_time'),
                    func.max(PerformanceMetric.cpu_time_ms).label('max_cpu_time'),
                    func.sum(PerformanceMetric.wall_time_ms).label('total_wall_time'),
                    func.avg(PerformanceMetric.wall_time_ms).label('avg_wall_time'),
                    func.min(PerformanceMetric.wall_time_ms).label('min_wall_time'),
                    func.max(PerformanceMetric.wall_time_ms).label('max_wall_time'),
                    func.avg(PerformanceMetric.cpu_percent).label('avg_cpu_percent'),
                    func.max(PerformanceMetric.cpu_percent).label('max_cpu_percent'),
                    func.avg(PerformanceMetric.memory_peak_mb).label('avg_memory'),
                    func.max(PerformanceMetric.memory_peak_mb).label('max_memory'),
                    func.min(PerformanceMetric.timestamp).label('first_call'),
                    func.max(PerformanceMetric.timestamp).label('last_call')
                ).group_by(
                    PerformanceMetric.function_name,
                    PerformanceMetric.module_name,
                    PerformanceMetric.file_path
                )
                
                results = stats_query.all()
                
                # Очищаем старую статистику
                session.query(FunctionStatistics).delete()
                
                # Добавляем новую статистику
                for row in results:
                    # Извлекаем папку из пути к файлу
                    folder_name = None
                    if row.file_path:
                        try:
                            import os
                            path_parts = os.path.normpath(row.file_path).split(os.sep)
                            # Ищем имя папки (обычно предпоследняя часть пути)
                            if len(path_parts) >= 2:
                                folder_name = path_parts[-2]
                        except Exception:
                            pass
                    
                    # Создаем полное имя функции
                    full_name = f"{folder_name}.{row.module_name}.{row.function_name}" if folder_name and row.module_name else \
                                f"{row.module_name}.{row.function_name}" if row.module_name else \
                                row.function_name
                    
                    stat = FunctionStatistics(
                        folder_name=folder_name,
                        module_name=row.module_name,
                        function_name=full_name,
                        total_calls=row.total_calls or 0,
                        success_count=row.success_count or 0,
                        error_count=row.error_count or 0,
                        total_cpu_time_ms=row.total_cpu_time or 0.0,
                        avg_cpu_time_ms=row.avg_cpu_time or 0.0,
                        min_cpu_time_ms=row.min_cpu_time,
                        max_cpu_time_ms=row.max_cpu_time,
                        total_wall_time_ms=row.total_wall_time or 0.0,
                        avg_wall_time_ms=row.avg_wall_time or 0.0,
                        min_wall_time_ms=row.min_wall_time,
                        max_wall_time_ms=row.max_wall_time,
                        avg_cpu_percent=row.avg_cpu_percent or 0.0,
                        max_cpu_percent=row.max_cpu_percent,
                        avg_memory_mb=row.avg_memory,
                        max_memory_mb=row.max_memory,
                        first_call=row.first_call,
                        last_call=row.last_call
                    )
                    session.add(stat)
                
                session.commit()
                print(f"✅ Статистика обновлена для {len(results)} функций")
                
        except Exception as e:
            print(f"❌ Ошибка обновления статистики: {e}")
            import traceback
            traceback.print_exc()
    
    def get_function_statistics(
        self,
        folder: Optional[str] = None,
        module: Optional[str] = None,
        function: Optional[str] = None,
        order_by: str = 'total_calls',
        limit: int = 50
    ) -> list:
        """
        Получение агрегированной статистики по функциям.
        
        Args:
            folder: Фильтр по папке
            module: Фильтр по модулю
            function: Фильтр по имени функции
            order_by: Поле для сортировки (total_calls, avg_cpu_time_ms, error_count и т.д.)
            limit: Максимальное количество записей
        
        Returns:
            Список словарей со статистикой
        """
        try:
            with self.get_session() as session:
                query = session.query(FunctionStatistics)
                
                # Применяем фильтры
                if folder:
                    query = query.filter(FunctionStatistics.folder_name == folder)
                if module:
                    query = query.filter(FunctionStatistics.module_name.like(f"%{module}%"))
                if function:
                    query = query.filter(FunctionStatistics.function_name.like(f"%{function}%"))
                
                # Сортировка
                if hasattr(FunctionStatistics, order_by):
                    query = query.order_by(getattr(FunctionStatistics, order_by).desc())
                else:
                    query = query.order_by(FunctionStatistics.total_calls.desc())
                
                results = query.limit(limit).all()
                
                # Форматируем вывод
                stats = []
                for stat in results:
                    success_rate = (stat.success_count / stat.total_calls * 100) if stat.total_calls > 0 else 0.0
                    
                    stats.append({
                        'function_name': stat.function_name,
                        'folder': stat.folder_name or 'N/A',
                        'module': stat.module_name or 'N/A',
                        'total_calls': stat.total_calls,
                        'success_count': stat.success_count,
                        'error_count': stat.error_count,
                        'success_rate': f"{success_rate:.1f}%",
                        'total_cpu_time_ms': f"{stat.total_cpu_time_ms:.2f}",
                        'avg_cpu_time_ms': f"{stat.avg_cpu_time_ms:.2f}",
                        'min_cpu_time_ms': f"{stat.min_cpu_time_ms:.2f}" if stat.min_cpu_time_ms else "N/A",
                        'max_cpu_time_ms': f"{stat.max_cpu_time_ms:.2f}" if stat.max_cpu_time_ms else "N/A",
                        'total_wall_time_ms': f"{stat.total_wall_time_ms:.2f}",
                        'avg_wall_time_ms': f"{stat.avg_wall_time_ms:.2f}",
                        'min_wall_time_ms': f"{stat.min_wall_time_ms:.2f}" if stat.min_wall_time_ms else "N/A",
                        'max_wall_time_ms': f"{stat.max_wall_time_ms:.2f}" if stat.max_wall_time_ms else "N/A",
                        'avg_cpu_percent': f"{stat.avg_cpu_percent:.1f}%" if stat.avg_cpu_percent else "N/A",
                        'max_cpu_percent': f"{stat.max_cpu_percent:.1f}%" if stat.max_cpu_percent else "N/A",
                        'avg_memory_mb': f"{stat.avg_memory_mb:.2f}" if stat.avg_memory_mb else "N/A",
                        'max_memory_mb': f"{stat.max_memory_mb:.2f}" if stat.max_memory_mb else "N/A",
                        'first_call': stat.first_call.strftime("%Y-%m-%d %H:%M:%S") if stat.first_call else "N/A",
                        'last_call': stat.last_call.strftime("%Y-%m-%d %H:%M:%S") if stat.last_call else "N/A"
                    })
                
                return stats
                
        except Exception as e:
            print(f"❌ Ошибка получения статистики: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def print_function_statistics_report(self, limit: int = 20) -> None:
        """Вывод отчета по агрегированной статистике функций."""
        print("\n" + "=" * 100)
        print("АГРЕГИРОВАННАЯ СТАТИСТИКА ПО ФУНКЦИЯМ")
        print("=" * 100)
        
        stats = self.get_function_statistics(limit=limit, order_by='total_calls')
        
        if not stats:
            print("📊 Статистика пока отсутствует. Запустите update_function_statistics() для обновления.")
            return
        
        print(f"\n{'Функция':<50} {'Вызовы':<10} {'Ошибки':<10} {'Успех':<10} {'Сред.CPU':<12} {'Сред.Wall':<12}")
        print("-" * 100)
        
        for stat in stats:
            print(f"{stat['function_name'][:48]:<50} "
                  f"{stat['total_calls']:<10} "
                  f"{stat['error_count']:<10} "
                  f"{stat['success_rate']:<10} "
                  f"{stat['avg_cpu_time_ms']:>10}ms "
                  f"{stat['avg_wall_time_ms']:>10}ms")
        
        print("\n" + "=" * 100)
    
    def clear_metrics(self) -> None:
        """Очистка всех метрик."""
        try:
            with self.get_session() as session:
                session.query(PerformanceMetric).delete()
                session.query(FunctionStatistics).delete()
                session.commit()
                self.call_stats.clear()
                print("✅ Все метрики очищены")
        except Exception as e:
            print(f"❌ Ошибка очистки метрик: {e}")
    
    def export_report(self, output_file: str = "performance_report.txt") -> None:
        """Экспорт отчета о производительности."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 100 + "\n")
                f.write("ОТЧЕТ О ПРОИЗВОДИТЕЛЬНОСТИ\n")
                f.write("=" * 100 + "\n\n")
                
                f.write(f"Система: {platform.system()} {platform.release()}\n")
                f.write(f"Процессор: {platform.processor()}\n")
                f.write(f"Python: {platform.python_version()}\n")
                f.write(f"Время создания отчета: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Агрегированная статистика по функциям
                f.write("=" * 100 + "\n")
                f.write("АГРЕГИРОВАННАЯ СТАТИСТИКА ПО ФУНКЦИЯМ (из таблицы function_statistics)\n")
                f.write("=" * 100 + "\n\n")
                
                func_stats = self.get_function_statistics(limit=100, order_by='total_calls')
                
                if func_stats:
                    for stat in func_stats:
                        f.write(f"\n{'─' * 100}\n")
                        f.write(f"📊 Функция: {stat['function_name']}\n")
                        f.write(f"{'─' * 100}\n")
                        f.write(f"  📁 Папка:              {stat['folder']}\n")
                        f.write(f"  📦 Модуль:             {stat['module']}\n")
                        f.write(f"\n  📞 Вызовы:\n")
                        f.write(f"     • Всего вызовов:    {stat['total_calls']}\n")
                        f.write(f"     • Успешных:         {stat['success_count']}\n")
                        f.write(f"     • Ошибок:           {stat['error_count']}\n")
                        f.write(f"     • Успешность:       {stat['success_rate']}\n")
                        f.write(f"\n  ⏱️  CPU время:\n")
                        f.write(f"     • Общее:            {stat['total_cpu_time_ms']} мс\n")
                        f.write(f"     • Среднее:          {stat['avg_cpu_time_ms']} мс\n")
                        f.write(f"     • Минимальное:      {stat['min_cpu_time_ms']} мс\n")
                        f.write(f"     • Максимальное:     {stat['max_cpu_time_ms']} мс\n")
                        f.write(f"\n  ⏰ Реальное время:\n")
                        f.write(f"     • Общее:            {stat['total_wall_time_ms']} мс\n")
                        f.write(f"     • Среднее:          {stat['avg_wall_time_ms']} мс\n")
                        f.write(f"     • Минимальное:      {stat['min_wall_time_ms']} мс\n")
                        f.write(f"     • Максимальное:     {stat['max_wall_time_ms']} мс\n")
                        f.write(f"\n  💻 Процессор:\n")
                        f.write(f"     • Средний %:        {stat['avg_cpu_percent']}\n")
                        f.write(f"     • Максимальный %:   {stat['max_cpu_percent']}\n")
                        f.write(f"\n  🧠 Память:\n")
                        f.write(f"     • Средняя:          {stat['avg_memory_mb']} MB\n")
                        f.write(f"     • Максимальная:     {stat['max_memory_mb']} MB\n")
                        f.write(f"\n  📅 Временные метки:\n")
                        f.write(f"     • Первый вызов:     {stat['first_call']}\n")
                        f.write(f"     • Последний вызов:  {stat['last_call']}\n")
                else:
                    f.write("  ⚠️  Агрегированная статистика отсутствует.\n")
                    f.write("     Запустите update_function_statistics() для её создания.\n")
                
                # Детальная статистика по функциям (старый метод для сравнения)
                f.write("\n\n" + "=" * 100 + "\n")
                f.write("ДЕТАЛЬНАЯ СТАТИСТИКА (с группировкой из performance_metrics)\n")
                f.write("=" * 100 + "\n\n")
                
                stats = self.get_statistics(group_by_function=True)
                for stat in stats:
                    f.write(f"\nФункция: {stat['function']}\n")
                    f.write(f"  Вызовов: {stat['calls']}\n")
                    f.write(f"  Среднее CPU время: {stat['avg_cpu_ms']} мс\n")
                    f.write(f"  Среднее реальное время: {stat['avg_wall_ms']} мс\n")
                    f.write(f"  Средний % CPU: {stat['avg_cpu_percent']}%\n")
                    f.write(f"  Общее CPU время: {stat['total_cpu_ms']} мс\n")
                    f.write(f"  Общее реальное время: {stat['total_wall_ms']} мс\n")
                    f.write(f"  Успешных вызовов: {stat['success_rate']}\n")
                
                # Потребление памяти
                f.write("\n\n" + "=" * 100 + "\n")
                f.write("ПОТРЕБЛЕНИЕ ПАМЯТИ\n")
                f.write("=" * 100 + "\n\n")
                
                memory_stats = self.get_memory_statistics()
                if memory_stats.get('top_memory_consumers'):
                    for mem in memory_stats['top_memory_consumers']:
                        f.write(f"\nФункция: {mem['function']}\n")
                        f.write(f"  Макс. память: {mem['max_mb']} MB\n")
                        f.write(f"  Сред. память: {mem['avg_mb']} MB\n")
                        f.write(f"  Вызовов: {mem['calls']}\n")
                
                f.write("\n" + "=" * 100 + "\n")
                f.write("КОНЕЦ ОТЧЕТА\n")
                f.write("=" * 100 + "\n")
                
            print(f"✅ Отчет сохранен в {output_file}")
            
        except Exception as e:
            print(f"❌ Ошибка экспорта отчета: {e}")

# Глобальный экземпляр трассировщика
from project_paths import get_cpu_tracer_db_path

cpu_tracer = CPUTracer(db_path=str(get_cpu_tracer_db_path()))

# Удобный декоратор для быстрого использования
def trace_cpu(func=None, **kwargs):
    """Декоратор для трассировки функции с CPU временем."""
    return cpu_tracer.trace_function(func, **kwargs)

