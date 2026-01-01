# requirements.txt
# dataset

# metrics.py
import dataset
from pathlib import Path

# Ваши классы-маркеры (для совместимости с вашим синтаксисом)

class Column:
    def __init__(self, name): self.name = name

class Unique(Column): ...
class Summation(Column): ...
class Minimal(Column): ...
class Maximal(Column): ...
class Mean(Column): ...

class Table:
    def __init__(self, db_path: str, *columns):
        # Создаём директорию
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Подключаемся к БД
        self.db = dataset.connect(f'sqlite:///{db_path}')
        self.table = self.db['metrics']
        
        # Сохраняем информацию о колонках для агрегации
        self.columns = columns
        self.primary_key = next(col.name for col in columns if isinstance(col, Unique))
    
    def write(self, **data):
        existing = self.table.find_one(**{self.primary_key: data[self.primary_key]})
        
        if existing:
            for col in self.columns:
                col_name = col.name
                if col_name in data:
                    if isinstance(col, Summation):
                        # Суммирование
                        data[col_name] = existing.get(col_name, 0) + data[col_name]
                    
                    elif isinstance(col, Minimal):
                        # Минимум
                        old_val = existing.get(col_name)
                        new_val = data[col_name]
                        if old_val is None or new_val < old_val:
                            data[col_name] = new_val
                        else:
                            data[col_name] = old_val
                    
                    elif isinstance(col, Maximal):
                        # Максимум
                        old_val = existing.get(col_name)
                        new_val = data[col_name]
                        if old_val is None or new_val > old_val:
                            data[col_name] = new_val
                        else:
                            data[col_name] = old_val
                    
                    elif isinstance(col, Mean):
                        # Среднее - нужна отдельная логика
                        # Для простоты храним сумму и количество
                        sum_col = f'_{col_name}_sum'
                        count_col = f'_{col_name}_count'
                        
                        # Инициализируем если нет
                        if sum_col not in existing:
                            existing[sum_col] = 0
                            existing[count_col] = 0
                        
                        # Обновляем сумму и количество
                        new_sum = existing[sum_col] + data[col_name]
                        new_count = existing[count_col] + 1
                        
                        # Сохраняем вспомогательные поля
                        data[sum_col] = new_sum
                        data[count_col] = new_count
                        
                        # Вычисляем новое среднее
                        data[col_name] = new_sum / new_count if new_count > 0 else 0
            
            self.table.update(data, [self.primary_key])
        else:
            for col in self.columns:
                if isinstance(col, Mean):
                    col_name = col.name
                    sum_col = f'_{col_name}_sum'
                    count_col = f'_{col_name}_count'
                    
                    data[sum_col] = data.get(col_name, 0)
                    data[count_col] = 1 if col_name in data else 0
            
            # Вставляем новую запись
            self.table.insert(data)
    
    def read(self, key: str = None):
        """Чтение данных"""
        if key:
            return self.table.find(**{self.primary_key: key})
        else:
            return self.table.all()
