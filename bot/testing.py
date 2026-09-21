"""
Модуль управления системой тестирования.
Использует GeneratorManager для диспетчеризации между DLL и AI генераторами.
"""

import os
import sys
import random
import re
from typing import Optional, Dict, List, Any

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import session as flask_session
from bot import topics
from bot.llm import LlmAccessError
from logger import console
from testing.generator_manager import generator_manager

from logger.tracer import trace

PYTHON_FILENAME = "testing"

# Константы
DEFAULT_NUM_QUESTIONS = 5
MIN_QUESTIONS = 3
MAX_QUESTIONS = 20

# Уровни сложности
DIFFICULTY_LEVELS = {
    "Лёгкий": {"icon": "🟢", "description": "Базовые вопросы", "style": "простые вопросы", "level": 1},
    "Средний": {"icon": "🟡", "description": "Средний уровень", "style": "вопросы среднего уровня", "level": 2},
    "Хардкор": {"icon": "🔴", "description": "Сложные вопросы", "style": "сложные вопросы", "level": 3}
}

# Типы тестов
TEST_TYPES = {
    "with_options": {"name": "С вариантами ответов", "icon": "📝", "description": "Выберите правильный вариант из предложенных"},
    "without_options": {"name": "Без вариантов ответов", "icon": "✍️", "description": "Введите ответ самостоятельно"}
}

# Стикеры для предметов
SUBJECT_DATA = {
    "Алгебра": {"emojis": "🔢➕➖✖️➗", "comments": ["Икс найден! 🕵️", "Формулы покорены! 💪"]},
    "Геометрия": {"emojis": "📐📏🔺⬜", "comments": ["Теорема доказана! 👑", "Углы покорены! 🔺"]},
    "Физика": {"emojis": "⚡🔬🌊🚀", "comments": ["Ньютон гордится! 🍎", "Законы соблюдены! ⚡"]}
}

