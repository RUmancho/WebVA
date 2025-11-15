import streamlit as st
from database import db
from data_processor.validation import validator
from settings import USER_ROLES, SESSION_STATE_KEY

class AuthManager:
    """Класс для управления аутентификацией и регистрацией"""
    
    @staticmethod
    def init_session_state():
        """Инициализация состояния сессии"""
        if SESSION_STATE_KEY not in st.session_state:
            st.session_state[SESSION_STATE_KEY] = {
                'logged_in': False,
                'user_data': None,
                'page': 'login'
            }
    
    @staticmethod
    def is_logged_in():
        """Проверка, авторизован ли пользователь"""
        AuthManager.init_session_state()
        return st.session_state[SESSION_STATE_KEY]['logged_in']
    
    @staticmethod
    def get_current_user():
        """Получение данных текущего пользователя"""
        AuthManager.init_session_state()
        return st.session_state[SESSION_STATE_KEY]['user_data']
    
    @staticmethod
    def login_user(user_data):
        """Вход пользователя в систему"""
        st.session_state[SESSION_STATE_KEY] = {
            'logged_in': True,
            'user_data': user_data,
            'page': 'dashboard'
        }
    
    @staticmethod
    def logout_user():
        """Выход пользователя из системы"""
        st.session_state[SESSION_STATE_KEY] = {
            'logged_in': False,
            'user_data': None,
            'page': 'login'
        }
    
    @staticmethod
    def show_login_form():
        """Отображение формы входа"""
        st.header("🔐 Вход в систему")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="example@mail.com")
            password = st.text_input("Пароль", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_submitted = st.form_submit_button("Войти", type="primary")
            with col2:
                register_button = st.form_submit_button("Регистрация")
        
        if login_submitted:
            if not email or not password:
                st.error("Пожалуйста, заполните все поля")
                return
            
            try:
                success, user_data = db.authenticate_user(email, password)
                if success:
                    AuthManager.login_user(user_data)
                    st.success("Успешный вход!")
                    st.rerun()
                else:
                    st.error("Неверный email или пароль")
            except Exception as e:
                st.error(f"Ошибка входа: {e}")
                print(f"Ошибка входа: {e}")
        
        if register_button:
            st.session_state[SESSION_STATE_KEY]['page'] = 'register'
            st.rerun()
    
    @staticmethod
    def show_registration_form():
        """Отображение формы регистрации"""
        st.header("📝 Регистрация")
        
        with st.form("registration_form"):
            # Основные поля
            st.subheader("Основная информация")
            email = st.text_input("Email*", placeholder="example@mail.com")
            password = st.text_input("Пароль*", type="password", 
                                   help="Минимум 6 символов, должен содержать буквы и цифры")
            password_confirm = st.text_input("Подтвердите пароль*", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("Имя*", placeholder="Иван")
            with col2:
                last_name = st.text_input("Фамилия*", placeholder="Иванов")
            
            role = st.selectbox("Роль*", options=[""] + USER_ROLES, index=0)
            
            # Дополнительные поля в зависимости от роли
            additional_data = {}
            
            if role == "Ученик":
                st.subheader("Информация об ученике")
                col1, col2 = st.columns(2)
                with col1:
                    city = st.text_input("Город*", placeholder="Москва")
                    school = st.text_input("Школа*", placeholder="МБОУ СОШ №1")
                with col2:
                    class_number = st.text_input("Класс*", placeholder="10А")
                
                additional_data = {
                    'city': city,
                    'school': school,
                    'class_number': class_number
                }
            
            elif role == "Учитель":
                st.subheader("Информация об учителе")
                col1, col2 = st.columns(2)
                with col1:
                    city = st.text_input("Город*", placeholder="Москва")
                    school = st.text_input("Школа*", placeholder="МБОУ СОШ №1")
                with col2:
                    subjects_input = st.text_area(
                        "Предметы*", 
                        placeholder="Математика, Физика, Информатика",
                        help="Укажите предметы через запятую"
                    )
                
                additional_data = {
                    'city': city,
                    'school': school,
                    'subjects': subjects_input
                }
            
            # Кнопки
            col1, col2 = st.columns(2)
            with col1:
                register_submitted = st.form_submit_button("Зарегистрироваться", type="primary")
            with col2:
                back_button = st.form_submit_button("Назад к входу")
        
        if back_button:
            st.session_state[SESSION_STATE_KEY]['page'] = 'login'
            st.rerun()
        
        if register_submitted:
            # Проверка совпадения паролей
            if password != password_confirm:
                st.error("Пароли не совпадают")
                return
            
            # Подготовка данных для валидации
            registration_data = {
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                **additional_data
            }
            
            # Валидация данных
            try:
                is_valid, errors = validator.validate_registration_data(registration_data)
                
                if not is_valid:
                    st.error("Ошибки в форме:")
                    for field, error in errors.items():
                        st.error(f"• {field}: {error}")
                    return
                
                # Регистрация пользователя
                success, result = db.register_user(registration_data)
                
                if success:
                    st.success("Регистрация прошла успешно! Теперь вы можете войти в систему.")
                    st.session_state[SESSION_STATE_KEY]['page'] = 'login'
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"Ошибка регистрации: {result}")
                    
            except Exception as e:
                st.error(f"Произошла ошибка: {e}")
                print(f"Ошибка регистрации: {e}")
    
    @staticmethod
    def show_user_profile():
        """Отображение профиля пользователя"""
        user = AuthManager.get_current_user()
        if not user:
            return
        
        st.sidebar.header("👤 Профиль")
        st.sidebar.write(f"**{user['first_name']} {user['last_name']}**")
        st.sidebar.write(f"Роль: {user['role']}")
        st.sidebar.write(f"Email: {user['email']}")
        
        if user['role'] == 'Ученик':
            st.sidebar.write(f"Город: {user['city']}")
            st.sidebar.write(f"Школа: {user['school']}")
            st.sidebar.write(f"Класс: {user['class_number']}")
        elif user['role'] == 'Учитель':
            st.sidebar.write(f"Город: {user['city']}")
            st.sidebar.write(f"Школа: {user['school']}")
            if user['subjects']:
                st.sidebar.write(f"Предметы: {user['subjects']}")
        
        if st.sidebar.button("🚪 Выйти", type="primary"):
            AuthManager.logout_user()
            st.rerun()
        
        st.sidebar.markdown("---")
        
        # Кнопка удаления профиля
        if st.sidebar.button("🗑️ Удалить профиль", help="Полное удаление профиля из системы"):
            AuthManager.show_delete_profile_form()
    
    @staticmethod
    def show_delete_profile_form():
        """Отображение формы удаления профиля"""
        user = AuthManager.get_current_user()
        if not user:
            return
        
        st.warning("⚠️ Внимание! Удаление профиля необратимо!")
        st.write("Все ваши данные, включая связи с учителями/учениками, звонки и записи уроков будут удалены.")
        
        with st.form("delete_profile_form"):
            st.subheader("Подтверждение удаления профиля")
            st.write("Для подтверждения введите ваш email и пароль:")
            
            email = st.text_input("Email", value=user['email'], disabled=True, help="Ваш текущий email")
            password = st.text_input("Пароль", type="password", placeholder="Введите ваш пароль")
            
            # Дополнительное подтверждение
            confirmation = st.checkbox("Я понимаю, что это действие необратимо")
            
            col1, col2 = st.columns(2)
            with col1:
                delete_submitted = st.form_submit_button("🗑️ Удалить профиль", type="primary")
            with col2:
                cancel_button = st.form_submit_button("Отменить")
        
        if cancel_button:
            st.rerun()
        
        if delete_submitted:
            if not password:
                st.error("Пожалуйста, введите пароль")
                return
            
            if not confirmation:
                st.error("Пожалуйста, подтвердите, что вы понимаете последствия")
                return
            
            try:
                success, message = db.delete_user(user['id'], user['email'], password)
                
                if success:
                    st.success(message)
                    st.balloons()
                    
                    # Выход из системы после удаления
                    AuthManager.logout_user()
                    st.info("Вы будете перенаправлены на страницу входа...")
                    st.rerun()
                else:
                    st.error(f"Ошибка удаления профиля: {message}")
                    
            except Exception as e:
                st.error(f"Произошла ошибка: {e}")
                print(f"Ошибка удаления профиля: {e}")

# Создание экземпляра менеджера аутентификации
auth_manager = AuthManager()
