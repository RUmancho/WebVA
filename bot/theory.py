"""
Модуль управления теоретическими материалами.
Использует LLM для генерации объяснений.
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
from bot.prompt import Prompt
from bot import chat  
from bot import topics
from logger import console

from logger.tracer import trace

PYTHON_FILENAME = "theory"

# Контексты для предметов
SUBJECT_CONTEXTS = {
    "Алгебра": {"style": "математический", "focus": "формулы и уравнения", "examples": "числовые примеры"},
    "Геометрия": {"style": "геометрический", "focus": "теоремы и свойства фигур", "examples": "задачи с чертежами"},
    "Физика": {"style": "научный", "focus": "законы физики", "examples": "примеры из жизни"}
}


class TheoryManager:
    """Менеджер теоретических материалов"""
    
    CURSOR_VARIANTS = ["▌", "▋", "▊", "▉", "█", "▐", "▎", "▍"]
    
    @trace
    def __init__(self):
        self.SUBJECTS_STRUCTURE = topics.SUBJECTS_STRUCTURE
        self._init_session()
    
    @trace
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
    
    @trace
    def init_theory_session(self):
        """Публичный метод инициализации сессии"""
        self._init_session()
    
    @trace
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
    
    @trace
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
    
    @trace
    def show_subjects(self) -> Dict[str, Any]:
        """Список предметов"""
        return {'subjects': list(self.SUBJECTS_STRUCTURE.keys()), 'subjects_structure': self.SUBJECTS_STRUCTURE}
    
    @trace
    def show_sections(self) -> Dict[str, Any]:
        """Разделы предмета"""
        state = flask_session.get('theory_state', {})
        subject = state.get('selected_subject')
        
        if not subject:
            return {'error': 'Предмет не выбран'}
        
        return {'subject': subject, 'sections': self.SUBJECTS_STRUCTURE.get(subject, {}).get('sections', {})}
    
    @trace
    def show_topics(self) -> Dict[str, Any]:
        """Темы раздела"""
        state = flask_session.get('theory_state', {})
        subject = state.get('selected_subject')
        section = state.get('selected_section')
        
        if not subject or not section:
            return {'error': 'Предмет или раздел не выбран'}
        
        topics_list = self.SUBJECTS_STRUCTURE.get(subject, {}).get('sections', {}).get(section, {}).get('topics', [])
        return {'subject': subject, 'section': section, 'topics': topics_list}
    
    @trace
    def get_topic_explanation(self, subject: str, section: str, topic: str, regenerate: bool = False) -> str:
        """Получение объяснения темы через LLM"""
        
        # Проверяем кэш
        if not regenerate:
            cached = self._get_cached(topic)
            if cached:
                print(f"[INFO] Объяснение загружено из кэша: {topic}")
                return cached
        
        # Генерируем через LLM
        try:
            print(f"[INFO] Генерация объяснения через LLM: {subject}/{section}/{topic}")
            explanation = self._generate_explanation(subject, section, topic)
            if explanation and len(explanation.strip()) > 50:
                print(f"[SUCCESS] Объяснение сгенерировано (длина: {len(explanation)})")
                return explanation
            else:
                print(f"[WARN] Объяснение слишком короткое: {len(explanation) if explanation else 0} символов")
        except Exception as e:
            print(f"[ERROR] Ошибка генерации через LLM: {e}")
            import traceback
            traceback.print_exc()
        
        # Локальные объяснения как fallback
        print(f"[INFO] Попытка использовать локальное объяснение")
        local_explanation = self._get_local_explanation(subject, section, topic)
        if local_explanation:
            print(f"[SUCCESS] Использовано локальное объяснение")
            return local_explanation
        
        # Сообщение об ошибке
        print(f"[ERROR] Не удалось получить объяснение для темы: {topic}")
        return self._get_error_message(subject, section, topic)
    
    @trace
    def _generate_explanation(self, subject: str, section: str, topic: str) -> str:
        """Генерация объяснения через LLM из chat.py"""
        
        # Проверяем доступность LLM
        if not chat.academic.is_available():
            raise RuntimeError("LLM клиент не инициализирован. Проверьте, что Ollama запущен: ollama serve")
        
        ctx = SUBJECT_CONTEXTS.get(subject, {"style": "образовательный", "focus": "ключевые понятия", "examples": "примеры"})
        
        print(f"[INFO] Создание промпта для темы: {topic}")
        print(f"[INFO] Контекст: стиль={ctx['style']}, фокус={ctx['focus']}")
        
        # Создаём промпт
        prompt = Prompt(
            role=f"Ты опытный учитель по предмету {subject}. Объясняй просто и понятно, используй Markdown форматирование. НЕ используй LaTeX ($$ или $)!",
            task=f"""Объясни тему "{topic}" из раздела "{section}" по предмету {subject}.

