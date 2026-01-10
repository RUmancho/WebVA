"""
Модели для хранения метрик в SQLite
"""
from sqlalchemy import Column, String, Float, DateTime, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path

Base = declarative_base()

class FunctionMetric(Base):
    """Таблица метрик функций без ID (составной первичный ключ)"""
    __tablename__ = 'function_metrics'
    
    # Составной первичный ключ: function + metric_type + timestamp
    function = Column(String(300), primary_key=True, index=True)  # folder.module.function
    metric_type = Column(String(20), primary_key=True)  # 'call', 'error', 'time'
    timestamp = Column(DateTime, primary_key=True, index=True, default=datetime.utcnow)
    
    # Метрики
    calls = Column(Integer, nullable=False, default=0)
    avg_time = Column(Float, nullable=False, default=0.0)
    total_time = Column(Float, nullable=False, default=0.0)
    min_time = Column(Float, nullable=False, default=0.0)
    max_time = Column(Float, nullable=False, default=0.0)
    errors = Column(Integer, nullable=False, default=0)
    error_type = Column(String(100), nullable=False, default='')
    
    def __repr__(self):
        if self.metric_type == 'time':
            return f"<{self.function}: avg={self.avg_time:.4f}s, calls={self.calls}>"
        elif self.metric_type == 'error':
            return f"<{self.function}: errors={self.errors}, type={self.error_type}>"
        return f"<{self.function}: calls={self.calls}>"


def get_metrics_db_path():
    """Получить абсолютный путь к базе данных метрик"""
    from pathlib import Path
    current_file = Path(__file__).resolve()
    logger_dir = current_file.parent  # logger/
    project_root = logger_dir.parent  # E:\Python\Sites\WebVA\
    return project_root / "logger" / "reports" / "metrics.db"

def init_metrics_db(db_path=None, recreate=False):
    """Инициализация базы данных метрик"""
    try:
        if db_path is None:
            db_path = get_metrics_db_path()
        
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        engine = create_engine(f'sqlite:///{db_path}', echo=False)
        
        if recreate:
            Base.metadata.drop_all(engine)
        
        Base.metadata.create_all(engine)
        
        print(f"[Metrics DB] База данных инициализирована: {db_path}")
        return True
    except Exception as e:
        print(f"[Metrics DB] Ошибка инициализации: {e}")
        return False

