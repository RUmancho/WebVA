# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки работы системы конфигурации
Запустите этот файл для проверки корректности настроек
"""

import sys
import os

def test_config_file_exists():
    """Проверка существования файла конфигурации"""
    print("🔍 Проверка 1: Существование файла конфигурации")
    if os.path.exists("app_config.json"):
        print("   ✅ Файл app_config.json найден")
        return True
    else:
        print("   ❌ Файл app_config.json НЕ найден!")
        return False

def test_config_manager_import():
    """Проверка импорта модуля config_manager"""
    print("\n🔍 Проверка 2: Импорт модуля config_manager")
    try:
        import config_manager
        print("   ✅ Модуль config_manager успешно импортирован")
        return True
    except ImportError as e:
        print(f"   ❌ Ошибка импорта config_manager: {e}")
        return False

def test_config_loading():
    """Проверка загрузки конфигурации"""
    print("\n🔍 Проверка 3: Загрузка конфигурации")
    try:
        from config_manager import load_config
        config = load_config()
        if config:
            print("   ✅ Конфигурация успешно загружена")
            print(f"   📊 Секций в конфиге: {len(config)}")
            return True
        else:
            print("   ❌ Конфигурация пустая")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка загрузки конфигурации: {e}")
        return False

def test_ai_settings():
    """Проверка настроек AI"""
    print("\n🔍 Проверка 4: Настройки AI моделей")
    try:
        from config_manager import (
            get_ai_model, get_ai_temperature, get_ai_max_tokens,
            get_ai_top_p, get_available_models
        )
        
        model = get_ai_model()
        temp = get_ai_temperature()
        max_tokens = get_ai_max_tokens()
        top_p = get_ai_top_p()
        models = get_available_models()
        
        print(f"   ✅ Модель: {model}")
        print(f"   ✅ Temperature: {temp}")
        print(f"   ✅ Max Tokens: {max_tokens}")
        print(f"   ✅ Top P: {top_p}")
        print(f"   ✅ Доступные модели: {len(models)} шт.")
        
        # Проверка валидности значений
        if not (0.0 <= temp <= 2.0):
            print(f"   ⚠️  ВНИМАНИЕ: Temperature {temp} вне диапазона [0.0, 2.0]")
        if max_tokens <= 0:
            print(f"   ⚠️  ВНИМАНИЕ: Max tokens {max_tokens} должен быть > 0")
        
        return True
    except Exception as e:
        print(f"   ❌ Ошибка получения настроек AI: {e}")
        return False

def test_logging_settings():
    """Проверка настроек логирования"""
    print("\n🔍 Проверка 5: Настройки логирования")
    try:
        from config_manager import (
            is_logging_enabled, is_ai_logs_enabled, get_log_level
        )
        
        test_modules = ["llm.py", "auth.py", "chatbot.py", "database.py"]
        
        print(f"   ✅ AI логи: {'ВКЛЮЧЕНЫ' if is_ai_logs_enabled() else 'ВЫКЛЮЧЕНЫ'}")
        print(f"   ✅ Уровень логирования: {get_log_level()}")
        print("   📝 Статус логов для модулей:")
        
        for module in test_modules:
            status = "ВКЛЮЧЕНЫ" if is_logging_enabled(module) else "ВЫКЛЮЧЕНЫ"
            print(f"      • {module}: {status}")
        
        return True
    except Exception as e:
        print(f"   ❌ Ошибка получения настроек логирования: {e}")
        return False

def test_logging_functions():
    """Проверка функций логирования"""
    print("\n🔍 Проверка 6: Функции логирования")
    try:
        from config_manager import log_info, log_error, log_warning, log_debug
        
        MODULE_NAME = "test_config.py"
        
        print("   Тестирование вывода логов:")
        log_info(MODULE_NAME, "Тестовое INFO сообщение")
        log_error(MODULE_NAME, "Тестовое ERROR сообщение")
        log_warning(MODULE_NAME, "Тестовое WARNING сообщение")
        log_debug(MODULE_NAME, "Тестовое DEBUG сообщение")
        
        print("   ✅ Функции логирования работают")
        return True
    except Exception as e:
        print(f"   ❌ Ошибка функций логирования: {e}")
        return False

def test_app_settings():
    """Проверка настроек приложения"""
    print("\n🔍 Проверка 7: Настройки приложения")
    try:
        from config_manager import (
            get_app_title, get_page_icon, get_database_name,
            get_min_name_length, get_min_password_length
        )
        
        print(f"   ✅ Название: {get_app_title()}")
        print(f"   ✅ Иконка: {get_page_icon()}")
        print(f"   ✅ База данных: {get_database_name()}")
        print(f"   ✅ Мин. длина имени: {get_min_name_length()}")
        print(f"   ✅ Мин. длина пароля: {get_min_password_length()}")
        
        return True
    except Exception as e:
        print(f"   ❌ Ошибка получения настроек приложения: {e}")
        return False

def test_feature_flags():
    """Проверка флагов функций"""
    print("\n🔍 Проверка 8: Флаги функций")
    try:
        from config_manager import is_feature_enabled
        
        features = [
            'enable_ai_assistant',
            'enable_video_calls',
            'enable_file_uploads',
            'enable_notifications'
        ]
        
        print("   Статус функций:")
        for feature in features:
            status = "ВКЛЮЧЕНА" if is_feature_enabled(feature) else "ВЫКЛЮЧЕНА"
            print(f"      • {feature}: {status}")
        
        print("   ✅ Флаги функций работают")
        return True
    except Exception as e:
        print(f"   ❌ Ошибка получения флагов функций: {e}")
        return False

def test_backward_compatibility():
    """Проверка обратной совместимости с config.py"""
    print("\n🔍 Проверка 9: Обратная совместимость (config.py)")
    try:
        import config
        
        # Проверяем, что старые переменные доступны
        assert hasattr(config, 'AI_LOGS'), "AI_LOGS не найден"
        assert hasattr(config, 'APP_TITLE'), "APP_TITLE не найден"
        assert hasattr(config, 'DATABASE_NAME'), "DATABASE_NAME не найден"
        
        print(f"   ✅ AI_LOGS: {config.AI_LOGS}")
        print(f"   ✅ APP_TITLE: {config.APP_TITLE}")
        print(f"   ✅ DATABASE_NAME: {config.DATABASE_NAME}")
        print("   ✅ Обратная совместимость работает")
        
        return True
    except Exception as e:
        print(f"   ❌ Ошибка обратной совместимости: {e}")
        return False

def test_universal_access():
    """Проверка универсального доступа к конфигу"""
    print("\n🔍 Проверка 10: Универсальный доступ")
    try:
        from config_manager import get_config
        
        # Получение целой секции
        ai_config = get_config('ai_models')
        print(f"   ✅ Секция 'ai_models' содержит {len(ai_config)} параметров")
        
        # Получение конкретного значения
        temperature = get_config('ai_models', 'temperature')
        print(f"   ✅ Значение 'temperature': {temperature}")
        
        # Получение с default значением
        custom = get_config('non_existent', 'key', default='default_value')
        print(f"   ✅ Default значение работает: {custom}")
        
        return True
    except Exception as e:
        print(f"   ❌ Ошибка универсального доступа: {e}")
        return False

def main():
    """Основная функция тестирования"""
    # Настройка кодировки для Windows
    if sys.platform == 'win32':
        import codecs
        sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
    
    print("\n")
    print("=" * 80)
    print(" " * 20 + "ТЕСТИРОВАНИЕ СИСТЕМЫ КОНФИГУРАЦИИ")
    print("=" * 80)
    print("\n")
    
    tests = [
        test_config_file_exists,
        test_config_manager_import,
        test_config_loading,
        test_ai_settings,
        test_logging_settings,
        test_logging_functions,
        test_app_settings,
        test_feature_flags,
        test_backward_compatibility,
        test_universal_access
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n   ❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            results.append(False)
    
    # Итоговый отчет
    print("\n")
    print("=" * 80)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    failed = total - passed
    
    print(f"\n✅ Пройдено тестов: {passed}/{total}")
    if failed > 0:
        print(f"❌ Провалено тестов: {failed}/{total}")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО! 🎉")
        print("Система конфигурации работает корректно.")
        return 0
    else:
        print("\n⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("Проверьте ошибки выше и исправьте конфигурацию.")
        return 1
    
if __name__ == "__main__":
    sys.exit(main())

