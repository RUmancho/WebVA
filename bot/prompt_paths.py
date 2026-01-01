"""
Модуль путей к файлам промптов.
Только константы путей - никакой логики загрузки.
"""

import os

# ========================== БАЗОВЫЕ ПУТИ ==========================

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
ROLES_DIR = os.path.join(PROMPTS_DIR, "roles")
ANSWERS_DIR = os.path.join(PROMPTS_DIR, "answers")
TASKS_DIR = os.path.join(PROMPTS_DIR, "tasks")

# ========================== EXPLAIN ПУТИ ==========================

EXPLAIN_DIR = os.path.join(TASKS_DIR, "explain")
EXPLAIN_ALGEBRA = os.path.join(EXPLAIN_DIR, "algebra")
EXPLAIN_ARITHMETIC = os.path.join(EXPLAIN_DIR, "arithmetic")
EXPLAIN_GEOMETRY = os.path.join(EXPLAIN_DIR, "geometry")
EXPLAIN_TRIGONOMETRY = os.path.join(EXPLAIN_DIR, "trigonometry")
EXPLAIN_PROBABILITY = os.path.join(EXPLAIN_DIR, "probability")
EXPLAIN_GENERAL = os.path.join(EXPLAIN_DIR, "general")

# ========================== GENERATE ПУТИ ==========================

GENERATE_DIR = os.path.join(TASKS_DIR, "generate")
GENERATE_ALGEBRA = os.path.join(GENERATE_DIR, "algebra")
GENERATE_ARITHMETIC = os.path.join(GENERATE_DIR, "arithmetic")
GENERATE_GEOMETRY = os.path.join(GENERATE_DIR, "geometry")
GENERATE_TRIGONOMETRY = os.path.join(GENERATE_DIR, "trigonometry")
GENERATE_PROBABILITY = os.path.join(GENERATE_DIR, "probability")
GENERATE_NUMBER_THEORY = os.path.join(GENERATE_DIR, "number_theory")
GENERATE_GENERAL = os.path.join(GENERATE_DIR, "general")


# ========================== РОЛИ ==========================

class RolePaths:
    """Пути к файлам ролей."""
    MATH_TEACHER = os.path.join(ROLES_DIR, "math_teacher.txt")
    TASK_GENERATOR = os.path.join(ROLES_DIR, "task_generator.txt")
    CHAT_HELPER = os.path.join(ROLES_DIR, "chat_helper.txt")
    THEORY_TEACHER = os.path.join(ROLES_DIR, "theory_teacher.txt")
    UNIVERSAL_TEACHER = os.path.join(ROLES_DIR, "universal_teacher.txt")


# ========================== ОТВЕТЫ ==========================

class AnswerPaths:
    """Пути к файлам форматов ответов."""
    DETAILED = os.path.join(ANSWERS_DIR, "detailed.txt")
    CONCISE = os.path.join(ANSWERS_DIR, "concise.txt")
    CALCULATION = os.path.join(ANSWERS_DIR, "calculation.txt")
    TASK_FORMAT = os.path.join(ANSWERS_DIR, "task_format.txt")


# ========================== ТЕОРИЯ (EXPLAIN) ==========================

