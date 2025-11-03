# -*- coding: utf-8 -*-
"""
Скрипт управления пользователями
Позволяет просматривать и удалять пользователей из базы данных
"""

import sqlite3
import os
import sys

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

DATABASE_NAME = "users.db"

def list_users():
    """Показать всех пользователей"""
    try:
        if not os.path.exists(DATABASE_NAME):
            print(f"[ОШИБКА] База данных {DATABASE_NAME} не найдена")
            return
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, email, first_name, last_name, role, city, school, class_number FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("[INFO] В базе данных нет пользователей")
            return
        
        print("\n" + "=" * 100)
        print("СПИСОК ПОЛЬЗОВАТЕЛЕЙ")
        print("=" * 100)
        print(f"{'ID':<5} {'Email':<30} {'Имя':<15} {'Фамилия':<15} {'Роль':<10} {'Город':<15}")
        print("-" * 100)
        
        for user in users:
            user_id, email, first_name, last_name, role, city, school, class_num = user
            print(f"{user_id:<5} {email:<30} {first_name:<15} {last_name:<15} {role:<10} {city:<15}")
        
        print("=" * 100)
        print(f"[INFO] Всего пользователей: {len(users)}\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"[ОШИБКА] {e}")

def delete_user_by_email(email):
    """Удалить пользователя по email"""
    try:
        if not os.path.exists(DATABASE_NAME):
            print(f"[ОШИБКА] База данных {DATABASE_NAME} не найдена")
            return False
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Проверяем, существует ли пользователь
        cursor.execute("SELECT id, email, first_name, last_name FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"[INFO] Пользователь с email '{email}' не найден")
            cursor.close()
            conn.close()
            return False
        
        user_id, user_email, first_name, last_name = user
        print(f"\n[INFO] Найден пользователь:")
        print(f"  ID: {user_id}")
        print(f"  Email: {user_email}")
        print(f"  Имя: {first_name} {last_name}")
        
        # Подтверждение удаления
        confirmation = input("\n[?] Вы уверены, что хотите удалить этого пользователя? (yes/no): ").strip().lower()
        
        if confirmation not in ['yes', 'y', 'да', 'д']:
            print("[INFO] Удаление отменено")
            cursor.close()
            conn.close()
            return False
        
        # Удаляем пользователя
        cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
        
        print(f"[SUCCESS] Пользователь '{email}' успешно удален")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ОШИБКА] {e}")
        return False

def delete_all_users():
    """Удалить всех пользователей"""
    try:
        if not os.path.exists(DATABASE_NAME):
            print(f"[ОШИБКА] База данных {DATABASE_NAME} не найдена")
            return False
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Считаем пользователей
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("[INFO] В базе данных нет пользователей")
            cursor.close()
            conn.close()
            return False
        
        print(f"\n[WARNING] В базе данных {count} пользователей")
        confirmation = input("[?] Вы уверены, что хотите удалить ВСЕХ пользователей? (yes/no): ").strip().lower()
        
        if confirmation not in ['yes', 'y', 'да', 'д']:
            print("[INFO] Удаление отменено")
            cursor.close()
            conn.close()
            return False
        
        # Удаляем всех пользователей
        cursor.execute("DELETE FROM users")
        conn.commit()
        
        print(f"[SUCCESS] Все пользователи ({count}) успешно удалены")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ОШИБКА] {e}")
        return False

def main():
    """Главное меню"""
    print("=" * 60)
    print("УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ - ОБРАЗОВАТЕЛЬНАЯ ПЛАТФОРМА")
    print("=" * 60)
    
    while True:
        print("\n[МЕНЮ]")
        print("1. Показать всех пользователей")
        print("2. Удалить пользователя по email")
        print("3. Удалить всех пользователей")
        print("4. Выход")
        
        choice = input("\nВыберите действие (1-4): ").strip()
        
        if choice == '1':
            list_users()
        
        elif choice == '2':
            email = input("\nВведите email пользователя для удаления: ").strip()
            if email:
                delete_user_by_email(email)
            else:
                print("[ОШИБКА] Email не может быть пустым")
        
        elif choice == '3':
            delete_all_users()
        
        elif choice == '4':
            print("\n[INFO] Выход из программы")
            break
        
        else:
            print("[ОШИБКА] Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Программа прервана пользователем")
    except Exception as e:
        print(f"\n[ОШИБКА] {e}")

