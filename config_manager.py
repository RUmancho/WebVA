# -*- coding: utf-8 -*-
"""
Менеджер конфигурации приложения
Централизованное управление всеми настройками проекта через JSON файл
"""

import json
import os
from functools import wraps
from typing import Any, Dict, Optional

CONFIG_FILE = "app_config.json"
_CONFIG_CACHE = {}

def load_config() -> Dict[str, Any]:
    """Загрузка конфигурации из JSON файла"""
    global _CONFIG_CACHE
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                _CONFIG_CACHE = json.load(f)
                print(f"[CONFIG] Конфигурация загружена из {CONFIG_FILE}")
        else:
            print(f"[CONFIG ERROR] Файл {CONFIG_FILE} не найден!")
            _CONFIG_CACHE = _get_default_config()
    except Exception as e:
        print(f"[CONFIG ERROR] Ошибка при загрузке конфигурации: {e}")
        _CONFIG_CACHE = _get_default_config()
    
    return _CONFIG_CACHE

def _get_default_config() -> Dict[str, Any]:
    """Возвращает конфигурацию по умолчанию"""
    return {
        "app": {"title": "Образовательная платформа"},
        "database": {"name": "users.db"},
        "ai_models": {"temperature": 0.3, "default_model": "gpt-4o-mini"},
        "logging": {"global_logging": True, "ai_logs": True, "enabled": {}}
    }

def get_config(section: Optional[str] = None, key: Optional[str] = None, default: Any = None) -> Any:
    """
    Получить значение из конфигурации
    
    Args:
        section: Секция конфигурации (например, 'ai_models')
        key: Ключ в секции (например, 'temperature')
        default: Значение по умолчанию, если ключ не найден
    
    Returns:
        Значение из конфигурации или default
    
    Examples:
        get_config('ai_models', 'temperature')  # Вернет 0.3
        get_config('ai_models')  # Вернет весь словарь ai_models
        get_config()  # Вернет весь конфиг
    """
    if not _CONFIG_CACHE:
        load_config()
    
    if section is None:
        return _CONFIG_CACHE
    
    if section not in _CONFIG_CACHE:
        return default
    
    if key is None:
        return _CONFIG_CACHE.get(section, default)
    
    return _CONFIG_CACHE.get(section, {}).get(key, default)

