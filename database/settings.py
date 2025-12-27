from pathlib import Path

DATABASE_DIR = Path(__file__).parent.resolve()
DATABASE_NAME = "users.db"
DATABASE_PATH = DATABASE_DIR / DATABASE_NAME
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
SESSION_STATE_KEY = "user_session"
USER_ROLES = ["Ученик", "Учитель"]