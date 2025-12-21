"""
Модуль управления теоретическими материалами.
Использует LLM (deepseek-r1:7b) для генерации объяснений.
"""

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import session as flask_session
import re
import socket
from pathlib import Path
from typing import Optional, Dict, Any
from bot.settings import OPENAI_API_KEY
from langchain_ollama import OllamaLLM
from bot import topics
from logger import console

PYTHON_FILENAME = "theory"

# Константы
DEFAULT_MODEL = "deepseek-r1:7b"
FALLBACK_MODEL = "deepseek:7b"
OPENAI_MODEL = "gpt-4o-mini"
OLLAMA_PORT = 11434
OLLAMA_HOST = "localhost"

# Контексты для предметов
SUBJECT_CONTEXTS = {
    "Алгебра": {"style": "математический", "focus": "формулы и уравнения", "examples": "числовые примеры"},
    "Геометрия": {"style": "геометрический", "focus": "теоремы и свойства фигур", "examples": "задачи с чертежами"},
    "Физика": {"style": "научный", "focus": "законы физики", "examples": "примеры из жизни"},
    "Химия": {"style": "химический", "focus": "реакции и свойства веществ", "examples": "лабораторные примеры"},
    "Биология": {"style": "биологический", "focus": "живые организмы", "examples": "примеры из природы"},
    "География": {"style": "географический", "focus": "страны и климат", "examples": "реальные объекты"},
    "История": {"style": "исторический", "focus": "события и даты", "examples": "исторические факты"},
    "Обществознание": {"style": "социальный", "focus": "общество и политика", "examples": "современные явления"},
    "Русский язык": {"style": "лингвистический", "focus": "правила языка", "examples": "примеры из литературы"},
    "Английский язык": {"style": "языковой", "focus": "грамматика и лексика", "examples": "диалоги и тексты"},
    "Информатика": {"style": "технический", "focus": "алгоритмы и программирование", "examples": "примеры кода"}
}


