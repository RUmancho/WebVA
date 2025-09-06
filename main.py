import streamlit as st
from auth import auth_manager
from database import db
from chatbot import chatbot
from theory import theory_manager
from testing import testing_manager
from config import PAGE_CONFIG

def main():
    """Основная функция приложения"""
    try:
        # Настройка страницы
        st.set_page_config(**PAGE_CONFIG)
        
        # Инициализация состояния сессии
        auth_manager.init_session_state()
        
        # Проверка авторизации
        if not auth_manager.is_logged_in():
            show_auth_page()
        else:
            show_dashboard()
            
    except Exception as e:
        st.error(f"Произошла ошибка: {e}")
        print(f"Основная ошибка приложения: {e}")

def show_auth_page():
    """Отображение страницы авторизации/регистрации"""
    try:
        # Заголовок приложения
        st.title("🎓 Система регистрации учителей и учеников")
        st.markdown("---")
        
        # Получение текущей страницы
        current_page = st.session_state.get('user_session', {}).get('page', 'login')
        
        # Отображение соответствующей формы
        if current_page == 'register':
            auth_manager.show_registration_form()
        else:
            auth_manager.show_login_form()
            
        # Дополнительная информация в боковой панели
        st.sidebar.header("ℹ️ Информация")
        st.sidebar.write("""
        **Добро пожаловать в образовательную систему!**
        
        Здесь вы можете:
        • Зарегистрироваться как ученик или учитель
        • Найти учителей по предметам
        • Изучать теоретические материалы
        • Проходить тесты по школьным предметам
        • Получить помощь от чат-бота
        • Проводить видеозвонки на встроенной платформе
        
        **Для учеников:**
        - Просмотр и связь с учителями
        - Принятие заявок от учителей
        - Изучение теории по 11 предметам
        - Тестирование с AI-генерацией вопросов
        - Участие в видеозвонках
        - Скачивание записей уроков (доступны 2 дня)
        
        **Для учителей:**
        - Отправка заявок ученикам
        - Планирование видеозвонков
        - Автоматическая запись уроков
        - Создание ручных записей уроков
        - Система тестирования учеников
        """)
        
    except Exception as e:
        st.error(f"Ошибка страницы авторизации: {e}")
        print(f"Ошибка страницы авторизации: {e}")

def show_dashboard():
    """Отображение главной панели после входа"""
    try:
        # Получение данных пользователя
        user = auth_manager.get_current_user()
        if not user:
            auth_manager.logout_user()
            st.rerun()
            return
        
        # Заголовок
        st.title(f"Добро пожаловать, {user['first_name']}! 👋")
        
        # Профиль пользователя в боковой панели
        auth_manager.show_user_profile()
        
        # Навигация
        tabs = st.tabs(["🏠 Главная", "👨‍🏫 Учителя", "💬 Чат-помощник", "📚 Теория", "📝 Тестирование", "📋 Заявки", "📞 Звонки", "🎥 Записи уроков"])
        
        with tabs[0]:
            show_main_dashboard(user)
        
        with tabs[1]:
            show_teachers_list()
        
        with tabs[2]:
            show_chat_section()
        
        with tabs[3]:
            show_theory_section()
        
        with tabs[4]:
            show_testing_section()
        
        with tabs[5]:
            show_requests_section(user)
        
        with tabs[6]:
            show_calls_section(user)
        
        with tabs[7]:
            show_lesson_records_section(user)
            
    except Exception as e:
        st.error(f"Ошибка панели управления: {e}")
        print(f"Ошибка панели управления: {e}")

