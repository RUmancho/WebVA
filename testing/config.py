"""
Конфигурация генераторов заданий.
Определяет, какой генератор использовать для каждой темы.
"""

from enum import Enum
from typing import Dict, Any


class GeneratorType(Enum):
    """Типы генераторов"""
    DLL = "DLL"      # Быстрый DLL генератор (для математики)
    AI = "AI"        # AI генератор (для остальных предметов)
    LOCAL = "LOCAL"  # Локальная база вопросов (fallback)


# ========================== КОНФИГУРАЦИЯ ГЕНЕРАТОРОВ ==========================
# Структура: Предмет -> Раздел -> Тема -> Тип генератора
# Если темы нет в словаре - используется AI по умолчанию

GENERATORS: Dict[str, Dict[str, Dict[str, GeneratorType]]] = {
    
    # ========================== АЛГЕБРА ==========================
    "Алгебра": {
        "Уравнения": {
            "Линейные уравнения": GeneratorType.DLL,
            "Квадратные уравнения": GeneratorType.DLL,
            "Системы уравнений": GeneratorType.AI,
            "Иррациональные уравнения": GeneratorType.AI,
            "Показательные уравнения": GeneratorType.DLL,
            "Логарифмические уравнения": GeneratorType.AI,
        },
        "Функции": {
            "Линейная функция": GeneratorType.AI,
            "Квадратичная функция": GeneratorType.AI,
            "Степенная функция": GeneratorType.AI,
            "Показательная функция": GeneratorType.AI,
            "Логарифмическая функция": GeneratorType.AI,
            "Тригонометрические функции": GeneratorType.AI,
        },
        "Неравенства": {
            "Линейные неравенства": GeneratorType.DLL,
            "Квадратные неравенства": GeneratorType.DLL,
        },
        "Прогрессии": {
            "Арифметическая прогрессия": GeneratorType.AI,
            "Геометрическая прогрессия": GeneratorType.AI,
            "Бесконечно убывающая прогрессия": GeneratorType.AI,
        },
    },
    
    # ========================== ГЕОМЕТРИЯ ==========================
    "Геометрия": {
        "Планиметрия": {
            "Треугольники": GeneratorType.AI,
            "Четырехугольники": GeneratorType.AI,
            "Окружность": GeneratorType.AI,
            "Многоугольники": GeneratorType.AI,
            "Площади фигур": GeneratorType.AI,
            "Подобие": GeneratorType.AI,
        },
        "Стереометрия": {
            "Прямые и плоскости": GeneratorType.AI,
            "Многогранники": GeneratorType.AI,
            "Призма": GeneratorType.AI,
            "Пирамида": GeneratorType.AI,
            "Цилиндр": GeneratorType.AI,
            "Конус": GeneratorType.AI,
            "Шар": GeneratorType.AI,
            "Объемы тел": GeneratorType.AI,
        },
        "Теоремы": {
            "Теорема Пифагора": GeneratorType.AI,
            "Теорема косинусов": GeneratorType.AI,
            "Теорема синусов": GeneratorType.AI,
            "Теорема о площади треугольника": GeneratorType.AI,
            "Теоремы о параллельных прямых": GeneratorType.AI,
            "Теоремы о подобии": GeneratorType.AI,
        },
    },
    
    # ========================== ФИЗИКА ==========================
    "Физика": {
        "Механика": {
            "Кинематика": GeneratorType.AI,
            "Динамика": GeneratorType.AI,
            "Законы Ньютона": GeneratorType.AI,
            "Импульс": GeneratorType.AI,
            "Энергия": GeneratorType.AI,
            "Колебания и волны": GeneratorType.AI,
        },
        "Термодинамика": {
            "Температура и теплота": GeneratorType.AI,
            "Газовые законы": GeneratorType.AI,
            "Первый закон термодинамики": GeneratorType.AI,
            "Второй закон термодинамики": GeneratorType.AI,
            "Тепловые машины": GeneratorType.AI,
        },
        "Электричество": {
            "Электростатика": GeneratorType.AI,
            "Постоянный ток": GeneratorType.AI,
            "Магнетизм": GeneratorType.AI,
            "Электромагнитная индукция": GeneratorType.AI,
            "Переменный ток": GeneratorType.AI,
        },
        "Оптика": {
            "Геометрическая оптика": GeneratorType.AI,
            "Линзы": GeneratorType.AI,
            "Волновая оптика": GeneratorType.AI,
            "Интерференция": GeneratorType.AI,
            "Дифракция": GeneratorType.AI,
        },
    },
    
    # ========================== ХИМИЯ ==========================
    "Химия": {
        "Общая химия": {
            "Атомное строение": GeneratorType.AI,
            "Периодическая система": GeneratorType.AI,
            "Химическая связь": GeneratorType.AI,
            "Валентность": GeneratorType.AI,
            "Степень окисления": GeneratorType.AI,
            "Типы химических реакций": GeneratorType.AI,
        },
        "Неорганическая химия": {
            "Металлы": GeneratorType.AI,
            "Неметаллы": GeneratorType.AI,
            "Кислоты": GeneratorType.AI,
            "Основания": GeneratorType.AI,
            "Соли": GeneratorType.AI,
            "Оксиды": GeneratorType.AI,
        },
        "Органическая химия": {
            "Углеводороды": GeneratorType.AI,
            "Спирты": GeneratorType.AI,
            "Альдегиды и кетоны": GeneratorType.AI,
            "Карбоновые кислоты": GeneratorType.AI,
            "Амины": GeneratorType.AI,
            "Белки и углеводы": GeneratorType.AI,
        },
    },
    
    # ========================== РУССКИЙ ЯЗЫК ==========================
    "Русский язык": {
        "Морфология": {
            "Имя существительное": GeneratorType.AI,
            "Имя прилагательное": GeneratorType.AI,
            "Глагол": GeneratorType.AI,
            "Наречие": GeneratorType.AI,
            "Местоимение": GeneratorType.AI,
            "Числительное": GeneratorType.AI,
        },
        "Синтаксис": {
            "Простое предложение": GeneratorType.AI,
            "Сложное предложение": GeneratorType.AI,
            "Однородные члены": GeneratorType.AI,
            "Обособленные члены": GeneratorType.AI,
            "Вводные слова": GeneratorType.AI,
            "Прямая и косвенная речь": GeneratorType.AI,
        },
        "Орфография": {
            "Правописание корней": GeneratorType.AI,
            "Правописание приставок": GeneratorType.AI,
            "Правописание суффиксов": GeneratorType.AI,
            "Правописание окончаний": GeneratorType.AI,
            "НЕ с разными частями речи": GeneratorType.AI,
            "Н и НН в разных частях речи": GeneratorType.AI,
        },
    },
    
    # ========================== АНГЛИЙСКИЙ ЯЗЫК ==========================
    "Английский язык": {
        "Грамматика": {
            "Времена глаголов": GeneratorType.AI,
            "Артикли": GeneratorType.AI,
            "Местоимения": GeneratorType.AI,
            "Модальные глаголы": GeneratorType.AI,
            "Условные предложения": GeneratorType.AI,
            "Пассивный залог": GeneratorType.AI,
        },
        "Лексика": {
            "Фразовые глаголы": GeneratorType.AI,
            "Идиомы": GeneratorType.AI,
            "Словообразование": GeneratorType.AI,
            "Синонимы и антонимы": GeneratorType.AI,
            "Устойчивые выражения": GeneratorType.AI,
        },
        "Разговорная речь": {
            "Повседневные диалоги": GeneratorType.AI,
            "Описание людей и мест": GeneratorType.AI,
            "Выражение мнения": GeneratorType.AI,
            "Рассказ о событиях": GeneratorType.AI,
            "Деловое общение": GeneratorType.AI,
        },
    },
    
    # ========================== ИСТОРИЯ ==========================
    "История": {
        "Древний мир": {
            "Первобытное общество": GeneratorType.AI,
            "Древний Египет": GeneratorType.AI,
            "Древняя Греция": GeneratorType.AI,
            "Древний Рим": GeneratorType.AI,
            "Древний Восток": GeneratorType.AI,
            "Великое переселение народов": GeneratorType.AI,
        },
        "Средние века": {
            "Феодализм": GeneratorType.AI,
            "Крестовые походы": GeneratorType.AI,
            "Византийская империя": GeneratorType.AI,
            "Арабские завоевания": GeneratorType.AI,
            "Монгольские завоевания": GeneratorType.AI,
            "Возрождение": GeneratorType.AI,
        },
        "Новое время": {
            "Великие географические открытия": GeneratorType.AI,
            "Реформация": GeneratorType.AI,
            "Промышленная революция": GeneratorType.AI,
            "Французская революция": GeneratorType.AI,
            "Наполеоновские войны": GeneratorType.AI,
            "Колониализм": GeneratorType.AI,
        },
    },
    
    # ========================== ОБЩЕСТВОЗНАНИЕ ==========================
    "Обществознание": {
        "Человек и общество": {
            "Природа человека": GeneratorType.AI,
            "Социализация": GeneratorType.AI,
            "Общество как система": GeneratorType.AI,
            "Социальные институты": GeneratorType.AI,
            "Культура": GeneratorType.AI,
            "Глобализация": GeneratorType.AI,
        },
        "Политика": {
            "Государство": GeneratorType.AI,
            "Формы правления": GeneratorType.AI,
            "Политические режимы": GeneratorType.AI,
            "Избирательные системы": GeneratorType.AI,
            "Политические партии": GeneratorType.AI,
            "Гражданское общество": GeneratorType.AI,
        },
        "Экономика": {
            "Рыночная экономика": GeneratorType.AI,
            "Спрос и предложение": GeneratorType.AI,
            "Конкуренция": GeneratorType.AI,
            "Деньги и банки": GeneratorType.AI,
            "Инфляция": GeneratorType.AI,
            "Безработица": GeneratorType.AI,
        },
    },
    
    # ========================== ГЕОГРАФИЯ ==========================
    "География": {
        "Физическая география": {
            "Литосфера": GeneratorType.AI,
            "Атмосфера": GeneratorType.AI,
            "Гидросфера": GeneratorType.AI,
            "Биосфера": GeneratorType.AI,
            "Климат": GeneratorType.AI,
            "Природные зоны": GeneratorType.AI,
        },
        "Экономическая география": {
            "Население мира": GeneratorType.AI,
            "Промышленность": GeneratorType.AI,
            "Сельское хозяйство": GeneratorType.AI,
            "Транспорт": GeneratorType.AI,
            "Мировое хозяйство": GeneratorType.AI,
            "Глобальные проблемы": GeneratorType.AI,
        },
        "География России": {
            "Географическое положение": GeneratorType.AI,
            "Рельеф и недра": GeneratorType.AI,
            "Климат России": GeneratorType.AI,
            "Внутренние воды": GeneratorType.AI,
            "Природные зоны России": GeneratorType.AI,
            "Население России": GeneratorType.AI,
        },
    },
    
    # ========================== ИНФОРМАТИКА ==========================
    "Информатика": {
        "Основы программирования": {
            "Алгоритмы": GeneratorType.AI,
            "Переменные и типы данных": GeneratorType.AI,
            "Условные операторы": GeneratorType.AI,
            "Циклы": GeneratorType.AI,
            "Функции": GeneratorType.AI,
            "Массивы": GeneratorType.AI,
        },
        "Информация и данные": {
            "Системы счисления": GeneratorType.AI,
            "Кодирование информации": GeneratorType.AI,
            "Базы данных": GeneratorType.AI,
            "Файловые системы": GeneratorType.AI,
            "Сжатие данных": GeneratorType.AI,
            "Защита информации": GeneratorType.AI,
        },
        "Компьютерные сети": {
            "Интернет": GeneratorType.AI,
            "Протоколы передачи данных": GeneratorType.AI,
            "Веб-технологии": GeneratorType.AI,
            "Электронная почта": GeneratorType.AI,
            "Безопасность в сети": GeneratorType.AI,
            "Облачные технологии": GeneratorType.AI,
        },
    },
    
    # ========================== БИОЛОГИЯ ==========================
    "Биология": {
        "Общая биология": {
            "Клеточная теория": GeneratorType.AI,
            "Строение клетки": GeneratorType.AI,
            "Обмен веществ": GeneratorType.AI,
            "Размножение": GeneratorType.AI,
            "Наследственность": GeneratorType.AI,
            "Эволюция": GeneratorType.AI,
        },
        "Ботаника": {
            "Строение растений": GeneratorType.AI,
            "Фотосинтез": GeneratorType.AI,
            "Размножение растений": GeneratorType.AI,
            "Систематика растений": GeneratorType.AI,
            "Экология растений": GeneratorType.AI,
            "Значение растений": GeneratorType.AI,
        },
        "Зоология": {
            "Простейшие": GeneratorType.AI,
            "Беспозвоночные": GeneratorType.AI,
            "Позвоночные": GeneratorType.AI,
            "Поведение животных": GeneratorType.AI,
            "Экология животных": GeneratorType.AI,
            "Эволюция животного мира": GeneratorType.AI,
        },
    },
}


