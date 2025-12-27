import os
import sys
import re
from flask import session

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from logger import console
from bot import chat  # Импортируем модуль с готовым LLM
from bot.llm import Prompt
from bot.prompts import Math

PYTHON_FILENAME = "chatbot"


class ChatBot:
    """Чат-бот для взаимодействия с пользователем."""
    
    def __init__(self):
        self.llm = chat.academic
    
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
            
        except Exception:
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
        
        return "Извините, произошла ошибка. Попробуйте переформулировать вопрос."
    
    @console.debug(PYTHON_FILENAME)
    def explain_theory(self, topic: str) -> str:
        """
        Объяснить теорию по теме.
        
        Args:
            topic: Название темы
        
        Returns:
            str: Объяснение теории
        """
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
            return f"Ошибка генерации теории: {e}"


# Глобальный экземпляр чат-бота
chatbot = ChatBot()
