from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
import hashlib
from datetime import datetime, timedelta
from database.settings import DATABASE_URL
from database.models import Base, User, StudentTeacherRelation, TeacherRequest, Call, LessonRecord

class Database:
    """Класс для работы с базой данных через SQLAlchemy ORM"""
    
    def __init__(self):
        """Инициализация базы данных"""
        try:
            self.engine = create_engine(DATABASE_URL, echo=False)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.Session = scoped_session(self.SessionLocal)
            self.init_database()
            print("База данных успешно инициализирована с SQLAlchemy")
        except Exception as e:
            print(f"Ошибка инициализации базы данных: {e}")
    
    def init_database(self):
        """Создание таблиц в базе данных"""
        try:
            Base.metadata.create_all(bind=self.engine)
            return True
        except SQLAlchemyError as e:
            print(f"Ошибка создания таблиц: {e}")
            return False
    
    def get_session(self):
        """Получение сессии базы данных"""
        return self.Session()
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()
    
    def register_user(self, user_data):
        """Регистрация нового пользователя"""
        session = self.get_session()
        try:
            # Проверка на существование пользователя с таким email
            existing_user = session.query(User).filter(User.email == user_data['email']).first()
            if existing_user:
                return False, "Пользователь с таким email уже существует"
            
            # Хеширование пароля
            password_hash = self.hash_password(user_data['password'])
            
            # Подготовка данных для вставки
            subjects = user_data.get('subjects', '')
            if isinstance(subjects, list):
                subjects = ', '.join(subjects)
            
            # Создание нового пользователя
            new_user = User(
                email=user_data['email'],
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
            
            print(f"Пользователь {user_data['email']} успешно зарегистрирован")
            return True, user_id
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка регистрации пользователя: {e}")
            return False, f"Ошибка базы данных: {e}"
        finally:
            session.close()
    
    def authenticate_user(self, email, password):
        """Аутентификация пользователя"""
        session = self.get_session()
        try:
            password_hash = self.hash_password(password)
            user = session.query(User).filter(
                and_(User.email == email, User.password_hash == password_hash)
            ).first()
            
            if user:
                user_dict = {
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
                print(f"Пользователь {email} успешно аутентифицирован")
                return True, user_dict
            else:
                print(f"Неудачная попытка входа для {email}")
                return False, None
                
        except SQLAlchemyError as e:
            print(f"Ошибка аутентификации: {e}")
            return False, None
        finally:
            session.close()
    
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
                    'school': teacher.school
                })
            
            return teachers_list
            
        except SQLAlchemyError as e:
            print(f"Ошибка получения списка учителей: {e}")
            return []
        finally:
            session.close()
    
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
                    'city': teacher.city
                })
            
            return teachers_list
            
        except SQLAlchemyError as e:
            print(f"Ошибка получения учителей ученика: {e}")
            return []
        finally:
            session.close()
    
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
                    'class_number': student.class_number
                })
            
            return students_list
            
        except SQLAlchemyError as e:
            print(f"Ошибка получения списка учеников: {e}")
            return []
        finally:
            session.close()
    
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
                    'class_number': student.class_number
                })
            
            return students_list
            
        except SQLAlchemyError as e:
            print(f"Ошибка получения учеников учителя: {e}")
            return []
        finally:
            session.close()

# Создание экземпляра базы данных
db = Database()