@console.debug(PYTHON_FILENAME)
def check_ollama() -> bool:
    """Проверка Ollama сервера"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((OLLAMA_HOST, OLLAMA_PORT))
        sock.close()
        is_available = result == 0
        if not is_available:
            print(f"[WARNING] Ollama сервер недоступен на {OLLAMA_HOST}:{OLLAMA_PORT}. Запустите: ollama serve")
        return is_available
    except Exception as e:
        print(f"[WARNING] Ошибка проверки Ollama: {e}")
        return False


class TheoryManager:
    """Менеджер теоретических материалов"""
    
    CURSOR_VARIANTS = ["▌", "▋", "▊", "▉", "█", "▐", "▎", "▍"]
    
    @console.debug(PYTHON_FILENAME)
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.SUBJECTS_STRUCTURE = topics.SUBJECTS_STRUCTURE
        self.ollama_client = None
        self.openai_client = None
        self.chatbot_llm = None
        
        # Пробуем использовать LLM из chatbot, если он доступен (ленивая загрузка)
        self._chatbot_llm_loaded = False
        
        self._init_ollama(model_name or DEFAULT_MODEL)
        self._init_session()
    
    @console.debug(PYTHON_FILENAME)
    def _init_ollama(self, model_name: str):
        """Инициализация Ollama"""
        # Пробуем инициализировать даже если сервер недоступен (может подключиться позже)
        try:
            kwargs = {"model": model_name, "temperature": 0.0, "num_thread": 1}
            if 'deepseek-r1' in model_name.lower():
                kwargs['reasoning'] = False
            
            self.ollama_client = OllamaLLM(**kwargs)
            if check_ollama():
                print(f"[SUCCESS] ✓ Ollama: {model_name} (сервер доступен и готов к работе)")
            else:
                print(f"[WARNING] ⚠ Ollama: {model_name} (клиент создан, но сервер недоступен)")
                print(f"[INFO] Для запуска сервера выполните в отдельном терминале: ollama serve")
                print(f"[INFO] Убедитесь, что модель установлена: ollama pull {model_name}")
        except Exception as e:
            print(f"[ERROR] ✗ Ошибка инициализации Ollama: {e}")
            import traceback
            traceback.print_exc()
            self.ollama_client = None
    
    @console.debug(PYTHON_FILENAME)
    def _init_session(self):
        """Инициализация сессии"""
        try:
            if 'theory_state' not in flask_session:
                flask_session['theory_state'] = {
                    'current_page': 'subjects', 'selected_subject': None,
                    'selected_section': None, 'selected_topic': None,
                    'explanation_text': None, 'last_topic_key': None
                }
        except Exception:
            pass
    
    @console.debug(PYTHON_FILENAME)
    def init_theory_session(self):
        """Публичный метод инициализации сессии"""
        self._init_session()
    
    @console.debug(PYTHON_FILENAME)
    def _clean_text(self, text: str) -> str:
        """Очистка текста от курсоров и мусора"""
        if not text:
            return ""
        
        cleaned = str(text)
        for cursor in self.CURSOR_VARIANTS:
            cleaned = cleaned.replace(cursor, "")
        
        # Убираем блоки раздумий
        cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'<reasoning>.*?</reasoning>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        return cleaned.strip()
    
    @console.debug(PYTHON_FILENAME)
    def show_theory_interface(self) -> Dict[str, Any]:
        """Главный интерфейс"""
        self._init_session()
        state = flask_session.get('theory_state', {})
        return {
            'current_page': state.get('current_page', 'subjects'),
            'selected_subject': state.get('selected_subject'),
            'selected_section': state.get('selected_section'),
            'selected_topic': state.get('selected_topic'),
            'explanation_text': state.get('explanation_text'),
            'subjects': self.SUBJECTS_STRUCTURE
        }
    
    @console.debug(PYTHON_FILENAME)
    def show_navigation(self) -> Dict[str, Any]:
        """Навигация"""
        state = flask_session.get('theory_state', {})
        breadcrumbs = []
        
        if state.get('current_page') != 'subjects':
            breadcrumbs.append("Предметы")
        if state.get('selected_subject') and state.get('current_page') not in ['subjects', 'sections']:
            breadcrumbs.append(state['selected_subject'])
        if state.get('selected_section') and state.get('current_page') not in ['subjects', 'sections', 'topics']:
            breadcrumbs.append(state['selected_section'])
        if state.get('selected_topic'):
            breadcrumbs.append(state['selected_topic'])
        
        return {'breadcrumbs': breadcrumbs, 'state': state}
    
    @console.debug(PYTHON_FILENAME)
    def navigate_back(self):
        """Навигация назад"""
        state = flask_session.get('theory_state', {})
        
        nav_map = {
            'explanation': ('topics', {'selected_topic': None, 'explanation_text': None}),
            'topics': ('sections', {'selected_section': None}),
            'sections': ('subjects', {'selected_subject': None})
        }
        
        if state.get('current_page') in nav_map:
            new_page, updates = nav_map[state['current_page']]
            state['current_page'] = new_page
            state.update(updates)
    
    @console.debug(PYTHON_FILENAME)
    def show_subjects(self) -> Dict[str, Any]:
        """Список предметов"""
        return {'subjects': list(self.SUBJECTS_STRUCTURE.keys()), 'subjects_structure': self.SUBJECTS_STRUCTURE}
    
    @console.debug(PYTHON_FILENAME)
    def show_sections(self) -> Dict[str, Any]:
        """Разделы предмета"""
        state = flask_session.get('theory_state', {})
        subject = state.get('selected_subject')
        
        if not subject:
            return {'error': 'Предмет не выбран'}
        
        return {'subject': subject, 'sections': self.SUBJECTS_STRUCTURE.get(subject, {}).get('sections', {})}
    
    @console.debug(PYTHON_FILENAME)
    def show_topics(self) -> Dict[str, Any]:
        """Темы раздела"""
        state = flask_session.get('theory_state', {})
        subject = state.get('selected_subject')
        section = state.get('selected_section')
        
        if not subject or not section:
            return {'error': 'Предмет или раздел не выбран'}
        
        topics_list = self.SUBJECTS_STRUCTURE.get(subject, {}).get('sections', {}).get(section, {}).get('topics', [])
        return {'subject': subject, 'section': section, 'topics': topics_list}
    
    @console.debug(PYTHON_FILENAME)
    def show_explanation(self) -> Dict[str, Any]:
        """Объяснение темы"""
        state = flask_session.get('theory_state', {})
        subject = state.get('selected_subject')
        section = state.get('selected_section')
        topic = state.get('selected_topic')
        
        if not all([subject, section, topic]):
            state['current_page'] = 'subjects'
            return {'error': 'Не все параметры выбраны'}
        
        icon = self.SUBJECTS_STRUCTURE[subject]["icon"]
        
        # Проверяем смену темы
        topic_key = f"{subject}_{section}_{topic}"
        if topic_key != state.get('last_topic_key'):
            state['last_topic_key'] = topic_key
            state['explanation_text'] = None
        
        explanation = state.get('explanation_text')
        if explanation:
            explanation = self._clean_text(explanation)
        
        # Генерируем если нет
        if not explanation:
            try:
                explanation = self.get_topic_explanation(subject, section, topic)
                explanation = self._clean_text(explanation)
                if explanation and len(explanation) > 50:
                    state['explanation_text'] = explanation
                else:
                    raise Exception("Пустой ответ")
            except Exception as e:
                print(f"Ошибка генерации: {e}")
                explanation = self._get_error_message(subject, section, topic)
                state['explanation_text'] = explanation
        
        return {
            'subject': subject, 'section': section, 'topic': topic,
            'icon': icon, 'explanation_text': explanation
        }
    
    @console.debug(PYTHON_FILENAME)
    def _load_chatbot_llm(self):
        """Ленивая загрузка LLM из chatbot"""
        if self._chatbot_llm_loaded:
            return self.chatbot_llm is not None
        
        self._chatbot_llm_loaded = True
        try:
            from bot.chatbot import chatbot
            if chatbot and hasattr(chatbot, 'llm') and chatbot.llm:
                self.chatbot_llm = chatbot.llm
                print(f"[INFO] ✓ LLM из chatbot загружен: {type(chatbot.llm).__name__}")
                if hasattr(chatbot.llm, 'client'):
                    print(f"[INFO] LLM client доступен: {type(chatbot.llm.client).__name__}")
                return True
            else:
                print(f"[WARNING] LLM из chatbot недоступен: chatbot={chatbot is not None}, has_llm={hasattr(chatbot, 'llm') if chatbot else False}, llm={chatbot.llm if chatbot and hasattr(chatbot, 'llm') else None}")
        except Exception as e:
            print(f"[ERROR] Не удалось загрузить LLM из chatbot: {e}")
            import traceback
            traceback.print_exc()
        
        return False
    
    @console.debug(PYTHON_FILENAME)
    def get_topic_explanation(self, subject: str, section: str, topic: str, regenerate: bool = False) -> str:
        """Получение объяснения темы"""
        # Проверяем кэш
        if not regenerate:
            cached = self._get_cached(topic)
            if cached:
                print(f"[INFO] Использовано кэшированное объяснение для темы: {topic}")
                return cached
        
        print(f"[INFO] Генерация объяснения для темы: {topic} (предмет: {subject}, раздел: {section})")
        
        # Пробуем LLM из chatbot (ПРИОРИТЕТ #1)
        # НЕ проверяем доступность Ollama - пусть LLM сам попробует подключиться
        # Может быть сервер запустится или уже работает, но проверка его не видит
        if self._load_chatbot_llm() and self.chatbot_llm:
            print(f"[INFO] Попытка генерации через LLM из chatbot (deepseek-r1:7b)...")
            print(f"[DEBUG] LLM тип: {type(self.chatbot_llm).__name__}")
            if hasattr(self.chatbot_llm, 'client'):
                print(f"[DEBUG] LLM client тип: {type(self.chatbot_llm.client).__name__}")
            try:
                explanation = self._generate_with_chatbot_llm(subject, section, topic)
                if explanation and len(explanation.strip()) > 50:
                    print(f"[SUCCESS] Объяснение успешно сгенерировано через LLM из chatbot ({len(explanation)} символов)")
                    return explanation
                else:
                    print(f"[WARNING] LLM вернул слишком короткий ответ: {len(explanation) if explanation else 0} символов")
            except Exception as e:
                error_msg = str(e)
                print(f"[ERROR] Ошибка chatbot LLM: {error_msg}")
                # Проверяем, связана ли ошибка с недоступностью сервера
                if "connection" in error_msg.lower() or "refused" in error_msg.lower() or "unreachable" in error_msg.lower():
                    print(f"[WARNING] Похоже, Ollama сервер не запущен. Запустите: ollama serve")
                print(f"[INFO] Пробуем альтернативные методы...")
                import traceback
                traceback.print_exc()
                # Продолжаем к следующим методам
        else:
            print(f"[WARNING] LLM из chatbot недоступен")
            if not self._chatbot_llm_loaded:
                print(f"[INFO] Попытка загрузки LLM из chatbot...")
            elif not self.chatbot_llm:
                print(f"[INFO] LLM из chatbot не загружен (chatbot.llm = None)")
        
        # Пробуем Ollama напрямую (ПРИОРИТЕТ #2)
        # Проверяем доступность сервера перед использованием
        if check_ollama():
            if not self.ollama_client:
                # Пробуем переинициализировать, если сервер стал доступен
                print(f"[INFO] Ollama сервер стал доступен, переинициализируем клиент...")
                self._init_ollama(DEFAULT_MODEL)
            
            if self.ollama_client:
                print(f"[INFO] Попытка генерации через Ollama напрямую...")
                try:
                    explanation = self._generate_with_ollama(subject, section, topic)
                    if explanation and len(explanation.strip()) > 50:
                        print(f"[SUCCESS] Объяснение успешно сгенерировано через Ollama ({len(explanation)} символов)")
                        return explanation
                except Exception as e:
                    print(f"[ERROR] Ошибка Ollama: {e}")
                    import traceback
                    traceback.print_exc()
        else:
            print(f"[WARNING] Ollama сервер недоступен. Запустите 'ollama serve' в отдельном терминале")
        
        # Fallback на OpenAI (ПРИОРИТЕТ #3)
        if self.api_key:
            print(f"[INFO] Попытка генерации через OpenAI...")
            try:
                explanation = self._generate_with_openai(subject, section, topic)
                if explanation and len(explanation.strip()) > 50:
                    print(f"[SUCCESS] Объяснение успешно сгенерировано через OpenAI ({len(explanation)} символов)")
                    return explanation
            except Exception as e:
                print(f"[ERROR] Ошибка OpenAI: {e}")
                import traceback
                traceback.print_exc()
        
        # Локальные объяснения как последний fallback (только если LLM недоступен)
        print(f"[WARNING] Все LLM методы не сработали, пробуем локальные объяснения...")
        local_explanation = self._get_local_explanation(subject, section, topic)
        if local_explanation:
            print(f"[INFO] Использовано локальное объяснение для темы: {topic}")
            return local_explanation
        
        # Локальный кэш
        cached = self._get_cached(topic)
        if cached:
            print(f"[INFO] Использовано кэшированное объяснение из файла")
            return cached
        
        # Сообщение об ошибке
        error_msg = self._get_error_message(subject, section, topic)
        print(f"[ERROR] Не удалось сгенерировать объяснение. Показываем сообщение об ошибке.")
        return error_msg
    
    @console.debug(PYTHON_FILENAME)
    def _generate_with_chatbot_llm(self, subject: str, section: str, topic: str) -> str:
        """Генерация через LLM из chatbot"""
        print(f"[DEBUG] _generate_with_chatbot_llm вызван для темы: {topic}")
        
        ctx = SUBJECT_CONTEXTS.get(subject, {"style": "образовательный", "focus": "ключевые понятия", "examples": "примеры"})
        
        prompt_text = f"""Ты опытный учитель {subject.lower()}а. Объясни тему "{topic}" из раздела "{section}".

