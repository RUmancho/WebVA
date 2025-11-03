# -*- coding: utf-8 -*-
"""
ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ СИСТЕМЫ КОНФИГУРАЦИИ

Этот файл показывает, как использовать централизованную систему управления настройками
через JSON конфигурацию (app_config.json)
"""

from config_manager import (
    # Настройки AI
    get_ai_model, get_ai_temperature, get_ai_max_tokens,
    get_ai_top_p, get_ai_frequency_penalty, get_ai_presence_penalty,
    get_available_models, get_ai_timeout, get_ai_max_retries,
    
    # Настройки Ollama
    is_ollama_enabled, get_ollama_model, get_ollama_base_url,
    
    # Настройки логирования
    log, log_info, log_error, log_warning, log_debug,
    is_logging_enabled, is_ai_logs_enabled,
    
    # Настройки приложения
    get_app_title, get_page_icon, get_page_config,
    
    # Настройки базы данных
    get_database_name, get_database_url,
    
    # Настройки валидации
    get_min_name_length, get_min_password_length,
    
    # Настройки чата
    get_chat_bot_name, get_chat_system_message, get_chat_max_history,
    
    # Настройки функций
    is_feature_enabled,
    
    # Универсальные функции
    get_config, update_config, save_config
)

# ===================== ПРИМЕР 1: ИСПОЛЬЗОВАНИЕ AI НАСТРОЕК =====================

def example_ai_settings():
    """Пример использования настроек AI моделей"""
    print("=" * 60)
    print("ПРИМЕР 1: Настройки AI моделей")
    print("=" * 60)
    
    # Получаем настройки модели
    model = get_ai_model()
    temperature = get_ai_temperature()
    max_tokens = get_ai_max_tokens()
    
    print(f"Модель: {model}")
    print(f"Temperature: {temperature}")
    print(f"Max Tokens: {max_tokens}")
    print(f"Top P: {get_ai_top_p()}")
    print(f"Frequency Penalty: {get_ai_frequency_penalty()}")
    print(f"Presence Penalty: {get_ai_presence_penalty()}")
    print(f"Timeout: {get_ai_timeout()} секунд")
    print(f"Max Retries: {get_ai_max_retries()}")
    print(f"Доступные модели: {', '.join(get_available_models())}")
    print()

def example_openai_call():
    """Пример вызова OpenAI API с настройками из конфига"""
    from openai import OpenAI
    import os
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Используем настройки из конфига
    response = client.chat.completions.create(
        model=get_ai_model(),
        temperature=get_ai_temperature(),
        max_tokens=get_ai_max_tokens(),
        top_p=get_ai_top_p(),
        frequency_penalty=get_ai_frequency_penalty(),
        presence_penalty=get_ai_presence_penalty(),
        messages=[{"role": "user", "content": "Привет!"}]
    )
    
    return response

# ===================== ПРИМЕР 2: СИСТЕМА ЛОГИРОВАНИЯ =====================

def example_logging():
    """Пример использования системы логирования"""
    print("=" * 60)
    print("ПРИМЕР 2: Система логирования")
    print("=" * 60)
    
    MODULE_NAME = "llm.py"
    
    # Проверяем, включены ли логи для модуля
    if is_logging_enabled(MODULE_NAME):
        print(f"Логирование для {MODULE_NAME}: ВКЛЮЧЕНО")
    else:
        print(f"Логирование для {MODULE_NAME}: ВЫКЛЮЧЕНО")
    
    # Попытка вывести логи (не выведется если в конфиге llm.py: false)
    log_info(MODULE_NAME, "Это информационное сообщение")
    log_error(MODULE_NAME, "Это сообщение об ошибке")
    log_warning(MODULE_NAME, "Это предупреждение")
    log_debug(MODULE_NAME, "Это отладочное сообщение")
    
    # Проверяем глобальные настройки логов AI
    print(f"AI логи: {'ВКЛЮЧЕНЫ' if is_ai_logs_enabled() else 'ВЫКЛЮЧЕНЫ'}")
    print()

# ===================== ПРИМЕР 3: НАСТРОЙКИ ПРИЛОЖЕНИЯ =====================

def example_app_settings():
    """Пример использования настроек приложения"""
    print("=" * 60)
    print("ПРИМЕР 3: Настройки приложения")
    print("=" * 60)
    
    print(f"Название: {get_app_title()}")
    print(f"Иконка: {get_page_icon()}")
    print(f"База данных: {get_database_name()}")
    print(f"URL БД: {get_database_url()}")
    print(f"Мин. длина имени: {get_min_name_length()}")
    print(f"Мин. длина пароля: {get_min_password_length()}")
    print(f"Имя чат-бота: {get_chat_bot_name()}")
    print(f"Макс. история чата: {get_chat_max_history()}")
    print()

# ===================== ПРИМЕР 4: STREAMLIT КОНФИГУРАЦИЯ =====================

