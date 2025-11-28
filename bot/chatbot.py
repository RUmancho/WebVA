import streamlit as st
from datetime import datetime
import json
import socket
from bot.settings import CHAT_BOT_NAME, CHAT_SYSTEM_MESSAGE
from bot.prompt_loader import load_prompt
from langchain_ollama import OllamaLLM

class ChatBot:
    """Класс для работы с чат-ботом поддержки"""
    
    def __init__(self):
        self.bot_name = CHAT_BOT_NAME
        self.system_message = CHAT_SYSTEM_MESSAGE
        # Не инициализируем session_state здесь, так как он может быть недоступен при импорте
        # Инициализация будет выполнена в show_chat_interface()
        self._init_ollama_client()
    
    def _check_ollama_server_available(self):
        """Проверка доступности Ollama сервера через проверку порта"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 11434))
            sock.close()
            return result == 0
        except Exception as e:
            print(f"Ошибка проверки доступности Ollama сервера: {e}")
            return False
    
    def _init_ollama_client(self):
        """Инициализация Ollama клиента для чат-бота"""
        # Проверяем доступность сервера перед инициализацией
        if not self._check_ollama_server_available():
            print("Ollama сервер недоступен (порт 11434 не отвечает), чат-бот будет использовать локальные ответы")
            self.ollama_client = None
            self.model_name = "deepseek-r1:7b"
            return
        
        try:
            # Пробуем использовать deepseek-r1:7b
            self.ollama_client = OllamaLLM(model="deepseek-r1:7b", temperature=0.7)
            self.model_name = "deepseek-r1:7b"
            print("Чат-бот использует модель: deepseek-r1:7b")
        except Exception as e:
            try:
                # Fallback на deepseek:7b
                print(f"Модель deepseek-r1:7b недоступна для чат-бота, пробуем deepseek:7b: {e}")
                self.ollama_client = OllamaLLM(model="deepseek:7b", temperature=0.7)
                self.model_name = "deepseek:7b"
                print("Чат-бот использует модель: deepseek:7b")
            except Exception as e2:
                try:
                    # Fallback на deepseek-coder:6.7b
                    print(f"Модель deepseek:7b недоступна, пробуем deepseek-coder:6.7b: {e2}")
                    self.ollama_client = OllamaLLM(model="deepseek-coder:6.7b", temperature=0.7)
                    self.model_name = "deepseek-coder:6.7b"
                    print("Чат-бот использует модель: deepseek-coder:6.7b")
                except Exception as e3:
                    self.ollama_client = None
                    self.model_name = "deepseek-r1:7b"
                    print(f"Ошибка инициализации Ollama клиента для чат-бота: {e3}")
                    print("Убедитесь, что Ollama установлен и модель deepseek-r1:7b загружена")
    
    def init_chat_session(self):
        """Инициализация сессии чата"""
        try:
            if 'chat_messages' not in st.session_state:
                st.session_state.chat_messages = [
                    {
                        "role": "assistant",
                        "content": f"Привет! Я {self.bot_name}, ваш помощник. Как дела? Чем могу помочь?",
                        "timestamp": datetime.now().strftime("%H:%M")
                    }
                ]
        except Exception as e:
            # Если session_state недоступен, просто игнорируем ошибку
            # Инициализация будет выполнена позже, когда session_state станет доступен
            print(f"Предупреждение: не удалось инициализировать сессию чата: {e}")
    
    def add_message(self, role, content):
        """Добавление сообщения в историю чата"""
        if 'chat_messages' not in st.session_state:
            self.init_chat_session()
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M")
        }
        st.session_state.chat_messages.append(message)
    
    def get_bot_response(self, user_message):
        """Получение ответа от бота"""
        try:
            # Инициализация сессии чата (если еще не инициализировано)
            self.init_chat_session()
            
            # Используем Ollama для чат-бота
            if self.ollama_client is not None:
                return self.get_ollama_response(user_message)
            else:
                return self.get_local_response(user_message)
        except Exception as e:
            print(f"Ошибка получения ответа от бота: {e}")
            return "Извините, произошла ошибка. Попробуйте позже или обратитесь к администратору."
    
    def get_ollama_response(self, user_message):
        """Получение ответа от Ollama (DeepSeek 7B)"""
        try:
            # Инициализация сессии чата (если еще не инициализировано)
            self.init_chat_session()
            
            if self.ollama_client is None:
                return self.get_local_response(user_message)
            
            # Формируем контекст из истории сообщений
            context_parts = [self.system_message]
            
            # Добавляем последние сообщения из истории для контекста (последние 10)
            recent_messages = st.session_state.chat_messages[-10:]
            for msg in recent_messages:
                if msg['role'] == 'user':
                    context_parts.append(f"Пользователь: {msg['content']}")
                elif msg['role'] == 'assistant':
                    context_parts.append(f"Помощник: {msg['content']}")
            
            # Добавляем текущее сообщение пользователя
            context_parts.append(f"Пользователь: {user_message}")
            context_parts.append("Помощник:")
            
            # Объединяем все в один промпт
            full_prompt = "\n".join(context_parts)
            
            # Получаем ответ от модели
            response_text = self.ollama_client.invoke(full_prompt)
            
            if not response_text:
                return self.get_local_response(user_message)
            
            # Очищаем ответ от возможных префиксов
            response_text = response_text.strip()
            if response_text.startswith("Помощник:"):
                response_text = response_text.replace("Помощник:", "").strip()
            
            return response_text
            
        except Exception as e:
            print(f"Ошибка Ollama API: {e}")
            return self.get_local_response(user_message)
    
    def _load_responses(self):
        """Загружает ответы бота из файла."""
        try:
            responses_text = load_prompt("chat_responses.json")
            if responses_text:
                return json.loads(responses_text)
            return {}
        except Exception as e:
            print(f"Ошибка загрузки ответов бота: {e}")
            return {}
    
    def get_local_response(self, user_message):
        """Локальные ответы бота (без использования API)"""
        user_message_lower = user_message.lower()
        
        # Загружаем ответы из файла
        responses = self._load_responses()
        
        # Поиск подходящего ответа
        for keyword, response in responses.items():
            if keyword in user_message_lower:
                return response
        
        # Ответы на вопросы со словом "как"
        if 'как' in user_message_lower:
            if any(word in user_message_lower for word in ['зарегистрироваться', 'регистрация']):
                return "Для регистрации нажмите кнопку 'Регистрация' на главной странице и заполните все необходимые поля."
            elif any(word in user_message_lower for word in ['войти', 'зайти']):
                return "Для входа введите ваш email и пароль на главной странице, затем нажмите 'Войти'."
            elif any(word in user_message_lower for word in ['найти', 'найдти']):
                return "После входа в систему перейдите в раздел 'Список учителей' для поиска нужного преподавателя."
        
        # Ответы на вопросы со словом "что"
        if 'что' in user_message_lower:
            if any(word in user_message_lower for word in ['делать', 'дальше']):
                return "После регистрации вы сможете:\n• Общаться со мной в чате\n• Просматривать список учителей\n• Использовать все функции системы"
        
        # Дефолтный ответ
        return "Интересный вопрос! Я стараюсь помочь с вопросами о регистрации, навигации по сайту и общими образовательными вопросами. Не могли бы вы переформулировать вопрос или задать что-то более конкретное?"
    
    def show_chat_interface(self):
        """Отображение интерфейса чата"""
        # Инициализация сессии чата (если еще не инициализировано)
        self.init_chat_session()
        
        st.header("💬 Чат с помощником")
        
        # Контейнер для сообщений
        chat_container = st.container()
        
        with chat_container:
            # Отображение истории сообщений
            for message in st.session_state.chat_messages:
                with st.chat_message(message["role"]):
                    col1, col2 = st.columns([6, 1])
                    with col1:
                        st.write(message["content"])
                    with col2:
                        st.caption(message["timestamp"])
        
        # Поле ввода сообщения
        user_input = st.chat_input("Введите ваше сообщение...")
        
        if user_input:
            # Добавляем сообщение пользователя
            self.add_message("user", user_input)
            
            # Отображаем сообщение пользователя
            with st.chat_message("user"):
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.write(user_input)
                with col2:
                    st.caption(datetime.now().strftime("%H:%M"))
            
            # Получаем и отображаем ответ бота
            with st.spinner("Помощник печатает..."):
                bot_response = self.get_bot_response(user_input)
            
            self.add_message("assistant", bot_response)
            
            with st.chat_message("assistant"):
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.write(bot_response)
                with col2:
                    st.caption(datetime.now().strftime("%H:%M"))
            
            # Обновляем интерфейс
            st.rerun()
    
    def clear_chat_history(self):
        """Очистка истории чата"""
        # Инициализация сессии чата (если еще не инициализировано)
        self.init_chat_session()
        
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": f"Привет! Я {self.bot_name}, ваш помощник. История чата очищена. Чем могу помочь?",
                "timestamp": datetime.now().strftime("%H:%M")
            }
        ]

chatbot = ChatBot()