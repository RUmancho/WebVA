# -*- coding: utf-8 -*-
"""
Скрипт миграции базы данных
Добавляет новые столбцы в существующую базу данных
"""

import sqlite3
from datetime import datetime
import os
import sys

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

DATABASE_NAME = "users.db"

def migrate_database():
    """Добавление новых столбцов в таблицу users"""
    try:
        print("[МИГРАЦИЯ] Начинаем миграцию базы данных...")
        
        # Проверяем, существует ли база данных
        if not os.path.exists(DATABASE_NAME):
            print(f"[ОШИБКА] База данных {DATABASE_NAME} не найдена")
            print("[INFO] Новая база будет создана автоматически при запуске приложения")
            return True
        
        # Подключаемся к базе данных
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Проверяем существующие столбцы
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        print(f"[INFO] Существующие столбцы: {', '.join(existing_columns)}")
        
        # Добавляем столбец is_online если его нет
        if 'is_online' not in existing_columns:
            print("[+] Добавляем столбец is_online...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_online INTEGER DEFAULT 0")
            print("[OK] Столбец is_online добавлен")
        else:
            print("[INFO] Столбец is_online уже существует")
        
        # Добавляем столбец last_seen если его нет
        if 'last_seen' not in existing_columns:
            print("[+] Добавляем столбец last_seen...")
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"ALTER TABLE users ADD COLUMN last_seen TIMESTAMP DEFAULT '{current_time}'")
            print("[OK] Столбец last_seen добавлен")
        else:
            print("[INFO] Столбец last_seen уже существует")
        
        # Сохраняем изменения
        conn.commit()
        
        # Проверяем результат
        cursor.execute("PRAGMA table_info(users)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print("\n[SUCCESS] Миграция завершена успешно!")
        print(f"[INFO] Обновленные столбцы: {', '.join(updated_columns)}")
        
        # Закрываем соединение
        cursor.close()
        conn.close()
        
        print("\n[INFO] Теперь вы можете запустить приложение: streamlit run main.py")
        
    except sqlite3.OperationalError as e:
        print(f"[ОШИБКА] Ошибка миграции: {e}")
        print("\n[РЕШЕНИЯ]:")
        print("   1. Закройте приложение Streamlit (Ctrl+C)")
        print("   2. Запустите этот скрипт снова: python migrate_database.py")
        print("   3. Или удалите users.db и дайте системе создать новую базу")
        return False
    except Exception as e:
        print(f"[ОШИБКА] Неожиданная ошибка: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("МИГРАЦИЯ БАЗЫ ДАННЫХ - ОБРАЗОВАТЕЛЬНАЯ ПЛАТФОРМА")
    print("=" * 60)
    print()
    
    success = migrate_database()
    
    if not success:
        print("\n[WARNING] Миграция не выполнена")
    
    print("\n" + "=" * 60)

