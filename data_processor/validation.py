from settings import MIN_NAME_LENGTH, MIN_PASSWORD_LENGTH
import settings
import re

class InputError:
    def __init__(self, description: str):
        self.description = description

class InputSuccess:
    def __init__(self, description: str):
        self.description = description

class Validator:
    @staticmethod
    def validate_name(name):
        if not name:
            return InputError("Поле не может быть пустым")
        
        if len(name) < MIN_NAME_LENGTH:
            return InputError(f"Минимальная длина {MIN_NAME_LENGTH} символа")
        
        # Проверка на содержание только букв (включая русские)
        if not re.match(r'^[а-яёА-ЯЁa-zA-Z\-\s]+$', name):
            return InputError("Имя может содержать только буквы, дефисы и пробелы")
        
        # Проверка на отсутствие цифр
        if re.search(r'\d', name):
            return InputError("Имя не может содержать цифры")
        
        # Проверка на отсутствие спецсимволов (кроме дефиса и пробела)
        if re.search(r'[!@#$%^&*()_+=\[\]{}|;:",.<>?/\\~`]', name):
            return InputError("Имя не может содержать специальные символы")
        
        return InputSuccess("OK")
    
    @staticmethod
    def validate_email(email):
        """Валидация email адреса"""
        if not email:
            return InputError("Email не может быть пустым")
        
        # Простая регулярка для email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return InputError("Неверный формат email")
        
        return InputSuccess("OK")
    
    @staticmethod
    def validate_password(password):
        """Валидация пароля"""
        if not password:
            return InputError("Пароль не может быть пустым")
        
        if len(password) < MIN_PASSWORD_LENGTH:
            return InputError(f"Минимальная длина пароля {MIN_PASSWORD_LENGTH} символов")
        
        # Проверка на наличие хотя бы одной буквы и одной цифры
        if not re.search(r'[a-zA-Zа-яёА-ЯЁ]', password):
            return InputError("Пароль должен содержать хотя бы одну букву")
        
        if not re.search(r'\d', password):
            return InputError("Пароль должен содержать хотя бы одну цифру")
        
        return InputSuccess("OK")
    
    @staticmethod
    def validate_role(role):
        """Валидация роли пользователя"""
        
        if not role:
            return InputError("Роль должна быть выбрана")
        
        if role not in settings.USER_ROLES:
            return InputError(f"Роль должна быть одной из: {', '.join(settings.USER_ROLES)}")
        
        return InputSuccess("OK")
    
    @staticmethod
    def validate_city(city):
        """Валидация города"""
        if not city or not city.strip():
            return InputError("Город не может быть пустым")
        
        if len(city.strip()) < 2:
            return InputError("Название города слишком короткое")
        
        # Проверка на содержание только букв, дефисов и пробелов
        if not re.match(r'^[а-яёА-ЯЁa-zA-Z\-\s]+$', city.strip()):
            return InputError("Название города может содержать только буквы, дефисы и пробелы")
        
        return InputSuccess("OK")
    
    @staticmethod
    def validate_school(school):
        """Валидация названия школы"""
        if not school or not school.strip():
            return InputError("Школа не может быть пустой")
        
        if len(school.strip()) < 3:
            return InputError("Название школы слишком короткое")
        
        return InputSuccess("OK")
    
    @staticmethod
    def validate_class_number(class_number):
        """Валидация номера класса"""
        if not class_number or not class_number.strip():
            return InputError("Класс не может быть пустым")
        
        # Проверка формата класса (например: 5А, 10Б, 11)
        if not re.match(r'^\d{1,2}[А-Я]?$', class_number.strip().upper()):
            return InputError("Неверный формат класса (например: 5А, 10Б, 11)")
        
        return InputSuccess("OK")
    
    @staticmethod
    def validate_subjects(subjects):
        """Валидация предметов для учителя"""
        if not subjects:
            return InputError("Необходимо указать хотя бы один предмет")
        
        if isinstance(subjects, str):
            subjects = [s.strip() for s in subjects.split(',') if s.strip()]
        
        if not subjects:
            return InputError("Необходимо указать хотя бы один предмет")
        
        for subject in subjects:
            if len(subject.strip()) < 2:
                return InputError(f"Название предмета '{subject}' слишком короткое")
        
        return InputSuccess("OK")
    
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
                if isinstance(result, InputError):
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
                    if isinstance(result, InputError):
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
                    if isinstance(result, InputError):
                        errors[field] = result.description
        
        return len(errors) == 0, errors

# Создание экземпляра валидатора
validator = Validator()