class TheoryPaths:
    """Пути к файлам теории по предметам."""
    
    # Алгебра
    LINEAR_EQUATIONS = os.path.join(EXPLAIN_ALGEBRA, "theory_linear_equations.txt")
    QUADRATIC_EQUATIONS = os.path.join(EXPLAIN_ALGEBRA, "theory_quadratic_equations.txt")
    POWERS = os.path.join(EXPLAIN_ALGEBRA, "theory_powers.txt")
    ROOTS = os.path.join(EXPLAIN_ALGEBRA, "theory_roots.txt")
    SYSTEMS_OF_EQUATIONS = os.path.join(EXPLAIN_ALGEBRA, "theory_systems_of_equations.txt")
    INEQUALITIES = os.path.join(EXPLAIN_ALGEBRA, "theory_inequalities.txt")
    FUNCTIONS = os.path.join(EXPLAIN_ALGEBRA, "theory_functions.txt")
    EQUATIONS = os.path.join(EXPLAIN_ALGEBRA, "equations.txt")
    EXPRESSION_VALUE = os.path.join(EXPLAIN_ALGEBRA, "expression_value.txt")
    FORMULAS_WORK = os.path.join(EXPLAIN_ALGEBRA, "formulas_work.txt")
    SHORTHAND_FORMULAS = os.path.join(EXPLAIN_ALGEBRA, "shorthand_formulas.txt")
    
    # Арифметика
    FRACTIONS = os.path.join(EXPLAIN_ARITHMETIC, "theory_fractions.txt")
    PROPORTIONS = os.path.join(EXPLAIN_ARITHMETIC, "theory_proportions.txt")
    PERCENTAGES = os.path.join(EXPLAIN_ARITHMETIC, "theory_percentages.txt")
    COMPUTATIONAL_SKILLS = os.path.join(EXPLAIN_ARITHMETIC, "computational_skills.txt")
    
    # Геометрия
    PYTHAGOREAN_THEOREM = os.path.join(EXPLAIN_GEOMETRY, "theory_pythagorean_theorem.txt")
    AREAS = os.path.join(EXPLAIN_GEOMETRY, "theory_areas.txt")
    VOLUMES = os.path.join(EXPLAIN_GEOMETRY, "theory_volumes.txt")
    TRIANGLES = os.path.join(EXPLAIN_GEOMETRY, "triangles.txt")
    QUADRILATERALS = os.path.join(EXPLAIN_GEOMETRY, "quadrilaterals.txt")
    CIRCLES = os.path.join(EXPLAIN_GEOMETRY, "circles.txt")
    AREAS_VOLUMES = os.path.join(EXPLAIN_GEOMETRY, "areas_volumes.txt")
    COORDINATE_GEOMETRY = os.path.join(EXPLAIN_GEOMETRY, "coordinate_geometry.txt")
    
    # Тригонометрия
    TRIGONOMETRY = os.path.join(EXPLAIN_TRIGONOMETRY, "theory_trigonometry.txt")
    TRIGONOMETRY_BASIC = os.path.join(EXPLAIN_TRIGONOMETRY, "trigonometry.txt")
    
    # Вероятность
    PROBABILITY = os.path.join(EXPLAIN_PROBABILITY, "theory_probability.txt")
    PROBABILITY_BASIC = os.path.join(EXPLAIN_PROBABILITY, "probability.txt")
    
    # Общие
    EXPLAIN = os.path.join(EXPLAIN_GENERAL, "explain.txt")
    EXPLAIN_BASIC = os.path.join(EXPLAIN_GENERAL, "explain_basic.txt")
    EXPLAIN_BEGINNER = os.path.join(EXPLAIN_GENERAL, "explain_beginner.txt")
    EXPLAIN_DETAILED = os.path.join(EXPLAIN_GENERAL, "explain_detailed.txt")
    EXPLAIN_FORMULAS = os.path.join(EXPLAIN_GENERAL, "explain_formulas.txt")
    EXPLAIN_PRACTICAL = os.path.join(EXPLAIN_GENERAL, "explain_practical.txt")
    EXPLAIN_SUMMARY = os.path.join(EXPLAIN_GENERAL, "explain_summary.txt")
    HELP_PROBLEM = os.path.join(EXPLAIN_GENERAL, "help_problem.txt")
    CHECK_SOLUTION = os.path.join(EXPLAIN_GENERAL, "check_solution.txt")
    TIPS = os.path.join(EXPLAIN_GENERAL, "tips.txt")
    PLAN = os.path.join(EXPLAIN_GENERAL, "plan.txt")
    GRAPHS = os.path.join(EXPLAIN_GENERAL, "graphs.txt")


# ========================== ТЕСТЫ (GENERATE) ==========================

