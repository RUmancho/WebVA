import os

from project_paths import ensure_data_dirs, get_users_db_path

ensure_data_dirs()

DATABASE_PATH = get_users_db_path()
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")
SESSION_STATE_KEY = "user_session"
USER_ROLES = ["Ученик", "Учитель"]