def show_main_dashboard(user):
    """Отображение главной панели"""
    try:
        st.header("📊 Главная панель")
        
        # Информационные карточки
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Ваша роль",
                value=user['role'],
                delta=None
            )
        
        with col2:
            try:
                teachers_count = len(db.get_teachers())
                st.metric(
                    label="Учителей в системе",
                    value=teachers_count,
                    delta=None
                )
            except Exception as e:
                st.metric(
                    label="Учителей в системе",
                    value="Ошибка",
                    delta=None
                )
                print(f"Ошибка получения количества учителей: {e}")
        
        with col3:
            st.metric(
                label="Статус",
                value="Активен",
                delta="Онлайн"
            )
        
        st.markdown("---")
        
        # Информация в зависимости от роли
        if user['role'] == 'Ученик':
            show_student_info(user)
        elif user['role'] == 'Учитель':
            show_teacher_info(user)
            
    except Exception as e:
        st.error(f"Ошибка главной панели: {e}")
        print(f"Ошибка главной панели: {e}")

def show_student_info(user):
    """Информация для ученика"""
    try:
        st.subheader("👨‍🎓 Информация об ученике")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Школа:** {user.get('school', 'Не указана')}")
            st.info(f"**Класс:** {user.get('class_number', 'Не указан')}")
        
        with col2:
            st.info(f"**Город:** {user.get('city', 'Не указан')}")
        
        st.write("### 📚 Возможности:")
        st.write("• Просмотр и связь с учителями")
        st.write("• Принятие заявок от учителей")
        st.write("• Изучение теоретических материалов")
        st.write("• Прохождение тестов по предметам")
        st.write("• Участие в видеозвонках на встроенной платформе")
        st.write("• Скачивание записей уроков (доступны 2 дня)")
        st.write("• Общение с чат-ботом поддержки")
        
    except Exception as e:
        st.error(f"Ошибка отображения информации ученика: {e}")
        print(f"Ошибка отображения информации ученика: {e}")

def show_teacher_info(user):
    """Информация для учителя"""
    try:
        st.subheader("👨‍🏫 Информация об учителе")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Школа:** {user.get('school', 'Не указана')}")
            st.info(f"**Город:** {user.get('city', 'Не указан')}")
        
        with col2:
            subjects = user.get('subjects', 'Не указаны')
            st.info(f"**Предметы:** {subjects}")
        
        st.write("### 🎯 Возможности:")
        st.write("• Отправка заявок ученикам")
        st.write("• Планирование видеозвонков на встроенной платформе")
        st.write("• Автоматическая запись уроков")
        st.write("• Создание ручных записей уроков")
        st.write("• Изучение теоретических материалов")
        st.write("• Создание и прохождение тестов")
        st.write("• Общение с чат-ботом поддержки")
        
    except Exception as e:
        st.error(f"Ошибка отображения информации учителя: {e}")
        print(f"Ошибка отображения информации учителя: {e}")

def show_teachers_list():
    """Отображение списка учителей"""
    try:
        st.header("👨‍🏫 Учителя")
        
        # Получение текущего пользователя
        user = auth_manager.get_current_user()
        
        # Для учеников показываем сначала их учителей
        if user and user['role'] == 'Ученик':
            show_student_teachers(user)
            st.markdown("---")
        
        st.subheader("🔍 Все учителя в системе")
        
        # Получение списка учителей
        teachers = db.get_teachers()
        
        if not teachers:
            st.info("В системе пока нет зарегистрированных учителей.")
            return
        
        # Поиск по предметам
        subjects_set = set()
        for teacher in teachers:
            if teacher.get('subjects'):
                teacher_subjects = [s.strip() for s in teacher['subjects'].split(',')]
                subjects_set.update(teacher_subjects)
        
        subjects_list = sorted(list(subjects_set))
        
        if subjects_list:
            selected_subject = st.selectbox(
                "Фильтр по предмету:",
                options=["Все предметы"] + subjects_list,
                index=0
            )
        else:
            selected_subject = "Все предметы"
        
        # Фильтрация учителей
        filtered_teachers = teachers
        if selected_subject != "Все предметы":
            filtered_teachers = [
                teacher for teacher in teachers
                if teacher.get('subjects') and selected_subject in teacher['subjects']
            ]
        
        # Отображение карточек учителей
        st.write(f"Найдено учителей: {len(filtered_teachers)}")
        
        for teacher in filtered_teachers:
            with st.expander(f"{teacher['first_name']} {teacher['last_name']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Предметы:** {teacher.get('subjects', 'Не указаны')}")
                    st.write(f"**Город:** {teacher.get('city', 'Не указан')}")
                
                with col2:
                    st.write(f"**Школа:** {teacher.get('school', 'Не указана')}")
                
    except Exception as e:
        st.error(f"Ошибка отображения списка учителей: {e}")
        print(f"Ошибка отображения списка учителей: {e}")