def save_config(config: Dict[str, Any]) -> bool:
    """
    Сохранить конфигурацию в файл
    
    Args:
        config: Словарь с конфигурацией
    
    Returns:
        True если сохранение успешно, False иначе
    """
    global _CONFIG_CACHE
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        _CONFIG_CACHE = config
        print(f"[CONFIG] Конфигурация сохранена в {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"[CONFIG ERROR] Ошибка при сохранении конфигурации: {e}")
        return False

def update_config(section: str, key: str, value: Any) -> bool:
    """
    Обновить значение в конфигурации
    
    Args:
        section: Секция конфигурации
        key: Ключ в секции
        value: Новое значение
    
    Returns:
        True если обновление успешно, False иначе
    """
    try:
        if not _CONFIG_CACHE:
            load_config()
        
        if section not in _CONFIG_CACHE:
            _CONFIG_CACHE[section] = {}
        
        _CONFIG_CACHE[section][key] = value
        return save_config(_CONFIG_CACHE)
    except Exception as e:
        print(f"[CONFIG ERROR] Ошибка при обновлении конфигурации: {e}")
        return False

# ==================== НАСТРОЙКИ ПРИЛОЖЕНИЯ ====================

def get_app_title() -> str:
    """Получить название приложения"""
    return get_config('app', 'title', 'Образовательная платформа')

def get_page_icon() -> str:
    """Получить иконку страницы"""
    return get_config('app', 'page_icon', '🎓')

def get_page_config() -> Dict[str, Any]:
    """Получить конфигурацию страницы Streamlit"""
    app_config = get_config('app', default={})
    return {
        "page_title": app_config.get('title', 'Образовательная платформа'),
        "page_icon": app_config.get('page_icon', '🎓'),
        "layout": app_config.get('layout', 'wide'),
        "initial_sidebar_state": app_config.get('sidebar_state', 'expanded')
    }

# ==================== НАСТРОЙКИ БАЗЫ ДАННЫХ ====================

def get_database_name() -> str:
    """Получить имя базы данных"""
    return get_config('database', 'name', 'users.db')

def get_database_url() -> str:
    """Получить URL базы данных"""
    prefix = get_config('database', 'url_prefix', 'sqlite:///')
    name = get_database_name()
    return f"{prefix}{name}"

# ==================== НАСТРОЙКИ AI МОДЕЛЕЙ ====================

def get_ai_model() -> str:
    """Получить название модели AI по умолчанию"""
    return get_config('ai_models', 'default_model', 'gpt-4o-mini')

def get_ai_temperature() -> float:
    """Получить temperature для AI модели"""
    return get_config('ai_models', 'temperature', 0.3)

def get_ai_max_tokens() -> int:
    """Получить max_tokens для AI модели"""
    return get_config('ai_models', 'max_tokens', 2000)

def get_ai_top_p() -> float:
    """Получить top_p для AI модели"""
    return get_config('ai_models', 'top_p', 1.0)

def get_ai_frequency_penalty() -> float:
    """Получить frequency_penalty для AI модели"""
    return get_config('ai_models', 'frequency_penalty', 0.0)

def get_ai_presence_penalty() -> float:
    """Получить presence_penalty для AI модели"""
    return get_config('ai_models', 'presence_penalty', 0.0)

def get_ai_timeout() -> int:
    """Получить timeout для AI запросов в секундах"""
    return get_config('ai_models', 'timeout_seconds', 60)

def get_ai_max_retries() -> int:
    """Получить максимальное количество повторных попыток"""
    return get_config('ai_models', 'max_retries', 3)

def get_available_models() -> list:
    """Получить список доступных моделей"""
    return get_config('ai_models', 'available_models', ['gpt-4o-mini'])

# ==================== НАСТРОЙКИ OLLAMA ====================

def is_ollama_enabled() -> bool:
    """Проверить, включен ли Ollama"""
    return get_config('ollama', 'enabled', False)

def get_ollama_model() -> str:
    """Получить название модели Ollama"""
    return get_config('ollama', 'model', 'deepseek-coder:6.7b')

def get_ollama_base_url() -> str:
    """Получить base URL для Ollama"""
    return get_config('ollama', 'base_url', 'http://localhost:11434')

# ==================== НАСТРОЙКИ ЛОГИРОВАНИЯ ====================

def is_logging_enabled(module_name: str) -> bool:
    """
    Проверить, включено ли логирование для модуля
    
    Args:
        module_name: Имя файла модуля (например, 'llm.py')
    
    Returns:
        True если логирование включено, False иначе
    """
    if not get_config('logging', 'global_logging', True):
        return False
    
    enabled = get_config('logging', 'enabled', {})
    return enabled.get(module_name, True)

def is_ai_logs_enabled() -> bool:
    """Проверить, включены ли логи AI"""
    return get_config('logging', 'ai_logs', True)

def get_log_level() -> str:
    """Получить уровень логирования"""
    return get_config('logging', 'log_level', 'INFO')

def are_colored_logs_enabled() -> bool:
    """Проверить, включены ли цветные логи"""
    return get_config('logging', 'colored_logs', True)

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ЛОГИРОВАНИЯ ====================

def log(module_name: str, message: str):
    """Условный вывод лог-сообщения"""
    if is_logging_enabled(module_name):
        print(message)

def log_info(module_name: str, message: str):
    """Вывод информационного сообщения"""
    log(module_name, f"[INFO] {message}")

def log_error(module_name: str, message: str):
    """Вывод сообщения об ошибке"""
    log(module_name, f"[ERROR] {message}")

def log_warning(module_name: str, message: str):
    """Вывод предупреждения"""
    log(module_name, f"[WARNING] {message}")

def log_debug(module_name: str, message: str):
    """Вывод отладочного сообщения"""
    log(module_name, f"[DEBUG] {message}")

# ==================== НАСТРОЙКИ ВАЛИДАЦИИ ====================

def get_min_name_length() -> int:
    """Получить минимальную длину имени"""
    return get_config('validation', 'min_name_length', 2)

def get_min_password_length() -> int:
    """Получить минимальную длину пароля"""
    return get_config('validation', 'min_password_length', 6)

def get_max_name_length() -> int:
    """Получить максимальную длину имени"""
    return get_config('validation', 'max_name_length', 100)

# ==================== НАСТРОЙКИ ЧАТА ====================

def get_chat_bot_name() -> str:
    """Получить имя чат-бота"""
    return get_config('chat', 'bot_name', 'Помощник')

def get_chat_system_message() -> str:
    """Получить системное сообщение для чата"""
    return get_config('chat', 'system_message', 'Вы - дружелюбный помощник.')

def get_chat_max_history() -> int:
    """Получить максимальное количество сообщений в истории"""
    return get_config('chat', 'max_history_messages', 50)

# ==================== НАСТРОЙКИ ФУНКЦИЙ ====================

def is_feature_enabled(feature_name: str) -> bool:
    """
    Проверить, включена ли функция
    
    Args:
        feature_name: Название функции (например, 'enable_ai_assistant')
    
    Returns:
        True если функция включена, False иначе
    """
    return get_config('features', feature_name, True)

# ==================== ИНИЦИАЛИЗАЦИЯ ====================

# Загружаем конфигурацию при импорте модуля
load_config()

# Экспортируем для обратной совместимости с config.py
AI_LOGS = is_ai_logs_enabled()
APP_TITLE = get_app_title()
DATABASE_NAME = get_database_name()
DATABASE_URL = get_database_url()
SESSION_STATE_KEY = "user_session"
USER_ROLES = ["Ученик", "Учитель"]
MIN_NAME_LENGTH = get_min_name_length()
MIN_PASSWORD_LENGTH = get_min_password_length()
CHAT_BOT_NAME = get_chat_bot_name()
CHAT_SYSTEM_MESSAGE = get_chat_system_message()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAGE_CONFIG = get_page_config()

