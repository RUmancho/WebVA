import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database.settings import USER_ROLES
from LibraryManager import loader

MIN_PASSWORD_LENGTH = 15

VALIDATOR_DIR = os.path.dirname(os.path.abspath(__file__))
VALIDATOR_DLL = loader.Library("validator", os.path.join(VALIDATOR_DIR, "validator.h"), VALIDATOR_DIR)


class Validator:
    """Класс для валидации пользовательских данных"""
    
    is_name = lambda line: VALIDATOR_DLL.lib.is_name(line)
    is_email = lambda line: VALIDATOR_DLL.lib.is_email(line)
    is_password = lambda line, min_len=MIN_PASSWORD_LENGTH: VALIDATOR_DLL.lib.is_password(line, min_len)
    is_ru_class = lambda line: VALIDATOR_DLL.lib.is_ru_class(line)
    is_ru_school = lambda line: VALIDATOR_DLL.lib.is_ru_school(line)
    is_ru_city = lambda line: VALIDATOR_DLL.lib.is_ru_city(line)
    
    @classmethod
    def is_role(cls, role: str):
        """Валидация роли пользователя"""
        return role in USER_ROLES 
    
    @classmethod
    def is_subjects(cls, subjects):
        """Валидация предметов для учителя"""
        if not subjects:
            return False
        
        if isinstance(subjects, str):
            subjects = [s.strip() for s in subjects.split(',') if s.strip()]
        
        if not subjects:
            return False
        
        for subject in subjects:
            if len(subject.strip()) < 2:
                return False
        
        return True
    
    @classmethod
    def validate_registration_data(cls, data: dict) -> tuple:
        """
        Валидация данных регистрации
        Возвращает (is_valid: bool, errors: dict)
        """
        errors = {}
        
        # Валидация email
        email = data.get('email', '')
        if not email:
            errors['email'] = 'Email обязателен'
        elif not cls.is_email(email):
            errors['email'] = 'Некорректный формат email'
        
        # Валидация пароля
        password = data.get('password', '')
        if not password:
            errors['password'] = 'Пароль обязателен'
        elif len(password) < 6:
            errors['password'] = 'Пароль должен содержать минимум 6 символов'
        elif not cls.is_password(password, 6):
            errors['password'] = 'Пароль должен содержать буквы и цифры'
        
        # Валидация имени
        first_name = data.get('first_name', '')
        if not first_name:
            errors['first_name'] = 'Имя обязательно'
        elif not cls.is_name(first_name):
            errors['first_name'] = 'Некорректное имя'
        
        # Валидация фамилии
        last_name = data.get('last_name', '')
        if not last_name:
            errors['last_name'] = 'Фамилия обязательна'
        elif not cls.is_name(last_name):
            errors['last_name'] = 'Некорректная фамилия'
        
        # Валидация роли
        role = data.get('role', '')
        if not role:
            errors['role'] = 'Роль обязательна'
        elif not cls.is_role(role):
            errors['role'] = 'Некорректная роль'
        
        # Валидация данных для ученика
        if role == 'Ученик':
            city = data.get('city', '')
            if not city:
                errors['city'] = 'Город обязателен для ученика'
            elif not cls.is_ru_city(city):
                errors['city'] = 'Некорректное название города'
            
            school = data.get('school', '')
            if not school:
                errors['school'] = 'Школа обязательна для ученика'
            elif not cls.is_ru_school(school):
                errors['school'] = 'Некорректное название школы'
            
            class_number = data.get('class_number', '')
            if not class_number:
                errors['class_number'] = 'Класс обязателен для ученика'
            elif not cls.is_ru_class(class_number):
                errors['class_number'] = 'Некорректный формат класса'
        
        # Валидация данных для учителя
        if role == 'Учитель':
            city = data.get('city', '')
            if city and not cls.is_ru_city(city):
                errors['city'] = 'Некорректное название города'
            
            school = data.get('school', '')
            if school and not cls.is_ru_school(school):
                errors['school'] = 'Некорректное название школы'
            
            subjects = data.get('subjects', '')
            if subjects and not cls.is_subjects(subjects):
                errors['subjects'] = 'Некорректный формат предметов'
        
        is_valid = len(errors) == 0
        return is_valid, errors