Стиль: {ctx['style']}. Фокус: {ctx['focus']}. Примеры: {ctx['examples']}.

Требования:
1. Простой язык, конкретные примеры
2. Структура: введение, понятия, объяснение, применение, выводы
3. Объём: 400-600 слов
4. На русском языке
5. Используй Markdown форматирование
6. НЕ используй LaTeX ($$ или $)!

Начни сразу с содержания."""
        
        response = None
        error_msg = None
        
        # Пробуем через Prompt класс
        try:
            print(f"[DEBUG] Пробуем метод через Prompt класс...")
            from bot.llm import Prompt
            prompt = Prompt(
                role=f"Ты опытный учитель {subject.lower()}а. Объясняй просто и понятно, используй Markdown форматирование.",
                task=f"Объясни тему '{topic}' из раздела '{section}' по предмету {subject}",
                answer="Дай подробное объяснение на русском языке с примерами и практическим применением."
            )
            print(f"[DEBUG] Вызываем chatbot_llm.ask()...")
            response = self.chatbot_llm.ask(prompt)
            print(f"[DEBUG] Получен ответ через Prompt метод, длина: {len(response) if response else 0}")
        except Exception as e:
            error_msg = f"Prompt метод: {e}"
            print(f"[WARNING] Prompt метод не сработал: {e}")
            # Если Prompt не работает, используем прямой вызов
            try:
                print(f"[DEBUG] Пробуем прямой вызов через client.invoke()...")
                if hasattr(self.chatbot_llm, 'client'):
                    print(f"[DEBUG] client найден: {type(self.chatbot_llm.client)}")
                    response = self.chatbot_llm.client.invoke(prompt_text)
                    print(f"[DEBUG] Получен ответ через прямой вызов, длина: {len(response) if response else 0}")
                else:
                    raise Exception("LLM client не найден")
            except Exception as e2:
                error_msg = f"Прямой вызов: {e2}"
                print(f"[ERROR] Прямой вызов тоже не сработал: {e2}")
                import traceback
                traceback.print_exc()
                raise Exception(f"Ошибка вызова LLM: {error_msg}")
        
        if not response or len(response.strip()) < 50:
            raise ValueError(f"Пустой ответ от LLM (длина: {len(response) if response else 0}). {error_msg or ''}")
        
        response = self._clean_text(response)
        print(f"[DEBUG] Очищенный ответ, длина: {len(response)}")
        self._cache_explanation(topic, response)
        
        return response
    
    @console.debug(PYTHON_FILENAME)
    def _generate_with_ollama(self, subject: str, section: str, topic: str) -> str:
        """Генерация через Ollama"""
        ctx = SUBJECT_CONTEXTS.get(subject, {"style": "образовательный", "focus": "ключевые понятия", "examples": "примеры"})
        
        prompt = f"""Ты опытный учитель {subject.lower()}а. Объясни тему "{topic}" из раздела "{section}".

