"""
Экспортер метрик OpenTelemetry в SQLite
"""
from opentelemetry.sdk.metrics.export import MetricExporter, MetricExportResult, AggregationTemporality
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path

from logger.models import Base, FunctionMetric

class SQLiteMetricExporter(MetricExporter):
    """Экспортер метрик в SQLite"""
    
    METRIC_TYPES = {'error': 'error', 'time': 'time', 'duration': 'time', 'call': 'call'}
    
    def __init__(self, db_path=None):
        """Инициализация экспортера"""
        self._preferred_temporality = {}
        self._preferred_aggregation = {}
        
        self.db_path = str(db_path if db_path else self._get_default_db_path())
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        print(f"[Exporter] Initialized: {self.db_path}")
    
    def _get_default_db_path(self):
        """Получить путь к БД по умолчанию"""
        project_root = Path(__file__).resolve().parent.parent
        return project_root / "logger" / "reports" / "metrics.db"
    
    def export(self, metrics_data, timeout_millis=10000, **kwargs):
        """Экспорт метрик в SQLite"""
        session = self.SessionLocal()
        try:
            timestamp = datetime.utcnow()
            records = [
                record
                for res_metric in metrics_data.resource_metrics
                for scope_metric in res_metric.scope_metrics
                for metric in scope_metric.metrics
                if hasattr(metric.data, 'data_points')
                for point in metric.data.data_points
                if (record := self._process_point(metric, point, timestamp))
            ]
            
            session.add_all(records)
            session.commit()
            
            if records:
                print(f"[Exporter] Saved {len(records)} metrics at {timestamp.strftime('%H:%M:%S')}")
            
            return MetricExportResult.SUCCESS
        except Exception as e:
            session.rollback()
            print(f"[Exporter] Error: {e}")
            return MetricExportResult.FAILURE
        finally:
            session.close()
    
    def _process_point(self, metric, point, timestamp):
        """Обработка точки данных"""
        attrs = {k: v for k, v in (point.attributes.items() if hasattr(point, 'attributes') and point.attributes else [])}
        full_name = self._build_function_name(attrs)
        metric_type = self._get_metric_type(metric.name)
        
        # Histogram (time)
        if hasattr(point, 'count') and hasattr(point, 'sum'):
            calls = point.count
            total = round(point.sum, 4)
            return FunctionMetric(
                function=full_name,
                metric_type='time',
                timestamp=timestamp,
                calls=calls,
                avg_time=round(total / calls, 4) if calls > 0 else 0.0,
                total_time=total,
                min_time=round(point.min, 4) if hasattr(point, 'min') and point.min else 0.0,
                max_time=round(point.max, 4) if hasattr(point, 'max') and point.max else 0.0,
                errors=0,
                error_type=''
            )
        
        # Counter (calls/errors)
        if hasattr(point, 'value'):
            value = int(point.value)
            is_error = metric_type == 'error'
            return FunctionMetric(
                function=full_name,
                metric_type=metric_type,
                timestamp=timestamp,
                calls=0 if is_error else value,
                avg_time=0.0,
                total_time=0.0,
                min_time=0.0,
                max_time=0.0,
                errors=value if is_error else 0,
                error_type=attrs.get('error', '') if is_error else ''
            )
        
        return None
    
    def _build_function_name(self, attrs):
        """Построить полное имя: folder.module.function"""
        module = attrs.get('module', 'unknown')
        function = attrs.get('function', 'unknown')
        
        # Преобразуем module в формат folder.module
        parts = module.split('.')
        if len(parts) >= 2:
            # Например: bot.testing → bot.testing
            # database.database → database.database
            return f"{module}.{function}"
        return f"{module}.{function}"
    
    def _get_metric_type(self, name):
        """Определить тип метрики"""
        name_lower = name.lower()
        for key, value in self.METRIC_TYPES.items():
            if key in name_lower:
                return value
        return 'call'
    
    def shutdown(self, timeout_millis=30000, **kwargs):
        """Закрытие экспортера"""
        return True
    
    def force_flush(self, timeout_millis=10000):
        """Принудительная отправка"""
        return True