def show_student_teachers(user):
    """Отображение учителей ученика"""
    try:
        st.subheader("👨‍🏫 Мои учителя")
        
        # Получение учителей ученика
        my_teachers = db.get_student_teachers(user['id'])
        
        if not my_teachers:
            st.info("У вас пока нет связанных учителей. Принимайте заявки в разделе 'Заявки'.")
            return
        
        st.write(f"У вас {len(my_teachers)} учителей:")
        
        for teacher in my_teachers:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**{teacher['first_name']} {teacher['last_name']}**")
                    st.write(f"**Предметы:** {teacher.get('subjects', 'Не указаны')}")
                
                with col2:
                    st.write(f"**Школа:** {teacher.get('school', 'Не указана')}")
                    st.write(f"**Город:** {teacher.get('city', 'Не указан')}")
                
                with col3:
                    st.write("✅ Связан")
                
                st.markdown("---")
        
    except Exception as e:
        st.error(f"Ошибка отображения учителей ученика: {e}")
        print(f"Ошибка отображения учителей ученика: {e}")

def show_chat_section():
    """Отображение секции чата"""
    try:
        # Кнопка очистки истории чата в боковой панели
        if st.sidebar.button("🗑️ Очистить историю чата"):
            chatbot.clear_chat_history()
            st.rerun()
        
        # Отображение чата
        chatbot.show_chat_interface()
        
    except Exception as e:
        st.error(f"Ошибка чата: {e}")
        print(f"Ошибка чата: {e}")

def show_theory_section():
    """Отображение секции теории"""
    try:
        # Кнопка сброса навигации в боковой панели
        if st.sidebar.button("🏠 К списку предметов"):
            theory_manager.init_theory_session()
            st.rerun()
        
        # Отображение теоретических материалов
        theory_manager.show_theory_interface()
        
    except Exception as e:
        st.error(f"Ошибка секции теории: {e}")
        print(f"Ошибка секции теории: {e}")

def show_testing_section():
    """Отображение секции тестирования"""
    try:
        # Кнопка сброса навигации в боковой панели
        if st.sidebar.button("🏠 К выбору предметов"):
            testing_manager.init_testing_session()
            st.rerun()
        
        # Отображение системы тестирования
        testing_manager.show_testing_interface()
        
    except Exception as e:
        st.error(f"Ошибка секции тестирования: {e}")
        print(f"Ошибка секции тестирования: {e}")

def show_requests_section(user):
    """Отображение секции заявок"""
    try:
        st.header("📋 Заявки")
        
        if user['role'] == 'Ученик':
            show_student_requests(user)
        elif user['role'] == 'Учитель':
            show_teacher_requests_management(user)
        
    except Exception as e:
        st.error(f"Ошибка секции заявок: {e}")
        print(f"Ошибка секции заявок: {e}")

