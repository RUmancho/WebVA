import os
from bot.prompt_loader import filereader

CHAT_BOT_NAME = "Помощник"
CHAT_SYSTEM_MESSAGE = filereader("chat_system_message.txt")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")