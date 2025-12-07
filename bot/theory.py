from flask import session as flask_session
import functools
from typing import Optional, Callable
from bot.settings import OPENAI_API_KEY
from langchain_ollama import OllamaLLM
from bot import topics

def log_function_execution(func: Callable) -> Callable:
    """Декоратор для логирования выполнения функций (успех/неудача)"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        try:
            result = func(*args, **kwargs)
            print(f"✓ {func_name} выполнена успешно")
            return result
        except Exception as e:
            print(f"✗ {func_name} завершилась с ошибкой: {e}")
            raise
    return wrapper


class LLMProvider:
    """Базовый класс для провайдеров LLM"""
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs
        self.client = None
    
    def initialize(self) -> bool:
        """Инициализация клиента провайдера"""
        raise NotImplementedError
    
    def invoke(self, prompt: str) -> str:
        """Выполнение запроса к LLM"""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Проверка доступности провайдера"""
        return self.client is not None


class OllamaProvider(LLMProvider):
    """Провайдер для Ollama"""
    
    def __init__(self, model_name: str = "deepseek-r1:7b", temperature: float = 0.0, **kwargs):
        super().__init__(model_name, **kwargs)
        self.temperature = temperature
    
    def initialize(self) -> bool:
        """Инициализация Ollama клиента"""
        try:
            # Создаем словарь параметров, исключая temperature из kwargs если он там есть
            ollama_kwargs = {k: v for k, v in self.kwargs.items() if k != 'temperature' and k != 'reasoning'}
            ollama_kwargs['temperature'] = self.temperature
            # Отключаем reasoning для deepseek-r1, чтобы убрать раздумья
            if 'deepseek-r1' in self.model_name.lower():
                ollama_kwargs['reasoning'] = False
            
            self.client = OllamaLLM(
                model=self.model_name,
                num_thread=1,
                **ollama_kwargs
            )
            print(f"Ollama клиент создан для модели {self.model_name}")
            return True
        except Exception as e:
            print(f"Ошибка при создании Ollama клиента: {e}")
            self.client = None
            return False
    
    def invoke(self, prompt: str) -> str:
        """Выполнение запроса к Ollama"""
        # Если клиент не создан, пробуем создать его
        if not self.client:
            print(f"Попытка создать Ollama клиент для модели {self.model_name}")
            if not self.initialize():
                raise ConnectionError("Ollama клиент не инициализирован. Убедитесь, что Ollama установлен и запущен.")
        
        try:
            print(f"Отправка запроса к Ollama (модель: {self.model_name})")
            response = self.client.invoke(prompt)
            print(f"Получен ответ от Ollama (длина: {len(response) if response else 0} символов)")
            return response
        except Exception as e:
            error_str = str(e).lower()
            print(f"Ошибка при вызове Ollama: {e}")
            # Проверяем, является ли это ошибкой подключения
            connection_keywords = ['connection', 'refused', 'unreachable', 'timeout', '10061', '10060', 'connect', 'failed', 'cannot connect']
            if any(keyword in error_str for keyword in connection_keywords):
                raise ConnectionError("Ollama сервер недоступен. Убедитесь, что сервер запущен: ollama serve")
            raise