def show_student_requests(user):
    """Отображение заявок для ученика"""
    try:
        st.subheader("📨 Входящие заявки от учителей")
        
        # Получение заявок
        requests = db.get_student_requests(user['id'])
        
        if not requests:
            st.info("У вас нет новых заявок от учителей.")
            return
        
        st.write(f"У вас {len(requests)} новых заявок:")
        
        for request in requests:
            with st.container():
                st.markdown("---")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Учитель:** {request['first_name']} {request['last_name']}")
                    st.write(f"**Предметы:** {request.get('subjects', 'Не указаны')}")
                    st.write(f"**Школа:** {request.get('school', 'Не указана')}")
                    if request.get('message'):
                        st.write(f"**Сообщение:** {request['message']}")
                    st.write(f"**Дата:** {request['created_at']}")
                
                with col2:
                    if st.button("✅ Принять", key=f"accept_{request['id']}"):
                        success, message = db.accept_teacher_request(request['id'], user['id'])
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                
                with col3:
                    if st.button("❌ Отклонить", key=f"reject_{request['id']}"):
                        success, message = db.reject_teacher_request(request['id'], user['id'])
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        
    except Exception as e:
        st.error(f"Ошибка отображения заявок ученика: {e}")
        print(f"Ошибка отображения заявок ученика: {e}")

def show_teacher_requests_management(user):
    """Управление заявками для учителя"""
    try:
        st.subheader("📤 Отправка заявок ученикам")
        
        # Получение списка всех учеников
        all_users = db.get_all_students()
        
        if not all_users:
            st.info("В системе нет зарегистрированных учеников.")
            return
        
        # Форма отправки заявки
        with st.form("send_request_form"):
            st.write("**Отправить заявку ученику:**")
            
            student_options = {f"{user['first_name']} {user['last_name']} ({user['email']})": user['id'] 
                             for user in all_users}
            
            selected_student = st.selectbox(
                "Выберите ученика:",
                options=list(student_options.keys())
            )
            
            message = st.text_area(
                "Сообщение (необязательно):",
                placeholder="Напишите короткое сообщение ученику..."
            )
            
            if st.form_submit_button("📤 Отправить заявку"):
                if selected_student:
                    student_id = student_options[selected_student]
                    success, result_message = db.create_teacher_request(user['id'], student_id, message)
                    
                    if success:
                        st.success(result_message)
                        st.rerun()
                    else:
                        st.error(result_message)
        
        # Отображение уже отправленных заявок
        st.markdown("---")
        st.subheader("📋 Мои отправленные заявки")
        
        sent_requests = db.get_teacher_sent_requests(user['id'])
        
        if sent_requests:
            for request in sent_requests:
                with st.container():
                    st.write(f"**Ученик:** {request['student_name']} {request['student_surname']}")
                    st.write(f"**Статус:** {request['status']}")
                    st.write(f"**Дата отправки:** {request['created_at']}")
                    if request.get('message'):
                        st.write(f"**Сообщение:** {request['message']}")
                    st.markdown("---")
        else:
            st.info("Вы не отправляли заявок ученикам.")
        
    except Exception as e:
        st.error(f"Ошибка управления заявками учителя: {e}")
        print(f"Ошибка управления заявками учителя: {e}")

def show_calls_section(user):
    """Отображение секции звонков"""
    try:
        st.header("📞 Встроенная платформа звонков")
        
        # Автоматическая очистка просроченных записей при каждом входе
        try:
            db.cleanup_expired_records()
        except Exception as e:
            print(f"Ошибка автоочистки: {e}")
        
        # Получение звонков пользователя
        calls = db.get_user_calls(user['id'])
        
        # Создание нового звонка
        if user['role'] == 'Учитель':
            show_create_call_form(user)
        
        st.markdown("---")
        st.subheader("📋 Мои звонки")
        
        if not calls:
            st.info("У вас нет запланированных звонков.")
            return
        
        # Группировка звонков по статусу
        scheduled_calls = [call for call in calls if call['status'] == 'scheduled']
        active_calls = [call for call in calls if call['status'] == 'active']
        completed_calls = [call for call in calls if call['status'] == 'completed']
        
        # Активные звонки
        if active_calls:
            st.subheader("🟢 Активные звонки")
            for call in active_calls:
                show_call_interface(call, user, 'active')
        
        # Запланированные звонки
        if scheduled_calls:
            st.subheader("🕐 Запланированные звонки")
            for call in scheduled_calls:
                show_call_interface(call, user, 'scheduled')
        
        # Завершенные звонки
        if completed_calls:
            st.subheader("✅ Завершенные звонки")
            for call in completed_calls[:5]:  # Показываем только последние 5
                show_call_interface(call, user, 'completed')
        
    except Exception as e:
        st.error(f"Ошибка секции звонков: {e}")
        print(f"Ошибка секции звонков: {e}")

