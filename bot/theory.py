import streamlit as st
import socket
import functools
from typing import Optional, Callable
from bot.settings import OPENAI_API_KEY
from langchain_ollama import OllamaLLM
import topics


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
    
    def __init__(self, model_name: str = "deepseek-r1:7b", temperature: float = 0.7, **kwargs):
        super().__init__(model_name, temperature=temperature, **kwargs)
        self.temperature = temperature
    
    @log_function_execution
    def _check_server_available(self) -> bool:
        """Проверка доступности Ollama сервера"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 11434))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def initialize(self) -> bool:
        """Инициализация Ollama клиента"""
        if not self._check_server_available():
                return False
            
        try:
            self.client = OllamaLLM(
                model=self.model_name,
                temperature=self.temperature,
                **self.kwargs
            )
            # Тестовый запрос для проверки доступности модели
            test_response = self.client.invoke("test")
            if test_response is not None:
                return True
            self.client = None
            return False
        except Exception:
            self.client = None
            return False
    
    def invoke(self, prompt: str) -> str:
        """Выполнение запроса к Ollama"""
        if not self.client:
            raise RuntimeError("Ollama клиент не инициализирован")
        return self.client.invoke(prompt)


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
                 temperature: float = 0.7, api_key: Optional[str] = None, **llm_kwargs):
        """
        Инициализация TheoryManager
        
        Args:
            llm_provider: Провайдер LLM ("ollama" или "openai")
            model_name: Название модели (например, "deepseek-r1:7b" для Ollama или "gpt-4o-mini" для OpenAI)
            temperature: Температура для генерации (по умолчанию 0.7)
            api_key: API ключ для OpenAI (если не указан, используется из settings)
            **llm_kwargs: Дополнительные параметры для LLM
        """
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
        
        self.llm_provider.initialize()
        self.init_theory_session()
    
    @log_function_execution
    def init_theory_session(self):
        """Инициализация сессии для теории"""
        if 'theory_state' not in st.session_state:
            st.session_state.theory_state = {
                'current_page': 'subjects',
                'selected_subject': None,
                'selected_section': None,
                'selected_topic': None,
                'explanation_text': None
            }
    
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
            st.session_state.theory_state['explanation_text'] = None
            return None
        
        cleaned_text = self._clean_text_from_cursor(text)
        st.session_state.theory_state['explanation_text'] = cleaned_text
        return cleaned_text
    
    @log_function_execution
    def show_theory_interface(self):
        """Главный интерфейс теории"""
        self.init_theory_session()
        
        st.header("📚 Теоретические материалы")
        self.show_navigation()
        
        page = st.session_state.theory_state['current_page']
        if page == 'subjects':
            self.show_subjects()
        elif page == 'sections':
            self.show_sections()
        elif page == 'topics':
            self.show_topics()
        elif page == 'explanation':
            self.show_explanation()
    
    def show_navigation(self):
        """Показать навигационные кнопки"""
        state = st.session_state.theory_state
        
        breadcrumbs = []
        if state['current_page'] != 'subjects':
            breadcrumbs.append("Предметы")
        if state['selected_subject'] and state['current_page'] not in ['subjects', 'sections']:
            breadcrumbs.append(state['selected_subject'])
        if state['selected_section'] and state['current_page'] not in ['subjects', 'sections', 'topics']:
            breadcrumbs.append(state['selected_section'])
        if state['selected_topic']:
            breadcrumbs.append(state['selected_topic'])
        
        if breadcrumbs:
            st.markdown(" → ".join(breadcrumbs))
            st.markdown("---")
        
        if state['current_page'] != 'subjects':
            if st.button("⬅️ Назад", key="theory_back_button"):
                self.navigate_back()
                st.rerun()
    
    def navigate_back(self):
        """Навигация назад"""
        state = st.session_state.theory_state
        
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
        """Показать список предметов"""
        st.subheader("Выберите предмет:")
        
        subjects = list(self.SUBJECTS_STRUCTURE.keys())
        
        for i in range(0, len(subjects), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(subjects):
                    subject = subjects[i + j]
                    with cols[j]:
                        icon = self.SUBJECTS_STRUCTURE[subject]["icon"]
                        if st.button(f"{icon} {subject}", key=f"subject_{subject}", use_container_width=True):
                            state = st.session_state.theory_state
                            state['selected_subject'] = subject
                            state['current_page'] = 'sections'
                            state['selected_section'] = None
                            state['selected_topic'] = None
                            state['explanation_text'] = None
                            st.rerun()
    
    def show_sections(self):
        """Показать разделы выбранного предмета"""
        state = st.session_state.theory_state
        subject = state['selected_subject']
        
        if not subject:
            state['current_page'] = 'subjects'
            st.rerun()
            return
        
        icon = self.SUBJECTS_STRUCTURE[subject]["icon"]
        st.subheader(f"{icon} {subject}")
        st.write("Выберите раздел:")
        
        sections = self.SUBJECTS_STRUCTURE[subject]["sections"]
        
        for section_name in sections.keys():
            if st.button(f"📖 {section_name}", key=f"section_{section_name}", use_container_width=True):
                state['selected_section'] = section_name
                state['current_page'] = 'topics'
                state['selected_topic'] = None
                state['explanation_text'] = None
                st.rerun()
    
    def show_topics(self):
        """Показать темы выбранного раздела"""
        state = st.session_state.theory_state
        subject = state['selected_subject']
        section = state['selected_section']
        
        if not subject or not section:
            state['current_page'] = 'subjects'
            st.rerun()
            return
        
        icon = self.SUBJECTS_STRUCTURE[subject]["icon"]
        st.subheader(f"{icon} {subject} → {section}")
        st.write("Выберите тему для изучения:")
        
        topics_list = self.SUBJECTS_STRUCTURE[subject]["sections"][section]["topics"]
        
        for topic in topics_list:
            if st.button(f"🎯 {topic}", key=f"topic_{topic}", use_container_width=True):
                state['selected_topic'] = topic
                state['current_page'] = 'explanation'
                state['explanation_text'] = None
                st.rerun()
            
    @log_function_execution
    def show_explanation(self):
        """Показать объяснение выбранной темы"""
        state = st.session_state.theory_state
        subject = state['selected_subject']
        section = state['selected_section']
        topic = state['selected_topic']
        
        if not all([subject, section, topic]):
            state['current_page'] = 'subjects'
            st.rerun()
            return
        
        icon = self.SUBJECTS_STRUCTURE[subject]["icon"]
        st.subheader(f"{icon} {subject} → {section} → {topic}")
        
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
        
        if not explanation_text:
            with st.spinner("🔄 Генерирую объяснение..."):
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
        
        # Отображаем объяснение
        if explanation_text:
            clean_text = self._clean_text_from_cursor(explanation_text)
            if clean_text:
                explanation_container = st.empty()
                try:
                    explanation_container.markdown(clean_text)
                except Exception:
                    st.markdown(clean_text)
                
                if clean_text != explanation_text:
                    self._save_explanation_text(clean_text)
        
        # Кнопка для нового объяснения
        if st.button("🔄 Получить другое объяснение", key="regenerate_explanation_button"):
            state['explanation_text'] = None
            state['explanation_displayed'] = False
            st.rerun()
            
    @log_function_execution
    def get_topic_explanation(self, subject: str, section: str, topic: str, regenerate: bool = False) -> str:
        """Получить объяснение темы от LLM"""
        # Проверяем локальное объяснение
        if not regenerate:
            local_explanation = self._get_local_explanation(subject, section, topic, generate_if_missing=False)
            if local_explanation:
                return local_explanation
        
        # Пробуем использовать основной провайдер
        if self.llm_provider.is_available():
            try:
                return self._get_llm_explanation(subject, section, topic)
            except Exception:
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
        
        ollama_available = isinstance(self.llm_provider, OllamaProvider) and self.llm_provider._check_server_available()
        has_openai_key = bool(self.api_key)
        model_name = self.llm_provider.model_name
        
        if not ollama_available:
            error_msg = f"""
