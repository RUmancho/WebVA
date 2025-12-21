import os
from pathlib import Path

from database.settings import USER_ROLES
from LibraryManager import loader

# Получаем абсолютный путь к папке validator
VALIDATOR_DIR = Path(__file__).parent.resolve()
VALIDATOR_HEADER = str(VALIDATOR_DIR / "validator.h")
VALIDATOR_DLL_PATH = str(VALIDATOR_DIR)

try:
    VALIDATOR_DLL = loader.Library("validator", VALIDATOR_HEADER, VALIDATOR_DLL_PATH)
except Exception as e:
    print(f"[WARNING] Не удалось загрузить validator DLL: {e}")
    VALIDATOR_DLL = None

class Validator:
    class InputError:
        def __init__(self, description: str):
            self.description = description

    class InputSuccess:
        def __init__(self, description: str):
            self.description = description

    @classmethod
    def validate_role(cls, role):
        """Валидация роли пользователя"""
        # Базовые проверки
        if not role:
            return cls.InputError("Роль должна быть выбрана")
        
        if role not in USER_ROLES:
            return cls.InputError(f"Роль должна быть одной из: {', '.join(USER_ROLES)}")
        
        return cls.InputSuccess("OK")
    
    @classmethod
    def validate_subjects(cls, subjects):
        """Валидация предметов для учителя"""
        # Базовые проверки
        if not subjects:
            return cls.InputError("Необходимо указать хотя бы один предмет")
        
        if isinstance(subjects, str):
            subjects = [s.strip() for s in subjects.split(',') if s.strip()]
        
        if not subjects:
            return cls.InputError("Необходимо указать хотя бы один предмет")
        
        for subject in subjects:
            if len(subject.strip()) < 2:
                return cls.InputError(f"Название предмета '{subject}' слишком короткое")
        
        return cls.InputSuccess("OK")
    
    @classmethod
    def validate_registration_data(cls, data):
        """
        Комплексная валидация всех данных регистрации
        Возвращает (is_valid, errors_dict)
        """
        errors = {}
        
        # Валидация основных полей
        fields_to_validate = [
            ('email', cls.validate_email),
            ('password', cls.validate_password),
            ('first_name', cls.validate_name),
            ('last_name', cls.validate_name),
            ('role', cls.validate_role)
        ]
        
        for field, validator in fields_to_validate:
            if field in data:
                result = validator(data[field])
                if isinstance(result, cls.InputError):
                    errors[field] = result.description
        
        # Валидация полей в зависимости от роли
        if 'role' in data and data['role'] == 'Ученик':
            student_fields = [
                ('city', cls.validate_city),
                ('school', cls.validate_school),
                ('class_number', cls.validate_class_number)
            ]
            
            for field, validator in student_fields:
                if field in data:
                    result = validator(data[field])
                    if isinstance(result, cls.InputError):
                        errors[field] = result.description
        
        elif 'role' in data and data['role'] == 'Учитель':
            teacher_fields = [
                ('city', cls.validate_city),
                ('school', cls.validate_school),
                ('subjects', cls.validate_subjects)
            ]
            
            for field, validator in teacher_fields:
                if field in data:
                    result = validator(data[field])
                    if isinstance(result, cls.InputError):
                        errors[field] = result.description
        
        return len(errors) == 0, errors