def show_call_interface(call, user, status):
    """Отображение интерфейса конкретного звонка"""
    try:
        participant_name = ""
        if user['role'] == 'Ученик':
            participant_name = f"{call['teacher_name']} {call['teacher_surname']}"
        else:
            participant_name = f"{call['student_name']} {call['student_surname']}"
        
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**Участник:** {participant_name}")
                st.write(f"**Время:** {call['scheduled_time'] or 'Не указано'}")
                if call.get('actual_start_time'):
                    st.write(f"**Начат:** {call['actual_start_time']}")
                if call.get('actual_end_time'):
                    st.write(f"**Завершен:** {call['actual_end_time']}")
            
            with col2:
                st.write(f"**Длительность:** {call['duration_minutes']} минут")
                st.write(f"**Статус:** {get_status_emoji(call['status'])} {call['status']}")
                if call.get('notes'):
                    st.write(f"**Заметки:** {call['notes']}")
            
            with col3:
                if status == 'scheduled':
                    if st.button("🟢 Начать", key=f"start_{call['id']}"):
                        success, message = db.start_call(call['id'])
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                
                elif status == 'active':
                    st.write("🔴 **В эфире**")
                    if st.button("⏹️ Завершить", key=f"end_{call['id']}"):
                        # Имитация пути к записи (в реальной системе здесь будет путь к файлу)
                        recording_path = f"/recordings/call_{call['id']}_{call['created_at']}.mp4"
                        success, message = db.end_call(call['id'], recording_path)
                        if success:
                            st.success(message)
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(message)
                
                elif status == 'completed':
                    if call.get('recording_path'):
                        st.write("📹 Записан")
            
            st.markdown("---")
    
    except Exception as e:
        st.error(f"Ошибка интерфейса звонка: {e}")
        print(f"Ошибка интерфейса звонка: {e}")

def get_status_emoji(status):
    """Получение эмодзи для статуса звонка"""
    status_emojis = {
        'scheduled': '🕐',
        'active': '🟢',
        'completed': '✅',
        'cancelled': '❌'
    }
    return status_emojis.get(status, '❓')

def show_create_call_form(user):
    """Форма создания звонка для учителя"""
    try:
        st.subheader("📅 Запланировать звонок на встроенной платформе")
        
        # Получение учеников учителя
        students = db.get_teacher_students(user['id'])
        
        if not students:
            st.info("У вас нет учеников для планирования звонков.")
            return
        
        with st.form("create_call_form"):
            student_options = {f"{student['first_name']} {student['last_name']}": student['id'] 
                              for student in students}
            
            selected_student = st.selectbox(
                "Выберите ученика:",
                options=list(student_options.keys())
            )
            
            col1, col2 = st.columns(2)
            with col1:
                call_date = st.date_input("Дата звонка:")
                call_time = st.time_input("Время звонка:")
            
            with col2:
                duration = st.number_input("Длительность (минуты):", min_value=15, max_value=180, value=60)
            
            notes = st.text_area("Заметки (необязательно):", placeholder="Тема урока, дополнительная информация...")
            
            st.info("💡 Звонок будет проходить на встроенной платформе. Запись автоматически сохранится в разделе 'Записи уроков' и будет доступна в течение 2 дней.")
            
            if st.form_submit_button("📞 Запланировать звонок"):
                if selected_student:
                    from datetime import datetime, time
                    
                    # Объединение даты и времени
                    scheduled_datetime = datetime.combine(call_date, call_time)
                    student_id = student_options[selected_student]
                    
                    success, result = db.create_call(
                        student_id, user['id'], scheduled_datetime, 
                        duration, notes
                    )
                    
                    if success:
                        st.success("Звонок запланирован! Уведомление отправлено ученику.")
                        st.rerun()
                    else:
                        st.error(result)
        
    except Exception as e:
        st.error(f"Ошибка формы создания звонка: {e}")
        print(f"Ошибка формы создания звонка: {e}")