class TestingManager:
    """Менеджер тестирования"""
    
    def __init__(self):
        self.SUBJECTS_STRUCTURE = topics.SUBJECTS_STRUCTURE
        self.generator = generator_manager  # Используем новый GeneratorManager
    
    @trace
    def _get_difficulty_level(self, difficulty: str) -> int:
        """Преобразование названия сложности в числовой уровень для генератора"""
        return DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS["Средний"]).get("level", 2)
    
    @trace
    def init_testing_session(self):
        """Инициализация сессии тестирования"""
        try:
            if 'testing_state' not in flask_session:
                flask_session['testing_state'] = {
                    'current_page': 'subjects', 'selected_subject': None,
                    'selected_section': None, 'selected_topic': None,
                    'selected_difficulty': None, 'current_test': None,
                    'user_answers': {}, 'test_results': None, 'current_question': 0,
                    # Новые настройки
                    'test_type': 'with_options',  # 'with_options' или 'without_options'
                    'num_questions': DEFAULT_NUM_QUESTIONS
                }
        except Exception:
            pass
    
    @trace
    def show_testing_interface(self) -> Dict[str, Any]:
        """Главный интерфейс"""
        self.init_testing_session()
        state = flask_session.get('testing_state', {})
        return {
            'current_page': state.get('current_page', 'subjects'),
            'selected_subject': state.get('selected_subject'),
            'selected_section': state.get('selected_section'),
            'selected_topic': state.get('selected_topic'),
            'selected_difficulty': state.get('selected_difficulty'),
            'test_type': state.get('test_type', 'with_options'),
            'num_questions': state.get('num_questions', DEFAULT_NUM_QUESTIONS),
            'subjects': self.SUBJECTS_STRUCTURE,
            'test_types': TEST_TYPES,
            'min_questions': MIN_QUESTIONS,
            'max_questions': MAX_QUESTIONS
        }
    
    @trace
    def navigate_back(self):
        """Навигация назад"""
        self.init_testing_session()
        state = flask_session.get('testing_state', {})
        
        nav_map = {
            'results': ('difficulty', {'test_results': None, 'user_answers': {}, 'current_test': None}),
            'difficulty': ('topics', {'selected_difficulty': None}),
            'topics': ('sections', {'selected_topic': None}),
            'sections': ('subjects', {'selected_section': None})
        }
        
        if state['current_page'] in nav_map:
            new_page, updates = nav_map[state['current_page']]
            state['current_page'] = new_page
            state.update(updates)
    
    @trace
    def show_subjects(self) -> Dict[str, Any]:
        """Список предметов"""
        self.init_testing_session()
        return {'subjects': list(self.SUBJECTS_STRUCTURE.keys()), 'subjects_structure': self.SUBJECTS_STRUCTURE}
    
    @trace
    def show_sections(self, subject: str = None) -> Dict[str, Any]:
        """Разделы предмета"""
        if not subject:
            self.init_testing_session()
            subject = flask_session.get('testing_state', {}).get('selected_subject')
        
        if not subject or subject not in self.SUBJECTS_STRUCTURE:
            return {'error': f'Предмет "{subject}" не найден'}
        
        return {
            'subject': subject,
            'icon': self.SUBJECTS_STRUCTURE[subject]["icon"],
            'sections': self.SUBJECTS_STRUCTURE[subject]["sections"]
        }
    
    @trace
    def show_topics(self, subject: str = None, section: str = None) -> Dict[str, Any]:
        """Темы раздела"""
        if not subject or not section:
            self.init_testing_session()
            state = flask_session.get('testing_state', {})
            subject = subject or state.get('selected_subject')
            section = section or state.get('selected_section')
        
        if not subject or not section:
            return {'error': 'Предмет или раздел не выбран'}
        if subject not in self.SUBJECTS_STRUCTURE:
            return {'error': f'Предмет "{subject}" не найден'}
        if section not in self.SUBJECTS_STRUCTURE[subject]["sections"]:
            return {'error': f'Раздел "{section}" не найден'}
        
        return {
            'subject': subject, 'section': section,
            'icon': self.SUBJECTS_STRUCTURE[subject]["icon"],
            'topics': self.SUBJECTS_STRUCTURE[subject]["sections"][section]["topics"]
        }
    
    @trace
    def show_difficulty_selection(self) -> Dict[str, Any]:
        """Выбор сложности и настроек теста"""
        self.init_testing_session()
        state = flask_session.get('testing_state', {})
        subject = state.get('selected_subject')
        topic = state.get('selected_topic')
        
        if not all([subject, state.get('selected_section'), topic]):
            state['current_page'] = 'subjects'
            return {'error': 'Не все параметры выбраны'}
        
        return {
            'subject': subject,
            'section': state.get('selected_section'),
            'topic': topic,
            'icon': self.SUBJECTS_STRUCTURE[subject]["icon"],
            'difficulty_levels': DIFFICULTY_LEVELS,
            'test_types': TEST_TYPES,
            'current_test_type': state.get('test_type', 'with_options'),
            'current_num_questions': state.get('num_questions', DEFAULT_NUM_QUESTIONS),
            'min_questions': MIN_QUESTIONS,
            'max_questions': MAX_QUESTIONS
        }
    
    @trace
    def set_test_settings(self, test_type: str, num_questions: int) -> Dict[str, Any]:
        """Установка настроек теста"""
        self.init_testing_session()
        state = flask_session.get('testing_state', {})
        
        # Валидация типа теста
        if test_type not in TEST_TYPES:
            test_type = 'with_options'
        
        # Валидация количества вопросов
        num_questions = max(MIN_QUESTIONS, min(MAX_QUESTIONS, int(num_questions)))
        
        state['test_type'] = test_type
        state['num_questions'] = num_questions
        flask_session['testing_state'] = state
        flask_session.modified = True
        
        return {
            'success': True,
            'test_type': test_type,
            'num_questions': num_questions
        }
    
    @trace
    def generate_test(self, subject: str, section: str, topic: str, difficulty: str, 
                      test_type: str = None, num_questions: int = None) -> Optional[Dict[str, Any]]:
        """Генерация теста через GeneratorManager"""
        try:
            self.init_testing_session()
            state = flask_session.get('testing_state', {})
            
            # Используем переданные параметры или из сессии
            if test_type is None:
                test_type = state.get('test_type', 'with_options')
            if num_questions is None:
                num_questions = state.get('num_questions', DEFAULT_NUM_QUESTIONS)
            
            # Валидация
            num_questions = max(MIN_QUESTIONS, min(MAX_QUESTIONS, int(num_questions)))
            with_options = test_type == 'with_options'
            difficulty_level = self._get_difficulty_level(difficulty)
            
            # Используем GeneratorManager для генерации теста
            result = self.generator.generate_test(
                subject=subject,
                section=section,
                topic=topic,
                difficulty=difficulty_level,
                num_questions=num_questions,
                with_options=with_options
            )
            
            if result and result.get("questions"):
                return result
            
            # Fallback на локальную генерацию
            return self._generate_local_test(subject, section, topic, difficulty, num_questions, with_options)
                
        except LlmAccessError as e:
            print(f"[ERROR] Проблема доступа к LLM: {e}")
            return {'error': e.user_message, 'questions': []}
        except Exception as e:
            return self._generate_local_test(subject, section, topic, difficulty, 
                                             num_questions or DEFAULT_NUM_QUESTIONS, 
                                             test_type != 'without_options')
    
    @trace
    def _generate_local_test(self, subject: str, section: str, topic: str, difficulty: str,
                             num_questions: int = DEFAULT_NUM_QUESTIONS,
                             with_options: bool = True) -> Dict:
        """Локальная генерация теста (fallback)"""
        local_tests = {
            "Линейные уравнения": [
                {"question": "Решите: 2x + 5 = 11", "options": ["x = 3", "x = 8", "x = -3", "x = 16"], "correct_answer": "x = 3"},
                {"question": "Коэффициент при x в 3x - 7 = 0?", "options": ["3", "-7", "0", "10"], "correct_answer": "3"},
                {"question": "Решите: x/2 = 6", "options": ["x = 3", "x = 12", "x = 8", "x = 4"], "correct_answer": "x = 12"},
                {"question": "Решений 0x + 5 = 5?", "options": ["Одно", "Два", "Бесконечно много", "Ни одного"], "correct_answer": "Бесконечно много"},
                {"question": "x при ax + b = 0?", "options": ["x = -b/a", "x = b/a", "x = a/b", "x = -a/b"], "correct_answer": "x = -b/a"},
                {"question": "Решите: 5x - 3 = 12", "options": ["x = 3", "x = 9", "x = 15", "x = 2"], "correct_answer": "x = 3"},
                {"question": "Решите: -2x = 8", "options": ["x = 4", "x = -4", "x = 16", "x = -16"], "correct_answer": "x = -4"},
            ],
            "Логарифмические уравнения": [
                {"question": "Решите: log₂(x) = 3", "options": ["x = 8", "x = 6", "x = 9", "x = 3"], "correct_answer": "x = 8"},
                {"question": "Решите: log₃(x) = 2", "options": ["x = 9", "x = 6", "x = 8", "x = 5"], "correct_answer": "x = 9"},
                {"question": "Решите: log₅(25) = x", "options": ["x = 2", "x = 5", "x = 25", "x = 10"], "correct_answer": "x = 2"},
                {"question": "Решите: log₁₀(100) = x", "options": ["x = 2", "x = 10", "x = 100", "x = 1"], "correct_answer": "x = 2"},
                {"question": "Решите: log₂(x) = 0", "options": ["x = 1", "x = 0", "x = 2", "x = -1"], "correct_answer": "x = 1"},
                {"question": "Решите: log₄(16) = x", "options": ["x = 2", "x = 4", "x = 8", "x = 1"], "correct_answer": "x = 2"},
                {"question": "Решите: log₃(27) = x", "options": ["x = 3", "x = 9", "x = 27", "x = 1"], "correct_answer": "x = 3"},
                {"question": "Чему равен ln(e)?", "options": ["1", "e", "0", "2"], "correct_answer": "1"},
                {"question": "Решите: log₂(8) + log₂(4) = x", "options": ["x = 5", "x = 7", "x = 12", "x = 32"], "correct_answer": "x = 5"},
                {"question": "Решите: log₅(x) = 1", "options": ["x = 5", "x = 1", "x = 0", "x = 25"], "correct_answer": "x = 5"},
            ],
            "Показательные уравнения": [
                {"question": "Решите: 2ˣ = 8", "options": ["x = 3", "x = 4", "x = 2", "x = 8"], "correct_answer": "x = 3"},
                {"question": "Решите: 3ˣ = 27", "options": ["x = 3", "x = 9", "x = 27", "x = 2"], "correct_answer": "x = 3"},
                {"question": "Решите: 5ˣ = 25", "options": ["x = 2", "x = 5", "x = 25", "x = 1"], "correct_answer": "x = 2"},
                {"question": "Решите: 4ˣ = 16", "options": ["x = 2", "x = 4", "x = 8", "x = 1"], "correct_answer": "x = 2"},
                {"question": "Решите: 10ˣ = 100", "options": ["x = 2", "x = 10", "x = 100", "x = 1"], "correct_answer": "x = 2"},
                {"question": "Решите: 2ˣ = 1", "options": ["x = 0", "x = 1", "x = 2", "x = -1"], "correct_answer": "x = 0"},
                {"question": "Решите: eˣ = 1", "options": ["x = 0", "x = 1", "x = e", "x = -1"], "correct_answer": "x = 0"},
            ],
            "Квадратные уравнения": [
                {"question": "Решите: x² - 4 = 0", "options": ["x = ±2", "x = 4", "x = -4", "x = 2"], "correct_answer": "x = ±2"},
                {"question": "Дискриминант x² - 5x + 6 = 0:", "options": ["1", "25", "6", "-11"], "correct_answer": "1"},
                {"question": "Сумма корней x² - 7x + 12 = 0:", "options": ["7", "12", "-7", "3"], "correct_answer": "7"},
                {"question": "Произведение корней x² + 3x - 10 = 0:", "options": ["-10", "10", "3", "-3"], "correct_answer": "-10"},
                {"question": "Решите: x² = 9", "options": ["x = ±3", "x = 3", "x = 9", "x = 81"], "correct_answer": "x = ±3"},
            ],
            "Треугольники": [
                {"question": "Сумма углов треугольника?", "options": ["90°", "180°", "270°", "360°"], "correct_answer": "180°"},
                {"question": "Треугольник с равными сторонами?", "options": ["Равнобедренный", "Прямоугольный", "Равносторонний", "Тупоугольный"], "correct_answer": "Равносторонний"},
                {"question": "Площадь треугольника?", "options": ["S = a×h", "S = (1/2)×a×h", "S = a²", "S = 2×a×h"], "correct_answer": "S = (1/2)×a×h"},
                {"question": "Неравенство сторон?", "options": ["a + b = c", "a + b < c", "a + b > c", "a = b = c"], "correct_answer": "a + b > c"},
                {"question": "Треугольник с углом 90°?", "options": ["Острый", "Тупой", "Прямоугольный", "Равнобедренный"], "correct_answer": "Прямоугольный"}
            ],
            "Кинематика": [
                {"question": "Формула пути?", "options": ["S = v × t", "S = v / t", "S = v + t", "S = v - t"], "correct_answer": "S = v × t"},
                {"question": "Единица скорости в СИ?", "options": ["м/с", "км/ч", "м/мин", "см/с"], "correct_answer": "м/с"},
                {"question": "Ускорение характеризует?", "options": ["Изменение скорости", "Путь", "Положение", "Массу"], "correct_answer": "Изменение скорости"},
                {"question": "При равномерном движении скорость?", "options": ["Постоянна", "Возрастает", "Убывает", "Равна нулю"], "correct_answer": "Постоянна"},
                {"question": "Путь при равноускоренном движении?", "options": ["S = v₀t + at²/2", "S = vt", "S = at", "S = v/t"], "correct_answer": "S = v₀t + at²/2"}
            ]
        }
        
        questions = []
        
        if topic in local_tests:
            base_questions = local_tests[topic]
            # Повторяем вопросы если нужно больше чем есть
            while len(questions) < num_questions:
                for q in base_questions:
                    if len(questions) >= num_questions:
                        break
                    question = {
                        "question": q["question"],
                        "correct_answer": q["correct_answer"]
                    }
                    if with_options and "options" in q:
                        question["options"] = q["options"]
                    questions.append(question)
        else:
        # Генерируем заглушку
            for i in range(num_questions):
                question = {
                    "question": f"Вопрос {i+1} по теме '{topic}'",
                    "correct_answer": "А"
                }
                if with_options:
                    question["options"] = ["А", "Б", "В", "Г"]
                questions.append(question)
        
        return {
            "questions": questions[:num_questions],
            "generator": "local",
            "test_type": "with_options" if with_options else "without_options"
        }
    
    @trace
    def _normalize_answer(self, answer: str) -> str:
        """Нормализация ответа для сравнения"""
        if not answer:
            return ""
        # Убираем лишние пробелы, приводим к нижнему регистру
        normalized = answer.strip().lower()
        # Убираем пробелы вокруг знаков
        normalized = re.sub(r'\s*([=<>±])\s*', r'\1', normalized)
        # Убираем "x =" в начале если есть
        normalized = re.sub(r'^x\s*=\s*', '', normalized)
        return normalized
    
    @trace
    def _compare_answers(self, user_answer: str, correct_answer: str) -> bool:
        """Сравнение ответов с учётом разных форматов"""
        user_norm = self._normalize_answer(user_answer)
        correct_norm = self._normalize_answer(correct_answer)
        
        # Прямое сравнение
        if user_norm == correct_norm:
            return True
        
        # Для числовых ответов
        try:
            user_nums = re.findall(r'-?\d+\.?\d*', user_norm)
            correct_nums = re.findall(r'-?\d+\.?\d*', correct_norm)
            
            if user_nums and correct_nums:
                # Сравниваем числа
                user_floats = sorted([float(n) for n in user_nums])
                correct_floats = sorted([float(n) for n in correct_nums])
                if user_floats == correct_floats:
                    return True
        except Exception:
            pass
        
        return False
    
    @trace
    def calculate_results(self) -> Optional[Dict[str, Any]]:
        """Подсчёт результатов"""
        try:
            self.init_testing_session()
            state = flask_session.get('testing_state', {})
            test = state.get('current_test')
            answers = state.get('user_answers', {})
            test_type = test.get('test_type', 'with_options') if test else 'with_options'
            
            if not test:
                return None
            
            questions = test['questions']
            
            # Подсчёт правильных ответов
            correct = 0
            detailed_results = []
            
            for i, q in enumerate(questions):
                # Проверяем оба варианта ключа (строковый и целочисленный)
                user_answer = answers.get(str(i), answers.get(i, ""))
                correct_answer = q['correct_answer']
                
                # Для тестов с вариантами - точное сравнение, без вариантов - нормализованное
                if test_type == 'with_options':
                    is_correct = user_answer == correct_answer
                else:
                    is_correct = self._compare_answers(user_answer, correct_answer)
                
                if is_correct:
                    correct += 1
                
                detailed_results.append({
                    'question': q['question'],
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_correct': is_correct
                })
            
            total = len(questions)
            pct = (correct / total) * 100 if total else 0
            
            # Оценка
            grades = [
                (90, "Отлично", "🏆", "Невероятно! Вы мастер!", "🎉🎊✨🌟💫"),
                (70, "Хорошо", "👍", "Отлично справились!", "👏🎈🌟💪"),
                (50, "Удовлетворительно", "👌", "Неплохо! Есть база!", "🌱💪📖"),
                (0, "Нужно подучить", "📚", "Не расстраивайтесь!", "💪🌟📚🚀")
            ]
            
            for threshold, grade, icon, msg, emojis in grades:
                if pct >= threshold:
                    break
            
            results = {
                'correct_count': correct, 'total_questions': total, 'percentage': pct,
                'grade': grade, 'grade_icon': icon, 'congratulations': msg,
                'celebration_emojis': emojis,
                'detailed_results': detailed_results,
                'test_type': test_type
            }
            
            state['test_results'] = results
            flask_session['testing_state'] = state
            flask_session.modified = True
            return results
        except Exception as e:
            return None
    
    @trace
    def get_funny_comment(self, subject: str) -> str:
        """Смешной комментарий для предмета"""
        data = SUBJECT_DATA.get(subject, {"comments": ["Отлично! 🎉"]})
        return random.choice(data["comments"])
    
    @trace
    def show_celebration(self, subject: str, percentage: float) -> Dict[str, Any]:
        """Данные для празднования"""
        data = SUBJECT_DATA.get(subject, {"emojis": "🎉✨", "comments": ["Молодец!"]})
        
        types = [(90, 'excellent', '🏆🎉🌟'), (70, 'good', '🌟👍💪'),
                (50, 'average', '🌱💪📚'), (0, 'low', '💪🌟📚🚀')]
        
        for threshold, t, stickers in types:
            if percentage >= threshold:
                break
        
        return {
            'animation_emojis': data['emojis'],
            'comment': random.choice(data['comments']),
            'grade_percentage': percentage,
            'type': t,
            'stickers': stickers
        }


# Экземпляр менеджера
testing_manager = TestingManager()
