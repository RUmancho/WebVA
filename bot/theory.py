"""
Модуль управления теоретическими материалами.
Использует LLM (deepseek-r1:7b) для генерации объяснений.
"""

import os
import sys
import re
from pathlib import Path
from typing import Optional, Dict, Any

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import session as flask_session
from bot.llm import Prompt
from bot import chat  # Импортируем модуль с готовым LLM
from bot import topics
from logger import console

PYTHON_FILENAME = "theory"

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


class TheoryManager:
    """Менеджер теоретических материалов"""
    
    CURSOR_VARIANTS = ["▌", "▋", "▊", "▉", "█", "▐", "▎", "▍"]
    
    @console.debug(PYTHON_FILENAME)
    def __init__(self):
        self.SUBJECTS_STRUCTURE = topics.SUBJECTS_STRUCTURE
        self._init_session()
    
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
        """Очистка текста от курсоров и тегов размышлений"""
        if not text:
            return ""
        
        cleaned = str(text)
        for cursor in self.CURSOR_VARIANTS:
            cleaned = cleaned.replace(cursor, "")
        
        # Убираем блоки раздумий deepseek-r1
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
    def get_topic_explanation(self, subject: str, section: str, topic: str, regenerate: bool = False) -> str:
        """Получение объяснения темы через LLM (deepseek-r1:7b)"""
        
        # Проверяем кэш
        if not regenerate:
            cached = self._get_cached(topic)
            if cached:
                return cached
        
        # Генерируем через LLM
        try:
            explanation = self._generate_explanation(subject, section, topic)
            if explanation and len(explanation.strip()) > 50:
                return explanation
        except Exception:
            pass
        
        # Локальные объяснения как fallback
        local_explanation = self._get_local_explanation(subject, section, topic)
        if local_explanation:
            return local_explanation
        
        # Сообщение об ошибке
        return self._get_error_message(subject, section, topic)
    
    @console.debug(PYTHON_FILENAME)
    def _generate_explanation(self, subject: str, section: str, topic: str) -> str:
        """Генерация объяснения через LLM из chat.py"""
        
        ctx = SUBJECT_CONTEXTS.get(subject, {"style": "образовательный", "focus": "ключевые понятия", "examples": "примеры"})
        
        # Создаём промпт
        prompt = Prompt(
            role=f"Ты опытный учитель {subject.lower()}а. Объясняй просто и понятно, используй Markdown форматирование. НЕ используй LaTeX ($$ или $)!",
            task=f"Объясни тему '{topic}' из раздела '{section}' по предмету {subject}. Стиль: {ctx['style']}. Фокус: {ctx['focus']}. Примеры: {ctx['examples']}.",
            answer="Дай подробное объяснение на русском языке (400-600 слов) с примерами и практическим применением. Структура: введение, основные понятия, объяснение, применение, выводы."
        )
        
        # Используем готовый LLM из chat.py
        response = chat.academic.ask(prompt)
        
        if not response or len(response.strip()) < 50:
            raise ValueError(f"Пустой ответ от LLM (длина: {len(response) if response else 0})")
        
        response = self._clean_text(response)
        self._cache_explanation(topic, response)
        
        return response
    
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
        except Exception:
            pass
    
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
        """Локальные объяснения для популярных тем (fallback)"""
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

### Выводы
Линейные уравнения — основа алгебры. Умение их решать необходимо для изучения более сложных тем.""",
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

❌ **Не удалось сгенерировать объяснение**

**Предмет:** {subject}  
**Раздел:** {section}  
**Тема:** {topic}

### 🔧 Возможные причины:
1. Проблема с подключением к LLM
2. Модель deepseek-r1:7b не отвечает

Попробуйте перезагрузить страницу или выбрать другую тему."""


# Экземпляр менеджера
theory_manager = TheoryManager()