Стиль: {ctx['style']}. Фокус: {ctx['focus']}. Примеры: {ctx['examples']}.

Требования:
1. Простой язык, конкретные примеры
2. Структура: введение, понятия, объяснение, применение, выводы
3. Объём: 400-600 слов
4. На русском языке

Начни сразу с содержания."""
        
        response = self.ollama_client.invoke(prompt)
        
        if not response or len(response.strip()) < 50:
            raise ValueError("Пустой ответ")
        
        response = self._clean_text(response)
        self._cache_explanation(topic, response)
        
        return response
    
    @console.debug(PYTHON_FILENAME)
    def _generate_with_openai(self, subject: str, section: str, topic: str) -> str:
        """Генерация через OpenAI"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            ctx = SUBJECT_CONTEXTS.get(subject, {"style": "образовательный", "focus": "понятия", "examples": "примеры"})
            
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": f"Ты учитель {subject.lower()}а. Объясняй просто и понятно."},
                    {"role": "user", "content": f"Объясни тему '{topic}' ({section}). Стиль: {ctx['style']}."}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            if response and response.choices:
                text = response.choices[0].message.content
                self._cache_explanation(topic, text)
                return text
            
            raise ValueError("Пустой ответ OpenAI")
        except ImportError:
            raise RuntimeError("OpenAI не установлен")
    
    @console.debug(PYTHON_FILENAME)
    def _get_cached(self, topic: str) -> Optional[str]:
        """Получение из кэша"""
        try:
            cache_dir = Path(__file__).parent / "explanations"
            filename = self._topic_to_filename(topic)
            cache_file = cache_dir / f"{filename}.txt"
            
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return self._clean_text(f.read())
            return None
        except Exception:
            return None
    
    @console.debug(PYTHON_FILENAME)
    def _cache_explanation(self, topic: str, content: str):
        """Сохранение в кэш"""
        try:
            cache_dir = Path(__file__).parent / "explanations"
            cache_dir.mkdir(exist_ok=True)
            
            filename = self._topic_to_filename(topic)
            with open(cache_dir / f"{filename}.txt", 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Ошибка кэширования: {e}")
    
    @console.debug(PYTHON_FILENAME)
    def _topic_to_filename(self, topic: str) -> str:
        """Транслитерация темы в имя файла"""
        translit = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }
        return ''.join(translit.get(c, c) if c.isalpha() else '_' if c == ' ' else '' 
                      for c in topic.lower() if c.isalnum() or c in ' _')
    
    @console.debug(PYTHON_FILENAME)
    def _get_local_explanation(self, subject: str, section: str, topic: str) -> Optional[str]:
        """Локальные объяснения для популярных тем"""
        local_explanations = {
            "Алгебра": {
                "Линейные уравнения": """## Линейные уравнения

### Введение
Линейное уравнение — это уравнение, в котором переменная входит только в первой степени. Общий вид: **ax + b = 0**, где a ≠ 0.

### Основные понятия
- **Коэффициент** — число перед переменной (a)
- **Свободный член** — число без переменной (b)
- **Корень уравнения** — значение переменной, при котором уравнение обращается в верное равенство

### Решение линейных уравнений
1. **Перенос слагаемых**: все слагаемые с переменной в одну сторону, числа — в другую
2. **Приведение подобных**: сложение/вычитание коэффициентов
3. **Деление на коэффициент**: делим обе части на число перед переменной

### Примеры
**Пример 1:** 2x + 5 = 11
- Переносим 5: 2x = 11 - 5
- Упрощаем: 2x = 6
- Делим на 2: x = 3
- **Ответ:** x = 3

**Пример 2:** 3x - 7 = 2x + 4
- Переносим 2x влево, -7 вправо: 3x - 2x = 4 + 7
- Упрощаем: x = 11
- **Ответ:** x = 11

### Применение
Линейные уравнения используются для решения задач на:
- Нахождение неизвестного числа
- Расчеты времени, скорости, расстояния
- Экономические расчеты
- Геометрические задачи

### Выводы
Линейные уравнения — основа алгебры. Умение их решать необходимо для изучения более сложных тем.""",
                "Квадратные уравнения": """## Квадратные уравнения

### Введение
Квадратное уравнение — это уравнение вида **ax² + bx + c = 0**, где a ≠ 0.

### Основные понятия
- **a, b, c** — коэффициенты (a — старший коэффициент)
- **Дискриминант** — D = b² - 4ac
- **Корни уравнения** — значения x, при которых уравнение равно нулю

### Формула решения
**x = (-b ± √D) / 2a**

### Типы решений
1. **D > 0** — два различных корня
2. **D = 0** — один корень (два совпадающих)
3. **D < 0** — нет действительных корней

### Примеры
**Пример 1:** x² - 5x + 6 = 0
- D = 25 - 24 = 1
- x₁ = (5 + 1) / 2 = 3
- x₂ = (5 - 1) / 2 = 2
- **Ответ:** x₁ = 3, x₂ = 2

**Пример 2:** x² - 4x + 4 = 0
- D = 16 - 16 = 0
- x = 4 / 2 = 2
- **Ответ:** x = 2 (два совпадающих корня)

### Применение
- Физика: расчет траекторий
- Геометрия: нахождение сторон фигур
- Экономика: оптимизация прибыли

### Выводы
Квадратные уравнения — важный инструмент для решения практических задач.""",
            }
        }
        
        if subject in local_explanations and topic in local_explanations[subject]:
            explanation = local_explanations[subject][topic]
            self._cache_explanation(topic, explanation)
            return explanation
        
        return None
    
    @console.debug(PYTHON_FILENAME)
    def _get_error_message(self, subject: str, section: str, topic: str) -> str:
        """Сообщение об ошибке"""
        return f"""## {topic}

❌ **Не удалось сгенерировать объяснение через LLM**

**Предмет:** {subject}  
**Раздел:** {section}  
**Тема:** {topic}

### 🔧 Что нужно сделать для работы LLM:

1. **Запустите Ollama сервер:**
   ```bash
   ollama serve
   ```

2. **Убедитесь, что модель загружена:**
   ```bash
   ollama pull {DEFAULT_MODEL}
   ```

3. **Проверьте, что сервер работает:**
   - Откройте http://localhost:11434 в браузере
   - Должен быть доступен API

4. **Перезапустите приложение** после запуска Ollama

5. **Попробуйте перегенерировать** объяснение

### 📝 Альтернатива:
Если Ollama недоступен, можно использовать OpenAI API:
- Установите переменную окружения: `OPENAI_API_KEY`
- Перезапустите приложение"""


# Экземпляр менеджера
theory_manager = TheoryManager(model_name=DEFAULT_MODEL)
