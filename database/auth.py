from flask import session as flask_session
from database.database import db
from validator.validation import Validator
from database.settings import USER_ROLES, SESSION_STATE_KEY

class AuthManager:
    """Класс для управления аутентификацией и регистрацией"""
    
    @staticmethod
    def _get_session():
        """Получение объекта сессии Flask"""
        try:
            return flask_session
        except RuntimeError:
            return {}
    
    @staticmethod
    def init_session_state():
        """Инициализация состояния сессии"""
        session = AuthManager._get_session()
        if isinstance(session, dict):
            if SESSION_STATE_KEY not in session:
                session[SESSION_STATE_KEY] = {
                    'logged_in': False,
                    'user_data': None,
                    'page': 'login'
                }
    
    @staticmethod
    def is_logged_in():
        """Проверка, авторизован ли пользователь"""
        AuthManager.init_session_state()
        session = AuthManager._get_session()
        if isinstance(session, dict):
            return session.get(SESSION_STATE_KEY, {}).get('logged_in', False)
        return False
    
    @staticmethod
    def get_current_user():
        """Получение данных текущего пользователя"""
        AuthManager.init_session_state()
        session = AuthManager._get_session()
        if isinstance(session, dict):
            return session.get(SESSION_STATE_KEY, {}).get('user_data')
        return None
    
    @staticmethod
    def login_user(user_data):
        """Вход пользователя в систему"""
        try:
            # Обновляем статус онлайн при входе
            db.update_user_online_status(user_data['id'], True)
        except Exception as e:
            print(f"Ошибка обновления статуса онлайн: {e}")
        
        session = AuthManager._get_session()
        session_data = {
            'logged_in': True,
            'user_data': user_data,
            'page': 'dashboard'
        }
        
        if isinstance(session, dict):
            session[SESSION_STATE_KEY] = session_data
    
    @staticmethod
    def logout_user():
        """Выход пользователя из системы"""
        session = AuthManager._get_session()
        user = None
        
        if isinstance(session, dict):
            user = session.get(SESSION_STATE_KEY, {}).get('user_data')
        
        try:
            # Обновляем статус офлайн при выходе
            if user and user.get('id'):
                db.update_user_online_status(user['id'], False)
        except Exception as e:
            print(f"Ошибка обновления статуса офлайн: {e}")
        
        session_data = {
            'logged_in': False,
            'user_data': None,
            'page': 'login'
        }
        
        if isinstance(session, dict):
            session[SESSION_STATE_KEY] = session_data
    
    # Методы show_login_form, show_registration_form, show_user_profile, show_delete_profile_form
    # больше не нужны для Flask, так как формы будут в HTML шаблонах

# Создание экземпляра менеджера аутентификации
auth_manager = AuthManager()