class OpenAIProvider(LLMProvider):
    """Провайдер для OpenAI"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None, temperature: float = 0.7, **kwargs):
        super().__init__(model_name, temperature=temperature, **kwargs)
        self.api_key = api_key or OPENAI_API_KEY
        self.temperature = temperature
    
    def initialize(self) -> bool:
        """Инициализация OpenAI клиента"""
        if not self.api_key:
            return False
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            return True
        except Exception:
            return False
    
    def invoke(self, prompt: str) -> str:
        """Выполнение запроса к OpenAI"""
        if not self.client:
            raise RuntimeError("OpenAI клиент не инициализирован")
        
        system_prompt = "Ты опытный учитель. Объясняй материал просто и понятно."
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=self.temperature
        )
        
        if response and response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        raise RuntimeError("Пустой ответ от OpenAI")


class TheoryManager:
    """Класс для управления теоретическими материалами"""
    
    # Константы для очистки текста
    CURSOR_VARIANTS = ["▌", "▋", "▊", "▉", "█", "▐", "▎", "▍"]
    TEXT_REPLACEMENTS = {
        "ollamapull": "ollama pull",
        "ollamalist": "ollama list",
        "deepseek :7b": "deepseek:7b",
        "deepseek-r1 :7b": "deepseek-r1:7b",
        "deepseek:7bзагружена": "deepseek:7b загружена",
        "deepseek-r1:7b загружена": "deepseek-r1:7b загружена",
        "deepseek:7b загружена:": "deepseek:7b загружена:",
        "модельdeepseek": "модель deepseek",
        "модель deepseek:7b": "модель deepseek:7b",
        "неудалось сгенерировать": "не удалось сгенерировать",
        ":ollama pull": ": `ollama pull",
        ":ollama list": ": `ollama list",
        "загружена:ollama": "загружена: `ollama",
        "доступна:ollama": "доступна: `ollama"
    }
    
    def __init__(self, llm_provider: str = "ollama", model_name: Optional[str] = None, 
                 temperature: float = 0.0, api_key: Optional[str] = None, **llm_kwargs):
        self.api_key = api_key or OPENAI_API_KEY
        self.SUBJECTS_STRUCTURE = topics.SUBJECTS_STRUCTURE
        
        # Инициализация провайдера LLM
        if llm_provider.lower() == "openai":
            model_name = model_name or "gpt-4o-mini"
            self.llm_provider = OpenAIProvider(
                model_name=model_name,
                api_key=self.api_key,
                temperature=temperature,
                **llm_kwargs
            )
        else:  # По умолчанию Ollama
            model_name = model_name or "deepseek-r1:7b"
            self.llm_provider = OllamaProvider(
                model_name=model_name,
                temperature=temperature,
                **llm_kwargs
            )
        
        # Инициализируем провайдер
        initialized = self.llm_provider.initialize()
        if initialized:
            print(f"Провайдер {type(self.llm_provider).__name__} успешно инициализирован (модель: {self.llm_provider.model_name})")
        else:
            print(f"Провайдер {type(self.llm_provider).__name__} не инициализирован, будет создан при первом запросе")
        
        self.init_theory_session()
    
    @log_function_execution
    def init_theory_session(self):
        """Инициализация сессии для теории"""
        # TODO: Полная адаптация для Flask UI требуется
        try:
            session = flask_session
            if 'theory_state' not in session:
                session['theory_state'] = {
                    'current_page': 'subjects',
                    'selected_subject': None,
                    'selected_section': None,
                    'selected_topic': None,
                    'explanation_text': None,
                    'topic_chat_active': False,
                    'topic_chat_messages': []
                }
        except Exception as e:
            print(f"Ошибка инициализации сессии теории: {e}")
    
    def _clean_text_from_cursor(self, text: str) -> str:
        """Очистить текст от курсора и лишних пробелов"""
        if not text:
            return ""
        
        cleaned = str(text)
        # Убираем курсоры
        for cursor in self.CURSOR_VARIANTS:
            cleaned = cleaned.replace(cursor, "")
        
        # Применяем замены
        for old, new in self.TEXT_REPLACEMENTS.items():
            cleaned = cleaned.replace(old, new)
        
        return cleaned.strip()
    
    def _save_explanation_text(self, text: Optional[str]) -> Optional[str]:
        """Безопасное сохранение текста объяснения с очисткой от курсора"""
        if not text:
            flask_session['theory_state']['explanation_text'] = None
            return None
        
        cleaned_text = self._clean_text_from_cursor(text)
        flask_session['theory_state']['explanation_text'] = cleaned_text
        return cleaned_text
    
    @log_function_execution
    def show_theory_interface(self):
        """Главный интерфейс теории - ТРЕБУЕТ АДАПТАЦИИ ДЛЯ FLASK"""
        # TODO: UI теперь в Flask шаблонах (templates/dashboard/theory.html)
        # Этот метод возвращает данные для шаблона вместо отображения UI
        self.init_theory_session()
        session = flask_session
        state = session.get('theory_state', {})
        return {
            'current_page': state.get('current_page', 'subjects'),
            'selected_subject': state.get('selected_subject'),
            'selected_section': state.get('selected_section'),
            'selected_topic': state.get('selected_topic'),
            'explanation_text': state.get('explanation_text'),
            'subjects': self.SUBJECTS_STRUCTURE
        }
    
    def show_navigation(self):
        """Показать навигационные кнопки - ТРЕБУЕТ АДАПТАЦИИ ДЛЯ FLASK"""
        # TODO: UI теперь в Flask шаблонах
        session = flask_session
        state = session.get('theory_state', {})
        
        breadcrumbs = []
        if state['current_page'] != 'subjects':
            breadcrumbs.append("Предметы")
        if state['selected_subject'] and state['current_page'] not in ['subjects', 'sections']:
            breadcrumbs.append(state['selected_subject'])
        if state['selected_section'] and state['current_page'] not in ['subjects', 'sections', 'topics']:
            breadcrumbs.append(state['selected_section'])
        if state['selected_topic']:
            breadcrumbs.append(state['selected_topic'])
        
        # TODO: UI теперь в Flask шаблонах - эти вызовы st.* не используются
        # if breadcrumbs:
        #     st.markdown(" → ".join(breadcrumbs))
        #     st.markdown("---")
        # 
        # if state['current_page'] != 'subjects':
        #     if st.button("⬅️ Назад", key="theory_back_button"):
        #         self.navigate_back()
        #         st.rerun()
        
        # Возвращаем данные для Flask шаблона
        return {'breadcrumbs': breadcrumbs, 'state': state}
    
    def navigate_back(self):
        """Навигация назад"""
        state = flask_session.get('theory_state', {})
        
        if state['current_page'] == 'explanation':
            state['current_page'] = 'topics'
            state['selected_topic'] = None
            state['explanation_text'] = None
        elif state['current_page'] == 'topics':
            state['current_page'] = 'sections'
            state['selected_section'] = None
        elif state['current_page'] == 'sections':
            state['current_page'] = 'subjects'
            state['selected_subject'] = None
    
    def show_subjects(self):
        """Показать список предметов - ТРЕБУЕТ АДАПТАЦИИ ДЛЯ FLASK"""
        # TODO: UI теперь в Flask шаблонах - все вызовы st.* закомментированы
        subjects = list(self.SUBJECTS_STRUCTURE.keys())
        return {'subjects': subjects, 'subjects_structure': self.SUBJECTS_STRUCTURE}
    
    def show_sections(self):
        """Показать разделы выбранного предмета - ТРЕБУЕТ АДАПТАЦИИ ДЛЯ FLASK"""
        # TODO: UI теперь в Flask шаблонах
        session = flask_session
        state = session.get('theory_state', {})
        subject = state.get('selected_subject')
        if not subject:
            return {'error': 'Предмет не выбран'}
        sections = self.SUBJECTS_STRUCTURE.get(subject, {}).get('sections', {})
        return {'subject': subject, 'sections': sections}
    
    def show_topics(self):
        """Показать темы выбранного раздела - ТРЕБУЕТ АДАПТАЦИИ ДЛЯ FLASK"""
        # TODO: UI теперь в Flask шаблонах
        session = flask_session
        state = session.get('theory_state', {})
        subject = state.get('selected_subject')
        section = state.get('selected_section')
        if not subject or not section:
            return {'error': 'Предмет или раздел не выбран'}
        topics = self.SUBJECTS_STRUCTURE.get(subject, {}).get('sections', {}).get(section, {}).get('topics', [])
        return {'subject': subject, 'section': section, 'topics': topics}
            
    @log_function_execution
    def show_explanation(self):
        """Показать объяснение выбранной темы"""
        state = flask_session.get('theory_state', {})
        subject = state['selected_subject']
        section = state['selected_section']
        topic = state['selected_topic']
            
        if not all([subject, section, topic]):
            state['current_page'] = 'subjects'
            return {'error': 'Не все параметры выбраны'}
        
        icon = self.SUBJECTS_STRUCTURE[subject]["icon"]
        # TODO: UI теперь в Flask шаблонах
        
        # Проверяем, изменилась ли тема
        current_topic_key = f"{subject}_{section}_{topic}"
        last_topic_key = state.get('last_topic_key')
        if current_topic_key != last_topic_key:
            state['explanation_displayed'] = False
            state['last_topic_key'] = current_topic_key
        
        explanation_text = state.get('explanation_text')
        if explanation_text:
            explanation_text = self._clean_text_from_cursor(explanation_text)
            self._save_explanation_text(explanation_text)
        
        # Проверяем на старые сообщения об ошибках
        is_error_template = explanation_text and any(
            indicator in explanation_text for indicator in [
                "К сожалению, не удалось сгенерировать",
                "неудалось сгенерировать",
                "не удалосьсгенерировать",
                "Сервер Ollama доступен, но была ошибка",
                "Что можно сделать:",
                "Убедитесь, что модель"
            ]
        )
        
        if is_error_template:
            state['explanation_text'] = None
            explanation_text = None
        
        # TODO: UI теперь в Flask шаблонах - все вызовы st.* закомментированы
        if not explanation_text:
            # with st.spinner("🔄 Генерирую объяснение..."):
            try:
                full_text = self.get_topic_explanation(subject, section, topic, regenerate=False)
                full_text = self._clean_text_from_cursor(full_text)
                
                if full_text and len(full_text) > 50:
                    is_final_error = (
                        f"## {topic}" in full_text and
                        "К сожалению, не удалось сгенерировать" in full_text and
                        "**Предмет:**" in full_text
                    )
                    
                    if is_final_error or len(full_text) > 200:
                        explanation_text = self._save_explanation_text(full_text)
                    else:
                        # Проверяем короткие ответы на ошибки
                        full_text_lower = full_text.lower()[:100]
                        explicit_errors = [
                            "к сожалению, не удалось сгенерировать",
                            "не удалось сгенерировать объяснение",
                            "оллама сервер недоступен",
                            "что можно сделать:",
                            "убедитесь, что модель"
                        ]
                        
                        is_explicit_error = any(err in full_text_lower for err in explicit_errors)
                        is_command = full_text.strip().startswith(("ollama", "Ollama"))
                        
                        if is_explicit_error or is_command:
                            local_explanation = self._get_local_explanation(subject, section, topic)
                            if local_explanation:
                                explanation_text = self._save_explanation_text(local_explanation)
                            else:
                                explanation_text = self._get_error_message(subject, section, topic)
                                explanation_text = self._clean_text_from_cursor(explanation_text)
                                self._save_explanation_text(explanation_text)
                        else:
                            explanation_text = self._save_explanation_text(full_text)
                else:
                    raise Exception("Получен пустой или некорректный ответ от модели")
            except Exception as e:
                explanation_text = self._get_error_message(subject, section, topic)
                explanation_text = self._clean_text_from_cursor(explanation_text)
                self._save_explanation_text(explanation_text)
        
        # TODO: UI теперь в Flask шаблонах - все вызовы st.* удалены
        # Отображаем объяснение
        if explanation_text:
            clean_text = self._clean_text_from_cursor(explanation_text)
            if clean_text != explanation_text:
                self._save_explanation_text(clean_text)
        
        # Возвращаем данные для Flask шаблона
        return {
            'subject': subject,
            'section': section,
            'topic': topic,
            'explanation_text': explanation_text,
            'topic_chat_active': state.get('topic_chat_active', False)
        }
    
    def _show_topic_chat(self, subject: str, section: str, topic: str, explanation_text: str):
        """Показать чат для обсуждения темы - ТРЕБУЕТ АДАПТАЦИИ ДЛЯ FLASK"""
        # TODO: UI теперь в Flask шаблонах - все вызовы st.* удалены
        state = flask_session.get('theory_state', {})
        
        # Инициализируем сообщения чата, если их нет
        if 'topic_chat_messages' not in state:
            state['topic_chat_messages'] = []
        
        # Если чат только что открыт, добавляем приветственное сообщение
        if len(state['topic_chat_messages']) == 0:
            state['topic_chat_messages'] = [{
                "role": "assistant",
                "content": f"Привет! Я готов ответить на твои вопросы по теме '{topic}' из раздела '{section}' предмета '{subject}'. Задавай вопросы!"
            }]
        
        # Возвращаем данные для Flask шаблона
        return {
            'subject': subject,
            'section': section,
            'topic': topic,
            'messages': state['topic_chat_messages']
        }
    
    def _get_topic_chat_response(self, subject: str, section: str, topic: str, explanation_text: str, 
                                  user_question: str, chat_history: list) -> str:
        """Получить ответ от LLM на вопрос по теме"""
        # Формируем системный промпт с контекстом темы
        system_prompt = f"""Ты опытный учитель {subject.lower()}а. Сейчас обсуждается тема "{topic}" из раздела "{section}".