def show_lesson_records_section(user):
    """Отображение секции записей уроков"""
    try:
        st.header("🎥 Записи уроков")
        
        # Создание новой записи урока
        if user['role'] == 'Учитель':
            show_create_lesson_form(user)
        
        st.markdown("---")
        
        # Получение записей уроков
        records = db.get_user_lesson_records(user['id'])
        
        if not records:
            st.info("У вас нет записей уроков.")
            return
        
        # Группировка записей
        auto_records = [r for r in records if r.get('is_auto_created')]
        manual_records = [r for r in records if not r.get('is_auto_created')]
        
        # Автоматические записи от звонков
        if auto_records:
            st.subheader("📞 Записи звонков (автоматические)")
            st.info("⏰ Эти записи автоматически удаляются через 2 дня")
            
            for record in auto_records:
                show_lesson_record_card(record, user, is_auto=True)
        
        # Ручные записи
        if manual_records:
            st.subheader("📚 Мои записи уроков")
            
            for record in manual_records:
                show_lesson_record_card(record, user, is_auto=False)
        
    except Exception as e:
        st.error(f"Ошибка секции записей уроков: {e}")
        print(f"Ошибка секции записей уроков: {e}")

def show_lesson_record_card(record, user, is_auto=False):
    """Отображение карточки записи урока"""
    try:
        # Определение статуса доступности
        availability = record.get('availability_status', 'permanent')
        title_prefix = "🤖 " if is_auto else ""
        
        if availability == 'expired':
            title_prefix += "⏰ [ИСТЕКЛА] "
        elif availability == 'available' and is_auto:
            title_prefix += "⏳ "
        
        with st.expander(f"{title_prefix}{record['lesson_title']} - {record['lesson_date'] or 'Дата не указана'}"):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                if user['role'] == 'Ученик':
                    st.write(f"**Учитель:** {record['teacher_name']} {record['teacher_surname']}")
                else:
                    st.write(f"**Ученик:** {record['student_name']} {record['student_surname']}")
                
                st.write(f"**Предмет:** {record['subject'] or 'Не указан'}")
                st.write(f"**Дата урока:** {record['lesson_date'] or 'Не указана'}")
                
                if is_auto:
                    if record.get('expires_at'):
                        st.write(f"**Истекает:** {record['expires_at']}")
            
            with col2:
                if record.get('description'):
                    st.write(f"**Описание:** {record['description']}")
                
                if record.get('homework'):
                    st.write(f"**Домашнее задание:** {record['homework']}")
                
                if record.get('video_url'):
                    st.write(f"**Видео ссылка:** [Открыть]({record['video_url']})")
            
            with col3:
                # Кнопки скачивания
                if record.get('video_file_path') and availability != 'expired':
                    if st.button("📥 Скачать", key=f"download_{record['id']}"):
                        download_lesson_video(record)
                
                elif availability == 'expired':
                    st.write("❌ Недоступно")
                
                # Тип записи
                if is_auto:
                    st.write("🤖 Авто")
                else:
                    st.write("✏️ Ручная")
    
    except Exception as e:
        st.error(f"Ошибка карточки записи: {e}")
        print(f"Ошибка карточки записи: {e}")