# ========================== МАППИНГ DLL МЕТОДОВ ==========================
# Связь между названием темы и методом DLL генератора

DLL_METHOD_MAPPING: Dict[str, str] = {
    # Алгебра - Уравнения
    "Линейные уравнения": "linear_equation",
    "Квадратные уравнения": "quadratic_equation",
    "Показательные уравнения": "exponential_equation",
    # Алгебра - Неравенства
    "Линейные неравенства": "linear_inequality",
    "Квадратные неравенства": "quadratic_inequality",
}


def get_generator_type(subject: str, section: str, topic: str) -> GeneratorType:
    """
    Получить тип генератора для указанной темы.
    
    Args:
        subject: Название предмета
        section: Название раздела
        topic: Название темы
    
    Returns:
        GeneratorType: Тип генератора (DLL, AI или LOCAL)
    """
    try:
        return GENERATORS.get(subject, {}).get(section, {}).get(topic, GeneratorType.AI)
    except Exception:
        return GeneratorType.AI


def get_dll_method(topic: str) -> str:
    """
    Получить название метода DLL для темы.
    
    Args:
        topic: Название темы
    
    Returns:
        str: Название метода или пустая строка
    """
    return DLL_METHOD_MAPPING.get(topic, "")


def is_dll_supported(topic: str) -> bool:
    """
    Проверить, поддерживается ли тема DLL генератором.
    
    Args:
        topic: Название темы
    
    Returns:
        bool: True если тема поддерживается DLL
    """
    return topic in DLL_METHOD_MAPPING

