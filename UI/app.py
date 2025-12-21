import sys
from pathlib import Path
from flask import *
from datetime import datetime
import os

# Получаем абсолютный путь к файлу и его родительскую директорию
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent

# Добавляем корневую директорию проекта в sys.path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database.auth import auth_manager
from database.database import db
from bot.chatbot import chatbot
from bot.theory import theory_manager
from bot.testing import testing_manager
from formulas import formula_manager

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Конфигурация
PAGE_TITLE = "Система регистрации учителей и учеников"
PAGE_ICON = "🎓"

@app.before_request
def before_request():
    """Инициализация перед каждым запросом"""
    try:
        auth_manager.init_session_state()
    except Exception as e:
        print(f"Ошибка инициализации сессии: {e}")

@app.route('/')
def index():
    """Главная страница"""
    if auth_manager.is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if auth_manager.is_logged_in():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Пожалуйста, заполните все поля', 'error')
            return render_template('login.html', page_title=PAGE_TITLE)
        
        try:
            email_normalized = email.lower()
            success, user_data = db.authenticate_user(email_normalized, password)
            if success:
                auth_manager.login_user(user_data)
                flash('Успешный вход!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Неверный email или пароль', 'error')
        except Exception as e:
            flash(f'Ошибка входа: {e}', 'error')
            print(f"Ошибка входа: {e}")
    
    return render_template('login.html', page_title=PAGE_TITLE)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Страница восстановления пароля"""
    if auth_manager.is_logged_in():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        if not email or not first_name or not last_name:
            flash('Пожалуйста, заполните все поля', 'error')
            return render_template('forgot_password.html', page_title=PAGE_TITLE)
        
        try:
            # Проверяем существование пользователя
            user = db.get_user_by_email(email)
            if not user:
                flash('Пользователь с таким email не найден', 'error')
                return render_template('forgot_password.html', page_title=PAGE_TITLE)
            
            # Проверяем совпадение имени и фамилии
            if user['first_name'].strip() != first_name.strip() or user['last_name'].strip() != last_name.strip():
                flash('Неверные имя или фамилия', 'error')
                return render_template('forgot_password.html', page_title=PAGE_TITLE)
            
            # Если все проверки пройдены, показываем форму сброса пароля
            session['reset_email'] = email
            session['reset_verified'] = True
            return redirect(url_for('reset_password'))
            
        except Exception as e:
            flash(f'Ошибка: {e}', 'error')
            print(f"Ошибка восстановления пароля: {e}")
    
    return render_template('forgot_password.html', page_title=PAGE_TITLE)

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Страница сброса пароля"""
    if auth_manager.is_logged_in():
        return redirect(url_for('dashboard'))
    
    # Проверяем, что пользователь прошел верификацию
    if not session.get('reset_verified') or not session.get('reset_email'):
        flash('Сначала пройдите проверку личности', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not new_password or not confirm_password:
            flash('Пожалуйста, заполните все поля', 'error')
            return render_template('reset_password.html', page_title=PAGE_TITLE)
        
        if new_password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('reset_password.html', page_title=PAGE_TITLE)
        
        if len(new_password) < 6:
            flash('Пароль должен содержать минимум 6 символов', 'error')
            return render_template('reset_password.html', page_title=PAGE_TITLE)
        
        try:
            email = session.get('reset_email')
            success, message = db.reset_user_password(email, new_password)
            
            if success:
                # Очищаем сессию
                session.pop('reset_email', None)
                session.pop('reset_verified', None)
                flash('Пароль успешно изменен! Теперь вы можете войти с новым паролем.', 'success')
                return redirect(url_for('login'))
            else:
                flash(message, 'error')
        except Exception as e:
            flash(f'Ошибка сброса пароля: {e}', 'error')
            print(f"Ошибка сброса пароля: {e}")
    
    return render_template('reset_password.html', page_title=PAGE_TITLE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if auth_manager.is_logged_in():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        from validator.validation import Validator as validator
        
        registration_data = {
            'email': request.form.get('email', '').strip().lower(),
            'password': request.form.get('password', ''),
            'password_confirm': request.form.get('password_confirm', ''),
            'first_name': request.form.get('first_name', ''),
            'last_name': request.form.get('last_name', ''),
            'role': request.form.get('role', ''),
            'city': request.form.get('city', ''),
            'school': request.form.get('school', ''),
            'class_number': request.form.get('class_number', ''),
            'subjects': request.form.get('subjects', '')
        }
        
        # Проверка совпадения паролей
        if registration_data['password'] != registration_data['password_confirm']:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html', page_title=PAGE_TITLE, form_data=registration_data)
        
        # Валидация данных
        try:
            is_valid, errors = validator.validate_registration_data(registration_data)
            if not is_valid:
                error_msg = "Ошибки в форме: " + ", ".join([f"{k}: {v}" for k, v in errors.items()])
                flash(error_msg, 'error')
                return render_template('register.html', page_title=PAGE_TITLE, form_data=registration_data)
            
            # Регистрация пользователя
            success, result = db.register_user(registration_data)
            if success:
                flash('Регистрация прошла успешно! Теперь вы можете войти в систему.', 'success')
                return redirect(url_for('login'))
            else:
                flash(f'Ошибка регистрации: {result}', 'error')
        except Exception as e:
            flash(f'Произошла ошибка: {e}', 'error')
            print(f"Ошибка регистрации: {e}")
    
    return render_template('register.html', page_title=PAGE_TITLE)

@app.route('/logout')
def logout():
    """Выход из системы"""
    auth_manager.logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Главная панель после входа"""
    if not auth_manager.is_logged_in():
        return redirect(url_for('login'))
    
    try:
        user = auth_manager.get_current_user()
        if not user:
            auth_manager.logout_user()
            return redirect(url_for('login'))
        
        # Определяем активную вкладку
        active_tab = request.args.get('tab', 'home')
        
        # Получаем данные для главной панели
        teachers_count = None
        try:
            teachers = db.get_teachers()
            teachers_count = len(teachers) if teachers else 0
        except Exception as e:
            print(f"Ошибка получения количества учителей: {e}")
        
        return render_template('dashboard.html', 
                             page_title=PAGE_TITLE,
                             user=user,
                             active_tab=active_tab,
                             teachers_count=teachers_count)
    except Exception as e:
        flash(f'Ошибка панели управления: {e}', 'error')
        print(f"Ошибка панели управления: {e}")
        return redirect(url_for('login'))

# API endpoints для AJAX запросов
@app.route('/api/chat/send', methods=['POST'])
def api_chat_send():
    """API для отправки сообщения в чат-бот"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Пустое сообщение'}), 400
        
        bot_response = chatbot.get_bot_response(user_message)
        chatbot.add_message("user", user_message)
        chatbot.add_message("assistant", bot_response)
        
        return jsonify({
            'success': True,
            'response': bot_response
        })
    except Exception as e:
        print(f"Ошибка API чата: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/history', methods=['GET'])
def api_chat_history():
    """API для получения истории чата"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        chatbot.init_chat_session()
        messages = session.get('chat_messages', [])
        return jsonify({'messages': messages})
    except Exception as e:
        print(f"Ошибка получения истории чата: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/clear', methods=['POST'])
def api_chat_clear():
    """API для очистки истории чата"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        chatbot.clear_chat_history()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Ошибка очистки чата: {e}")
        return jsonify({'error': str(e)}), 500

# Маршруты для разделов dashboard
@app.route('/api/dashboard/teachers')
def api_teachers():
    """API для получения списка учителей"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        teachers = db.get_teachers()
        
        # Фильтр по предмету
        subject_filter = request.args.get('subject', '')
        if subject_filter and subject_filter != 'Все предметы':
            teachers = [t for t in teachers if t.get('subjects') and subject_filter in t.get('subjects', '')]
        
        # Получаем предметы для фильтра
        subjects_set = set()
        for teacher in db.get_teachers():
            if teacher.get('subjects'):
                teacher_subjects = [s.strip() for s in teacher['subjects'].split(',')]
                subjects_set.update(teacher_subjects)
        subjects_list = sorted(list(subjects_set))
        
        # Для учеников - их учителя
        my_teachers = []
        if user['role'] == 'Ученик':
            my_teachers = db.get_student_teachers(user['id'])
        
        # Для учителей - их ученики (дерево)
        students_tree = {}
        if user['role'] == 'Учитель':
            students_tree = db.get_teacher_students_tree(user['id'])
        
        return jsonify({
            'teachers': teachers,
            'my_teachers': my_teachers,
            'students_tree': students_tree,
            'subjects': subjects_list
        })
    except Exception as e:
        print(f"Ошибка получения учителей: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/notifications')
def api_notifications():
    """API для получения уведомлений"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        notifications = db.get_user_notifications(user['id'])
        unread_count = len([n for n in notifications if not n['is_read']])
        
        return jsonify({
            'notifications': notifications,
            'unread_count': unread_count
        })
    except Exception as e:
        print(f"Ошибка получения уведомлений: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/notifications/<int:notification_id>/read', methods=['POST'])
def api_mark_notification_read(notification_id):
    """API для отметки уведомления как прочитанного"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        success, message = db.mark_notification_read(notification_id, user['id'])
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        print(f"Ошибка отметки уведомления: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/personal-chat/users')
def api_personal_chat_users():
    """API для получения списка пользователей для личного чата"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        available_users = []
        
        if user['role'] == 'Ученик':
            teachers = db.get_student_teachers(user['id'])
            students = db.get_all_students()
            students = [s for s in students if s['id'] != user['id']]
            
            for t in teachers:
                available_users.append({
                    'id': t['id'],
                    'name': f"{t['first_name']} {t['last_name']}",
                    'role': 'Учитель',
                    'is_online': t.get('is_online', False)
                })
            for s in students:
                available_users.append({
                    'id': s['id'],
                    'name': f"{s['first_name']} {s['last_name']}",
                    'role': 'Ученик',
                    'is_online': s.get('is_online', False)
                })
        else:  # Учитель
            students = db.get_teacher_students(user['id'])
            for s in students:
                available_users.append({
                    'id': s['id'],
                    'name': f"{s['first_name']} {s['last_name']}",
                    'role': 'Ученик',
                    'is_online': s.get('is_online', False)
                })
        
        return jsonify({'users': available_users})
    except Exception as e:
        print(f"Ошибка получения пользователей для чата: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/personal-chat/<int:other_user_id>/messages', methods=['GET', 'POST'])
def api_personal_chat_messages(other_user_id):
    """API для получения и отправки сообщений личного чата"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        
        if request.method == 'GET':
            messages = db.get_chat_messages(user['id'], other_user_id)
            return jsonify({'messages': messages})
        else:  # POST
            data = request.get_json()
            message_text = data.get('message', '')
            if not message_text:
                return jsonify({'error': 'Пустое сообщение'}), 400
            
            success, result = db.send_chat_message(user['id'], other_user_id, message_text)
            if success:
                return jsonify({'success': True, 'message': result})
            else:
                return jsonify({'error': result}), 400
    except Exception as e:
        print(f"Ошибка личного чата: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/requests')
def api_requests():
    """API для получения заявок"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        
        if user['role'] == 'Ученик':
            requests = db.get_student_requests(user['id'])
            return jsonify({'requests': requests, 'role': 'student'})
        else:  # Учитель
            sent_requests = db.get_teacher_sent_requests(user['id'])
            all_students = db.get_all_students()
            return jsonify({
                'sent_requests': sent_requests,
                'all_students': all_students,
                'role': 'teacher'
            })
    except Exception as e:
        print(f"Ошибка получения заявок: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/requests/<int:request_id>/accept', methods=['POST'])
def api_accept_request(request_id):
    """API для принятия заявки"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        if user['role'] != 'Ученик':
            return jsonify({'error': 'Только ученики могут принимать заявки'}), 403
        
        success, message = db.accept_teacher_request(request_id, user['id'])
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        print(f"Ошибка принятия заявки: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/requests/<int:request_id>/reject', methods=['POST'])
def api_reject_request(request_id):
    """API для отклонения заявки"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        if user['role'] != 'Ученик':
            return jsonify({'error': 'Только ученики могут отклонять заявки'}), 403
        
        success, message = db.reject_teacher_request(request_id, user['id'])
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        print(f"Ошибка отклонения заявки: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/requests/create', methods=['POST'])
def api_create_request():
    """API для создания заявки учителем"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        if user['role'] != 'Учитель':
            return jsonify({'error': 'Только учителя могут создавать заявки'}), 403
        
        data = request.get_json()
        student_id = data.get('student_id')
        message = data.get('message', '')
        
        if not student_id:
            return jsonify({'error': 'Не указан ученик'}), 400
        
        success, result = db.create_teacher_request(user['id'], student_id, message)
        return jsonify({'success': success, 'message': result})
    except Exception as e:
        print(f"Ошибка создания заявки: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/calls')
def api_calls():
    """API для получения звонков"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        # Автоматическая очистка просроченных записей
        try:
            db.cleanup_expired_records()
        except Exception as e:
            print(f"Ошибка автоочистки: {e}")
        
        user = auth_manager.get_current_user()
        calls = db.get_user_calls(user['id'])
        
        # Группировка по статусу
        call_groups = {
            'active': [c for c in calls if c['status'] == 'active'],
            'scheduled': [c for c in calls if c['status'] == 'scheduled'],
            'completed': [c for c in calls if c['status'] == 'completed'][:5]
        }
        
        # Для учителей - список учеников для создания звонка
        students = []
        if user['role'] == 'Учитель':
            students = db.get_teacher_students(user['id'])
        
        return jsonify({
            'calls': calls,
            'call_groups': call_groups,
            'students': students
        })
    except Exception as e:
        print(f"Ошибка получения звонков: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/calls/create', methods=['POST'])
def api_create_call():
    """API для создания звонка"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        if user['role'] != 'Учитель':
            return jsonify({'error': 'Только учителя могут создавать звонки'}), 403
        
        data = request.get_json()
        student_id = data.get('student_id')
        scheduled_datetime_str = data.get('scheduled_datetime')
        duration = data.get('duration', 60)
        notes = data.get('notes', '')
        
        if not student_id or not scheduled_datetime_str:
            return jsonify({'error': 'Не указаны обязательные поля'}), 400
        
        scheduled_datetime = datetime.fromisoformat(scheduled_datetime_str)
        success, result = db.create_call(student_id, user['id'], scheduled_datetime, duration, notes)
        return jsonify({'success': success, 'message': result})
    except Exception as e:
        print(f"Ошибка создания звонка: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/calls/<int:call_id>/start', methods=['POST'])
def api_start_call(call_id):
    """API для начала звонка"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        success, message = db.start_call(call_id)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        print(f"Ошибка начала звонка: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/calls/<int:call_id>/end', methods=['POST'])
def api_end_call(call_id):
    """API для завершения звонка"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        recording_path = data.get('recording_path', f'/recordings/call_{call_id}_{datetime.now().isoformat()}.mp4')
        success, message = db.end_call(call_id, recording_path)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        print(f"Ошибка завершения звонка: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/lessons')
def api_lessons():
    """API для получения записей уроков"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        records = db.get_user_lesson_records(user['id'])
        
        auto_records = [r for r in records if r.get('is_auto_created')]
        manual_records = [r for r in records if not r.get('is_auto_created')]
        
        # Для учителей - список учеников для создания записи
        students = []
        if user['role'] == 'Учитель':
            students = db.get_teacher_students(user['id'])
        
        return jsonify({
            'auto_records': auto_records,
            'manual_records': manual_records,
            'students': students
        })
    except Exception as e:
        print(f"Ошибка получения записей уроков: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/lessons/create', methods=['POST'])
def api_create_lesson():
    """API для создания записи урока"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        if user['role'] != 'Учитель':
            return jsonify({'error': 'Только учителя могут создавать записи уроков'}), 403
        
        data = request.get_json()
        student_id = data.get('student_id')
        lesson_title = data.get('lesson_title')
        lesson_datetime_str = data.get('lesson_datetime')
        subject = data.get('subject', '')
        video_url = data.get('video_url', '')
        video_file_path = data.get('video_file_path', '')
        description = data.get('description', '')
        homework = data.get('homework', '')
        
        if not student_id or not lesson_title or not lesson_datetime_str:
            return jsonify({'error': 'Не указаны обязательные поля'}), 400
        
        lesson_datetime = datetime.fromisoformat(lesson_datetime_str)
        success, message = db.create_lesson_record(
            student_id, user['id'], lesson_title, lesson_datetime,
            subject, video_url, video_file_path, description, homework
        )
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        print(f"Ошибка создания записи урока: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/lessons/<int:lesson_id>/comments', methods=['GET', 'POST'])
def api_lesson_comments(lesson_id):
    """API для получения и добавления комментариев к записи урока"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        
        if request.method == 'GET':
            comments = db.get_video_comments(lesson_id)
            return jsonify({'comments': comments})
        else:  # POST
            data = request.get_json()
            comment_text = data.get('comment_text', '')
            timestamp = data.get('timestamp')
            
            if not comment_text:
                return jsonify({'error': 'Пустой комментарий'}), 400
            
            ts = timestamp if timestamp and timestamp > 0 else None
            success, message = db.add_video_comment(lesson_id, user['id'], comment_text, ts)
            return jsonify({'success': success, 'message': message})
    except Exception as e:
        print(f"Ошибка работы с комментариями: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/auto-match', methods=['POST'])
def api_auto_match():
    """API для автоматического прикрепления учеников к учителям"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        if user['role'] != 'Учитель':
            return jsonify({'error': 'Только учителя могут использовать эту функцию'}), 403
        
        success, message = db.auto_match_teachers_students()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        print(f"Ошибка автоматического прикрепления: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== API для ТЕОРИИ ====================
@app.route('/api/theory/subjects', methods=['GET'])
def api_theory_subjects():
    """API для получения списка предметов"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        print(f"[API] Запрос на получение предметов")
        theory_manager.init_theory_session()
        data = theory_manager.show_theory_interface()
        subjects_structure = data.get('subjects', {})
        subjects_list = list(subjects_structure.keys())
        print(f"[API] Найдено предметов: {len(subjects_list)}")
        print(f"[API] Предметы: {subjects_list}")
        return jsonify({
            'subjects': subjects_list,
            'subjects_structure': subjects_structure
        })
    except Exception as e:
        print(f"[API ERROR] Ошибка получения предметов: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/theory/sections', methods=['GET'])
def api_theory_sections():
    """API для получения разделов предмета"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        subject = request.args.get('subject')
        print(f"[API] Запрос на получение разделов для предмета: {subject}")
        if not subject:
            print(f"[API ERROR] Предмет не указан")
            return jsonify({'error': 'Предмет не указан'}), 400
        
        # Сохраняем в сессию
        if 'theory_state' not in session:
            session['theory_state'] = {}
        session['theory_state']['selected_subject'] = subject
        session['theory_state']['current_page'] = 'sections'
        session.modified = True
        
        # Получаем разделы напрямую из структуры
        if subject not in theory_manager.SUBJECTS_STRUCTURE:
            print(f"[API ERROR] Предмет '{subject}' не найден в структуре")
            print(f"[API] Доступные предметы: {list(theory_manager.SUBJECTS_STRUCTURE.keys())}")
            return jsonify({'error': f'Предмет "{subject}" не найден'}), 400
        
        sections = theory_manager.SUBJECTS_STRUCTURE[subject]["sections"]
        sections_list = list(sections.keys())
        print(f"[API] Найдено разделов: {len(sections_list)}")
        print(f"[API] Разделы: {sections_list}")
        return jsonify({
            'subject': subject,
            'sections': sections
        })
    except Exception as e:
        print(f"[API ERROR] Ошибка получения разделов: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/theory/topics', methods=['GET'])
def api_theory_topics():
    """API для получения тем раздела"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        subject = request.args.get('subject')
        section = request.args.get('section')
        if not subject or not section:
            return jsonify({'error': 'Предмет или раздел не указан'}), 400
        
        # Сохраняем в сессию
        if 'theory_state' not in session:
            session['theory_state'] = {}
        session['theory_state']['selected_subject'] = subject
        session['theory_state']['selected_section'] = section
        session['theory_state']['current_page'] = 'topics'
        session.modified = True
        
        # Получаем темы напрямую из структуры
        if subject not in theory_manager.SUBJECTS_STRUCTURE:
            return jsonify({'error': f'Предмет "{subject}" не найден'}), 400
        
        if section not in theory_manager.SUBJECTS_STRUCTURE[subject]["sections"]:
            return jsonify({'error': f'Раздел "{section}" не найден'}), 400
        
        topics = theory_manager.SUBJECTS_STRUCTURE[subject]["sections"][section]["topics"]
        return jsonify({
            'subject': subject,
            'section': section,
            'topics': topics
        })
    except Exception as e:
        print(f"Ошибка получения тем: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/theory/explanation', methods=['POST'])
def api_theory_explanation():
    """API для генерации объяснения темы"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        subject = data.get('subject')
        section = data.get('section')
        topic = data.get('topic')
        regenerate = data.get('regenerate', False)
        
        print(f"[API] Запрос на генерацию теории: subject={subject}, section={section}, topic={topic}, regenerate={regenerate}")
        
        if not all([subject, section, topic]):
            print(f"[API ERROR] Не все параметры указаны: subject={subject}, section={section}, topic={topic}")
            return jsonify({'error': 'Не все параметры указаны'}), 400
        
        session['theory_state'] = session.get('theory_state', {})
        session['theory_state']['selected_subject'] = subject
        session['theory_state']['selected_section'] = section
        session['theory_state']['selected_topic'] = topic
        session['theory_state']['current_page'] = 'explanation'
        
        if regenerate:
            session['theory_state']['explanation_text'] = None
            print(f"[API] Режим перегенерации включен")
        
        # Генерируем объяснение
        print(f"[API] Вызываем theory_manager.get_topic_explanation()...")
        explanation = theory_manager.get_topic_explanation(subject, section, topic, regenerate=regenerate)
        print(f"[API] Получено объяснение, длина: {len(explanation) if explanation else 0} символов")
        
        return jsonify({
            'success': True,
            'explanation': explanation,
            'subject': subject,
            'section': section,
            'topic': topic
        })
    except Exception as e:
        print(f"[API ERROR] Ошибка генерации объяснения: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/theory/state', methods=['GET'])
def api_theory_state():
    """API для получения текущего состояния теории"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        theory_manager.init_theory_session()
        data = theory_manager.show_theory_interface()
        return jsonify(data)
    except Exception as e:
        print(f"Ошибка получения состояния: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/theory/navigate-back', methods=['POST'])
def api_theory_navigate_back():
    """API для навигации назад"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        theory_manager.navigate_back()
        data = theory_manager.show_theory_interface()
        return jsonify(data)
    except Exception as e:
        print(f"Ошибка навигации: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== API для ТЕСТИРОВАНИЯ ====================
@app.route('/api/testing/subjects', methods=['GET'])
def api_testing_subjects():
    """API для получения предметов для тестирования"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        testing_manager.init_testing_session()
        data = testing_manager.show_testing_interface()
        return jsonify({
            'subjects': list(data.get('subjects', {}).keys()) if isinstance(data.get('subjects'), dict) else [],
            'subjects_structure': data.get('subjects', {})
        })
    except Exception as e:
        print(f"Ошибка получения предметов: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/testing/select-subject', methods=['POST'])
def api_testing_select_subject():
    """API для выбора предмета"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401

    try:
        data = request.get_json()
        subject = data.get('subject')
        if not subject:
            return jsonify({'error': 'Предмет не указан'}), 400

        # Сохраняем в сессию
        if 'testing_state' not in session:
            session['testing_state'] = {}
        session['testing_state']['selected_subject'] = subject
        session['testing_state']['current_page'] = 'sections'
        session['testing_state']['selected_section'] = None
        session['testing_state']['selected_topic'] = None
        session.modified = True

        # Передаём предмет напрямую в метод
        result = testing_manager.show_sections(subject=subject)
        return jsonify(result)
    except Exception as e:
        print(f"Ошибка выбора предмета: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/testing/select-section', methods=['POST'])
def api_testing_select_section():
    """API для выбора раздела"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401

    try:
        data = request.get_json()
        section = data.get('section')
        if not section:
            return jsonify({'error': 'Раздел не указан'}), 400

        # Получаем предмет из сессии
        testing_state = session.get('testing_state', {})
        subject = testing_state.get('selected_subject')
        
        if not subject:
            return jsonify({'error': 'Сначала выберите предмет'}), 400

        # Сохраняем в сессию
        session['testing_state']['selected_section'] = section
        session['testing_state']['current_page'] = 'topics'
        session['testing_state']['selected_topic'] = None
        session.modified = True

        # Передаём параметры напрямую в метод
        result = testing_manager.show_topics(subject=subject, section=section)
        return jsonify(result)
    except Exception as e:
        print(f"Ошибка выбора раздела: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/testing/select-topic', methods=['POST'])
def api_testing_select_topic():
    """API для выбора темы"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        topic = data.get('topic')
        if not topic:
            return jsonify({'error': 'Тема не указана'}), 400
        
        session['testing_state']['selected_topic'] = topic
        session['testing_state']['current_page'] = 'difficulty'
        session['testing_state']['selected_difficulty'] = None
        
        return jsonify({
            'success': True,
            'difficulty_levels': testing_manager.DIFFICULTY_LEVELS
        })
    except Exception as e:
        print(f"Ошибка выбора темы: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/testing/generate-test', methods=['POST'])
def api_testing_generate_test():
    """API для генерации теста"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        subject = data.get('subject')
        section = data.get('section')
        topic = data.get('topic')
        difficulty = data.get('difficulty')
        
        if not all([subject, section, topic, difficulty]):
            return jsonify({'error': 'Не все параметры указаны'}), 400
        
        session['testing_state']['selected_difficulty'] = difficulty
        session['testing_state']['current_page'] = 'test'
        session['testing_state']['current_test'] = None
        session['testing_state']['user_answers'] = {}
        
        # Генерируем тест
        test = testing_manager.generate_test(subject, section, topic, difficulty)
        
        if not test or 'questions' not in test:
            return jsonify({'error': 'Не удалось сгенерировать тест'}), 500
        
        session['testing_state']['current_test'] = test
        
        return jsonify({
            'success': True,
            'test': test
        })
    except Exception as e:
        print(f"Ошибка генерации теста: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/testing/submit-answer', methods=['POST'])
def api_testing_submit_answer():
    """API для отправки ответа на вопрос"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        question_index = data.get('question_index')
        answer = data.get('answer')
        
        if question_index is None or answer is None:
            return jsonify({'error': 'Не все параметры указаны'}), 400
        
        session['testing_state'] = session.get('testing_state', {})
        if 'user_answers' not in session['testing_state']:
            session['testing_state']['user_answers'] = {}
        
        session['testing_state']['user_answers'][int(question_index)] = answer
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Ошибка отправки ответа: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/testing/finish-test', methods=['POST'])
def api_testing_finish_test():
    """API для завершения теста и получения результатов"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        session['testing_state'] = session.get('testing_state', {})
        test = session['testing_state'].get('current_test')
        user_answers = session['testing_state'].get('user_answers', {})
        
        if not test:
            return jsonify({'error': 'Тест не найден'}), 400
        
        # Подсчитываем результаты
        results = testing_manager.calculate_results()
        
        session['testing_state']['current_page'] = 'results'
        session['testing_state']['test_results'] = results
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        print(f"Ошибка завершения теста: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/testing/state', methods=['GET'])
def api_testing_state():
    """API для получения текущего состояния тестирования"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        testing_manager.init_testing_session()
        session_state = session.get('testing_state', {})
        return jsonify({
            'current_page': session_state.get('current_page', 'subjects'),
            'selected_subject': session_state.get('selected_subject'),
            'selected_section': session_state.get('selected_section'),
            'selected_topic': session_state.get('selected_topic'),
            'selected_difficulty': session_state.get('selected_difficulty')
        })
    except Exception as e:
        print(f"Ошибка получения состояния: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== API для ФОРМУЛ ====================
@app.route('/api/formulas/categories', methods=['GET'])
def api_formulas_categories():
    """API для получения категорий формул"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        formula_manager.init_formula_state()
        data = formula_manager.show_formula_interface()
        if 'error' in data:
            return jsonify(data), 500
        return jsonify(data)
    except Exception as e:
        print(f"Ошибка получения категорий: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/formulas/select-category', methods=['POST'])
def api_formulas_select_category():
    """API для выбора категории формул"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        category = data.get('category')
        if not category:
            return jsonify({'error': 'Категория не указана'}), 400
        
        session['formula_state'] = session.get('formula_state', {})
        session['formula_state']['current_category'] = category
        session['formula_state']['current_subcategory'] = None
        
        result = formula_manager.show_subcategories()
        return jsonify(result)
    except Exception as e:
        print(f"Ошибка выбора категории: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/formulas/select-subcategory', methods=['POST'])
def api_formulas_select_subcategory():
    """API для выбора подкатегории"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        subcategory = data.get('subcategory')
        if not subcategory:
            return jsonify({'error': 'Подкатегория не указана'}), 400
        
        formula_manager.init_formula_state()
        session['formula_state'] = session.get('formula_state', {})
        session['formula_state']['current_subcategory'] = subcategory
        
        result = formula_manager.show_subcategories()
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        print(f"Ошибка выбора подкатегории: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/formulas/calculate', methods=['POST'])
def api_formulas_calculate():
    """API для вычисления формулы"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        formula_name = data.get('formula_name')
        category = data.get('category')
        subcategory = data.get('subcategory')
        values = data.get('values', {})
        target = data.get('target')
        
        if not all([formula_name, category, subcategory, target]):
            return jsonify({'error': 'Не все параметры указаны'}), 400
        
        result = formula_manager.calculate_formula(formula_name, category, subcategory, values, target)
        
        if result is None:
            return jsonify({'error': 'Не удалось вычислить результат'}), 500
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        print(f"Ошибка вычисления формулы: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== API для НАСТРОЕК ====================
@app.route('/api/settings', methods=['GET'])
def api_get_settings():
    """API для получения настроек пользователя"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        settings = db.get_user_settings(user['id'])
        return jsonify({'settings': settings})
    except Exception as e:
        print(f"Ошибка получения настроек: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def api_update_settings():
    """API для обновления настроек пользователя"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        data = request.get_json()
        success, message = db.update_user_settings(user['id'], data)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        print(f"Ошибка обновления настроек: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/theme', methods=['POST'])
def api_update_theme():
    """API для обновления темы"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        data = request.get_json()
        theme = data.get('theme', 'light')
        success, message = db.update_user_settings(user['id'], {'theme': theme})
        return jsonify({'success': success})
    except Exception as e:
        print(f"Ошибка обновления темы: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/reset', methods=['POST'])
def api_reset_settings():
    """API для сброса настроек"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        success, message = db.reset_user_settings(user['id'])
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        print(f"Ошибка сброса настроек: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== API для ЗАДАНИЙ КЛАССУ ====================
@app.route('/api/assignments', methods=['GET'])
def api_get_assignments():
    """API для получения заданий"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        
        if user['role'] == 'Учитель':
            assignments = db.get_teacher_assignments(user['id'])
            return jsonify({'role': 'teacher', 'assignments': assignments})
        else:
            assignments = db.get_student_assignments(user['id'])
            return jsonify({'role': 'student', 'assignments': assignments})
    except Exception as e:
        print(f"Ошибка получения заданий: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assignments/<int:assignment_id>', methods=['GET'])
def api_get_assignment(assignment_id):
    """API для получения конкретного задания"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        assignment = db.get_assignment_by_id(assignment_id)
        if not assignment:
            return jsonify({'error': 'Задание не найдено'}), 404
        return jsonify(assignment)
    except Exception as e:
        print(f"Ошибка получения задания: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assignments/create', methods=['POST'])
def api_create_assignment():
    """API для создания задания"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        if user['role'] != 'Учитель':
            return jsonify({'error': 'Только учителя могут создавать задания'}), 403
        
        data = request.get_json()
        
        title = data.get('title')
        subject = data.get('subject')
        
        if not title or not subject:
            return jsonify({'error': 'Название и предмет обязательны'}), 400
        
        import json
        questions_json = json.dumps(data.get('questions', []), ensure_ascii=False)
        
        deadline = None
        if data.get('deadline'):
            deadline = datetime.fromisoformat(data['deadline'])
        
        success, result = db.create_class_assignment(
            teacher_id=user['id'],
            title=title,
            description=data.get('description', ''),
            subject=subject,
            topic=data.get('topic', ''),
            difficulty=data.get('difficulty', 'Средний'),
            assignment_type='test',
            questions_json=questions_json,
            target_city=data.get('target_city', ''),
            target_school=data.get('target_school', ''),
            target_class=data.get('target_class', ''),
            deadline=deadline
        )
        
        if success:
            return jsonify({'success': True, 'assignment_id': result})
        else:
            return jsonify({'error': result}), 500
    except Exception as e:
        print(f"Ошибка создания задания: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assignments/generate-test', methods=['POST'])
def api_generate_test():
    """API для генерации теста (через LLM или math_generator)"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        subject = data.get('subject')
        topic = data.get('topic', '')
        difficulty = data.get('difficulty', 'Средний')
        gen_type = data.get('generation_type', 'llm')
        count = data.get('count', 5)
        
        if not subject:
            return jsonify({'error': 'Укажите предмет'}), 400
        
        # Используем testing_manager для генерации
        test = testing_manager.generate_test(subject, '', topic or subject, difficulty)
        
        if test and 'questions' in test:
            # Ограничиваем количество вопросов
            test['questions'] = test['questions'][:count]
            return jsonify({'test': test})
        else:
            return jsonify({'error': 'Не удалось сгенерировать тест'}), 500
    except Exception as e:
        print(f"Ошибка генерации теста: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assignments/<int:assignment_id>/submit', methods=['POST'])
def api_submit_assignment(assignment_id):
    """API для отправки ответа на задание"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        if user['role'] != 'Ученик':
            return jsonify({'error': 'Только ученики могут отправлять ответы'}), 403
        
        data = request.get_json()
        answers = data.get('answers', {})
        time_spent = data.get('time_spent', 0)
        
        # Получаем задание для проверки ответов
        assignment = db.get_assignment_by_id(assignment_id)
        if not assignment:
            return jsonify({'error': 'Задание не найдено'}), 404
        
        import json
        questions = json.loads(assignment['questions_json'])
        
        # Проверяем ответы
        score = 0
        max_score = len(questions)
        
        for i, q in enumerate(questions):
            user_answer = answers.get(str(i)) or answers.get(i)
            if user_answer == q['correct_answer']:
                score += 1
        
        percentage = int((score / max_score) * 100) if max_score > 0 else 0
        
        answers_json = json.dumps(answers, ensure_ascii=False)
        
        success, result = db.submit_assignment(
            assignment_id=assignment_id,
            student_id=user['id'],
            answers_json=answers_json,
            score=score,
            max_score=max_score,
            time_spent=time_spent
        )
        
        if success:
            return jsonify({
                'success': True,
                'score': score,
                'max_score': max_score,
                'percentage': percentage
            })
        else:
            return jsonify({'error': result}), 400
    except Exception as e:
        print(f"Ошибка отправки ответа: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assignments/<int:assignment_id>/statistics', methods=['GET'])
def api_assignment_statistics(assignment_id):
    """API для получения статистики по заданию"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        if user['role'] != 'Учитель':
            return jsonify({'error': 'Только учителя могут просматривать статистику'}), 403
        
        stats = db.get_assignment_statistics(assignment_id)
        if not stats:
            return jsonify({'error': 'Статистика не найдена'}), 404
        
        return jsonify(stats)
    except Exception as e:
        print(f"Ошибка получения статистики: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assignments/<int:assignment_id>/toggle', methods=['POST'])
def api_toggle_assignment(assignment_id):
    """API для активации/деактивации задания"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        if user['role'] != 'Учитель':
            return jsonify({'error': 'Только учителя могут управлять заданиями'}), 403
        
        success, message = db.toggle_assignment_active(assignment_id, user['id'])
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        print(f"Ошибка переключения задания: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/class-statistics', methods=['GET'])
def api_class_statistics():
    """API для получения статистики по классу"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        user = auth_manager.get_current_user()
        if user['role'] != 'Учитель':
            return jsonify({'error': 'Только учителя могут просматривать статистику'}), 403
        
        city = request.args.get('city')
        school = request.args.get('school')
        class_number = request.args.get('class')
        
        stats = db.get_class_statistics(user['id'], city, school, class_number)
        return jsonify(stats)
    except Exception as e:
        print(f"Ошибка получения статистики класса: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Получаем локальный IP-адрес
    import socket
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = '127.0.0.1'
    
    print("\n" + "="*70)
    print(" " * 10 + "Запуск Flask приложения")
    print("="*70)
    print("\nПриложение будет доступно по адресам:")
    print(f"  Локально:  http://localhost:5000")
    print(f"  Локально:  http://127.0.0.1:5000")
    if local_ip != '127.0.0.1':
        print(f"  В сети:    http://{local_ip}:5000")
    print("\nДля остановки нажмите Ctrl+C")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

