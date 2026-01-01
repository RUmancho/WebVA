import sys
from pathlib import Path
from flask import *
import os

from sqlalchemy.sql.expression import False_

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
from logger.stats import log_info, log_error

PYTHON_FILENAME = "app"

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
    except Exception:
        pass

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
        except Exception:
            pass
        
        return render_template('dashboard.html', 
                             page_title=PAGE_TITLE,
                             user=user,
                             active_tab=active_tab,
                             teachers_count=teachers_count)
    except Exception as e:
        flash(f'Ошибка панели управления: {e}', 'error')
        return redirect(url_for('login'))


# ========================== API: ТЕОРИЯ ==========================

@app.route('/api/theory/state')
def api_theory_state():
    """Получение текущего состояния теории"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = theory_manager.show_theory_interface()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/theory/subjects')
def api_theory_subjects():
    """Получение списка предметов"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = theory_manager.show_subjects()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/theory/sections')
def api_theory_sections():
    """Получение разделов предмета"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    subject = request.args.get('subject', '').strip()
    if not subject:
        return jsonify({'error': 'Предмет не указан'}), 400
    
    try:
        # Сохраняем выбранный предмет в сессию
        if 'theory_state' not in session:
            session['theory_state'] = {}
        session['theory_state']['selected_subject'] = subject
        session['theory_state']['current_page'] = 'sections'
        session.modified = True
        
        data = theory_manager.show_sections()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/theory/topics')
def api_theory_topics():
    """Получение тем раздела"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    subject = request.args.get('subject', '').strip()
    section = request.args.get('section', '').strip()
    
    if not subject or not section:
        return jsonify({'error': 'Предмет или раздел не указан'}), 400
    
    try:
        # Сохраняем выбранные данные в сессию
        if 'theory_state' not in session:
            session['theory_state'] = {}
        session['theory_state']['selected_subject'] = subject
        session['theory_state']['selected_section'] = section
        session['theory_state']['current_page'] = 'topics'
        session.modified = True
        
        data = theory_manager.show_topics()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/theory/explanation', methods=['POST'])
def api_theory_explanation():
    """Генерация объяснения темы через LLM (deepseek-r1:7b)"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Некорректные данные'}), 400
        
        subject = data.get('subject', '').strip()
        section = data.get('section', '').strip()
        topic = data.get('topic', '').strip()
        regenerate = data.get('regenerate', False)
        
        if not all([subject, section, topic]):
            return jsonify({'error': 'Не все параметры указаны'}), 400
        
        # Сохраняем выбранные данные в сессию
        if 'theory_state' not in session:
            session['theory_state'] = {}
        session['theory_state']['selected_subject'] = subject
        session['theory_state']['selected_section'] = section
        session['theory_state']['selected_topic'] = topic
        session['theory_state']['current_page'] = 'explanation'
        session.modified = True
        
        # Получаем объяснение через LLM
        explanation = theory_manager.get_topic_explanation(subject, section, topic, regenerate=regenerate)
        
        # Преобразуем Markdown в HTML
        try:
            import markdown
            explanation_html = markdown.markdown(explanation, extensions=['fenced_code', 'tables', 'nl2br'])
        except ImportError:
            # Если markdown не установлен, возвращаем как есть
            explanation_html = f"<pre>{explanation}</pre>"
        
        return jsonify({
            'subject': subject,
            'section': section,
            'topic': topic,
            'explanation': explanation_html
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации: {str(e)}'}), 500


# ========================== API: ТЕСТИРОВАНИЕ ==========================

@app.route('/api/testing/state')
def api_testing_state():
    """Получение текущего состояния тестирования"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = testing_manager.show_testing_interface()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/testing/subjects')
def api_testing_subjects():
    """Получение списка предметов для тестирования"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = testing_manager.show_subjects()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/testing/select-subject', methods=['POST'])
def api_testing_select_subject():
    """Выбор предмета для тестирования"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Некорректные данные'}), 400
        
        subject = data.get('subject', '').strip()
        if not subject:
            return jsonify({'error': 'Предмет не указан'}), 400
        
        # Сохраняем в сессию
        if 'testing_state' not in session:
            session['testing_state'] = {}
        session['testing_state']['selected_subject'] = subject
        session['testing_state']['current_page'] = 'sections'
        session.modified = True
        
        result = testing_manager.show_sections(subject)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/testing/select-section', methods=['POST'])