Контекст темы:
{explanation_text[:1000]}

Твоя задача:
1. Отвечать на вопросы ученика по этой теме
2. Использовать простой и понятный язык
3. Приводить примеры из контекста темы
4. Если вопрос не относится к теме, вежливо напомни о теме обсуждения
5. Отвечай кратко и по делу, без лишних раздумий

ВАЖНО: Отвечай только на русском языке и только по теме. Не показывай процесс размышления, только финальный ответ."""
        
        # Формируем историю диалога
        messages_text = system_prompt + "\n\n"
        for msg in chat_history[-5:]:  # Берем последние 5 сообщений для контекста
            if msg['role'] == 'user':
                messages_text += f"Ученик: {msg['content']}\n"
            elif msg['role'] == 'assistant':
                messages_text += f"Учитель: {msg['content']}\n"
        
        messages_text += f"Ученик: {user_question}\nУчитель:"
        
        # Получаем ответ от LLM
        try:
            response = self.llm_provider.invoke(messages_text)
            
            # Очищаем ответ от раздумий (если они все же появились)
            response = self._clean_reasoning_from_response(response)
            
            return response.strip()
        except ConnectionError:
            return "Извините, сервер LLM недоступен. Проверьте подключение."
        except Exception as e:
            return f"Извините, произошла ошибка: {e}"
    
    def _clean_reasoning_from_response(self, text: str) -> str:
        """Очистить ответ от раздумий deepseek-r1"""
        if not text:
            return ""
        
        # Убираем маркеры раздумий
        reasoning_markers = [
            "<think>",
            "</think>",
            "<reasoning>",
            "</reasoning>",
            "```thinking",
            "```reasoning"
        ]
        
        cleaned = text
        for marker in reasoning_markers:
            cleaned = cleaned.replace(marker, "")
        
        # Убираем блоки между маркерами раздумий
        import re
        cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'<reasoning>.*?</reasoning>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'```thinking.*?```', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'```reasoning.*?```', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        return cleaned.strip()
            
    @log_function_execution
    def get_topic_explanation(self, subject: str, section: str, topic: str, regenerate: bool = False) -> str:
        """Получить объяснение темы от LLM"""
        # Проверяем локальное объяснение
        if not regenerate:
            local_explanation = self._get_local_explanation(subject, section, topic, generate_if_missing=False)
            if local_explanation:
                return local_explanation
        
        # Пробуем использовать основной провайдер
        # Всегда пробуем, даже если объект не создан (он создастся при вызове)
        try:
            print(f"Попытка получить объяснение от {type(self.llm_provider).__name__}")
            return self._get_llm_explanation(subject, section, topic)
        except ConnectionError as e:
            # Ошибка подключения - сервер недоступен
            print(f"Ошибка подключения к LLM: {e}")
            pass
        except (RuntimeError, ValueError) as e:
            # Другие ошибки LLM
            print(f"Ошибка при обращении к LLM: {e}")
            pass
        except Exception as e:
            print(f"Неожиданная ошибка LLM: {e}")
            import traceback
            traceback.print_exc()
            pass
        
        # Fallback на OpenAI, если основной провайдер - Ollama
        if isinstance(self.llm_provider, OllamaProvider) and self.api_key:
            try:
                openai_provider = OpenAIProvider(model_name="gpt-4o-mini", api_key=self.api_key, temperature=0.7)
                if openai_provider.initialize():
                    return self._get_llm_explanation_with_provider(subject, section, topic, openai_provider)
            except Exception:
                pass
        
        # Пробуем локальное объяснение
            local_explanation = self._get_local_explanation(subject, section, topic, generate_if_missing=True)
            if local_explanation:
                return local_explanation
            
            return self._get_error_message(subject, section, topic)
    
    def _get_llm_explanation(self, subject: str, section: str, topic: str) -> str:
        """Получить объяснение от текущего LLM провайдера"""
        return self._get_llm_explanation_with_provider(subject, section, topic, self.llm_provider)
    
    def _get_llm_explanation_with_provider(self, subject: str, section: str, topic: str, provider: LLMProvider) -> str:
        """Получить объяснение от указанного провайдера"""
        system_prompt = f"""Ты опытный учитель {subject.lower()}а с 20-летним стажем. 