Требования:
- Стиль изложения: {ctx['style']}
- Акцент на: {ctx['focus']}
- Примеры: {ctx['examples']}
- Объём: 400-600 слов
- Язык: русский
- Формат: Markdown (без LaTeX)

Структура объяснения:
1. Введение (что это такое)
2. Основные понятия и определения
3. Подробное объяснение с примерами
4. Практическое применение
5. Выводы и рекомендации""",
            answer="Дай подробное и понятное объяснение темы на русском языке."
        )
        
        print(f"[INFO] Отправка запроса к LLM...")
        
        # Используем готовый LLM из chat.py
        try:
            response = chat.academic.ask(prompt)
        except Exception as e:
            raise RuntimeError(f"Ошибка при обращении к LLM: {e}")
        
        print(f"[INFO] Получен ответ от LLM (длина: {len(response) if response else 0})")
        
        if not response:
            raise ValueError("LLM вернул пустой ответ")
        
        if len(response.strip()) < 50:
            raise ValueError(f"Ответ от LLM слишком короткий (длина: {len(response.strip())})")
        
        print(f"[INFO] Очистка ответа от служебных тегов...")
        response = self._clean_text(response)
        
        print(f"[INFO] Сохранение в кэш...")
        self._cache_explanation(topic, response)
        
        print(f"[SUCCESS] Объяснение успешно сгенерировано и сохранено")
        return response
    
    @trace
    def _get_cached(self, topic: str) -> Optional[str]:
        """Получение из кэша"""
        try:
            cache_dir = Path(__file__).parent / "explanations"
            filename = self._topic_to_filename(topic)
            cache_file = cache_dir / f"{filename}.txt"
            
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return self._clean_text(content)
            return None
        except Exception as e:
            print(f"[ERROR] Ошибка чтения кэша для темы '{topic}': {e}")
            return None
    
    @trace
    def _cache_explanation(self, topic: str, content: str):
        """Сохранение в кэш"""
        try:
            cache_dir = Path(__file__).parent / "explanations"
            cache_dir.mkdir(exist_ok=True)
            
            filename = self._topic_to_filename(topic)
            cache_file = cache_dir / f"{filename}.txt"
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"[INFO] Объяснение сохранено в кэш: {cache_file}")
        except Exception as e:
            print(f"[ERROR] Ошибка сохранения в кэш для темы '{topic}': {e}")
    
    @trace
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
    
    @trace
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
    
    @trace
    def _get_error_message(self, subject: str, section: str, topic: str) -> str:
        """Сообщение об ошибке"""
        return f"""## {topic}

❌ **Не удалось сгенерировать объяснение**

**Предмет:** {subject}  
**Раздел:** {section}  
**Тема:** {topic}

### 🔧 Возможные причины:
1. Проблема с подключением к LLM
2. LLM не отвечает

Попробуйте перезагрузить страницу или выбрать другую тему."""


# Экземпляр менеджера
theory_manager = TheoryManager()
