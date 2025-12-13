"""
Модуль управления теоретическими материалами.
Использует LLM (deepseek-r1:7b) для генерации объяснений.
"""

from flask import session as flask_session
import re
import socket
from pathlib import Path
from typing import Optional, Dict, Any
from bot.settings import OPENAI_API_KEY
from langchain_ollama import OllamaLLM
from bot import topics


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


def check_ollama() -> bool:
    """Проверка Ollama сервера"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((OLLAMA_HOST, OLLAMA_PORT))
        sock.close()
        return result == 0
    except Exception:
        return False


class TheoryManager:
    """Менеджер теоретических материалов"""
    
    CURSOR_VARIANTS = ["▌", "▋", "▊", "▉", "█", "▐", "▎", "▍"]
    
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.SUBJECTS_STRUCTURE = topics.SUBJECTS_STRUCTURE
        self.ollama_client = None
        self.openai_client = None
        
        self._init_ollama(model_name or DEFAULT_MODEL)
        self._init_session()
    
    def _init_ollama(self, model_name: str):
        """Инициализация Ollama"""
        if not check_ollama():
            print("Ollama недоступен")
            return
        
        try:
            kwargs = {"model": model_name, "temperature": 0.0, "num_thread": 1}
            if 'deepseek-r1' in model_name.lower():
                kwargs['reasoning'] = False
            
            self.ollama_client = OllamaLLM(**kwargs)
            print(f"✓ Ollama: {model_name}")
        except Exception as e:
            print(f"✗ Ollama: {e}")
    
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
    
    def init_theory_session(self):
        """Публичный метод инициализации сессии"""
        self._init_session()
    
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
    
    def show_subjects(self) -> Dict[str, Any]:
        """Список предметов"""
        return {'subjects': list(self.SUBJECTS_STRUCTURE.keys()), 'subjects_structure': self.SUBJECTS_STRUCTURE}
    
    def show_sections(self) -> Dict[str, Any]:
        """Разделы предмета"""
        state = flask_session.get('theory_state', {})
        subject = state.get('selected_subject')
        
        if not subject:
            return {'error': 'Предмет не выбран'}
        
        return {'subject': subject, 'sections': self.SUBJECTS_STRUCTURE.get(subject, {}).get('sections', {})}
    
    def show_topics(self) -> Dict[str, Any]:
        """Темы раздела"""
        state = flask_session.get('theory_state', {})
        subject = state.get('selected_subject')
        section = state.get('selected_section')
        
        if not subject or not section:
            return {'error': 'Предмет или раздел не выбран'}
        
        topics_list = self.SUBJECTS_STRUCTURE.get(subject, {}).get('sections', {}).get(section, {}).get('topics', [])
        return {'subject': subject, 'section': section, 'topics': topics_list}
    
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
    
    def get_topic_explanation(self, subject: str, section: str, topic: str, regenerate: bool = False) -> str:
        """Получение объяснения темы"""
        # Проверяем кэш
        if not regenerate:
            cached = self._get_cached(topic)
            if cached:
                return cached
        
        # Пробуем Ollama
        if self.ollama_client:
            try:
                return self._generate_with_ollama(subject, section, topic)
            except Exception as e:
                print(f"Ошибка Ollama: {e}")
        
        # Fallback на OpenAI
        if self.api_key:
            try:
                return self._generate_with_openai(subject, section, topic)
            except Exception as e:
                print(f"Ошибка OpenAI: {e}")
        
        # Локальный кэш
        return self._get_cached(topic) or self._get_error_message(subject, section, topic)
    
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
    
    def _get_error_message(self, subject: str, section: str, topic: str) -> str:
        """Сообщение об ошибке"""
        return f"""## {topic}

К сожалению, не удалось сгенерировать объяснение.

**Предмет:** {subject}  
**Раздел:** {section}  
**Тема:** {topic}

### Что можно сделать:
1. Проверьте Ollama: `ollama serve`
2. Загрузите модель: `ollama pull {DEFAULT_MODEL}`
3. Попробуйте перегенерировать"""


# Экземпляр менеджера
theory_manager = TheoryManager(model_name=DEFAULT_MODEL)