## {topic}

**К сожалению, не удалось сгенерировать объяснение этой темы.**

**Ollama сервер недоступен!**

**Чтобы использовать локальную модель {model_name}, выполните следующие шаги:**

1. **Убедитесь, что Ollama установлен:**
   - Скачайте с https://ollama.ai
   - Установите на ваш компьютер

2. **Запустите Ollama сервер:**
   - Откройте командную строку (терминал)
   - Выполните команду: `ollama serve`
   - Сервер должен запуститься на порту 11434

3. **Загрузите модель {model_name}:**
   - В другом окне терминала выполните: `ollama pull {model_name}`
   - Дождитесь завершения загрузки

4. **После этого обновите страницу** и попробуйте снова

**Альтернативные варианты:**
- Настройте API ключ OpenAI для использования облачной модели
- Обратитесь к учителю за дополнительной информацией
- Используйте учебники и онлайн-ресурсы

**Предмет:** {subject}  
**Раздел:** {section}  
**Тема:** {topic}

Эта тема важна для понимания дальнейшего материала. Рекомендуем изучить её более подробно.
"""
        else:
            if has_openai_key:
                error_msg = f"""## {topic}

**К сожалению, не удалось сгенерировать объяснение этой темы.**

**Ollama сервер доступен, но возникла ошибка при генерации. OpenAI также не смог сгенерировать объяснение.**

**Что можно сделать:**

1. Убедитесь, что модель {model_name} загружена: `ollama pull {model_name}`
2. Проверьте, что модель доступна: `ollama list`
3. Проверьте подключение к интернету (для OpenAI)
4. Обратитесь к учителю за дополнительной информацией
5. Используйте учебники и онлайн-ресурсы

**Предмет:** {subject}  
**Раздел:** {section}  
**Тема:** {topic}

Эта тема важна для понимания дальнейшего материала. Рекомендуем изучить её более подробно.
"""
            else:
                error_msg = f"""## {topic}

**К сожалению, не удалось сгенерировать объяснение этой темы.**

**Ollama сервер доступен, но возникла ошибка при генерации.**

**Что можно сделать:**

1. Убедитесь, что модель {model_name} загружена: `ollama pull {model_name}`
2. Проверьте, что модель доступна: `ollama list`
3. Настройте API ключ OpenAI для использования облачной модели (рекомендуется)
4. Обратитесь к учителю за дополнительной информацией
5. Используйте учебники и онлайн-ресурсы

**Предмет:** {subject}  
**Раздел:** {section}  
**Тема:** {topic}

Эта тема важна для понимания дальнейшего материала. Рекомендуем изучить её более подробно.
"""
        
        return self._clean_text_from_cursor(error_msg.strip())


# Создание экземпляра менеджера теории
# Для тестов: theory_manager = TheoryManager(llm_provider="ollama", model_name="deepseek-r1:7b", temperature=0.7)
# Для релиза: theory_manager = TheoryManager(llm_provider="openai", model_name="gpt-4o-mini", temperature=0.7)
theory_manager = TheoryManager()
