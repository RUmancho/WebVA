"""
Модуль чат-бота для веб-интерфейса.
"""

import os
import sys
import re
from flask import session

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from logger import console

PYTHON_FILENAME = "chatbot"

try:
    import langchain_ollama
    from bot.llm import LLM, Prompt
    from bot.prompts import Math
    LLM_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] LLM модули недоступны: {e}")
    LLM_AVAILABLE = False

# ========================== НАСТРОЙКИ ==========================

MODEL_NAME = "deepseek-r1:7b"
NUM_THREADS = 1
TEMPERATURE = 0.0


class ChatBot:
    """Чат-бот для взаимодействия с пользователем."""
    
    def __init__(self):
        self.llm = None
        self._init_llm()
    
    @console.debug(PYTHON_FILENAME)
    def _init_llm(self):
        """Инициализация LLM."""
        if not LLM_AVAILABLE:
            print("[WARNING] LLM недоступен, используется заглушка")
            return
        
        try:
            self.llm = LLM(
                langchain_ollama.OllamaLLM,
                MODEL_NAME,
                num_thread=NUM_THREADS,
                temperature=TEMPERATURE
            )
            print(f"[INFO] LLM инициализирован: {MODEL_NAME}")
        except Exception as e:
            print(f"[ERROR] Ошибка инициализации LLM: {e}")
            self.llm = None
    
    @console.debug(PYTHON_FILENAME)
    def init_chat_session(self):
        """Инициализация сессии чата."""
        if 'chat_messages' not in session:
            session['chat_messages'] = []
    
    @console.debug(PYTHON_FILENAME)
    def add_message(self, role: str, content: str):
        """Добавить сообщение в историю чата."""
        self.init_chat_session()
        session['chat_messages'].append({
            'role': role,
            'content': content
        })
        session.modified = True
    
    @console.debug(PYTHON_FILENAME)
    def get_chat_history(self) -> list:
        """Получить историю чата."""
        self.init_chat_session()
        return session.get('chat_messages', [])
    
    @console.debug(PYTHON_FILENAME)
    def clear_chat_history(self):
        """Очистить историю чата."""
        session['chat_messages'] = []
        session.modified = True
    
    @console.debug(PYTHON_FILENAME)
    def get_bot_response(self, user_message: str) -> str:
        """
        Получить ответ бота на сообщение пользователя.
        
        Args:
            user_message: Сообщение пользователя
        
        Returns:
            str: Ответ бота
        """
        if not self.llm:
            return self._get_fallback_response(user_message)
        
        try:
            # Создаём промпт для чата
            prompt = Prompt(
                role="Ты дружелюбный AI-помощник по обучению. Отвечай на русском языке, используй Markdown форматирование. НЕ используй LaTeX ($$ или $)!",
                task=f"Ответь на вопрос пользователя: {user_message}",
                answer="Дай полезный и понятный ответ на русском языке."
            )
            
            response = self.llm.ask(prompt)
            
            # Очищаем ответ от тегов размышлений deepseek
            response = self._clean_response(response)
            
            return response if response else self._get_fallback_response(user_message)
            
        except Exception as e:
            print(f"[ERROR] Ошибка получения ответа от LLM: {e}")
            return self._get_fallback_response(user_message)
    
    @console.debug(PYTHON_FILENAME)
    def _clean_response(self, response: str) -> str:
        """Очистить ответ от служебных тегов."""
        if not response:
            return ""
        
        # Удаляем теги <think>...</think> от deepseek-r1
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        response = response.strip()
        
        return response
    
    @console.debug(PYTHON_FILENAME)
    def _get_fallback_response(self, user_message: str) -> str:
        """Заглушка ответа когда LLM недоступен."""
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ['привет', 'здравствуй', 'добрый']):
            return "Привет! Я AI-помощник. Чем могу помочь?"
        
        if any(word in user_lower for word in ['помощь', 'помоги', 'как']):
            return "Я могу помочь с:\n- Объяснением теории\n- Генерацией заданий\n- Ответами на вопросы по математике"
        
        if any(word in user_lower for word in ['спасибо', 'благодар']):
            return "Рад помочь! Если есть ещё вопросы - спрашивайте."
        
        return "Извините, в данный момент AI-модель недоступна. Попробуйте позже или обратитесь к разделам Теория и Тестирование."
    
    @console.debug(PYTHON_FILENAME)
    def explain_theory(self, topic: str) -> str:
        """
        Объяснить теорию по теме.
        
        Args:
            topic: Название темы
        
        Returns:
            str: Объяснение теории
        """
        if not self.llm:
            return "LLM недоступен для генерации теории."
        
        topics_map = {
            "linear_equations": Math.Theory.linear_equations,
            "quadratic_equations": Math.Theory.quadratic_equations,
            "fractions": Math.Theory.fractions,
            "proportions": Math.Theory.proportions,
            "percentages": Math.Theory.percentages,
            "powers": Math.Theory.powers,
            "roots": Math.Theory.roots,
            "systems_of_equations": Math.Theory.systems_of_equations,
            "inequalities": Math.Theory.inequalities,
            "functions": Math.Theory.functions,
            "pythagorean_theorem": Math.Theory.pythagorean_theorem,
            "trigonometry": Math.Theory.trigonometry,
            "areas": Math.Theory.areas,
            "volumes": Math.Theory.volumes,
            "probability": Math.Theory.probability,
        }
        
        prompt = topics_map.get(topic)
        if not prompt:
            return f"Неизвестная тема: {topic}"
        
        try:
            response = self.llm.ask(prompt)
            return self._clean_response(response)
        except Exception as e:
            print(f"[ERROR] Ошибка генерации теории: {e}")
            return f"Ошибка генерации теории: {e}"
    
    @console.debug(PYTHON_FILENAME)
    def generate_tasks(self, topic: str, difficulty: str, n: int) -> str:
        """
        Сгенерировать задания по теме.
        
        Args:
            topic: Название темы
            difficulty: Уровень сложности (easy, standard, hard)
            n: Количество заданий
        
        Returns:
            str: Сгенерированные задания
        """
        if not self.llm:
            return "LLM недоступен для генерации заданий."
        
        easy_topics = {
            "linear_equations": Math.Test.Easy.linear_equations,
            "fractions": Math.Test.Easy.fractions,
            "percentages": Math.Test.Easy.percentages,
            "powers": Math.Test.Easy.powers,
            "roots": Math.Test.Easy.roots,
            "arithmetic": Math.Test.Easy.arithmetic,
        }
        
        standard_topics = {
            "linear_equations": Math.Test.Standard.linear_equations,
            "quadratic_equations": Math.Test.Standard.quadratic_equations,
            "fractions": Math.Test.Standard.fractions,
            "systems_of_equations": Math.Test.Standard.systems_of_equations,
            "inequalities": Math.Test.Standard.inequalities,
            "word_problems": Math.Test.Standard.word_problems,
            "geometry": Math.Test.Standard.geometry,
            "trigonometry": Math.Test.Standard.trigonometry,
            "probability": Math.Test.Standard.probability,
        }
        
        hard_topics = {
            "algebra": Math.Test.Hard.algebra,
            "geometry": Math.Test.Hard.geometry,
            "combinatorics": Math.Test.Hard.combinatorics,
            "number_theory": Math.Test.Hard.number_theory,
            "logic": Math.Test.Hard.logic,
            "functions": Math.Test.Hard.functions,
            "inequalities": Math.Test.Hard.inequalities,
            "sequences": Math.Test.Hard.sequences,
        }
        
        difficulty_map = {
            "easy": easy_topics,
            "standard": standard_topics,
            "hard": hard_topics,
        }
        
        topics = difficulty_map.get(difficulty)
        if not topics:
            return f"Неизвестная сложность: {difficulty}"
        
        prompt = topics.get(topic)
        if not prompt:
            return f"Неизвестная тема для уровня {difficulty}: {topic}"
        
        try:
            response = self.llm.ask_with_params(prompt, n=n)
            return self._clean_response(response)
        except Exception as e:
            print(f"[ERROR] Ошибка генерации заданий: {e}")
            return f"Ошибка генерации заданий: {e}"


# Глобальный экземпляр чат-бота
chatbot = ChatBot()
