"""
Модуль управления системой тестирования.
Использует DLL генератор для математики и LLM для других предметов.
"""

from flask import session as flask_session
import json
import random
import socket
from typing import Optional, Dict, List, Any
from bot.settings import OPENAI_API_KEY
from bot.theory import TheoryManager
from langchain_ollama import OllamaLLM


# Константы
DEFAULT_MODEL = "deepseek-r1:7b"
FALLBACK_MODEL = "deepseek:7b"
OLLAMA_PORT = 11434
OLLAMA_HOST = "localhost"
NUM_QUESTIONS = 5

# Уровни сложности
DIFFICULTY_LEVELS = {
    "Лёгкий": {"icon": "🟢", "description": "Базовые вопросы", "style": "простые вопросы"},
    "Средний": {"icon": "🟡", "description": "Средний уровень", "style": "вопросы среднего уровня"},
    "Хардкор": {"icon": "🔴", "description": "Сложные вопросы", "style": "сложные вопросы"}
}

# Стикеры для предметов (сокращённо)
SUBJECT_DATA = {
    "Алгебра": {"emojis": "🔢➕➖✖️➗", "comments": ["Икс найден! 🕵️", "Формулы покорены! 💪"]},
    "Геометрия": {"emojis": "📐📏🔺⬜", "comments": ["Теорема доказана! 👑", "Углы покорены! 🔺"]},
    "Физика": {"emojis": "⚡🔬🌊🚀", "comments": ["Ньютон гордится! 🍎", "Законы соблюдены! ⚡"]},
    "Химия": {"emojis": "🧪⚗️🔬💎", "comments": ["Реакция успешна! 💥", "Менделеев доволен! 👏"]},
    "Биология": {"emojis": "🧬🔬🌱🦋", "comments": ["Дарвин восхищён! 🐒", "ДНК расшифрована! 🧬"]},
    "География": {"emojis": "🌍🗺️🏔️🌊", "comments": ["Континенты найдены! 🗺️", "GPS не нужен! 🧭"]},
    "История": {"emojis": "🏛️👑⚔️📜", "comments": ["История покорена! 👑", "Эпохи изучены! ⏳"]},
    "Обществознание": {"emojis": "👥🏛️⚖️🗳️", "comments": ["Общество понято! 👥", "Социум под контролем! 🌐"]},
    "Русский язык": {"emojis": "📝📚✒️📖", "comments": ["Пушкин аплодирует! 👏", "Грамматика покорена! ✍️"]},
    "Английский язык": {"emojis": "🇬🇧🇺🇸💬📖", "comments": ["English conquered! 🎭", "Welcome to the club! 🎉"]},
    "Информатика": {"emojis": "💻🖥️⌨️🤖", "comments": ["Код работает! 🐛❌", "Алгоритм оптимизирован! 🔥"]}
}


