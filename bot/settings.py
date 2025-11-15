import os
from bot.prompt_loader import load_prompt

CHAT_BOT_NAME = "Помощник"
CHAT_SYSTEM_MESSAGE = load_prompt("chat_system_message.txt")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")