"""
Высокоуровневый AI интерфейс.
Предоставляет ChatBot и другие AI-сервисы приложению.
"""

import os
import sys
import re

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import session

from bot.prompt import Prompt
from bot.prompt_registry import Math
from bot import chat

PYTHON_FILENAME = "AI"


class ChatBot:
    """Чат-бот для взаимодействия с пользователем."""
    
    CURSOR_VARIANTS = ["▌", "▋", "▊", "▉", "█", "▐", "▎", "▍"]
    
    def __init__(self):
        self.llm = chat.academic
    
    def init_chat_session(self):
        """Инициализация сессии чата."""
        if 'chat_messages' not in session:
            session['chat_messages'] = []
    
    def add_message(self, role: str, content: str):
        """Добавить сообщение в историю чата."""
        self.init_chat_session()
        session['chat_messages'].append({
            'role': role,
            'content': content
        })
        session.modified = True
    
    def get_chat_history(self) -> list:
        """Получить историю чата."""
        self.init_chat_session()
        return session.get('chat_messages', [])
    
    def clear_chat_history(self):
        """Очистить историю чата."""
        session['chat_messages'] = []
        session.modified = True
    
    def get_bot_response(self, user_message: str) -> str:
        """
        Получить ответ бота на сообщение пользователя.
        
        Args:
            user_message: Сообщение пользователя
            
        Returns:
            str: Ответ бота
        """
        try:
            prompt = Prompt(
                role="Ты дружелюбный AI-помощник по обучению. Отвечай на русском языке, используй Markdown форматирование. НЕ используй LaTeX ($$ или $)!",
                task=f"Ответь на вопрос пользователя: {user_message}",
                answer="Дай полезный и понятный ответ на русском языке."
            )
            
            response = self.llm.ask(prompt)
            response = self._clean_response(response)
            
            return response if response else self._get_fallback_response(user_message)
            
        except Exception as e:
            print(f"[ERROR] Ошибка получения ответа бота: {e}")
            return self._get_fallback_response(user_message)
    
    def _clean_response(self, response: str) -> str:
        """Очистить ответ от служебных тегов."""
        if not response:
            return ""
        
        cleaned = str(response)
        
        # Удаляем курсоры
        for cursor in self.CURSOR_VARIANTS:
            cleaned = cleaned.replace(cursor, "")
        
        # Удаляем теги <think>...</think> от deepseek-r1
        cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'<reasoning>.*?</reasoning>', '', cleaned, flags=re.DOTALL)
        
        return cleaned.strip()
    
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
        
        prompt_factory = topics_map.get(topic)
        if not prompt_factory:
            return f"Неизвестная тема: {topic}"
        
        try:
            prompt = prompt_factory()
            response = self.llm.ask(prompt)
            return self._clean_response(response)
        except Exception as e:
            return f"Ошибка генерации теории: {e}"


# Глобальный экземпляр чат-бота
chatbot = ChatBot()
