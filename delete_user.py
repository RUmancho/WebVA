# -*- coding: utf-8 -*-
"""
Быстрое удаление пользователя по email
Использование: python delete_user.py <email>
Пример: python delete_user.py ryzovr601@gmail.com
"""

import sqlite3
import os
import sys

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

DATABASE_NAME = "users.db"

def delete_user(email):
    """Удалить пользователя по email"""
    try:
        if not os.path.exists(DATABASE_NAME):
            print(f"[ОШИБКА] База данных {DATABASE_NAME} не найдена")
            return False
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Проверяем, существует ли пользователь
        cursor.execute("SELECT id, email, first_name, last_name, role FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"[INFO] Пользователь с email '{email}' не найден в базе данных")
            cursor.close()
            conn.close()
            return False
        
        user_id, user_email, first_name, last_name, role = user
        print(f"\n[INFO] Найден пользователь:")
        print(f"  ID: {user_id}")
        print(f"  Email: {user_email}")
        print(f"  Имя: {first_name} {last_name}")
        print(f"  Роль: {role}")
        
        # Удаляем пользователя
        cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
        
        print(f"\n[SUCCESS] Пользователь '{email}' успешно удален из базы данных!")
        print(f"[INFO] Теперь вы можете зарегистрироваться с этим email\n")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ОШИБКА] {e}")
        return False

def list_all_users():
    """Показать всех пользователей"""
    try:
        if not os.path.exists(DATABASE_NAME):
            print(f"[ОШИБКА] База данных {DATABASE_NAME} не найдена")
            return
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, email, first_name, last_name, role FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("[INFO] В базе данных нет пользователей")
            cursor.close()
            conn.close()
            return
        
        print("\n" + "=" * 80)
        print("СПИСОК ВСЕХ ПОЛЬЗОВАТЕЛЕЙ")
        print("=" * 80)
        print(f"{'ID':<5} {'Email':<35} {'Имя':<15} {'Роль':<10}")
        print("-" * 80)
        
        for user in users:
            user_id, email, first_name, last_name, role = user
            full_name = f"{first_name} {last_name}"
            print(f"{user_id:<5} {email:<35} {full_name:<15} {role:<10}")
        
        print("=" * 80)
        print(f"[INFO] Всего пользователей: {len(users)}\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"[ОШИБКА] {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ ИЗ БАЗЫ ДАННЫХ")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("[INFO] Использование:")
        print("  python delete_user.py <email>")
        print("  python delete_user.py list  - показать всех пользователей")
        print()
        print("[INFO] Пример:")
        print("  python delete_user.py ryzovr601@gmail.com")
        print()
        
        # Показываем текущих пользователей
        list_all_users()
        
        sys.exit(1)
    
    if sys.argv[1].lower() == 'list':
        list_all_users()
    else:
        email = sys.argv[1].strip()
        delete_user(email)
    
    print("=" * 60)

