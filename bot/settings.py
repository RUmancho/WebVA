"""
Настройки для бота.
"""

import os

# API ключ
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Настройки модели
MODEL_NAME = "deepseek-r1:7b"
FALLBACK_MODEL = "deepseek:7b"
OPENAI_MODEL = "gpt-4o-mini"

# Настройки генерации
NUM_THREADS = 1
TEMPERATURE = 0.0
