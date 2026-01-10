from sqlalchemy import create_engine, and_, or_, func, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
import hashlib
from datetime import datetime, timedelta
from database.settings import DATABASE_URL
from database.models import *
from logger.tracer import trace

class Database:
    """Класс для работы с базой данных через SQLAlchemy ORM"""
    
    def __init__(self):
        """Инициализация базы данных"""
        try:
            self.engine = create_engine(DATABASE_URL, echo=False)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.Session = scoped_session(self.SessionLocal)
            self.init_database()
        except Exception:
            pass
    
    def init_database(self):
        """Создание таблиц в базе данных"""
        try:
            Base.metadata.create_all(bind=self.engine)
            self.update_database_schema()
            return True
        except SQLAlchemyError:
            return False
    
    def update_database_schema(self):
        """Обновление схемы базы данных (добавление отсутствующих столбцов)"""
        try:
            with self.engine.begin() as conn:
                # Проверяем, существует ли таблица users
                result = conn.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
                ))
                table_exists = result.fetchone() is not None
                
                if not table_exists:
                    # Таблица будет создана через Base.metadata.create_all
                    return
                
                # Проверяем наличие столбца is_online в таблице users
                result = conn.execute(text("PRAGMA table_info(users)"))
                rows = result.fetchall()
                
                columns = [row[1] for row in rows]  # row[1] - это имя столбца
                
                # Добавляем столбец is_online, если его нет
                if 'is_online' not in columns:
                    try:
                        conn.execute(text("ALTER TABLE users ADD COLUMN is_online BOOLEAN DEFAULT 0"))
                    except Exception:
                        raise
                        
        except Exception:
            pass
    
    def get_session(self):
        """Получение сессии базы данных"""
        return self.Session()
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()
    
    @trace
    def register_user(self, user_data):
        """Регистрация нового пользователя"""
        session = self.get_session()
        try:
            # Нормализация email 
            email = user_data['email'].strip().lower() if user_data.get('email') else ''
            
            if not email:
                return False, "Email не может быть пустым"
            
            # Проверка на существование пользователя с таким email
            # Получаем всех пользователей и проверяем в Python для надежности
            all_users = session.query(User).all()
            for user in all_users:
                user_email_normalized = user.email.strip().lower() if user.email else ''
                if user_email_normalized == email:
                    print(f"Попытка регистрации с существующим email: {email} (найден пользователь ID: {user.id}, email в БД: '{user.email}')")
                    return False, "Пользователь с таким email уже существует"
            
            # Хеширование пароля
            password_hash = self.hash_password(user_data['password'])
            
            # Подготовка данных для вставки
            subjects = user_data.get('subjects', '')
            if isinstance(subjects, list):
                subjects = ', '.join(subjects)
            
            # Создание нового пользователя
            new_user = User(
                email=email,
                password_hash=password_hash,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role'],
                city=user_data.get('city', ''),
                school=user_data.get('school', ''),
                class_number=user_data.get('class_number', ''),
                subjects=subjects
            )
            
            session.add(new_user)
            session.commit()
            user_id = new_user.id
            
            print(f"Пользователь {email} успешно зарегистрирован (ID: {user_id})")
            return True, user_id
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка регистрации пользователя: {e}")
            return False, f"Ошибка базы данных: {e}"
        except Exception as e:
            session.rollback()
            print(f"Неожиданная ошибка при регистрации пользователя: {e}")
            return False, f"Ошибка: {e}"
        finally:
            session.close()
    
    @trace
    def get_user_by_email(self, email):
        """Получение пользователя по email"""
        session = self.get_session()
        try:
            email = email.strip().lower() if email else ''
            if not email:
                return None
            
            all_users = session.query(User).all()
            for u in all_users:
                user_email_normalized = u.email.strip().lower() if u.email else ''
                if user_email_normalized == email:
                    return {
                        'id': u.id,
                        'email': u.email,
                        'first_name': u.first_name,
                        'last_name': u.last_name,
                        'role': u.role
                    }
            return None
        except Exception as e:
            print(f"Ошибка получения пользователя по email: {e}")
            return None
        finally:
            session.close()
    
    @trace
    def reset_user_password(self, email, new_password):
        """Сброс пароля пользователя"""
        session = self.get_session()
        try:
            email = email.strip().lower() if email else ''
            if not email:
                return False, "Email не может быть пустым"
            
            all_users = session.query(User).all()
            user = None
            for u in all_users:
                user_email_normalized = u.email.strip().lower() if u.email else ''
                if user_email_normalized == email:
                    user = u
                    break
            
            if not user:
                return False, "Пользователь с таким email не найден"
            
            # Хеширование нового пароля
            password_hash = self.hash_password(new_password)
            user.password_hash = password_hash
            session.commit()
            
            print(f"Пароль успешно сброшен для пользователя {email}")
            return True, "Пароль успешно изменен"
            
        except Exception as e:
            session.rollback()
            print(f"Ошибка сброса пароля: {e}")
            return False, f"Ошибка: {e}"
        finally:
            session.close()
    
    @trace
    def authenticate_user(self, email, password):
        """Аутентификация пользователя"""
        session = self.get_session()
        try:
            # Нормализация email
            email = email.strip().lower() if email else ''
            
            if not email:
                return False, None
            
            password_hash = self.hash_password(password)
            # Получаем всех пользователей и проверяем в Python для надежности
            all_users = session.query(User).all()
            user = None
            for u in all_users:
                user_email_normalized = u.email.strip().lower() if u.email else ''
                if user_email_normalized == email and u.password_hash == password_hash:
                    user = u
                    break
            
            if user:
                user_dict = {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'city': user.city,
                    'is_online': user.is_online if hasattr(user, 'is_online') else False,
                    'school': user.school,
                    'class_number': user.class_number,
                    'subjects': user.subjects,
                    'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None
                }
                print(f"Пользователь {email} успешно аутентифицирован")
                return True, user_dict
            else:
                print(f"Неудачная попытка входа для {email}")
                return False, None
                
        except SQLAlchemyError as e:
            print(f"Ошибка аутентификации: {e}")
            return False, None
        except Exception as e:
            print(f"Неожиданная ошибка при аутентификации: {e}")
            return False, None
        finally:
            session.close()
    
    @trace
    def get_teachers(self):
        """Получение списка всех учителей"""
        session = self.get_session()
        try:
            teachers = session.query(User).filter(User.role == 'Учитель').all()
            teachers_list = []
            
            for teacher in teachers:
                teachers_list.append({
                    'id': teacher.id,
                    'first_name': teacher.first_name,
                    'last_name': teacher.last_name,
                    'subjects': teacher.subjects,
                    'city': teacher.city,
                    'school': teacher.school,
                    'is_online': teacher.is_online if hasattr(teacher, 'is_online') else False
                })
            
            return teachers_list
            
        except SQLAlchemyError as e:
            print(f"Ошибка получения списка учителей: {e}")
            return []
        finally:
            session.close()
    
    @trace
    def get_user_by_id(self, user_id):
        """Получение пользователя по ID"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                return {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'city': user.city,
                    'school': user.school,
                    'class_number': user.class_number,
                    'subjects': user.subjects,
                    'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None
                }
            return None
            
        except SQLAlchemyError as e:
            print(f"Ошибка получения пользователя: {e}")
            return None
        finally:
            session.close()
    
    @trace
    def delete_user(self, user_id, email, password):
        """Удаление пользователя с подтверждением"""
        session = self.get_session()
        try:
            # Проверка подлинности пользователя
            password_hash = self.hash_password(password)
            user = session.query(User).filter(
                and_(User.id == user_id, User.email == email, User.password_hash == password_hash)
            ).first()
            
            if not user:
                return False, "Неверный email или пароль"
            
            # Удаление связанных записей
            session.query(StudentTeacherRelation).filter(
                or_(StudentTeacherRelation.student_id == user_id, StudentTeacherRelation.teacher_id == user_id)
            ).delete()
            
            session.query(TeacherRequest).filter(
                or_(TeacherRequest.student_id == user_id, TeacherRequest.teacher_id == user_id)
            ).delete()
            
            session.query(LessonRecord).filter(
                or_(LessonRecord.student_id == user_id, LessonRecord.teacher_id == user_id)
            ).delete()
            
            session.query(Call).filter(
                or_(Call.student_id == user_id, Call.teacher_id == user_id)
            ).delete()
            
            # Удаление пользователя
            session.delete(user)
            session.commit()
            
            print(f"Пользователь с ID {user_id} успешно удален")
            return True, "Профиль успешно удален"
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка удаления пользователя: {e}")
            return False, f"Ошибка базы данных: {e}"
        finally:
            session.close()
    
    @trace
    def create_teacher_request(self, teacher_id, student_id, message=""):
        """Создание заявки от учителя к ученику"""
        session = self.get_session()
        try:
            # Проверка существования заявки
            existing_request = session.query(TeacherRequest).filter(
                and_(
                    TeacherRequest.teacher_id == teacher_id,
                    TeacherRequest.student_id == student_id,
                    TeacherRequest.status == 'pending'
                )
            ).first()
            
            if existing_request:
                return False, "Заявка уже отправлена"
            
            # Создание заявки
            new_request = TeacherRequest(
                teacher_id=teacher_id,
                student_id=student_id,
                message=message,
                status='pending'
            )
            
            session.add(new_request)
            session.commit()
            
            print(f"Заявка от учителя {teacher_id} к ученику {student_id} создана")
            return True, "Заявка отправлена"
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка создания заявки: {e}")
            return False, f"Ошибка базы данных: {e}"
        finally:
            session.close()
    
    @trace
    def get_student_requests(self, student_id):
        """Получение заявок для ученика"""
        session = self.get_session()
        try:
            requests = session.query(TeacherRequest, User).join(
                User, TeacherRequest.teacher_id == User.id
            ).filter(
                and_(TeacherRequest.student_id == student_id, TeacherRequest.status == 'pending')
            ).order_by(TeacherRequest.created_at.desc()).all()
            
            requests_list = []
            for request, teacher in requests:
                requests_list.append({
                    'id': request.id,
                    'teacher_id': request.teacher_id,
                    'message': request.message,
                    'created_at': request.created_at.strftime('%Y-%m-%d %H:%M:%S') if request.created_at else None,
                    'first_name': teacher.first_name,
                    'last_name': teacher.last_name,
                    'subjects': teacher.subjects,
                    'school': teacher.school
                })
            
            return requests_list
            
        except SQLAlchemyError as e:
            print(f"Ошибка получения заявок: {e}")
            return []
        finally:
            session.close()
    
    @trace
    def accept_teacher_request(self, request_id, student_id):
        """Принятие заявки от учителя"""
        session = self.get_session()
        try:
            # Получение данных заявки
            request = session.query(TeacherRequest).filter(
                and_(
                    TeacherRequest.id == request_id,
                    TeacherRequest.student_id == student_id,
                    TeacherRequest.status == 'pending'
                )
            ).first()
            
            if not request:
                return False, "Заявка не найдена"
            
            # Обновление статуса заявки
            request.status = 'accepted'
            request.updated_at = datetime.utcnow()
            
            # Добавление связи ученик-учитель
            new_relation = StudentTeacherRelation(
                student_id=student_id,
                teacher_id=request.teacher_id
            )
            session.add(new_relation)
            
            session.commit()
            
            print(f"Заявка {request_id} принята")
            return True, "Заявка принята, учитель добавлен"
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка принятия заявки: {e}")
            return False, f"Ошибка базы данных: {e}"
        finally:
            session.close()
    
    @trace
    def reject_teacher_request(self, request_id, student_id):
        """Отклонение заявки от учителя"""
        session = self.get_session()
        try:
            # Удаление заявки
            request = session.query(TeacherRequest).filter(
                and_(
                    TeacherRequest.id == request_id,
                    TeacherRequest.student_id == student_id,
                    TeacherRequest.status == 'pending'
                )
            ).first()
            
            if not request:
                return False, "Заявка не найдена"
            
            session.delete(request)
            session.commit()
            
            print(f"Заявка {request_id} отклонена")
            return True, "Заявка отклонена"
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка отклонения заявки: {e}")
            return False, f"Ошибка базы данных: {e}"
        finally:
            session.close()
    
    @trace
    def get_student_teachers(self, student_id):
        """Получение списка учителей ученика"""
        session = self.get_session()
        try:
            teachers = session.query(User).join(
                StudentTeacherRelation, StudentTeacherRelation.teacher_id == User.id
            ).filter(StudentTeacherRelation.student_id == student_id).all()
            
            teachers_list = []
            for teacher in teachers:
                teachers_list.append({
                    'id': teacher.id,
                    'first_name': teacher.first_name,
                    'last_name': teacher.last_name,
                    'subjects': teacher.subjects,
                    'school': teacher.school,
                    'city': teacher.city,
                    'is_online': teacher.is_online if hasattr(teacher, 'is_online') else False
                })
            
            return teachers_list
            
        except SQLAlchemyError as e:
            print(f"Ошибка получения учителей ученика: {e}")
            return []
        finally:
            session.close()
    
    @trace
    def create_call(self, student_id, teacher_id, scheduled_time, duration_minutes=60, notes=""):
        """Создание записи о звонке"""
        session = self.get_session()
        try:
            new_call = Call(
                student_id=student_id,
                teacher_id=teacher_id,
                scheduled_time=scheduled_time,
                duration_minutes=duration_minutes,
                notes=notes
            )
            
            session.add(new_call)
            session.commit()
            call_id = new_call.id
            
            print(f"Звонок запланирован между учеником {student_id} и учителем {teacher_id}")
            return True, call_id
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка создания звонка: {e}")
            return False, f"Ошибка базы данных: {e}"
        finally:
            session.close()
    
    @trace
    def start_call(self, call_id):
        """Начало звонка"""
        session = self.get_session()
        try:
            call = session.query(Call).filter(
                and_(Call.id == call_id, Call.status == 'scheduled')
            ).first()
            
            if not call:
                return False, "Звонок не найден или уже начат"
            
            call.status = 'active'
            call.actual_start_time = datetime.utcnow()
            session.commit()
            
            print(f"Звонок {call_id} начат")
            return True, "Звонок начат"
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка начала звонка: {e}")
            return False, f"Ошибка базы данных: {e}"
        finally:
            session.close()
    
    @trace
    def end_call(self, call_id, recording_path=""):
        """Завершение звонка и создание записи урока"""
        session = self.get_session()
        try:
            call = session.query(Call).filter(
                and_(Call.id == call_id, Call.status == 'active')
            ).first()
            
            if not call:
                return False, "Звонок не найден или не активен"
            
            # Обновление статуса звонка
            call.status = 'completed'
            call.actual_end_time = datetime.utcnow()
            call.recording_path = recording_path
            
            # Создание автоматической записи урока
            lesson_title = f"Урок (запись звонка от {call.scheduled_time})"
            expires_at = datetime.utcnow() + timedelta(days=2)
            
            new_lesson = LessonRecord(
                student_id=call.student_id,
                teacher_id=call.teacher_id,
                lesson_title=lesson_title,
                lesson_date=datetime.utcnow(),
                video_file_path=recording_path,
                description=call.notes or "Автоматически созданная запись урока",
                is_auto_created=True,
                call_id=call_id,
                expires_at=expires_at
            )
            
            session.add(new_lesson)
            session.commit()
            
            print(f"Звонок {call_id} завершен, запись урока создана")
            return True, "Звонок завершен, запись сохранена"
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка завершения звонка: {e}")
            return False, f"Ошибка базы данных: {e}"
        finally:
            session.close()
    
    @trace
    def get_user_calls(self, user_id):
        """Получение звонков пользователя"""
        session = self.get_session()
        try:
            calls = session.query(Call, User.first_name.label('student_name'), User.last_name.label('student_surname')).join(
                User, Call.student_id == User.id
            ).filter(
                or_(Call.student_id == user_id, Call.teacher_id == user_id)
            ).order_by(Call.scheduled_time.desc()).all()
            
            # Дополнительно получаем данные учителей
            calls_with_teacher = session.query(Call, 
                User.first_name.label('teacher_name'), 
                User.last_name.label('teacher_surname')
            ).join(
                User, Call.teacher_id == User.id
            ).filter(
                or_(Call.student_id == user_id, Call.teacher_id == user_id)
            ).order_by(Call.scheduled_time.desc()).all()
            
            calls_list = []
            for i, (call, student_name, student_surname) in enumerate(calls):
                teacher_name = calls_with_teacher[i][1]
                teacher_surname = calls_with_teacher[i][2]
                
                calls_list.append({
                    'id': call.id,
                    'student_id': call.student_id,
                    'teacher_id': call.teacher_id,
                    'scheduled_time': call.scheduled_time.strftime('%Y-%m-%d %H:%M:%S') if call.scheduled_time else None,
                    'actual_start_time': call.actual_start_time.strftime('%Y-%m-%d %H:%M:%S') if call.actual_start_time else None,
                    'actual_end_time': call.actual_end_time.strftime('%Y-%m-%d %H:%M:%S') if call.actual_end_time else None,
                    'duration_minutes': call.duration_minutes,
                    'status': call.status,
                    'recording_path': call.recording_path,
                    'notes': call.notes,
                    'created_at': call.created_at.strftime('%Y-%m-%d %H:%M:%S') if call.created_at else None,
                    'student_name': student_name,
                    'student_surname': student_surname,
                    'teacher_name': teacher_name,
                    'teacher_surname': teacher_surname
                })
            
            return calls_list
            
        except SQLAlchemyError as e:
            print(f"Ошибка получения звонков: {e}")
            return []
        finally:
            session.close()
    
    @trace
    def cleanup_expired_records(self):
        """Очистка просроченных записей уроков (старше 2 дней)"""
        session = self.get_session()
        try:
            # Удаление просроченных автоматических записей
            deleted_count = session.query(LessonRecord).filter(
                and_(
                    LessonRecord.is_auto_created == True,
                    LessonRecord.expires_at < datetime.utcnow()
                )
            ).delete()
            
            session.commit()
            
            if deleted_count > 0:
                print(f"Удалено {deleted_count} просроченных записей уроков")
            
            return True, f"Удалено {deleted_count} просроченных записей"
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка очистки записей: {e}")
            return False, f"Ошибка базы данных: {e}"
        finally:
            session.close()
    
    @trace
    def create_lesson_record(self, student_id, teacher_id, lesson_title, lesson_date, subject="", video_url="", video_file_path="", description="", homework=""):
        """Создание записи урока"""
        session = self.get_session()
        try:
            new_lesson = LessonRecord(
                student_id=student_id,
                teacher_id=teacher_id,
                lesson_title=lesson_title,
                lesson_date=lesson_date,
                subject=subject,
                video_url=video_url,
                video_file_path=video_file_path,
                description=description,
                homework=homework,
                is_auto_created=False
            )
            
            session.add(new_lesson)
            session.commit()
            
            print(f"Запись урока создана для ученика {student_id} и учителя {teacher_id}")
            return True, "Запись урока создана"
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка создания записи урока: {e}")
            return False, f"Ошибка базы данных: {e}"
        finally:
            session.close()
    
    @trace
    def get_user_lesson_records(self, user_id):
        """Получение записей уроков пользователя"""
        session = self.get_session()
        try:
            records = session.query(LessonRecord, 
                User.first_name.label('student_name'), 
                User.last_name.label('student_surname')
            ).join(
                User, LessonRecord.student_id == User.id
            ).filter(
                or_(LessonRecord.student_id == user_id, LessonRecord.teacher_id == user_id)
            ).order_by(LessonRecord.lesson_date.desc()).all()
            
            # Дополнительно получаем данные учителей
            records_with_teacher = session.query(LessonRecord,
                User.first_name.label('teacher_name'),
                User.last_name.label('teacher_surname')
            ).join(
                User, LessonRecord.teacher_id == User.id
            ).filter(
                or_(LessonRecord.student_id == user_id, LessonRecord.teacher_id == user_id)
            ).order_by(LessonRecord.lesson_date.desc()).all()
            
            records_list = []
            for i, (record, student_name, student_surname) in enumerate(records):
                teacher_name = records_with_teacher[i][1]
                teacher_surname = records_with_teacher[i][2]
                
                records_list.append({
                    'id': record.id,
                    'student_id': record.student_id,
                    'teacher_id': record.teacher_id,
                    'lesson_title': record.lesson_title,
                    'lesson_date': record.lesson_date.strftime('%Y-%m-%d %H:%M:%S') if record.lesson_date else None,
                    'subject': record.subject,
                    'video_url': record.video_url,
                    'video_file_path': record.video_file_path,
                    'description': record.description,
                    'homework': record.homework,
                    'is_auto_created': record.is_auto_created,
                    'call_id': record.call_id,
                    'expires_at': record.expires_at.strftime('%Y-%m-%d %H:%M:%S') if record.expires_at else None,
                    'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S') if record.created_at else None,
                    'student_name': student_name,
                    'student_surname': student_surname,
                    'teacher_name': teacher_name,
                    'teacher_surname': teacher_surname,
                    'availability_status': record.availability_status
                })
            
            return records_list
            
        except SQLAlchemyError as e:
            print(f"Ошибка получения записей уроков: {e}")
            return []
        finally:
            session.close()
    
    @trace
    def get_all_students(self):
        """Получение списка всех учеников"""
        session = self.get_session()
        try:
            students = session.query(User).filter(User.role == 'Ученик').order_by(User.first_name, User.last_name).all()
            
            students_list = []
            for student in students:
                students_list.append({
                    'id': student.id,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'city': student.city,
                    'school': student.school,
                    'class_number': student.class_number,
                    'is_online': student.is_online if hasattr(student, 'is_online') else False
                })
            
            return students_list
            
        except SQLAlchemyError as e:
            print(f"Ошибка получения списка учеников: {e}")
            return []
        finally:
            session.close()
    
    @trace
    def get_pending_requests_for_student(self, student_id):
        """Получение входящих заявок для ученика"""
        session = self.get_session()
        try:
            requests = session.query(TeacherRequest, User).join(
                User, TeacherRequest.teacher_id == User.id
            ).filter(
                TeacherRequest.student_id == student_id,
                TeacherRequest.status == 'pending'
            ).order_by(TeacherRequest.created_at.desc()).all()
            
            requests_list = []
            for request, teacher in requests:
                requests_list.append({
                    'id': request.id,
                    'teacher_id': request.teacher_id,
                    'first_name': teacher.first_name,
                    'last_name': teacher.last_name,
                    'email': teacher.email,
                    'subjects': teacher.subjects if hasattr(teacher, 'subjects') else None,
                    'school': teacher.school,
                    'city': teacher.city,
                    'message': request.message,
                    'created_at': request.created_at.strftime('%Y-%m-%d %H:%M') if request.created_at else None
                })
            
            return requests_list
            
        except SQLAlchemyError as e:
            print(f"Ошибка получения входящих заявок: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            session.close()
    
    @trace
    def get_requests_by_teacher(self, teacher_id):
        """Получение всех заявок отправленных учителем"""
        session = self.get_session()
        try:
            requests = session.query(TeacherRequest, User).join(
                User, TeacherRequest.student_id == User.id
            ).filter(TeacherRequest.teacher_id == teacher_id).order_by(TeacherRequest.created_at.desc()).all()
            
            requests_list = []
            for request, student in requests:
                requests_list.append({
                    'id': request.id,
                    'student_id': request.student_id,
                    'student_name': f"{student.first_name} {student.last_name}",
                    'student_email': student.email,
                    'status': request.status,
                    'message': request.message,
                    'created_at': request.created_at.strftime('%Y-%m-%d %H:%M') if request.created_at else None
                })
            
            return requests_list
            
        except SQLAlchemyError as e:
            print(f"Ошибка получения отправленных заявок: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            session.close()
    
    @trace
    def get_teacher_sent_requests(self, teacher_id):
        """Получение отправленных заявок учителя"""
        session = self.get_session()
        try:
            requests = session.query(TeacherRequest, User).join(
                User, TeacherRequest.student_id == User.id
            ).filter(TeacherRequest.teacher_id == teacher_id).order_by(TeacherRequest.created_at.desc()).all()
            
            requests_list = []
            for request, student in requests:
                requests_list.append({
                    'id': request.id,
                    'student_id': request.student_id,
                    'status': request.status,
                    'message': request.message,
                    'created_at': request.created_at.strftime('%Y-%m-%d %H:%M:%S') if request.created_at else None,
                    'student_name': student.first_name,
                    'student_surname': student.last_name
                })
            
            return requests_list
            
        except SQLAlchemyError as e:
            print(f"Ошибка получения отправленных заявок: {e}")
            return []
        finally:
            session.close()
    
    @trace
    def get_teacher_students(self, teacher_id):
        """Получение учеников учителя"""
        session = self.get_session()
        try:
            students = session.query(User).join(
                StudentTeacherRelation, StudentTeacherRelation.student_id == User.id
            ).filter(StudentTeacherRelation.teacher_id == teacher_id).order_by(User.first_name, User.last_name).all()
            
            students_list = []
            for student in students:
                students_list.append({
                    'id': student.id,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'city': student.city,
                    'school': student.school,
                    'class_number': student.class_number,
                    'is_online': student.is_online if hasattr(student, 'is_online') else False
                })
            
            return students_list
            
        except SQLAlchemyError as e:
            print(f"Ошибка получения учеников учителя: {e}")
            return []
        finally:
            session.close()
    
    @trace
    def update_user_online_status(self, user_id, is_online):
        """Обновление статуса онлайн пользователя"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.is_online = is_online
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка обновления статуса онлайн: {e}")
            return False
        finally:
            session.close()
    
    @trace
    def get_user_notifications(self, user_id):
        """Получение уведомлений пользователя"""
        session = self.get_session()
        try:
            notifications = session.query(Notification).filter(
                Notification.user_id == user_id
            ).order_by(Notification.created_at.desc()).all()
            
            notifications_list = []
            for notification in notifications:
                notifications_list.append({
                    'id': notification.id,
                    'user_id': notification.user_id,
                    'title': notification.title,
                    'message': notification.message,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S') if notification.created_at else None
                })
            
            return notifications_list
        except SQLAlchemyError as e:
            print(f"Ошибка получения уведомлений: {e}")
            return []
        finally:
            session.close()
    
    @trace
    def mark_notification_read(self, notification_id, user_id):
        """Отметить уведомление как прочитанное"""
        session = self.get_session()
        try:
            notification = session.query(Notification).filter(
                and_(Notification.id == notification_id, Notification.user_id == user_id)
            ).first()
            
            if not notification:
                return False, "Уведомление не найдено"
            
            notification.is_read = True
            session.commit()
            return True, "Уведомление отмечено как прочитанное"
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка отметки уведомления: {e}")
            return False, f"Ошибка базы данных: {e}"
        finally:
            session.close()
    
    @trace
    def create_notification(self, user_id, title, message):
        """Создание нового уведомления"""
        session = self.get_session()
        try:
            new_notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                is_read=False
            )
            
            session.add(new_notification)
            session.commit()
            notification_id = new_notification.id
            
            return True, notification_id
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка создания уведомления: {e}")
            return False, f"Ошибка базы данных: {e}"
        finally:
            session.close()
    
    @trace
    def get_teacher_students_tree(self, teacher_id):
        """Получение древовидной структуры учеников учителя: Город → Школа → Класс → Ученики"""
        session = self.get_session()
        try:
            students = session.query(User).join(
                StudentTeacherRelation, StudentTeacherRelation.student_id == User.id
            ).filter(StudentTeacherRelation.teacher_id == teacher_id).order_by(
                User.city, User.school, User.class_number, User.first_name, User.last_name
            ).all()
            
            tree = {}
            for student in students:
                city = student.city or "Не указан"
                school = student.school or "Не указана"
                class_num = student.class_number or "Не указан"
                
                if city not in tree:
                    tree[city] = {}
                if school not in tree[city]:
                    tree[city][school] = {}
                if class_num not in tree[city][school]:
                    tree[city][school][class_num] = []
                
                tree[city][school][class_num].append({
                    'id': student.id,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'city': student.city,
                    'school': student.school,
                    'class_number': student.class_number,
                    'is_online': student.is_online if hasattr(student, 'is_online') else False
                })
            
            return tree
        except SQLAlchemyError as e:
            print(f"Ошибка получения дерева учеников: {e}")
            return {}
        finally:
            session.close()

    # ==================== Методы для настроек пользователя ====================
    
    @trace
    def get_user_settings(self, user_id):
        """Получение настроек пользователя"""
        session = self.get_session()
        try:
            settings = session.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            if settings:
                return settings.to_dict()
            return UserSettings.get_defaults()
        except SQLAlchemyError as e:
            print(f"Ошибка получения настроек: {e}")
            return UserSettings.get_defaults()
        finally:
            session.close()
    
    @trace
    def update_user_settings(self, user_id, settings_data):
        """Обновление настроек пользователя"""
        session = self.get_session()
        try:
            settings = session.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            if not settings:
                settings = UserSettings(user_id=user_id)
                session.add(settings)
            
            if 'theme' in settings_data:
                settings.theme = settings_data['theme']
            if 'font_size' in settings_data:
                settings.font_size = settings_data['font_size']
            if 'notifications_enabled' in settings_data:
                settings.notifications_enabled = settings_data['notifications_enabled']
            if 'sound_enabled' in settings_data:
                settings.sound_enabled = settings_data['sound_enabled']
            if 'language' in settings_data:
                settings.language = settings_data['language']
            
            session.commit()
            return True, "Настройки обновлены"
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка обновления настроек: {e}")
            return False, str(e)
        finally:
            session.close()
    
    @trace
    def reset_user_settings(self, user_id):
        """Сброс настроек пользователя к значениям по умолчанию"""
        session = self.get_session()
        try:
            settings = session.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            if settings:
                defaults = UserSettings.get_defaults()
                settings.theme = defaults['theme']
                settings.font_size = defaults['font_size']
                settings.notifications_enabled = defaults['notifications_enabled']
                settings.sound_enabled = defaults['sound_enabled']
                settings.language = defaults['language']
                session.commit()
            return True, "Настройки сброшены"
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка сброса настроек: {e}")
            return False, str(e)
        finally:
            session.close()
    
    # ==================== Методы для заданий классу ====================
    
    @trace
    def create_class_assignment(self, teacher_id, title, description, subject, topic, 
                                 difficulty, assignment_type, questions_json,
                                 target_city, target_school, target_class, deadline=None):
        """Создание задания для класса"""
        session = self.get_session()
        try:
            new_assignment = ClassAssignment(
                teacher_id=teacher_id,
                title=title,
                description=description,
                subject=subject,
                topic=topic,
                difficulty=difficulty,
                assignment_type=assignment_type,
                questions_json=questions_json,
                target_city=target_city,
                target_school=target_school,
                target_class=target_class,
                deadline=deadline,
                is_active=True
            )
            
            session.add(new_assignment)
            session.commit()
            assignment_id = new_assignment.id
            
            # Создаём уведомления для учеников
            students = self._get_students_by_criteria(session, target_city, target_school, target_class)
            for student in students:
                notification = Notification(
                    user_id=student.id,
                    title=f"📝 Новое задание: {title}",
                    message=f"Учитель назначил новое задание по предмету {subject}. Тема: {topic}",
                    is_read=False
                )
                session.add(notification)
            
            session.commit()
            
            print(f"Задание создано: {title} для класса {target_class}")
            return True, assignment_id
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка создания задания: {e}")
            return False, str(e)
        finally:
            session.close()
    
    def _get_students_by_criteria(self, session, city, school, class_number):
        """Получение учеников по критериям (внутренний метод)"""
        query = session.query(User).filter(User.role == 'Ученик')
        
        if city:
            query = query.filter(User.city == city)
        if school:
            query = query.filter(User.school == school)
        if class_number:
            # Поддержка нескольких классов через запятую
            classes = [c.strip() for c in class_number.split(',')]
            query = query.filter(User.class_number.in_(classes))
        
        return query.all()
    
    @trace
    def get_teacher_assignments(self, teacher_id):
        """Получение заданий учителя"""
        session = self.get_session()
        try:
            assignments = session.query(ClassAssignment).filter(
                ClassAssignment.teacher_id == teacher_id
            ).order_by(ClassAssignment.created_at.desc()).all()
            
            result = []
            for a in assignments:
                submissions = session.query(AssignmentSubmission).filter(
                    AssignmentSubmission.assignment_id == a.id
                ).all()
                
                result.append({
                    'id': a.id,
                    'title': a.title,
                    'description': a.description,
                    'subject': a.subject,
                    'topic': a.topic,
                    'difficulty': a.difficulty,
                    'assignment_type': a.assignment_type,
                    'target_city': a.target_city,
                    'target_school': a.target_school,
                    'target_class': a.target_class,
                    'deadline': a.deadline.strftime('%Y-%m-%d %H:%M') if a.deadline else None,
                    'is_active': a.is_active,
                    'created_at': a.created_at.strftime('%Y-%m-%d %H:%M'),
                    'submissions_count': len(submissions),
                    'avg_score': sum(s.percentage for s in submissions) / len(submissions) if submissions else 0
                })
            
            return result
        except SQLAlchemyError as e:
            print(f"Ошибка получения заданий: {e}")
            return []
        finally:
            session.close()
    
    @trace
    def get_student_assignments(self, student_id):
        """Получение заданий для ученика"""
        session = self.get_session()
        try:
            student = session.query(User).filter(User.id == student_id).first()
            if not student:
                return []
            
            # Получаем задания, подходящие для ученика
            query = session.query(ClassAssignment).filter(
                ClassAssignment.is_active == True
            )
            
            if student.city:
                query = query.filter(
                    or_(ClassAssignment.target_city == student.city, ClassAssignment.target_city == None)
                )
            if student.school:
                query = query.filter(
                    or_(ClassAssignment.target_school == student.school, ClassAssignment.target_school == None)
                )
            if student.class_number:
                query = query.filter(
                    or_(
                        ClassAssignment.target_class.contains(student.class_number),
                        ClassAssignment.target_class == None
                    )
                )
            
            assignments = query.order_by(ClassAssignment.created_at.desc()).all()
            
            result = []
            for a in assignments:
                # Проверяем, отправил ли ученик ответ
                submission = session.query(AssignmentSubmission).filter(
                    and_(
                        AssignmentSubmission.assignment_id == a.id,
                        AssignmentSubmission.student_id == student_id
                    )
                ).first()
                
                teacher = session.query(User).filter(User.id == a.teacher_id).first()
                
                result.append({
                    'id': a.id,
                    'title': a.title,
                    'description': a.description,
                    'subject': a.subject,
                    'topic': a.topic,
                    'difficulty': a.difficulty,
                    'assignment_type': a.assignment_type,
                    'deadline': a.deadline.strftime('%Y-%m-%d %H:%M') if a.deadline else None,
                    'created_at': a.created_at.strftime('%Y-%m-%d %H:%M'),
                    'teacher_name': f"{teacher.first_name} {teacher.last_name}" if teacher else "Неизвестно",
                    'is_submitted': submission is not None,
                    'submission': {
                        'score': submission.score,
                        'max_score': submission.max_score,
                        'percentage': submission.percentage,
                        'submitted_at': submission.submitted_at.strftime('%Y-%m-%d %H:%M')
                    } if submission else None
                })
            
            return result
        except SQLAlchemyError as e:
            print(f"Ошибка получения заданий ученика: {e}")
            return []
        finally:
            session.close()
    
    @trace
    def get_assignment_by_id(self, assignment_id):
        """Получение задания по ID"""
        session = self.get_session()
        try:
            assignment = session.query(ClassAssignment).filter(
                ClassAssignment.id == assignment_id
            ).first()
            
            if not assignment:
                return None
            
            teacher = session.query(User).filter(User.id == assignment.teacher_id).first()
            
            return {
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'subject': assignment.subject,
                'topic': assignment.topic,
                'difficulty': assignment.difficulty,
                'assignment_type': assignment.assignment_type,
                'questions_json': assignment.questions_json,
                'target_city': assignment.target_city,
                'target_school': assignment.target_school,
                'target_class': assignment.target_class,
                'deadline': assignment.deadline.strftime('%Y-%m-%d %H:%M') if assignment.deadline else None,
                'is_active': assignment.is_active,
                'created_at': assignment.created_at.strftime('%Y-%m-%d %H:%M'),
                'teacher_id': assignment.teacher_id,
                'teacher_name': f"{teacher.first_name} {teacher.last_name}" if teacher else "Неизвестно"
            }
        except SQLAlchemyError as e:
            print(f"Ошибка получения задания: {e}")
            return None
        finally:
            session.close()
    
    @trace
    def submit_assignment(self, assignment_id, student_id, answers_json, score, max_score, time_spent=0):
        """Отправка ответа на задание"""
        session = self.get_session()
        try:
            # Проверяем, не отправлял ли ученик уже ответ
            existing = session.query(AssignmentSubmission).filter(
                and_(
                    AssignmentSubmission.assignment_id == assignment_id,
                    AssignmentSubmission.student_id == student_id
                )
            ).first()
            
            if existing:
                return False, "Вы уже отправили ответ на это задание"
            
            percentage = int((score / max_score) * 100) if max_score > 0 else 0
            
            submission = AssignmentSubmission(
                assignment_id=assignment_id,
                student_id=student_id,
                answers_json=answers_json,
                score=score,
                max_score=max_score,
                percentage=percentage,
                time_spent=time_spent,
                status='submitted'
            )
            
            session.add(submission)
            session.commit()
            
            print(f"Ответ на задание {assignment_id} от ученика {student_id} отправлен")
            return True, submission.id
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка отправки ответа: {e}")
            return False, str(e)
        finally:
            session.close()
    
    @trace
    def get_assignment_statistics(self, assignment_id):
        """Получение статистики по заданию"""
        session = self.get_session()
        try:
            assignment = session.query(ClassAssignment).filter(
                ClassAssignment.id == assignment_id
            ).first()
            
            if not assignment:
                return None
            
            submissions = session.query(AssignmentSubmission).filter(
                AssignmentSubmission.assignment_id == assignment_id
            ).all()
            
            if not submissions:
                return {
                    'assignment_id': assignment_id,
                    'title': assignment.title,
                    'total_submissions': 0,
                    'avg_score': 0,
                    'avg_percentage': 0,
                    'avg_time': 0,
                    'max_score': 0,
                    'min_score': 0,
                    'submissions': []
                }
            
            submissions_data = []
            for s in submissions:
                student = session.query(User).filter(User.id == s.student_id).first()
                submissions_data.append({
                    'student_id': s.student_id,
                    'student_name': f"{student.first_name} {student.last_name}" if student else "Неизвестно",
                    'student_class': student.class_number if student else "",
                    'score': s.score,
                    'max_score': s.max_score,
                    'percentage': s.percentage,
                    'time_spent': s.time_spent,
                    'submitted_at': s.submitted_at.strftime('%Y-%m-%d %H:%M')
                })
            
            avg_score = sum(s.score for s in submissions) / len(submissions)
            avg_percentage = sum(s.percentage for s in submissions) / len(submissions)
            avg_time = sum(s.time_spent for s in submissions) / len(submissions)
            
            return {
                'assignment_id': assignment_id,
                'title': assignment.title,
                'subject': assignment.subject,
                'topic': assignment.topic,
                'total_submissions': len(submissions),
                'avg_score': round(avg_score, 2),
                'avg_percentage': round(avg_percentage, 2),
                'avg_time': round(avg_time),
                'max_score': max(s.percentage for s in submissions),
                'min_score': min(s.percentage for s in submissions),
                'submissions': submissions_data
            }
        except SQLAlchemyError as e:
            print(f"Ошибка получения статистики: {e}")
            return None
        finally:
            session.close()
    
    @trace
    def get_class_statistics(self, teacher_id, city=None, school=None, class_number=None):
        """Получение статистики по классу"""
        session = self.get_session()
        try:
            # Получаем все задания учителя
            assignments = session.query(ClassAssignment).filter(
                ClassAssignment.teacher_id == teacher_id
            )
            
            if city:
                assignments = assignments.filter(ClassAssignment.target_city == city)
            if school:
                assignments = assignments.filter(ClassAssignment.target_school == school)
            if class_number:
                assignments = assignments.filter(ClassAssignment.target_class.contains(class_number))
            
            assignments = assignments.all()
            
            if not assignments:
                return {'total_assignments': 0, 'students': []}
            
            # Собираем статистику по ученикам
            students_stats = {}
            for a in assignments:
                submissions = session.query(AssignmentSubmission).filter(
                    AssignmentSubmission.assignment_id == a.id
                ).all()
                
                for s in submissions:
                    if s.student_id not in students_stats:
                        student = session.query(User).filter(User.id == s.student_id).first()
                        students_stats[s.student_id] = {
                            'student_id': s.student_id,
                            'name': f"{student.first_name} {student.last_name}" if student else "Неизвестно",
                            'class': student.class_number if student else "",
                            'total_submissions': 0,
                            'total_score': 0,
                            'avg_percentage': 0
                        }
                    
                    students_stats[s.student_id]['total_submissions'] += 1
                    students_stats[s.student_id]['total_score'] += s.percentage
            
            # Вычисляем средние
            for student_id in students_stats:
                if students_stats[student_id]['total_submissions'] > 0:
                    students_stats[student_id]['avg_percentage'] = round(
                        students_stats[student_id]['total_score'] / students_stats[student_id]['total_submissions'],
                        2
                    )
            
            return {
                'total_assignments': len(assignments),
                'students': list(students_stats.values())
            }
        except SQLAlchemyError as e:
            print(f"Ошибка получения статистики класса: {e}")
            return {'total_assignments': 0, 'students': []}
        finally:
            session.close()
    
    @trace
    def toggle_assignment_active(self, assignment_id, teacher_id):
        """Активация/деактивация задания"""
        session = self.get_session()
        try:
            assignment = session.query(ClassAssignment).filter(
                and_(
                    ClassAssignment.id == assignment_id,
                    ClassAssignment.teacher_id == teacher_id
                )
            ).first()
            
            if not assignment:
                return False, "Задание не найдено"
            
            assignment.is_active = not assignment.is_active
            session.commit()
            
            status = "активировано" if assignment.is_active else "деактивировано"
            return True, f"Задание {status}"
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка изменения статуса задания: {e}")
            return False, str(e)
        finally:
            session.close()


db = Database()