def show_create_lesson_form(user):
    """Форма создания записи урока для учителя"""
    try:
        st.subheader("📝 Создать запись урока")
        
        # Получение учеников учителя
        students = db.get_teacher_students(user['id'])
        
        if not students:
            st.info("У вас нет учеников для создания записей уроков.")
            return
        
        with st.form("create_lesson_form"):
            student_options = {f"{student['first_name']} {student['last_name']}": student['id'] 
                              for student in students}
            
            selected_student = st.selectbox(
                "Выберите ученика:",
                options=list(student_options.keys())
            )
            
            col1, col2 = st.columns(2)
            with col1:
                lesson_title = st.text_input("Название урока:", placeholder="Урок математики: Квадратные уравнения")
                subject = st.text_input("Предмет:", placeholder="Математика")
            
            with col2:
                lesson_date = st.date_input("Дата урока:")
                lesson_time = st.time_input("Время урока:")
            
            # Выбор типа видео
            video_type = st.radio(
                "Тип видео:",
                ["Ссылка на видео", "Загрузка файла"],
                help="Выберите, как вы хотите добавить видео к уроку"
            )
            
            video_url = ""
            video_file_path = ""
            
            if video_type == "Ссылка на видео":
                video_url = st.text_input("Ссылка на видео (необязательно):", placeholder="https://youtube.com/...")
            else:
                uploaded_file = st.file_uploader(
                    "Загрузить видеофайл (необязательно):",
                    type=['mp4', 'avi', 'mov', 'mkv'],
                    help="Поддерживаемые форматы: MP4, AVI, MOV, MKV"
                )
                if uploaded_file is not None:
                    # В реальной системе здесь будет сохранение файла
                    video_file_path = f"/uploads/lessons/{uploaded_file.name}"
                    st.success(f"Файл {uploaded_file.name} готов к загрузке")
            
            description = st.text_area("Описание урока:", placeholder="Краткое описание пройденного материала...")
            homework = st.text_area("Домашнее задание:", placeholder="Задания для самостоятельного выполнения...")
            
            st.info("💡 Ручные записи уроков сохраняются постоянно (в отличие от автоматических записей звонков)")
            
            if st.form_submit_button("💾 Создать запись урока"):
                if selected_student and lesson_title:
                    from datetime import datetime
                    
                    # Объединение даты и времени
                    lesson_datetime = datetime.combine(lesson_date, lesson_time)
                    student_id = student_options[selected_student]
                    
                    success, message = db.create_lesson_record(
                        student_id, user['id'], lesson_title, lesson_datetime,
                        subject, video_url, video_file_path, description, homework
                    )
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Пожалуйста, заполните обязательные поля (ученик и название урока)")
        
    except Exception as e:
        st.error(f"Ошибка формы создания урока: {e}")
        print(f"Ошибка формы создания урока: {e}")

def download_lesson_video(record):
    """Функция скачивания видео урока"""
    try:
        # В реальной системе здесь будет настоящее скачивание файла
        import os
        import base64
        
        video_path = record.get('video_file_path', '')
        lesson_title = record.get('lesson_title', 'lesson')
        
        # Имитация файла для демонстрации
        if video_path:
            st.success("✅ Скачивание начато!")
            st.info(f"📁 Файл: {os.path.basename(video_path)}")
            st.info(f"📝 Урок: {lesson_title}")
            st.info(f"💾 Путь: {video_path}")
            
            # В реальной системе здесь будет:
            # with open(video_path, "rb") as file:
            #     st.download_button(
            #         label="📥 Скачать видео",
            #         data=file,
            #         file_name=f"{lesson_title}.mp4",
            #         mime="video/mp4"
            #     )
            
            st.warning("💡 В реальной системе здесь будет прямое скачивание файла")
        else:
            st.error("❌ Файл не найден")
            
    except Exception as e:
        st.error(f"Ошибка скачивания: {e}")
        print(f"Ошибка скачивания видео: {e}")

if __name__ == "__main__":
    main()