Тебе необходимо просто и понятно объяснить тему "{topic}" из раздела "{section}".

Требования к объяснению:
1. Используй простой и доступный язык
2. Приводи конкретные примеры
3. Объясняй шаг за шагом
4. Используй аналогии из повседневной жизни
5. Структурируй материал логично
6. Выделяй ключевые моменты
7. Пиши на русском языке
8. Объем: 300-500 слов

Начни объяснение с краткого введения в тему, затем подробно разбери основные понятия и заверши практическими советами или примерами применения."""
        
        user_prompt = f"Объясни тему '{topic}' из раздела '{section}' предмета '{subject}'"
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response_text = provider.invoke(full_prompt)
        
        if not response_text or len(response_text.strip()) < 50:
            raise ValueError("Пустой или слишком короткий ответ")
        
        # Проверяем на сообщения об ошибках
            error_indicators = [
                "К сожалению, не удалось сгенерировать",
                "неудалось сгенерировать",
                "Ollama сервер недоступен",
                "ollama serve",
                "ollama pull",
                "Что можно сделать:",
            "Убедитесь, что модель"
            ]
        
            response_lower = response_text.lower()
            if any(indicator.lower() in response_lower for indicator in error_indicators):
                raise ValueError("Ответ содержит сообщение об ошибке")
        
        if response_text.strip().startswith(("ollama", "Ollama")):
            raise ValueError("Ответ похож на команду")
        
        return response_text.strip()
    
    def _get_local_explanation(self, subject: str, section: str, topic: str, generate_if_missing: bool = True) -> Optional[str]:
        """Получить локальное объяснение темы"""
        try:
            from pathlib import Path
            
            # Транслитерация кириллицы в латиницу
            translit_map = {
                'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
                'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm',
                'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
                'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
            }
            
            topic_lower = topic.lower()
            topic_filename = ''.join(
                translit_map.get(char, char) if char.isalpha() else '_' if char == ' ' else ''
                for char in topic_lower
                if char.isalnum() or char == '_' or char == ' '
            )
            
            explanations_dir = Path(__file__).parent / "explanations"
            explanations_dir.mkdir(exist_ok=True)
            explanation_file = explanations_dir / f"{topic_filename}.txt"
            
            # Если файл существует, читаем его
            if explanation_file.exists():
                with open(explanation_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content = content.replace('{topic}', topic)
                    content = content.replace('{subject}', subject)
                    content = content.replace('{section}', section)
                    return self._clean_text_from_cursor(content)
            
            # Генерируем, если нужно
            if generate_if_missing and isinstance(self.llm_provider, OllamaProvider):
                if self.llm_provider.is_available():
                    try:
                        response_text = self._get_llm_explanation(subject, section, topic)
                        if response_text and len(response_text.strip()) > 50:
                            content = self._clean_text_from_cursor(response_text.strip())
                            with open(explanation_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            return content
                    except Exception:
                        pass
            
            return None
        except Exception:
            return None
    
    def _get_error_message(self, subject: str, section: str, topic: str) -> str:
        """Сообщение об ошибке, когда LLM недоступны"""
        local_explanation = self._get_local_explanation(subject, section, topic, generate_if_missing=False)
        if local_explanation:
            return self._clean_text_from_cursor(local_explanation)
        
        # Определяем тип провайдера и доступность
        is_ollama = isinstance(self.llm_provider, OllamaProvider)
        has_openai_key = bool(self.api_key)
        model_name = self.llm_provider.model_name
        

# Для релиза с OpenAI: theory_manager = TheoryManager(llm_provider="openai", model_name="gpt-4o-mini", temperature=0.7)
theory_manager = TheoryManager(llm_provider="ollama", model_name="deepseek-r1:7b")