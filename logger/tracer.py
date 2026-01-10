"""
Система трассировки функций с сохранением в SQLite через OpenTelemetry
"""
import time
import functools
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Импорт экспортера
try:
    from logger.exporter import SQLiteMetricExporter
    EXPORTER_AVAILABLE = True
except Exception as e:
    print(f"[Tracer] Failed to load exporter: {e}")
    EXPORTER_AVAILABLE = False

# ============= Инициализация OpenTelemetry =============

if EXPORTER_AVAILABLE:
    try:
        sqlite_exporter = SQLiteMetricExporter()
        metric_reader = PeriodicExportingMetricReader(
            exporter=sqlite_exporter,
            export_interval_millis=60000  # 60 секунд
        )
        meter_provider = MeterProvider(metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)
        print("[Tracer] Monitoring system initialized")
    except Exception as e:
        print(f"[Tracer] Init error: {e}")
        meter_provider = MeterProvider()
        metrics.set_meter_provider(meter_provider)
else:
    meter_provider = MeterProvider()
    metrics.set_meter_provider(meter_provider)
    print("[Tracer] Running without export")

# ============= Инструменты =============

meter = metrics.get_meter(__name__)

call_counter = meter.create_counter("function_calls", description="Total calls")
error_counter = meter.create_counter("function_errors", description="Total errors")
time_histogram = meter.create_histogram("function_time", description="Execution time (sec)")

# ============= Декоратор =============

def trace(func):
    """
    Декоратор трассировки функции
    
    Автоматически логирует:
    - Количество вызовов
    - Время выполнения (округлено до 4 знаков)
    - Ошибки с типами
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        module_name = func.__module__
        func_name = func.__name__
        attrs = {"module": module_name, "function": func_name}
        
        call_counter.add(1, attrs)
        
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error_counter.add(1, {**attrs, "error": type(e).__name__})
            raise
        finally:
            duration = round(time.perf_counter() - start, 4)
            time_histogram.record(duration, attrs)
    
    return wrapper

# ============= Утилиты =============

def flush():
    """Принудительно экспортировать метрики в БД"""
    try:
        meter_provider.force_flush()
        print("[Tracer] Metrics flushed")
        return True
    except Exception as e:
        print(f"[Tracer] Flush error: {e}")
        return False

def shutdown():
    """Корректное завершение трассировки"""
    try:
        meter_provider.shutdown()
        print("[Tracer] Shutdown complete")
        return True
    except Exception as e:
        print(f"[Tracer] Shutdown error: {e}")
        return False
