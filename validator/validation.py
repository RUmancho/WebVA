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
    is_password = lambda line: VALIDATOR_DLL.lib.is_password(line)
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