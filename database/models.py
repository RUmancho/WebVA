from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)  # Ученик или Учитель
    city = Column(String(100))
    school = Column(String(255))
    class_number = Column(String(10))  # Для учеников
    subjects = Column(Text)  # Для учителей (через запятую)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    # Как ученик
    student_relations = relationship("StudentTeacherRelation", foreign_keys="StudentTeacherRelation.student_id", back_populates="student")
    student_requests = relationship("TeacherRequest", foreign_keys="TeacherRequest.student_id", back_populates="student")
    student_calls = relationship("Call", foreign_keys="Call.student_id", back_populates="student")
    student_lessons = relationship("LessonRecord", foreign_keys="LessonRecord.student_id", back_populates="student")
    
    # Как учитель
    teacher_relations = relationship("StudentTeacherRelation", foreign_keys="StudentTeacherRelation.teacher_id", back_populates="teacher")
    teacher_requests = relationship("TeacherRequest", foreign_keys="TeacherRequest.teacher_id", back_populates="teacher")
    teacher_calls = relationship("Call", foreign_keys="Call.teacher_id", back_populates="teacher")
    teacher_lessons = relationship("LessonRecord", foreign_keys="LessonRecord.teacher_id", back_populates="teacher")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

class StudentTeacherRelation(Base):
    """Модель связи ученик-учитель"""
    __tablename__ = 'student_teacher_relations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    student = relationship("User", foreign_keys=[student_id], back_populates="student_relations")
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="teacher_relations")
    
    def __repr__(self):
        return f"<StudentTeacherRelation(student_id={self.student_id}, teacher_id={self.teacher_id})>"

class TeacherRequest(Base):
    """Модель заявки от учителя к ученику"""
    __tablename__ = 'teacher_requests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(20), default='pending')  # pending, accepted, rejected
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="teacher_requests")
    student = relationship("User", foreign_keys=[student_id], back_populates="student_requests")
    
    def __repr__(self):
        return f"<TeacherRequest(id={self.id}, teacher_id={self.teacher_id}, student_id={self.student_id}, status='{self.status}')>"

class Call(Base):
    """Модель звонка"""
    __tablename__ = 'calls'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    scheduled_time = Column(DateTime)
    actual_start_time = Column(DateTime)
    actual_end_time = Column(DateTime)
    duration_minutes = Column(Integer)
    status = Column(String(20), default='scheduled')  # scheduled, active, completed, cancelled
    recording_path = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    student = relationship("User", foreign_keys=[student_id], back_populates="student_calls")
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="teacher_calls")
    lesson_records = relationship("LessonRecord", back_populates="call")
    
    def __repr__(self):
        return f"<Call(id={self.id}, student_id={self.student_id}, teacher_id={self.teacher_id}, status='{self.status}')>"

class LessonRecord(Base):
    """Модель записи урока"""
    __tablename__ = 'lesson_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    lesson_title = Column(String(255), nullable=False)
    lesson_date = Column(DateTime)
    subject = Column(String(100))
    video_url = Column(Text)
    video_file_path = Column(Text)
    description = Column(Text)
    homework = Column(Text)
    is_auto_created = Column(Boolean, default=False)  # Автоматически созданная запись от звонка
    call_id = Column(Integer, ForeignKey('calls.id'))
    expires_at = Column(DateTime)  # Для автоматических записей (2 дня)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    student = relationship("User", foreign_keys=[student_id], back_populates="student_lessons")
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="teacher_lessons")
    call = relationship("Call", back_populates="lesson_records")
    
    @property
    def availability_status(self):
        """Статус доступности записи"""
        if self.expires_at is None:
            return 'permanent'
        elif self.expires_at > datetime.utcnow():
            return 'available'
        else:
            return 'expired'
    
    def __repr__(self):
        return f"<LessonRecord(id={self.id}, title='{self.lesson_title}', student_id={self.student_id}, teacher_id={self.teacher_id})>"
