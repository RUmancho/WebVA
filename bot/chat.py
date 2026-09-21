"""
Модуль чата с LLM.
Использует LLM сервис и реестр промптов.
Поддерживает OpenRouter, OpenAI и Ollama.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Загрузка .env файла из корня проекта
load_dotenv(Path(project_root) / '.env', override=True)

from bot.llm import AcademicLLM
from bot.prompt_registry import Math
from logger import console

from logger.tracer import trace

PYTHON_FILENAME = "chat"

# ========================== НАСТРОЙКИ ==========================

# Выбор провайдера LLM (можно переключать через .env)
# Варианты: "openrouter", "openai", "ollama"
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai').lower()
ACTIVE_LLM_PROVIDER = LLM_PROVIDER

# Настройки Ollama
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'deepseek-r1:7b')
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')
OLLAMA_PORT = int(os.getenv('OLLAMA_PORT', '11434'))

# Настройки OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

# Настройки OpenRouter (OpenAI-compatible API)
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '') or OPENAI_API_KEY
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'openrouter/free')
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
OPENROUTER_FALLBACK_MODELS = [
    model.strip()
    for model in os.getenv(
        'OPENROUTER_FALLBACK_MODELS',
        'nvidia/nemotron-3.5-lightning:free,z-ai/glm-5.2:free,liquid/lfm-2.5-2.6b:free',
    ).split(',')
    if model.strip() and model.strip() != OPENROUTER_MODEL
][:3]

# Общие настройки
NUM_THREADS = 1
TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.0'))


# ========================== ИНИЦИАЛИЗАЦИЯ LLM ==========================

def init_llm():
    """Инициализация LLM в зависимости от выбранного провайдера"""
    global ACTIVE_LLM_PROVIDER

    if LLM_PROVIDER == 'openrouter':
        ACTIVE_LLM_PROVIDER = 'openrouter'
        return init_openrouter()

    if LLM_PROVIDER == 'openai':
        ACTIVE_LLM_PROVIDER = 'openai'
        return init_openai()

    ACTIVE_LLM_PROVIDER = 'ollama'
    return init_ollama()


def init_openrouter():
    """Инициализация OpenRouter через OpenAI-совместимый API."""
    if not OPENROUTER_API_KEY:
        print("[ERROR] OpenRouter key is not set. Put it in OPENROUTER_API_KEY or OPENAI_API_KEY in .env")
        return None

    try:
        from langchain_openai import ChatOpenAI

        print(f"[INFO] Инициализация OpenRouter: {OPENROUTER_MODEL}")
        if OPENROUTER_FALLBACK_MODELS:
            print(f"[INFO] OpenRouter fallbacks: {', '.join(OPENROUTER_FALLBACK_MODELS)}")

        extra_body = {}
        if OPENROUTER_FALLBACK_MODELS:
            extra_body['models'] = OPENROUTER_FALLBACK_MODELS

        return AcademicLLM(
            ChatOpenAI,
            OPENROUTER_MODEL,
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            temperature=TEMPERATURE,
            max_tokens=2000,
            extra_body=extra_body or None,
            default_headers={
                "HTTP-Referer": "http://localhost:5000",
                "X-OpenRouter-Title": "WebVA",
            },
        )
    except ImportError:
        print("[ERROR] langchain-openai не установлен!")
        print("[INFO] Установите: pip install langchain-openai")
        return None
    except Exception as e:
        print(f"[ERROR] Ошибка инициализации OpenRouter: {e}")
        return None


def init_openai():
    """Инициализация OpenAI"""
    if not OPENAI_API_KEY:
        print("[ERROR] OPENAI_API_KEY не установлен! Укажите в .env файле")
        print("[INFO] Переключаюсь на Ollama...")
        return init_ollama()

    try:
        from langchain_openai import ChatOpenAI

        print(f"[INFO] Инициализация OpenAI: {OPENAI_MODEL}")
        return AcademicLLM(
            ChatOpenAI,
            OPENAI_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=TEMPERATURE,
            max_tokens=2000
        )
    except ImportError:
        print("[ERROR] langchain-openai не установлен!")
        print("[INFO] Установите: pip install langchain-openai")
        print("[INFO] Переключаюсь на Ollama...")
        return init_ollama()
    except Exception as e:
        print(f"[ERROR] Ошибка инициализации OpenAI: {e}")
        print("[INFO] Переключаюсь на Ollama...")
        return init_ollama()


def init_ollama():
    """Инициализация Ollama LLM"""
    global ACTIVE_LLM_PROVIDER
    ACTIVE_LLM_PROVIDER = 'ollama'
    try:
        import langchain_ollama
        
        print(f"[INFO] Инициализация Ollama: {OLLAMA_MODEL}")
        return AcademicLLM(
            langchain_ollama.OllamaLLM,
            OLLAMA_MODEL,
            num_thread=NUM_THREADS,
            temperature=TEMPERATURE
        )
    except ImportError:
        print("[ERROR] langchain-ollama не установлен!")
        print("[INFO] Установите: pip install langchain-ollama")
        return None
    except Exception as e:
        print(f"[ERROR] Ошибка инициализации Ollama: {e}")
        return None


# Инициализируем LLM
academic = init_llm()

if academic and academic.is_available():
    print(f"[SUCCESS] LLM инициализирован: {ACTIVE_LLM_PROVIDER.upper()} ({academic.model})")
else:
    print("[ERROR] LLM не инициализирован!")


# ========================== API ФУНКЦИИ ==========================

@trace
def explain_theory(topic: str) -> str:
    """
    Объяснить теорию по выбранной теме.
    
    Args:
        topic: Название темы (linear_equations, fractions, и т.д.)
        
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
        print(f"[WARN] Неизвестная тема: {topic}")
        return ""
    
    try:
        prompt = prompt_factory()
        return academic.explain(prompt)
    except Exception as e:
        print(f"[ERROR] Ошибка генерации теории для {topic}: {e}")
        return ""


@trace
def generate_tasks(topic: str, difficulty: str, n: int) -> str:
    """
    Сгенерировать задания по теме.
    
    Args:
        topic: Название темы
        difficulty: Уровень сложности (easy, standard, hard)
        n: Количество заданий
        
    Returns:
        str: Сгенерированные задания
    """
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
        print(f"[WARN] Неизвестная сложность: {difficulty}")
        return ""
    
    prompt_factory = topics.get(topic)
    if not prompt_factory:
        print(f"[WARN] Неизвестная тема {topic} для сложности {difficulty}")
        return ""
    
    try:
        prompt = prompt_factory()
        return academic.generate_tasks(prompt, count=n)
    except Exception as e:
        print(f"[ERROR] Ошибка генерации заданий: {e}")
        return ""
