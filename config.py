# -*- coding: utf-8 -*-
"""
УСТАРЕВШИЙ МОДУЛЬ - Используйте config_manager.py

Этот файл оставлен для обратной совместимости.
Все настройки теперь хранятся в app_config.json и управляются через config_manager.py

Для новых проектов используйте:
    from config_manager import get_ai_model, get_ai_temperature, log_info, ...
"""

import os
import warnings

# Предупреждение при импорте (можно закомментировать после миграции)
# warnings.warn(
#     "config.py устарел. Используйте config_manager.py для доступа к настройкам.",
#     DeprecationWarning,
#     stacklevel=2
# )

# Импортируем из нового менеджера конфигурации
try:
    from config_manager import (
        AI_LOGS,
        APP_TITLE,
        DATABASE_NAME,
        DATABASE_URL,
        SESSION_STATE_KEY,
        USER_ROLES,
        MIN_NAME_LENGTH,
        MIN_PASSWORD_LENGTH,
        CHAT_BOT_NAME,
        CHAT_SYSTEM_MESSAGE,
        OPENAI_API_KEY,
        PAGE_CONFIG,
        # Дополнительные функции для удобства
        get_ai_model,
        get_ai_temperature,
        get_ai_max_tokens,
        log_info,
        log_error,
        log_warning,
        is_logging_enabled,
        is_ai_logs_enabled,
    )
except ImportError as e:
    # Если config_manager не доступен, используем значения по умолчанию
    print(f"[CONFIG WARNING] Не удалось импортировать config_manager: {e}")
    print("[CONFIG WARNING] Используются значения по умолчанию")
    
    AI_LOGS = True
    APP_TITLE = "Система регистрации учителей и учеников"
    DATABASE_NAME = "users.db"
    SESSION_STATE_KEY = "user_session"
    DATABASE_URL = f"sqlite:///{DATABASE_NAME}"
    USER_ROLES = ["Ученик", "Учитель"]
    MIN_NAME_LENGTH = 2
    MIN_PASSWORD_LENGTH = 6
    CHAT_BOT_NAME = "Помощник"
    CHAT_SYSTEM_MESSAGE = """Вы - дружелюбный помощник в образовательной системе. 
Помогайте пользователям с вопросами о регистрации, навигации по сайту и общими вопросами об образовании.
Отвечайте вежливо и по существу на русском языке."""
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PAGE_CONFIG = {
        "page_title": APP_TITLE,
        "page_icon": "🎓",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
