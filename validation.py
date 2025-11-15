from config import MIN_NAME_LENGTH, MIN_PASSWORD_LENGTH
import re

class Validator:
    """Класс для валидации пользовательских данных"""
    
    @staticmethod
    def validate_name(name):
        """
        Валидация имени/фамилии
        Правила: только буквы, длина больше 1 символа, без цифр и спецсимволов
        """
        if not name:
            return False, "Поле не может быть пустым"
        
        if len(name) < MIN_NAME_LENGTH:
            return False, f"Минимальная длина {MIN_NAME_LENGTH} символа"
        
        # Проверка на содержание только букв (включая русские)
        if not re.match(r'^[а-яёА-ЯЁa-zA-Z\-\s]+$', name):
            return False, "Имя может содержать только буквы, дефисы и пробелы"
        
        # Проверка на отсутствие цифр
        if re.search(r'\d', name):
            return False, "Имя не может содержать цифры"
        
        # Проверка на отсутствие спецсимволов (кроме дефиса и пробела)
        if re.search(r'[!@#$%^&*()_+=\[\]{}|;:",.<>?/\\~`]', name):
            return False, "Имя не может содержать специальные символы"
        
        return True, "OK"
    
    @staticmethod
    def validate_email(email):
        """Валидация email адреса"""
        if not email:
            return False, "Email не может быть пустым"
        
        # Простая регулярка для email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Неверный формат email"
        
        return True, "OK"
    
    @staticmethod
    def validate_password(password):
        """Валидация пароля"""
        if not password:
            return False, "Пароль не может быть пустым"
        
        if len(password) < MIN_PASSWORD_LENGTH:
            return False, f"Минимальная длина пароля {MIN_PASSWORD_LENGTH} символов"
        
        # Проверка на наличие хотя бы одной буквы и одной цифры
        if not re.search(r'[a-zA-Zа-яёА-ЯЁ]', password):
            return False, "Пароль должен содержать хотя бы одну букву"
        
        if not re.search(r'\d', password):
            return False, "Пароль должен содержать хотя бы одну цифру"
        
        return True, "OK"
    
    @staticmethod
    def validate_role(role):
        """Валидация роли пользователя"""
        from config import USER_ROLES
        
        if not role:
            return False, "Роль должна быть выбрана"
        
        if role not in USER_ROLES:
            return False, f"Роль должна быть одной из: {', '.join(USER_ROLES)}"
        
        return True, "OK"
    
    @staticmethod
    def validate_city(city):
        """Валидация города"""
        if not city or not city.strip():
            return False, "Город не может быть пустым"
        
        if len(city.strip()) < 2:
            return False, "Название города слишком короткое"
        
        # Проверка на содержание только букв, дефисов и пробелов
        if not re.match(r'^[а-яёА-ЯЁa-zA-Z\-\s]+$', city.strip()):
            return False, "Название города может содержать только буквы, дефисы и пробелы"
        
        return True, "OK"
    
    @staticmethod
    def validate_school(school):
        """Валидация названия школы"""
        if not school or not school.strip():
            return False, "Школа не может быть пустой"
        
        if len(school.strip()) < 3:
            return False, "Название школы слишком короткое"
        
        return True, "OK"
    
    @staticmethod
    def validate_class_number(class_number):
        """Валидация номера класса"""
        if not class_number or not class_number.strip():
            return False, "Класс не может быть пустым"
        
        # Проверка формата класса (например: 5А, 10Б, 11)
        if not re.match(r'^\d{1,2}[А-Я]?$', class_number.strip().upper()):
            return False, "Неверный формат класса (например: 5А, 10Б, 11)"
        
        return True, "OK"
    
    @staticmethod
    def validate_subjects(subjects):
        """Валидация предметов для учителя"""
        if not subjects:
            return False, "Необходимо указать хотя бы один предмет"
        
        if isinstance(subjects, str):
            subjects = [s.strip() for s in subjects.split(',') if s.strip()]
        
        if not subjects:
            return False, "Необходимо указать хотя бы один предмет"
        
        for subject in subjects:
            if len(subject.strip()) < 2:
                return False, f"Название предмета '{subject}' слишком короткое"
        
        return True, "OK"
    
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
                is_valid, message = validator(data[field])
                if not is_valid:
                    errors[field] = message
        
        # Валидация полей в зависимости от роли
        if 'role' in data and data['role'] == 'Ученик':
            student_fields = [
                ('city', cls.validate_city),
                ('school', cls.validate_school),
                ('class_number', cls.validate_class_number)
            ]
            
            for field, validator in student_fields:
                if field in data:
                    is_valid, message = validator(data[field])
                    if not is_valid:
                        errors[field] = message
        
        elif 'role' in data and data['role'] == 'Учитель':
            teacher_fields = [
                ('city', cls.validate_city),
                ('school', cls.validate_school),
                ('subjects', cls.validate_subjects)
            ]
            
            for field, validator in teacher_fields:
                if field in data:
                    is_valid, message = validator(data[field])
                    if not is_valid:
                        errors[field] = message
        
        return len(errors) == 0, errors

# Создание экземпляра валидатора
validator = Validator()
