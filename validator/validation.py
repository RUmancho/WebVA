from __future__ import annotations

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database.settings import USER_ROLES
from LibraryManager import loader
from validator import python_fallback


VALIDATOR_DIR = os.path.dirname(os.path.abspath(__file__))
VALIDATOR_DLL = None

try:
    VALIDATOR_DLL = loader.Library(
        "validator",
        os.path.join(VALIDATOR_DIR, "validator.h"),
        VALIDATOR_DIR,
    )
    print("[Validator] Native library loaded")
except Exception as e:
    print(f"[Validator] Native library not available ({e}). Using Python fallback.")
    VALIDATOR_DLL = None


def _use_native(name: str, *args):
    """Call a native validator function, or None if it is unavailable."""
    if VALIDATOR_DLL is None:
        return None
    try:
        func = getattr(VALIDATOR_DLL.lib, name)
        return bool(func(*args))
    except Exception as e:
        print(f"[Validator] Native {name} failed ({e}). Using Python fallback.")
        return None


class Validator:
    MIN_PASSWORD_LENGTH = 15
    """Класс для валидации пользовательских данных"""

    @staticmethod
    def is_name(line):
        result = _use_native("is_name", line)
        if result is not None:
            return result
        return python_fallback.is_name(line if line is not None else "")

    @staticmethod
    def is_email(line):
        result = _use_native("is_email", line)
        if result is not None:
            return result
        return python_fallback.is_email(line if line is not None else "")

    @staticmethod
    def is_password(line, min_len=MIN_PASSWORD_LENGTH):
        # Native is_password often returns False via CFFI (char16_t calling mismatch).
        # Accept the password if either backend says it is valid.
        native = _use_native("is_password", line, min_len)
        fallback = python_fallback.is_password(line if line is not None else "", min_len)
        if native is True:
            return True
        return fallback

    @staticmethod
    def is_ru_class(line):
        result = _use_native("is_ru_class", line)
        if result is not None:
            return result
        return python_fallback.is_ru_class(line if line is not None else "")

    @staticmethod
    def is_ru_school(line):
        result = _use_native("is_ru_school", line)
        if result is not None:
            return result
        return python_fallback.is_ru_school(line if line is not None else "")

    @staticmethod
    def is_ru_city(line):
        result = _use_native("is_ru_city", line)
        if result is not None:
            return result
        return python_fallback.is_ru_city(line if line is not None else "")
    
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