def api_testing_select_section():
    """Выбор раздела для тестирования"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Некорректные данные'}), 400
        
        section = data.get('section', '').strip()
        if not section:
            return jsonify({'error': 'Раздел не указан'}), 400
        
        # Сохраняем в сессию
        if 'testing_state' not in session:
            session['testing_state'] = {}
        session['testing_state']['selected_section'] = section
        session['testing_state']['current_page'] = 'topics'
        session.modified = True
        
        subject = session['testing_state'].get('selected_subject')
        result = testing_manager.show_topics(subject, section)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/testing/select-topic', methods=['POST'])
def api_testing_select_topic():
    """Выбор темы для тестирования"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Некорректные данные'}), 400
        
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({'error': 'Тема не указана'}), 400
        
        # Сохраняем в сессию
        if 'testing_state' not in session:
            session['testing_state'] = {}
        session['testing_state']['selected_topic'] = topic
        session['testing_state']['current_page'] = 'difficulty'
        session.modified = True
        
        result = testing_manager.show_difficulty_selection()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/testing/generate-test', methods=['POST'])
def api_testing_generate_test():
    """Генерация теста"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Некорректные данные'}), 400
        
        subject = data.get('subject', '').strip()
        section = data.get('section', '').strip()
        topic = data.get('topic', '').strip()
        difficulty = data.get('difficulty', '').strip()
        test_type = data.get('test_type', 'with_options')
        num_questions = data.get('num_questions', 5)
        
        if not all([subject, section, topic, difficulty]):
            return jsonify({'error': 'Не все параметры указаны'}), 400
        
        # Сохраняем настройки в сессию
        if 'testing_state' not in session:
            session['testing_state'] = {}
        session['testing_state']['selected_difficulty'] = difficulty
        session['testing_state']['test_type'] = test_type
        session['testing_state']['num_questions'] = num_questions
        session['testing_state']['current_page'] = 'test'
        session['testing_state']['user_answers'] = {}
        session.modified = True
        
        # Генерируем тест
        test = testing_manager.generate_test(subject, section, topic, difficulty, test_type, num_questions)
        
        if not test or not test.get('questions'):
            return jsonify({'error': 'Не удалось сгенерировать тест'}), 500
        
        # Сохраняем тест в сессию
        session['testing_state']['current_test'] = test
        session.modified = True
        
        return jsonify({'test': test})
    except Exception as e:
        log_error(f"Ошибка генерации теста: {e}", PYTHON_FILENAME)
        return jsonify({'error': str(e)}), 500


@app.route('/api/testing/submit-answer', methods=['POST'])
def api_testing_submit_answer():
    """Сохранение ответа на вопрос"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Некорректные данные'}), 400
        
        question_index = data.get('question_index')
        answer = data.get('answer', '')
        
        if question_index is None:
            return jsonify({'error': 'Индекс вопроса не указан'}), 400
        
        # Сохраняем ответ в сессию (используем строковый ключ для корректной сериализации)
        if 'testing_state' not in session:
            session['testing_state'] = {}
        if 'user_answers' not in session['testing_state']:
            session['testing_state']['user_answers'] = {}
        
        # Преобразуем ключ в строку для надёжной сериализации JSON
        session['testing_state']['user_answers'][str(question_index)] = answer
        session.modified = True
        
        return jsonify({'success': True})
    except Exception as e:
        log_error(f"Ошибка сохранения ответа: {e}", PYTHON_FILENAME)
        return jsonify({'error': str(e)}), 500


@app.route('/api/testing/submit-all-answers', methods=['POST'])
def api_testing_submit_all_answers():
    """Сохранение всех ответов сразу (для надёжности перед завершением теста)"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Некорректные данные'}), 400
        
        answers = data.get('answers', {})
        
        # Сохраняем все ответы в сессию
        if 'testing_state' not in session:
            session['testing_state'] = {}
        if 'user_answers' not in session['testing_state']:
            session['testing_state']['user_answers'] = {}
        
        # Преобразуем все ключи в строки
        for question_index, answer in answers.items():
            session['testing_state']['user_answers'][str(question_index)] = answer
        
        session.modified = True
        
        log_info(f"Сохранено {len(answers)} ответов: {session['testing_state']['user_answers']}", PYTHON_FILENAME)
        
        return jsonify({'success': True, 'saved_count': len(answers)})
    except Exception as e:
        log_error(f"Ошибка сохранения всех ответов: {e}", PYTHON_FILENAME)
        return jsonify({'error': str(e)}), 500


@app.route('/api/testing/finish-test', methods=['POST'])
def api_testing_finish_test():
    """Завершение теста и подсчёт результатов"""
    if not auth_manager.is_logged_in():
        return jsonify({'error': 'Не авторизован'}), 401
    
    try:
        results = testing_manager.calculate_results()
        
        if not results:
            return jsonify({'error': 'Не удалось подсчитать результаты'}), 500
        
        return jsonify({'results': results})
    except Exception as e:
        log_error(f"Ошибка подсчёта результатов: {e}", PYTHON_FILENAME)
        return jsonify({'error': str(e)}), 500

import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
if __name__ == '__main__':
    app.logger.disabled = True
    app.run(host='0.0.0.0', port=5000, debug = False)