def example_streamlit_config():
    """Пример использования с Streamlit"""
    print("=" * 60)
    print("ПРИМЕР 4: Конфигурация Streamlit")
    print("=" * 60)
    
    # В вашем main.py используйте так:
    # import streamlit as st
    # from config_manager import get_page_config
    # 
    # st.set_page_config(**get_page_config())
    
    config = get_page_config()
    print("Конфигурация страницы Streamlit:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()

# ===================== ПРИМЕР 5: ПРОВЕРКА ФУНКЦИЙ =====================

def example_feature_flags():
    """Пример использования флагов функций"""
    print("=" * 60)
    print("ПРИМЕР 5: Флаги функций")
    print("=" * 60)
    
    features = [
        'enable_ai_assistant',
        'enable_video_calls',
        'enable_file_uploads',
        'enable_notifications',
        'enable_student_teacher_chat'
    ]
    
    for feature in features:
        status = "ВКЛЮЧЕНА" if is_feature_enabled(feature) else "ВЫКЛЮЧЕНА"
        print(f"{feature}: {status}")
    print()

# ===================== ПРИМЕР 6: OLLAMA НАСТРОЙКИ =====================

def example_ollama_settings():
    """Пример использования настроек Ollama"""
    print("=" * 60)
    print("ПРИМЕР 6: Настройки Ollama")
    print("=" * 60)
    
    if is_ollama_enabled():
        print("Ollama: ВКЛЮЧЕН")
        print(f"Модель: {get_ollama_model()}")
        print(f"Base URL: {get_ollama_base_url()}")
    else:
        print("Ollama: ВЫКЛЮЧЕН")
    print()

# ===================== ПРИМЕР 7: УНИВЕРСАЛЬНЫЙ ДОСТУП К КОНФИГУ =====================

def example_generic_config():
    """Пример универсального доступа к конфигурации"""
    print("=" * 60)
    print("ПРИМЕР 7: Универсальный доступ")
    print("=" * 60)
    
    # Получить всю секцию
    ui_config = get_config('ui')
    print("Настройки UI:", ui_config)
    
    # Получить конкретное значение
    theme = get_config('ui', 'theme', default='light')
    print(f"Тема: {theme}")
    
    # Получить с default значением
    custom_setting = get_config('custom_section', 'custom_key', default='default_value')
    print(f"Кастомная настройка: {custom_setting}")
    print()

# ===================== ПРИМЕР 8: ОБНОВЛЕНИЕ КОНФИГУРАЦИИ =====================

def example_update_config():
    """Пример обновления конфигурации"""
    print("=" * 60)
    print("ПРИМЕР 8: Обновление конфигурации")
    print("=" * 60)
    
    # Текущее значение
    current_temp = get_ai_temperature()
    print(f"Текущая temperature: {current_temp}")
    
    # Обновление значения (раскомментируйте если хотите изменить)
    # new_temp = 0.7
    # success = update_config('ai_models', 'temperature', new_temp)
    # if success:
    #     print(f"Temperature обновлена на: {new_temp}")
    # else:
    #     print("Ошибка при обновлении конфигурации")
    
    print("(Обновление закомментировано для безопасности)")
    print()

# ===================== ПРИМЕР 9: ИСПОЛЬЗОВАНИЕ В РЕАЛЬНОМ КОДЕ =====================

def example_real_world_usage():
    """Пример использования в реальном коде"""
    print("=" * 60)
    print("ПРИМЕР 9: Реальное использование")
    print("=" * 60)
    
    MODULE_NAME = "chatbot.py"
    
    # Проверяем, включена ли функция
    if not is_feature_enabled('enable_ai_assistant'):
        log_warning(MODULE_NAME, "AI ассистент отключен в конфигурации")
        return
    
    # Логируем начало работы
    log_info(MODULE_NAME, "Инициализация чат-бота...")
    
    try:
        # Получаем настройки
        model = get_ai_model()
        temperature = get_ai_temperature()
        max_tokens = get_ai_max_tokens()
        
        log_info(MODULE_NAME, f"Используется модель: {model}")
        log_info(MODULE_NAME, f"Temperature: {temperature}, Max tokens: {max_tokens}")
        
        # Здесь ваш код работы с AI...
        log_info(MODULE_NAME, "Чат-бот успешно инициализирован")
        
    except Exception as e:
        log_error(MODULE_NAME, f"Ошибка инициализации чат-бота: {e}")

# ===================== ГЛАВНАЯ ФУНКЦИЯ =====================

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ КОНФИГУРАЦИИ" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")
    
    example_ai_settings()
    example_logging()
    example_app_settings()
    example_streamlit_config()
    example_feature_flags()
    example_ollama_settings()
    example_generic_config()
    example_update_config()
    example_real_world_usage()
    
    print("=" * 80)
    print("ИНСТРУКЦИИ:")
    print("=" * 80)
    print("1. Все настройки находятся в файле: app_config.json")
    print("2. Измените значения в JSON файле для изменения поведения приложения")
    print("3. Не нужно перезапускать приложение - конфиг загружается автоматически")
    print("4. Используйте функции из config_manager.py в своем коде")
    print("5. Для логирования используйте log_info(), log_error() и т.д.")
    print("=" * 80)