class TestingManager:
    """Менеджер тестирования"""
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.theory_manager = TheoryManager()
        self.SUBJECTS_STRUCTURE = self.theory_manager.SUBJECTS_STRUCTURE
        self.ollama_client = None
        self.math_generator = None
        
        self._init_ollama()
        self._init_math_generator()
    
    def _check_ollama(self) -> bool:
        """Проверка Ollama сервера"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((OLLAMA_HOST, OLLAMA_PORT))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def _init_ollama(self):
        """Инициализация Ollama"""
        if not self._check_ollama():
            print("Ollama недоступен, тесты будут генерироваться локально")
            return
        
        try:
            self.ollama_client = OllamaLLM(model=DEFAULT_MODEL, temperature=0.7, reasoning=False)
            print(f"✓ Ollama: {DEFAULT_MODEL}")
        except Exception as e:
            try:
                self.ollama_client = OllamaLLM(model=FALLBACK_MODEL, temperature=0.7)
                print(f"✓ Ollama fallback: {FALLBACK_MODEL}")
            except Exception:
                print(f"✗ Ollama недоступен: {e}")
    
    def _init_math_generator(self):
        """Инициализация математического генератора"""
        try:
            from math_generator import get_math_generator
            self.math_generator = get_math_generator()
            status = "DLL + Python" if self.math_generator.dll_available else "Python"
            print(f"✓ Математический генератор: {status}")
        except Exception as e:
            print(f"✗ Математический генератор: {e}")
    
    def init_session(self):
        """Инициализация сессии"""
        try:
            if 'testing_state' not in flask_session:
                flask_session['testing_state'] = {
                    'current_page': 'subjects', 'selected_subject': None,
                    'selected_section': None, 'selected_topic': None,
                    'selected_difficulty': None, 'current_test': None,
                    'user_answers': {}, 'test_results': None, 'current_question': 0
                }
        except Exception as e:
            print(f"Ошибка инициализации сессии: {e}")
    
    def show_testing_interface(self) -> Dict[str, Any]:
        """Главный интерфейс"""
        self.init_session()
        state = flask_session.get('testing_state', {})
        return {
            'current_page': state.get('current_page', 'subjects'),
            'selected_subject': state.get('selected_subject'),
            'selected_section': state.get('selected_section'),
            'selected_topic': state.get('selected_topic'),
            'selected_difficulty': state.get('selected_difficulty'),
            'subjects': self.SUBJECTS_STRUCTURE
        }
    
    def navigate_back(self):
        """Навигация назад"""
        self.init_session()
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
    
    def show_subjects(self) -> Dict[str, Any]:
        """Список предметов"""
        self.init_session()
        return {'subjects': list(self.SUBJECTS_STRUCTURE.keys()), 'subjects_structure': self.SUBJECTS_STRUCTURE}
    
    def show_sections(self, subject: str = None) -> Dict[str, Any]:
        """Разделы предмета"""
        if not subject:
            self.init_session()
            subject = flask_session.get('testing_state', {}).get('selected_subject')
        
        if not subject or subject not in self.SUBJECTS_STRUCTURE:
            return {'error': f'Предмет "{subject}" не найден'}
        
        return {
            'subject': subject,
            'icon': self.SUBJECTS_STRUCTURE[subject]["icon"],
            'sections': self.SUBJECTS_STRUCTURE[subject]["sections"]
        }
    
    def show_topics(self, subject: str = None, section: str = None) -> Dict[str, Any]:
        """Темы раздела"""
        if not subject or not section:
            self.init_session()
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
    
    def show_difficulty_selection(self) -> Dict[str, Any]:
        """Выбор сложности"""
        self.init_session()
        state = flask_session.get('testing_state', {})
        subject = state.get('selected_subject')
        
        if not all([subject, state.get('selected_section'), state.get('selected_topic')]):
            state['current_page'] = 'subjects'
            return {'error': 'Не все параметры выбраны'}
        
        return {
            'subject': subject,
            'section': state.get('selected_section'),
            'topic': state.get('selected_topic'),
            'icon': self.SUBJECTS_STRUCTURE[subject]["icon"],
            'difficulty_levels': DIFFICULTY_LEVELS
        }
    
    def generate_test(self, subject: str, section: str, topic: str, difficulty: str) -> Optional[Dict[str, Any]]:
        """Генерация теста"""
        try:
            print(f"Генерация теста: {subject} -> {section} -> {topic} [{difficulty}]")
            
            # Математика - используем DLL генератор
            if subject in ["Алгебра", "Математика"] and self.math_generator:
                return self._generate_math_test(topic, difficulty)
            
            # Другие предметы - LLM или локальные
            if self.ollama_client:
                return self._generate_llm_test(subject, section, topic, difficulty)
            
            return self._generate_local_test(subject, section, topic, difficulty)
        except Exception as e:
            print(f"Ошибка генерации теста: {e}")
            return self._generate_local_test(subject, section, topic, difficulty)
    
    def _generate_math_test(self, topic: str, difficulty: str) -> Dict[str, Any]:
        """Тест по математике через DLL генератор"""
        questions = []
        
        if self.math_generator and self.math_generator.is_topic_supported(topic):
            for _ in range(NUM_QUESTIONS):
                problem = self.math_generator.generate_problem_by_topic(topic, difficulty)
                if problem:
                    options = self._generate_options(problem['correct_answer'])
                    questions.append({
                        "question": problem['question'],
                        "options": options,
                        "correct_answer": problem['correct_answer']
                    })
        
        # Дополняем LLM или локальными вопросами
        while len(questions) < NUM_QUESTIONS:
            local = self._get_local_math_question(topic)
            if local:
                questions.append(local)
            else:
                break
        
        return {"questions": questions[:NUM_QUESTIONS]}
    
    def _generate_options(self, correct: str) -> List[str]:
        """Генерация вариантов ответов"""
        import re
        options = [correct]
        numbers = re.findall(r'-?\d+\.?\d*', correct)
        
        if numbers:
            base = float(numbers[0])
            variants = [base + random.randint(1, 3), base - random.randint(1, 3),
                       base * 2 if abs(base) < 10 else base + 5]
            
            for v in variants:
                v_str = str(int(v)) if v == int(v) else str(round(v, 2))
                new_opt = correct.replace(str(numbers[0]), v_str)
                if new_opt not in options:
                    options.append(new_opt)
        
        while len(options) < 4:
            options.append(f"x = {random.randint(-10, 10)}")
        
        random.shuffle(options)
        return options[:4]
    
    def _generate_llm_test(self, subject: str, section: str, topic: str, difficulty: str) -> Optional[Dict]:
        """Генерация через LLM"""
        try:
            diff_info = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS["Средний"])
            
            prompt = f"""Ты преподаватель {subject.lower()}а. Создай {NUM_QUESTIONS} вопросов по теме "{topic}" ({section}).
