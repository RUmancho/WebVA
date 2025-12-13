"""
Настройки для бота.
"""

import os

# API ключи
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Настройки модели
MODEL_NAME = "deepseek-r1:7b"
FALLBACK_MODEL = "deepseek:7b"
OPENAI_MODEL = "gpt-4o-mini"

# Настройки Ollama
OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11434

# Настройки генерации
NUM_THREADS = 1
TEMPERATURE = 0.0

