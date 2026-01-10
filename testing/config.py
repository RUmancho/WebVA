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
        "Неорганическая химия": {
            "Строение атома": GeneratorType.AI,
            "Периодическая система": GeneratorType.AI,
            "Химическая связь": GeneratorType.AI,
            "Классы неорганических соединений": GeneratorType.AI,
            "Металлы": GeneratorType.AI,
            "Неметаллы": GeneratorType.AI,
        },
        "Органическая химия": {
            "Углеводороды": GeneratorType.AI,
            "Спирты и фенолы": GeneratorType.AI,
            "Альдегиды и кетоны": GeneratorType.AI,
            "Карбоновые кислоты": GeneratorType.AI,
            "Амины": GeneratorType.AI,
            "Белки и углеводы": GeneratorType.AI,
        },
        "Химические реакции": {
            "Типы химических реакций": GeneratorType.AI,
            "Окислительно-восстановительные реакции": GeneratorType.AI,
            "Электролитическая диссоциация": GeneratorType.AI,
            "Гидролиз": GeneratorType.AI,
            "Скорость химических реакций": GeneratorType.AI,
        },
    },
    
    # ========================== БИОЛОГИЯ ==========================
    "Биология": {
        "Ботаника": {
            "Строение растительной клетки": GeneratorType.AI,
            "Ткани растений": GeneratorType.AI,
            "Корень, стебель, лист": GeneratorType.AI,
            "Фотосинтез": GeneratorType.AI,
            "Размножение растений": GeneratorType.AI,
            "Систематика растений": GeneratorType.AI,
        },
        "Зоология": {
            "Простейшие": GeneratorType.AI,
            "Беспозвоночные": GeneratorType.AI,
            "Позвоночные": GeneratorType.AI,
            "Млекопитающие": GeneratorType.AI,
            "Птицы": GeneratorType.AI,
            "Рыбы и земноводные": GeneratorType.AI,
        },
        "Анатомия человека": {
            "Опорно-двигательная система": GeneratorType.AI,
            "Кровеносная система": GeneratorType.AI,
            "Дыхательная система": GeneratorType.AI,
            "Пищеварительная система": GeneratorType.AI,
            "Нервная система": GeneratorType.AI,
            "Органы чувств": GeneratorType.AI,
        },
        "Общая биология": {
            "Клетка": GeneratorType.AI,
            "Генетика": GeneratorType.AI,
            "Эволюция": GeneratorType.AI,
            "Экология": GeneratorType.AI,
        },
    },
    
    # ========================== РУССКИЙ ЯЗЫК ==========================
    "Русский язык": {
        "Фонетика": {
            "Звуки и буквы": GeneratorType.AI,
            "Ударение": GeneratorType.AI,
            "Слог": GeneratorType.AI,
        },
        "Морфемика": {
            "Состав слова": GeneratorType.AI,
            "Корень и основа": GeneratorType.AI,
            "Приставки и суффиксы": GeneratorType.AI,
        },
        "Морфология": {
            "Имя существительное": GeneratorType.AI,
            "Имя прилагательное": GeneratorType.AI,
            "Глагол": GeneratorType.AI,
            "Местоимение": GeneratorType.AI,
            "Наречие": GeneratorType.AI,
            "Причастие и деепричастие": GeneratorType.AI,
        },
        "Синтаксис": {
            "Словосочетание": GeneratorType.AI,
            "Простое предложение": GeneratorType.AI,
            "Сложное предложение": GeneratorType.AI,
            "Прямая и косвенная речь": GeneratorType.AI,
        },
        "Орфография": {
            "Правописание гласных": GeneratorType.AI,
            "Правописание согласных": GeneratorType.AI,
            "Правописание приставок": GeneratorType.AI,
            "НЕ с разными частями речи": GeneratorType.AI,
        },
        "Пунктуация": {
            "Знаки препинания в простом предложении": GeneratorType.AI,
            "Знаки препинания в сложном предложении": GeneratorType.AI,
            "Обособленные члены предложения": GeneratorType.AI,
        },
    },
    
    # ========================== ЛИТЕРАТУРА ==========================
    "Литература": {
        "Теория литературы": {
            "Роды и жанры литературы": GeneratorType.AI,
            "Литературные направления": GeneratorType.AI,
            "Средства художественной выразительности": GeneratorType.AI,
            "Стихосложение": GeneratorType.AI,
        },
        "Русская литература XIX века": {
            "А.С. Пушкин": GeneratorType.AI,
            "М.Ю. Лермонтов": GeneratorType.AI,
            "Н.В. Гоголь": GeneratorType.AI,
            "Л.Н. Толстой": GeneratorType.AI,
            "Ф.М. Достоевский": GeneratorType.AI,
        },
        "Русская литература XX века": {
            "М. Горький": GeneratorType.AI,
            "М.А. Булгаков": GeneratorType.AI,
            "М.А. Шолохов": GeneratorType.AI,
            "А.А. Ахматова": GeneratorType.AI,
            "Б.Л. Пастернак": GeneratorType.AI,
        },
    },
    
    # ========================== ИСТОРИЯ ==========================
    "История": {
        "История России": {
            "Древняя Русь": GeneratorType.AI,
            "Московское государство": GeneratorType.AI,
            "Российская империя": GeneratorType.AI,
            "СССР": GeneratorType.AI,
            "Современная Россия": GeneratorType.AI,
        },
        "Всеобщая история": {
            "Древний мир": GeneratorType.AI,
            "Средние века": GeneratorType.AI,
            "Новое время": GeneratorType.AI,
            "Новейшее время": GeneratorType.AI,
            "Великие географические открытия": GeneratorType.AI,
        },
        "Культура и быт": {
            "Культура Древней Руси": GeneratorType.AI,
            "Культура XVIII века": GeneratorType.AI,
            "Культура XIX века": GeneratorType.AI,
            "Культура XX века": GeneratorType.AI,
        },
    },
    
    # ========================== ОБЩЕСТВОЗНАНИЕ ==========================
    "Обществознание": {
        "Человек и общество": {
            "Природа человека": GeneratorType.AI,
            "Деятельность": GeneratorType.AI,
            "Познание": GeneratorType.AI,
            "Общество и его структура": GeneratorType.AI,
        },
        "Экономика": {
            "Экономические системы": GeneratorType.AI,
            "Рынок и рыночная экономика": GeneratorType.AI,
            "Спрос и предложение": GeneratorType.AI,
            "Деньги и инфляция": GeneratorType.AI,
            "Налоги": GeneratorType.AI,
        },
        "Политика": {
            "Государство и его формы": GeneratorType.AI,
            "Политические режимы": GeneratorType.AI,
            "Избирательные системы": GeneratorType.AI,
            "Политические партии": GeneratorType.AI,
        },
        "Право": {
            "Конституция РФ": GeneratorType.AI,
            "Права и свободы человека": GeneratorType.AI,
            "Гражданское право": GeneratorType.AI,
            "Уголовное право": GeneratorType.AI,
            "Семейное право": GeneratorType.AI,
        },
    },
    
    # ========================== АНГЛИЙСКИЙ ЯЗЫК ==========================
    "Английский язык": {
        "Грамматика": {
            "Времена глаголов": GeneratorType.AI,
            "Артикли": GeneratorType.AI,
            "Модальные глаголы": GeneratorType.AI,
            "Пассивный залог": GeneratorType.AI,
            "Условные предложения": GeneratorType.AI,
        },
        "Лексика": {
            "Словообразование": GeneratorType.AI,
            "Фразовые глаголы": GeneratorType.AI,
            "Идиомы": GeneratorType.AI,
            "Устойчивые выражения": GeneratorType.AI,
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
        },
        "Системы счисления": {
            "Двоичная система": GeneratorType.AI,
            "Восьмеричная система": GeneratorType.AI,
            "Шестнадцатеричная система": GeneratorType.AI,
            "Перевод чисел": GeneratorType.AI,
        },
        "Логика": {
            "Логические операции": GeneratorType.AI,
            "Таблицы истинности": GeneratorType.AI,
            "Логические выражения": GeneratorType.AI,
        },
    },
    
    # ========================== ГЕОГРАФИЯ ==========================
    "География": {
        "Физическая география": {
            "План и карта": GeneratorType.AI,
            "Литосфера": GeneratorType.AI,
            "Гидросфера": GeneratorType.AI,
            "Атмосфера": GeneratorType.AI,
            "Биосфера": GeneratorType.AI,
        },
        "География России": {
            "Географическое положение России": GeneratorType.AI,
            "Рельеф и полезные ископаемые": GeneratorType.AI,
            "Климат": GeneratorType.AI,
            "Внутренние воды": GeneratorType.AI,
            "Природные зоны": GeneratorType.AI,
        },
        "Экономическая география": {
            "Население": GeneratorType.AI,
            "Хозяйство России": GeneratorType.AI,
            "Промышленность": GeneratorType.AI,
            "Сельское хозяйство": GeneratorType.AI,
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

