"""
WebVA - Виртуальный Ассистент для Обучения
Главный файл запуска проекта
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Константы
PROJECT_ROOT = Path(__file__).resolve().parent
UI_DIR = PROJECT_ROOT / "UI"
APP_FILE = UI_DIR / "app.py"
HOST = "0.0.0.0"
PORT = 5000

def print_banner():
    """Вывод баннера при запуске"""
    print("=" * 50)
    print("🚀 ЗАПУСК WEBVA")
    print("   Виртуальный Ассистент для Обучения")
    print("=" * 50)
    print()

def check_venv():
    """Проверка виртуального окружения"""
    venv_path = PROJECT_ROOT / "venv"
    if not venv_path.exists():
        print("❌ Виртуальное окружение не найдено!")
        print("   Создайте его командой: python -m venv venv")
        print("   Затем установите зависимости: pip install -r requirements.txt")
        sys.exit(1)
    print("✅ Виртуальное окружение найдено")

def check_ollama():
    """Проверка и запуск Ollama (опционально)"""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Ollama найден")
            try:
                print("[2/4] Запуск Ollama сервера...")
                if sys.platform == "win32":
                    subprocess.Popen(
                        ["cmd", "/c", "start", "/MIN", "ollama", "serve"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    subprocess.Popen(
                        ["ollama", "serve"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                time.sleep(3)
                print("✅ Ollama запущен в фоновом режиме")
            except Exception as e:
                print(f"⚠️ Не удалось запустить Ollama: {e}")
                print("   Продолжаю без AI генерации...")
        else:
            print("⚠️ Ollama не найден")
            print("   Установите с https://ollama.ai/ для AI генерации")
            print("   Продолжаю без AI генерации...")
    except FileNotFoundError:
        print("⚠️ Ollama не установлен")
        print("   Установите с https://ollama.ai/ для AI генерации")
        print("   Продолжаю без AI генерации...")
    except Exception as e:
        print(f"⚠️ Ошибка при проверке Ollama: {e}")
        print("   Продолжаю без AI генерации...")

def check_environment():
    """Проверка переменных окружения"""
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        print("⚠️ Файл .env не найден")
        print(f"   Создайте .env файл на основе {PROJECT_ROOT / 'ENV_EXAMPLE.txt'}")
        print("   Некоторые функции могут быть недоступны")
    else:
        print("✅ Файл .env найден")

def start_flask_app():
    """Запуск Flask приложения"""
    print()
    print("[4/4] Запуск Flask приложения...")
    print("=" * 50)
    print()
    print(f"🌐 Сервер запускается на http://localhost:{PORT}")
    print(f"📁 Корневая директория: {PROJECT_ROOT}")
    print()
    print("Для остановки сервера нажмите Ctrl+C")
    print("=" * 50)
    print()
    
    try:
        # Переходим в директорию UI и запускаем приложение
        os.chdir(UI_DIR)
        sys.path.insert(0, str(PROJECT_ROOT))
        
        # Импортируем и запускаем Flask приложение
        from UI.app import app
        app.run(host=HOST, port=PORT, debug=False)
        
    except KeyboardInterrupt:
        print()
        print("=" * 50)
        print("🛑 Сервер остановлен пользователем")
        print("=" * 50)
        sys.exit(0)
    except Exception as e:
        print()
        print("=" * 50)
        print(f"❌ Ошибка при запуске сервера: {e}")
        print("=" * 50)
        sys.exit(1)

def main():
    """Главная функция запуска"""
    try:
        print_banner()
        
        print("[1/4] Проверка окружения...")
        check_venv()
        check_environment()
        print()
        
        check_ollama()
        print()
        
        start_flask_app()
        
    except Exception as e:
        print()
        print("=" * 50)
        print(f"❌ Критическая ошибка: {e}")
        print("=" * 50)
        sys.exit(1)

if __name__ == "__main__":
    main()

