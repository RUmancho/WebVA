"""
LLM сервис.
Чистый интерфейс для взаимодействия с языковыми моделями.
Не содержит путей к промптам или бизнес-логики.
"""

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from bot.prompt import Prompt
from logger import console
from messages.system import LLM_ACCESS_ERROR

from logger.tracer import trace


PYTHON_FILENAME = "llm"


class LlmAccessError(Exception):
    """Invalid API key, auth failure, or LLM provider unreachable."""

    def __init__(self, detail: str = "") -> None:
        self.detail = detail
        self.user_message = LLM_ACCESS_ERROR
        super().__init__(detail or LLM_ACCESS_ERROR)


def _is_llm_access_error(exc: BaseException) -> bool:
    """True when the provider rejected the key or the API could not be reached."""
    try:
        import openai

        access_types = (
            openai.AuthenticationError,
            openai.APIConnectionError,
            openai.APITimeoutError,
            openai.PermissionDeniedError,
            openai.RateLimitError,
        )
        if isinstance(exc, access_types):
            return True
        if isinstance(exc, openai.APIStatusError):
            status_code = getattr(exc, "status_code", None)
            if status_code in (401, 402, 403, 429, 500, 502, 503):
                return True
    except Exception as e:
        print(f"[ERROR] Could not import OpenAI exception types: {e}")

    text = str(exc).lower()
    markers = (
        "incorrect api key",
        "invalid api key",
        "invalid_api_key",
        "authentication",
        "unauthorized",
        "permission denied",
        "error code: 401",
        "error code: 403",
        "error code: 402",
        "payment required",
        "insufficient credits",
        "connection error",
        "connecterror",
        "connection refused",
        "connection timed out",
        "timeout",
        "apiconnectionerror",
        "could not connect",
        "name or service not known",
        "max retries exceeded",
        "ssl",
    )
    return any(marker in text for marker in markers)


def _raise_if_access_error(exc: BaseException) -> None:
    if _is_llm_access_error(exc):
        print(f"[ERROR] LLM access problem: {exc}")
        raise LlmAccessError(str(exc)) from exc


class LLM:
    """
    Базовый класс для работы с LLM.
    
    Обеспечивает:
    - Инициализацию провайдера
    - Отправку промптов
    - Обработку ответов
    """
    
    def __init__(self, provider, model: str, **kwargs):
        """
        Инициализация LLM.
        
        Args:
            provider: Класс провайдера (например, langchain_ollama.OllamaLLM)
            model: Название модели
            **kwargs: Дополнительные параметры для провайдера
        """
        self.model = model
        self.kwargs = kwargs
        try:
            self.client = provider(model=model, **kwargs)
        except Exception as e:
            print(f"[ERROR] Ошибка инициализации LLM ({model}): {e}")
            self.client = None
    
    @trace
    def ask(self, prompt: Prompt) -> str:
        """
        Отправить промпт и получить ответ.
        
        Args:
            prompt: Объект Prompt
            
        Returns:
            str: Ответ от LLM
        """
        if not self.client:
            print("[ERROR] LLM клиент не инициализирован")
            raise LlmAccessError("LLM client is not initialized")
        
        try:
            prompt_text = prompt.build()
            
            # Проверяем тип клиента для правильного вызова
            client_type = type(self.client).__name__
            
            if 'ChatOpenAI' in client_type or 'OpenAI' in client_type:
                # Для OpenAI используем messages формат
                from langchain_core.messages import HumanMessage
                response = self.client.invoke([HumanMessage(content=prompt_text)])
                # Извлекаем текст из ответа
                if hasattr(response, 'content'):
                    return str(response.content) if response.content else ""
                else:
                    return str(response) if response else ""
            else:
                # Для Ollama и других - обычный invoke
                response = self.client.invoke(prompt_text)
                return str(response) if response else ""
                
        except LlmAccessError:
            raise
        except Exception as e:
            print(f"[ERROR] Ошибка при запросе к LLM: {e}")
            import traceback
            traceback.print_exc()
            _raise_if_access_error(e)
            return ""
    
    @trace
    def ask_raw(self, prompt_text: str) -> str:
        """
        Отправить текстовый промпт напрямую.
        
        Args:
            prompt_text: Текст промпта
            
        Returns:
            str: Ответ от LLM
        """
        if not self.client:
            print("[ERROR] LLM клиент не инициализирован")
            raise LlmAccessError("LLM client is not initialized")
        
        try:
            client_type = type(self.client).__name__
            
            if 'ChatOpenAI' in client_type or 'OpenAI' in client_type:
                # Для OpenAI используем messages формат
                from langchain_core.messages import HumanMessage
                response = self.client.invoke([HumanMessage(content=prompt_text)])
                if hasattr(response, 'content'):
                    return str(response.content) if response.content else ""
                else:
                    return str(response) if response else ""
            else:
                # Для Ollama и других
                response = self.client.invoke(prompt_text)
                return str(response) if response else ""
                
        except LlmAccessError:
            raise
        except Exception as e:
            print(f"[ERROR] Ошибка при запросе к LLM: {e}")
            import traceback
            traceback.print_exc()
            _raise_if_access_error(e)
            return ""
    
    @trace
    def ask_with_params(self, prompt: Prompt, **params) -> str:
        """
        Отправить промпт с подстановкой параметров.
        
        Args:
            prompt: Объект Prompt с плейсхолдерами
            **params: Параметры для подстановки
            
        Returns:
            str: Ответ от LLM
        """
        parameterized_prompt = prompt.with_params(**params)
        return self.ask(parameterized_prompt)
    
    def is_available(self) -> bool:
        """Проверяет доступность LLM."""
        return self.client is not None


class AcademicLLM(LLM):
    """
    LLM для академических/образовательных задач.
    Расширяет базовый LLM дополнительной функциональностью.
    """
    
    def __init__(self, provider, model: str, **kwargs):
        super().__init__(provider, model, **kwargs)
    
    @trace
    def explain(self, prompt: Prompt) -> str:
        """
        Получить объяснение темы.
        
        Args:
            prompt: Промпт для объяснения
            
        Returns:
            str: Текст объяснения
        """
        response = self.ask(prompt)
        return self._clean_response(response)
    
    @trace
    def generate_tasks(self, prompt: Prompt, count: int = 5) -> str:
        """
        Сгенерировать задания.
        
        Args:
            prompt: Промпт для генерации
            count: Количество заданий
            
        Returns:
            str: Сгенерированные задания
        """
        response = self.ask_with_params(prompt, n=count)
        return self._clean_response(response)
    
    def _clean_response(self, response: str) -> str:
        """
        Очистка ответа от служебных тегов.
        
        Args:
            response: Ответ от LLM
            
        Returns:
            str: Очищенный ответ
        """
        if not response:
            return ""
        
        import re
        
        # Удаляем теги размышлений deepseek-r1
        cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'<reasoning>.*?</reasoning>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        return cleaned.strip()
