"""
Пакет формул для физических и математических расчетов
"""
# Импортируем formula_manager из UI
import sys
from pathlib import Path

# Получаем путь к корню проекта
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent

# Добавляем корневую директорию проекта в sys.path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Импортируем formula_manager
from UI.formulas import formula_manager

__all__ = ['formula_manager']

