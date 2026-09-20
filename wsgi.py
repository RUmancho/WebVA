"""Точка входа для production-деплоя (Amvera и другие WSGI-хостинги)."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from project_paths import ensure_data_dirs

ensure_data_dirs()

from UI.app import app

application = app
