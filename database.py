# -*- coding: utf-8 -*-
import sqlite3
import hashlib
from datetime import datetime
from config import DATABASE_NAME

class Database:
    def __init__(self):
        """Инициализация базы данных"""
        self.db_name = DATABASE_NAME
        self.init_database()
    
    def get_connection(self):
        """Получение соединения с базой данных"""
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return None
    
    def init_database(self):
        """Создание таблиц в базе данных"""
        try:
            conn = self.get_connection()
            if conn is None:
                return False
                
            cursor = conn.cursor()
            
            # Создание таблицы пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    city TEXT,
                    school TEXT,
                    class_number TEXT,
                    subjects TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Создание таблицы для связи учеников и учителей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS student_teacher_relations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    teacher_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES users (id),
                    FOREIGN KEY (teacher_id) REFERENCES users (id)
                )
            ''')
            
            # Создание таблицы заявок от учителей к ученикам
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teacher_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (teacher_id) REFERENCES users (id),
                    FOREIGN KEY (student_id) REFERENCES users (id)
                )
            ''')
            
            # Создание таблицы звонков
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    teacher_id INTEGER NOT NULL,
                    scheduled_time TIMESTAMP,
                    actual_start_time TIMESTAMP,
                    actual_end_time TIMESTAMP,
                    duration_minutes INTEGER,
                    status TEXT DEFAULT 'scheduled',
                    recording_path TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES users (id),
                    FOREIGN KEY (teacher_id) REFERENCES users (id)
                )
            ''')
            
            # Создание таблицы записей уроков
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lesson_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    teacher_id INTEGER NOT NULL,
                    lesson_title TEXT NOT NULL,
                    lesson_date TIMESTAMP,
                    subject TEXT,
                    video_url TEXT,
                    video_file_path TEXT,
                    description TEXT,
                    homework TEXT,
                    is_auto_created INTEGER DEFAULT 0,
                    call_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES users (id),
                    FOREIGN KEY (teacher_id) REFERENCES users (id),
                    FOREIGN KEY (call_id) REFERENCES calls (id)
                )
            ''')
            
            # Миграция: добавление новых колонок в существующие таблицы
            self.migrate_database(cursor)
            
            conn.commit()
            conn.close()
            print("База данных успешно инициализирована")
            return True
            
        except sqlite3.Error as e:
            print(f"Ошибка инициализации базы данных: {e}")
            return False
    
    def migrate_database(self, cursor):
        """Миграция базы данных - добавление новых колонок"""
        try:
            # Проверка и добавление колонок в таблицу calls
            cursor.execute("PRAGMA table_info(calls)")
            calls_columns = [column[1] for column in cursor.fetchall()]
            
            if 'actual_start_time' not in calls_columns:
                cursor.execute("ALTER TABLE calls ADD COLUMN actual_start_time TIMESTAMP")
                print("Добавлена колонка actual_start_time в таблицу calls")
            
            if 'actual_end_time' not in calls_columns:
                cursor.execute("ALTER TABLE calls ADD COLUMN actual_end_time TIMESTAMP") 
                print("Добавлена колонка actual_end_time в таблицу calls")
            
            if 'recording_path' not in calls_columns:
                cursor.execute("ALTER TABLE calls ADD COLUMN recording_path TEXT")
                print("Добавлена колонка recording_path в таблицу calls")
            
            # Проверка и добавление колонок в таблицу lesson_records
            cursor.execute("PRAGMA table_info(lesson_records)")
            records_columns = [column[1] for column in cursor.fetchall()]
            
            if 'video_file_path' not in records_columns:
                cursor.execute("ALTER TABLE lesson_records ADD COLUMN video_file_path TEXT")
                print("Добавлена колонка video_file_path в таблицу lesson_records")
            
            if 'is_auto_created' not in records_columns:
                cursor.execute("ALTER TABLE lesson_records ADD COLUMN is_auto_created INTEGER DEFAULT 0")
                print("Добавлена колонка is_auto_created в таблицу lesson_records")
            
            if 'call_id' not in records_columns:
                cursor.execute("ALTER TABLE lesson_records ADD COLUMN call_id INTEGER")
                print("Добавлена колонка call_id в таблицу lesson_records")
            
            if 'expires_at' not in records_columns:
                cursor.execute("ALTER TABLE lesson_records ADD COLUMN expires_at TIMESTAMP")
                print("Добавлена колонка expires_at в таблицу lesson_records")
            
            # Удаление колонки call_link из calls если она существует (её больше не используем)
            if 'call_link' in calls_columns:
                print("Колонка call_link найдена в таблице calls (устарела, но оставляем для совместимости)")
            
            print("Миграция базы данных завершена")
            
        except sqlite3.Error as e:
            print(f"Ошибка миграции базы данных: {e}")
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, user_data):
        """Регистрация нового пользователя"""
        try:
            conn = self.get_connection()
            if conn is None:
                return False, "Ошибка подключения к базе данных"
                
            cursor = conn.cursor()
            
            # Проверка на существование пользователя с таким email
            cursor.execute("SELECT id FROM users WHERE email = ?", (user_data['email'],))
            if cursor.fetchone():
                conn.close()
                return False, "Пользователь с таким email уже существует"
            
            # Хеширование пароля
            password_hash = self.hash_password(user_data['password'])
            
            # Подготовка данных для вставки
            subjects = user_data.get('subjects', '')
            if isinstance(subjects, list):
                subjects = ', '.join(subjects)
            
            # Вставка данных
            cursor.execute('''
                INSERT INTO users (email, password_hash, first_name, last_name, role, 
                                 city, school, class_number, subjects)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['email'],
                password_hash,
                user_data['first_name'],
                user_data['last_name'],
                user_data['role'],
                user_data.get('city', ''),
                user_data.get('school', ''),
                user_data.get('class_number', ''),
                subjects
            ))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            print(f"Пользователь {user_data['email']} успешно зарегистрирован")
            return True, user_id
            
        except sqlite3.Error as e:
            print(f"Ошибка регистрации пользователя: {e}")
            return False, f"Ошибка базы данных: {e}"
    
    def authenticate_user(self, email, password):
        """Аутентификация пользователя"""
        try:
            conn = self.get_connection()
            if conn is None:
                return False, None
                
            cursor = conn.cursor()
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT * FROM users WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                user_dict = dict(user)
                print(f"Пользователь {email} успешно аутентифицирован")
                return True, user_dict
            else:
                print(f"Неудачная попытка входа для {email}")
                return False, None
                
        except sqlite3.Error as e:
            print(f"Ошибка аутентификации: {e}")
            return False, None
    
    def get_teachers(self):
        """Получение списка всех учителей"""
        try:
            conn = self.get_connection()
            if conn is None:
                return []
                
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, first_name, last_name, subjects, city, school 
                FROM users WHERE role = ?
            ''', ('Учитель',))
            
            teachers = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return teachers
            
        except sqlite3.Error as e:
            print(f"Ошибка получения списка учителей: {e}")
            return []
    
    def get_user_by_id(self, user_id):
        """Получение пользователя по ID"""
        try:
            conn = self.get_connection()
            if conn is None:
                return None
                
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            
            user = cursor.fetchone()
            conn.close()
            
            return dict(user) if user else None
            
        except sqlite3.Error as e:
            print(f"Ошибка получения пользователя: {e}")
            return None
    
    def delete_user(self, user_id, email, password):
        """Удаление пользователя с подтверждением"""
        try:
            conn = self.get_connection()
            if conn is None:
                return False, "Ошибка подключения к базе данных"
            
            cursor = conn.cursor()
            
            # Проверка подлинности пользователя
            password_hash = self.hash_password(password)
            cursor.execute(
                "SELECT id FROM users WHERE id = ? AND email = ? AND password_hash = ?",
                (user_id, email, password_hash)
            )
            
            if not cursor.fetchone():
                conn.close()
                return False, "Неверный email или пароль"
            
            # Удаление связанных записей
            cursor.execute("DELETE FROM student_teacher_relations WHERE student_id = ? OR teacher_id = ?", (user_id, user_id))
            cursor.execute("DELETE FROM teacher_requests WHERE student_id = ? OR teacher_id = ?", (user_id, user_id))
            cursor.execute("DELETE FROM calls WHERE student_id = ? OR teacher_id = ?", (user_id, user_id))
            cursor.execute("DELETE FROM lesson_records WHERE student_id = ? OR teacher_id = ?", (user_id, user_id))
            
            # Удаление пользователя
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            
            print(f"Пользователь с ID {user_id} успешно удален")
            return True, "Профиль успешно удален"
            
        except sqlite3.Error as e:
            print(f"Ошибка удаления пользователя: {e}")
            return False, f"Ошибка базы данных: {e}"
    
    def create_teacher_request(self, teacher_id, student_id, message=""):
        """Создание заявки от учителя к ученику"""
        try:
            conn = self.get_connection()
            if conn is None:
                return False, "Ошибка подключения к базе данных"
            
            cursor = conn.cursor()
            
            # Проверка существования заявки
            cursor.execute(
                "SELECT id FROM teacher_requests WHERE teacher_id = ? AND student_id = ? AND status = 'pending'",
                (teacher_id, student_id)
            )
            
            if cursor.fetchone():
                conn.close()
                return False, "Заявка уже отправлена"
            
            # Создание заявки
            cursor.execute('''
                INSERT INTO teacher_requests (teacher_id, student_id, message, status)
                VALUES (?, ?, ?, 'pending')
            ''', (teacher_id, student_id, message))
            
            conn.commit()
            conn.close()
            
            print(f"Заявка от учителя {teacher_id} к ученику {student_id} создана")
            return True, "Заявка отправлена"
            
        except sqlite3.Error as e:
            print(f"Ошибка создания заявки: {e}")
            return False, f"Ошибка базы данных: {e}"
    
    def get_student_requests(self, student_id):
        """Получение заявок для ученика"""
        try:
            conn = self.get_connection()
            if conn is None:
                return []
            
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tr.id, tr.teacher_id, tr.message, tr.created_at,
                       u.first_name, u.last_name, u.subjects, u.school
                FROM teacher_requests tr
                JOIN users u ON tr.teacher_id = u.id
                WHERE tr.student_id = ? AND tr.status = 'pending'
                ORDER BY tr.created_at DESC
            ''', (student_id,))
            
            requests = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return requests
            
        except sqlite3.Error as e:
            print(f"Ошибка получения заявок: {e}")
            return []
    
    def accept_teacher_request(self, request_id, student_id):
        """Принятие заявки от учителя"""
        try:
            conn = self.get_connection()
            if conn is None:
                return False, "Ошибка подключения к базе данных"
            
            cursor = conn.cursor()
            
            # Получение данных заявки
            cursor.execute(
                "SELECT teacher_id FROM teacher_requests WHERE id = ? AND student_id = ? AND status = 'pending'",
                (request_id, student_id)
            )
            
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False, "Заявка не найдена"
            
            teacher_id = result[0]
            
            # Обновление статуса заявки
            cursor.execute(
                "UPDATE teacher_requests SET status = 'accepted', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (request_id,)
            )
            
            # Добавление связи ученик-учитель
            cursor.execute(
                "INSERT INTO student_teacher_relations (student_id, teacher_id) VALUES (?, ?)",
                (student_id, teacher_id)
            )
            
            conn.commit()
            conn.close()
            
            print(f"Заявка {request_id} принята")
            return True, "Заявка принята, учитель добавлен"
            
        except sqlite3.Error as e:
            print(f"Ошибка принятия заявки: {e}")
            return False, f"Ошибка базы данных: {e}"
    
    def reject_teacher_request(self, request_id, student_id):
        """Отклонение заявки от учителя"""
        try:
            conn = self.get_connection()
            if conn is None:
                return False, "Ошибка подключения к базе данных"
            
            cursor = conn.cursor()
            
            # Удаление заявки
            cursor.execute(
                "DELETE FROM teacher_requests WHERE id = ? AND student_id = ? AND status = 'pending'",
                (request_id, student_id)
            )
            
            if cursor.rowcount == 0:
                conn.close()
                return False, "Заявка не найдена"
            
            conn.commit()
            conn.close()
            
            print(f"Заявка {request_id} отклонена")
            return True, "Заявка отклонена"
            
        except sqlite3.Error as e:
            print(f"Ошибка отклонения заявки: {e}")
            return False, f"Ошибка базы данных: {e}"
    
    def get_student_teachers(self, student_id):
        """Получение списка учителей ученика"""
        try:
            conn = self.get_connection()
            if conn is None:
                return []
            
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.first_name, u.last_name, u.subjects, u.school, u.city
                FROM student_teacher_relations str
                JOIN users u ON str.teacher_id = u.id
                WHERE str.student_id = ?
            ''', (student_id,))
            
            teachers = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return teachers
            
        except sqlite3.Error as e:
            print(f"Ошибка получения учителей ученика: {e}")
            return []
    
    def create_call(self, student_id, teacher_id, scheduled_time, duration_minutes=60, notes=""):
        """Создание записи о звонке"""
        try:
            conn = self.get_connection()
            if conn is None:
                return False, "Ошибка подключения к базе данных"
            
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO calls (student_id, teacher_id, scheduled_time, duration_minutes, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, teacher_id, scheduled_time, duration_minutes, notes))
            
            call_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"Звонок запланирован между учеником {student_id} и учителем {teacher_id}")
            return True, call_id
            
        except sqlite3.Error as e:
            print(f"Ошибка создания звонка: {e}")
            return False, f"Ошибка базы данных: {e}"
    
    def start_call(self, call_id):
        """Начало звонка"""
        try:
            conn = self.get_connection()
            if conn is None:
                return False, "Ошибка подключения к базе данных"
            
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE calls SET status = 'active', actual_start_time = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'scheduled'
            ''', (call_id,))
            
            if cursor.rowcount == 0:
                conn.close()
                return False, "Звонок не найден или уже начат"
            
            conn.commit()
            conn.close()
            
            print(f"Звонок {call_id} начат")
            return True, "Звонок начат"
            
        except sqlite3.Error as e:
            print(f"Ошибка начала звонка: {e}")
            return False, f"Ошибка базы данных: {e}"
    
    def end_call(self, call_id, recording_path=""):
        """Завершение звонка и создание записи урока"""
        try:
            conn = self.get_connection()
            if conn is None:
                return False, "Ошибка подключения к базе данных"
            
            cursor = conn.cursor()
            
            # Обновление статуса звонка
            cursor.execute('''
                UPDATE calls SET 
                    status = 'completed', 
                    actual_end_time = CURRENT_TIMESTAMP,
                    recording_path = ?
                WHERE id = ? AND status = 'active'
            ''', (recording_path, call_id))
            
            if cursor.rowcount == 0:
                conn.close()
                return False, "Звонок не найден или не активен"
            
            # Получение данных звонка для создания записи урока
            cursor.execute('''
                SELECT student_id, teacher_id, scheduled_time, notes
                FROM calls WHERE id = ?
            ''', (call_id,))
            
            call_data = cursor.fetchone()
            if call_data:
                from datetime import datetime, timedelta
                
                # Создание автоматической записи урока
                lesson_title = f"Урок (запись звонка от {call_data[2]})"
                expires_at = datetime.now() + timedelta(days=2)
                
                cursor.execute('''
                    INSERT INTO lesson_records 
                    (student_id, teacher_id, lesson_title, lesson_date, video_file_path, 
                     description, is_auto_created, call_id, expires_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, 1, ?, ?)
                ''', (call_data[0], call_data[1], lesson_title, recording_path, 
                      call_data[3] or "Автоматически созданная запись урока", call_id, expires_at))
            
            conn.commit()
            conn.close()
            
            print(f"Звонок {call_id} завершен, запись урока создана")
            return True, "Звонок завершен, запись сохранена"
            
        except sqlite3.Error as e:
            print(f"Ошибка завершения звонка: {e}")
            return False, f"Ошибка базы данных: {e}"
    
    def get_user_calls(self, user_id):
        """Получение звонков пользователя"""
        try:
            conn = self.get_connection()
            if conn is None:
                return []
            
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.*, 
                       u1.first_name as student_name, u1.last_name as student_surname,
                       u2.first_name as teacher_name, u2.last_name as teacher_surname
                FROM calls c
                JOIN users u1 ON c.student_id = u1.id
                JOIN users u2 ON c.teacher_id = u2.id
                WHERE c.student_id = ? OR c.teacher_id = ?
                ORDER BY c.scheduled_time DESC
            ''', (user_id, user_id))
            
            calls = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return calls
            
        except sqlite3.Error as e:
            print(f"Ошибка получения звонков: {e}")
            return []
    
    def get_call_by_id(self, call_id):
        """Получение звонка по ID"""
        try:
            conn = self.get_connection()
            if conn is None:
                return None
            
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.*, 
                       u1.first_name as student_name, u1.last_name as student_surname,
                       u2.first_name as teacher_name, u2.last_name as teacher_surname
                FROM calls c
                JOIN users u1 ON c.student_id = u1.id
                JOIN users u2 ON c.teacher_id = u2.id
                WHERE c.id = ?
            ''', (call_id,))
            
            call = cursor.fetchone()
            conn.close()
            
            return dict(call) if call else None
            
        except sqlite3.Error as e:
            print(f"Ошибка получения звонка: {e}")
            return None
    
    def cleanup_expired_records(self):
        """Очистка просроченных записей уроков (старше 2 дней)"""
        try:
            conn = self.get_connection()
            if conn is None:
                return False, "Ошибка подключения к базе данных"
            
            cursor = conn.cursor()
            
            # Удаление просроченных автоматических записей
            cursor.execute('''
                DELETE FROM lesson_records 
                WHERE is_auto_created = 1 
                AND expires_at < CURRENT_TIMESTAMP
            ''')
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                print(f"Удалено {deleted_count} просроченных записей уроков")
            
            return True, f"Удалено {deleted_count} просроченных записей"
            
        except sqlite3.Error as e:
            print(f"Ошибка очистки записей: {e}")
            return False, f"Ошибка базы данных: {e}"
    
    def create_lesson_record(self, student_id, teacher_id, lesson_title, lesson_date, subject="", video_url="", video_file_path="", description="", homework=""):
        """Создание записи урока"""
        try:
            conn = self.get_connection()
            if conn is None:
                return False, "Ошибка подключения к базе данных"
            
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO lesson_records (student_id, teacher_id, lesson_title, lesson_date, subject, video_url, video_file_path, description, homework, is_auto_created)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', (student_id, teacher_id, lesson_title, lesson_date, subject, video_url, video_file_path, description, homework))
            
            conn.commit()
            conn.close()
            
            print(f"Запись урока создана для ученика {student_id} и учителя {teacher_id}")
            return True, "Запись урока создана"
            
        except sqlite3.Error as e:
            print(f"Ошибка создания записи урока: {e}")
            return False, f"Ошибка базы данных: {e}"
    
    def get_downloadable_records(self, user_id):
        """Получение записей с возможностью скачивания"""
        try:
            conn = self.get_connection()
            if conn is None:
                return []
            
            cursor = conn.cursor()
            cursor.execute('''
                SELECT lr.*,
                       u1.first_name as student_name, u1.last_name as student_surname,
                       u2.first_name as teacher_name, u2.last_name as teacher_surname,
                       CASE 
                           WHEN lr.expires_at IS NULL THEN 'permanent'
                           WHEN lr.expires_at > CURRENT_TIMESTAMP THEN 'available'
                           ELSE 'expired'
                       END as availability_status
                FROM lesson_records lr
                JOIN users u1 ON lr.student_id = u1.id
                JOIN users u2 ON lr.teacher_id = u2.id
                WHERE (lr.student_id = ? OR lr.teacher_id = ?)
                AND lr.video_file_path IS NOT NULL 
                AND lr.video_file_path != ''
                ORDER BY lr.lesson_date DESC
            ''', (user_id, user_id))
            
            records = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return records
            
        except sqlite3.Error as e:
            print(f"Ошибка получения записей для скачивания: {e}")
            return []
    
    def get_user_lesson_records(self, user_id):
        """Получение записей уроков пользователя"""
        try:
            conn = self.get_connection()
            if conn is None:
                return []
            
            cursor = conn.cursor()
            cursor.execute('''
                SELECT lr.*,
                       u1.first_name as student_name, u1.last_name as student_surname,
                       u2.first_name as teacher_name, u2.last_name as teacher_surname,
                       CASE 
                           WHEN lr.expires_at IS NULL THEN 'permanent'
                           WHEN lr.expires_at > CURRENT_TIMESTAMP THEN 'available'
                           ELSE 'expired'
                       END as availability_status
                FROM lesson_records lr
                JOIN users u1 ON lr.student_id = u1.id
                JOIN users u2 ON lr.teacher_id = u2.id
                WHERE lr.student_id = ? OR lr.teacher_id = ?
                ORDER BY lr.lesson_date DESC
            ''', (user_id, user_id))
            
            records = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return records
            
        except sqlite3.Error as e:
            print(f"Ошибка получения записей уроков: {e}")
            return []
    
    def get_all_students(self):
        """Получение списка всех учеников"""
        try:
            conn = self.get_connection()
            if conn is None:
                return []
            
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, first_name, last_name, email, city, school, class_number
                FROM users WHERE role = ?
                ORDER BY first_name, last_name
            ''', ('Ученик',))
            
            students = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return students
            
        except sqlite3.Error as e:
            print(f"Ошибка получения списка учеников: {e}")
            return []
    
    def get_teacher_sent_requests(self, teacher_id):
        """Получение отправленных заявок учителя"""
        try:
            conn = self.get_connection()
            if conn is None:
                return []
            
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tr.*, u.first_name as student_name, u.last_name as student_surname
                FROM teacher_requests tr
                JOIN users u ON tr.student_id = u.id
                WHERE tr.teacher_id = ?
                ORDER BY tr.created_at DESC
            ''', (teacher_id,))
            
            requests = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return requests
            
        except sqlite3.Error as e:
            print(f"Ошибка получения отправленных заявок: {e}")
            return []
    
    def get_teacher_students(self, teacher_id):
        """Получение учеников учителя"""
        try:
            conn = self.get_connection()
            if conn is None:
                return []
            
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.first_name, u.last_name, u.email, u.city, u.school, u.class_number
                FROM student_teacher_relations str
                JOIN users u ON str.student_id = u.id
                WHERE str.teacher_id = ?
                ORDER BY u.first_name, u.last_name
            ''', (teacher_id,))
            
            students = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return students
            
        except sqlite3.Error as e:
            print(f"Ошибка получения учеников учителя: {e}")
            return []

# Создание экземпляра базы данных
db = Database()
