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

PYTHON_FILENAME = "llm"


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
    
    @console.debug(PYTHON_FILENAME)
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
            return ""
        
        try:
            prompt_text = prompt.build()
            response = self.client.invoke(prompt_text)
            return str(response) if response else ""
        except Exception as e:
            print(f"[ERROR] Ошибка при запросе к LLM: {e}")
            return ""
    
    @console.debug(PYTHON_FILENAME)
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
            return ""
        
        try:
            response = self.client.invoke(prompt_text)
            return str(response) if response else ""
        except Exception as e:
            print(f"[ERROR] Ошибка при запросе к LLM: {e}")
            return ""
    
    @console.debug(PYTHON_FILENAME)
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
    
    @console.debug(PYTHON_FILENAME)
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
    
    @console.debug(PYTHON_FILENAME)
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