class TestPaths:
    """Пути к файлам генерации тестов."""
    
    class Easy:
        """Лёгкий уровень."""
        LINEAR_EQUATIONS = os.path.join(GENERATE_ALGEBRA, "test_easy_linear_equations.txt")
        POWERS = os.path.join(GENERATE_ALGEBRA, "test_easy_powers.txt")
        ROOTS = os.path.join(GENERATE_ALGEBRA, "test_easy_roots.txt")
        FRACTIONS = os.path.join(GENERATE_ARITHMETIC, "test_easy_fractions.txt")
        PERCENTAGES = os.path.join(GENERATE_ARITHMETIC, "test_easy_percentages.txt")
        ARITHMETIC = os.path.join(GENERATE_ARITHMETIC, "test_easy_arithmetic.txt")
    
    class Standard:
        """Стандартный уровень."""
        LINEAR_EQUATIONS = os.path.join(GENERATE_ALGEBRA, "test_standard_linear_equations.txt")
        QUADRATIC_EQUATIONS = os.path.join(GENERATE_ALGEBRA, "test_standard_quadratic_equations.txt")
        SYSTEMS_OF_EQUATIONS = os.path.join(GENERATE_ALGEBRA, "test_standard_systems_of_equations.txt")
        INEQUALITIES = os.path.join(GENERATE_ALGEBRA, "test_standard_inequalities.txt")
        FRACTIONS = os.path.join(GENERATE_ARITHMETIC, "test_standard_fractions.txt")
        GEOMETRY = os.path.join(GENERATE_GEOMETRY, "test_standard_geometry.txt")
        TRIGONOMETRY = os.path.join(GENERATE_TRIGONOMETRY, "test_standard_trigonometry.txt")
        PROBABILITY = os.path.join(GENERATE_PROBABILITY, "test_standard_probability.txt")
        WORD_PROBLEMS = os.path.join(GENERATE_GENERAL, "test_standard_word_problems.txt")
    
    class Hard:
        """Олимпиадный уровень."""
        ALGEBRA = os.path.join(GENERATE_ALGEBRA, "test_hard_algebra.txt")
        FUNCTIONS = os.path.join(GENERATE_ALGEBRA, "test_hard_functions.txt")
        INEQUALITIES = os.path.join(GENERATE_ALGEBRA, "test_hard_inequalities.txt")
        GEOMETRY = os.path.join(GENERATE_GEOMETRY, "test_hard_geometry.txt")
        COMBINATORICS = os.path.join(GENERATE_PROBABILITY, "test_hard_combinatorics.txt")
        NUMBER_THEORY = os.path.join(GENERATE_NUMBER_THEORY, "test_hard_number_theory.txt")
        LOGIC = os.path.join(GENERATE_NUMBER_THEORY, "test_hard_logic.txt")
        SEQUENCES = os.path.join(GENERATE_NUMBER_THEORY, "test_hard_sequences.txt")
    
    class General:
        """Общие шаблоны генерации."""
        GENERATE_EASY = os.path.join(GENERATE_GENERAL, "generate_easy.txt")
        GENERATE_EASY_CHOICE = os.path.join(GENERATE_GENERAL, "generate_easy_choice.txt")
        GENERATE_EASY_MENTAL = os.path.join(GENERATE_GENERAL, "generate_easy_mental.txt")
        GENERATE_STANDARD = os.path.join(GENERATE_GENERAL, "generate_standard.txt")
        GENERATE_STANDARD_MULTI = os.path.join(GENERATE_GENERAL, "generate_standard_multi.txt")
        GENERATE_STANDARD_WORD = os.path.join(GENERATE_GENERAL, "generate_standard_word.txt")
        GENERATE_HARD = os.path.join(GENERATE_GENERAL, "generate_hard.txt")
        GENERATE_HARD_COMBINED = os.path.join(GENERATE_GENERAL, "generate_hard_combined.txt")
        GENERATE_HARD_OLYMPIAD = os.path.join(GENERATE_GENERAL, "generate_hard_olympiad.txt")
        GENERATE_HARD_RESEARCH = os.path.join(GENERATE_GENERAL, "generate_hard_research.txt")
        GENERATE_TASK = os.path.join(GENERATE_GENERAL, "generate_task.txt")
        PRACTICE = os.path.join(GENERATE_GENERAL, "practice.txt")