Сложность: {difficulty} ({diff_info['style']}).

Ответь СТРОГО в JSON:
{{"questions": [{{"question": "Текст", "options": ["A", "B", "C", "D"], "correct_answer": "A"}}]}}

Вопросы на русском. Только JSON."""
            
            response = self.ollama_client.invoke(prompt).strip()
            
            # Очистка markdown
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            if "questions" in data:
                return data
        except Exception as e:
            print(f"Ошибка LLM: {e}")
        
        return self._generate_local_test(subject, section, topic, difficulty)
    
    def _get_local_math_question(self, topic: str) -> Optional[Dict]:
        """Локальные математические вопросы"""
        questions = {
            "Линейные уравнения": [
                {"question": "Решите: 2x + 5 = 11", "options": ["x = 3", "x = 8", "x = -3", "x = 16"], "correct_answer": "x = 3"},
                {"question": "Решите: x/2 = 6", "options": ["x = 3", "x = 12", "x = 8", "x = 4"], "correct_answer": "x = 12"}
            ],
            "Квадратные уравнения": [
                {"question": "Решите: x² - 4 = 0", "options": ["x = ±2", "x = 4", "x = -4", "x = 2"], "correct_answer": "x = ±2"},
                {"question": "Дискриминант x² - 5x + 6 = 0:", "options": ["1", "25", "6", "-11"], "correct_answer": "1"}
            ]
        }
        return random.choice(questions.get(topic, [])) if topic in questions else None
    
    def _generate_local_test(self, subject: str, section: str, topic: str, difficulty: str) -> Dict:
        """Локальная генерация теста (fallback)"""
        local_tests = {
            "Линейные уравнения": [
                {"question": "Решите: 2x + 5 = 11", "options": ["x = 3", "x = 8", "x = -3", "x = 16"], "correct_answer": "x = 3"},
                {"question": "Коэффициент при x в 3x - 7 = 0?", "options": ["3", "-7", "0", "10"], "correct_answer": "3"},
                {"question": "Решите: x/2 = 6", "options": ["x = 3", "x = 12", "x = 8", "x = 4"], "correct_answer": "x = 12"},
                {"question": "Решений 0x + 5 = 5?", "options": ["Одно", "Два", "Бесконечно много", "Ни одного"], "correct_answer": "Бесконечно много"},
                {"question": "x при ax + b = 0?", "options": ["x = -b/a", "x = b/a", "x = a/b", "x = -a/b"], "correct_answer": "x = -b/a"}
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
        
        if topic in local_tests:
            return {"questions": local_tests[topic][:NUM_QUESTIONS]}
        
        # Генерируем заглушку
        return {"questions": [
            {"question": f"Вопрос {i+1} по теме '{topic}'", 
             "options": ["А", "Б", "В", "Г"], "correct_answer": "А"}
            for i in range(NUM_QUESTIONS)
        ]}
    
    def calculate_results(self) -> Optional[Dict[str, Any]]:
        """Подсчёт результатов"""
        try:
            self.init_session()
            state = flask_session.get('testing_state', {})
            test = state.get('current_test')
            answers = state.get('user_answers', {})
            
            if not test:
                return None
            
            questions = test['questions']
            correct = sum(1 for i, q in enumerate(questions) if answers.get(i) == q['correct_answer'])
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
                'detailed_results': [
                    {'question': q['question'], 'user_answer': answers.get(i, ""),
                     'correct_answer': q['correct_answer'], 'is_correct': answers.get(i) == q['correct_answer']}
                    for i, q in enumerate(questions)
                ]
            }
            
            state['test_results'] = results
            return results
        except Exception as e:
            print(f"Ошибка подсчёта: {e}")
            return None
    
    def get_funny_comment(self, subject: str) -> str:
        """Смешной комментарий для предмета"""
        data = SUBJECT_DATA.get(subject, {"comments": ["Отлично! 🎉"]})
        return random.choice(data["comments"])
    
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
