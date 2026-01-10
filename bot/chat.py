"""
Модуль чата с LLM.
Использует LLM сервис и реестр промптов.
Поддерживает Ollama и OpenAI (gpt-4o-mini).
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Загрузка .env файла из корня проекта
load_dotenv(Path(project_root) / '.env')

from bot.llm import AcademicLLM
from bot.prompt_registry import Math
from logger import console

from logger.tracer import trace

PYTHON_FILENAME = "chat"

# ========================== НАСТРОЙКИ ==========================

# Выбор провайдера LLM (можно переключать через .env)
# Варианты: "ollama", "openai"
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai').lower()

# Настройки Ollama
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'deepseek-r1:7b')
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')
OLLAMA_PORT = int(os.getenv('OLLAMA_PORT', '11434'))

# Настройки OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

# Общие настройки
NUM_THREADS = 1
TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.0'))


# ========================== ИНИЦИАЛИЗАЦИЯ LLM ==========================

def init_llm():
    """Инициализация LLM в зависимости от выбранного провайдера"""
    
    if LLM_PROVIDER == 'openai':
        # Инициализация OpenAI
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
    
    else:
        # Инициализация Ollama (по умолчанию)
        return init_ollama()


def init_ollama():
    """Инициализация Ollama LLM"""
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
    print(f"[SUCCESS] LLM инициализирован: {LLM_PROVIDER.upper()}")
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
