import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from bot.llm import Prompt

#Модуль готовых промптов для объяснения теории и генерации заданий по математике.
# ========================== ПУТИ К ПАПКАМ ==========================

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
ROLES_DIR = os.path.join(PROMPTS_DIR, "roles")
TASKS_DIR = os.path.join(PROMPTS_DIR, "tasks")
ANSWERS_DIR = os.path.join(PROMPTS_DIR, "answers")

# ========================== ЗАГРУЗКА РОЛЕЙ ==========================

ROLE_MATH_TEACHER = Prompt.load(os.path.join(ROLES_DIR, "math_teacher.txt"))
ROLE_TASK_GENERATOR = Prompt.load(os.path.join(ROLES_DIR, "task_generator.txt"))

# ========================== ЗАГРУЗКА ФОРМАТОВ ОТВЕТОВ ==========================

ANSWER_DETAILED = Prompt.load(os.path.join(ANSWERS_DIR, "detailed.txt"))
ANSWER_CONCISE = Prompt.load(os.path.join(ANSWERS_DIR, "concise.txt"))
ANSWER_TASK_FORMAT = Prompt.load(os.path.join(ANSWERS_DIR, "task_format.txt"))

# ========================== ЗАГРУЗКА ЗАДАЧ ТЕОРИИ ==========================

TASK_THEORY_LINEAR_EQUATIONS = Prompt.load(os.path.join(TASKS_DIR, "theory_linear_equations.txt"))
TASK_THEORY_QUADRATIC_EQUATIONS = Prompt.load(os.path.join(TASKS_DIR, "theory_quadratic_equations.txt"))
TASK_THEORY_FRACTIONS = Prompt.load(os.path.join(TASKS_DIR, "theory_fractions.txt"))
TASK_THEORY_PROPORTIONS = Prompt.load(os.path.join(TASKS_DIR, "theory_proportions.txt"))
TASK_THEORY_PERCENTAGES = Prompt.load(os.path.join(TASKS_DIR, "theory_percentages.txt"))
TASK_THEORY_POWERS = Prompt.load(os.path.join(TASKS_DIR, "theory_powers.txt"))
TASK_THEORY_ROOTS = Prompt.load(os.path.join(TASKS_DIR, "theory_roots.txt"))
TASK_THEORY_SYSTEMS_OF_EQUATIONS = Prompt.load(os.path.join(TASKS_DIR, "theory_systems_of_equations.txt"))
TASK_THEORY_INEQUALITIES = Prompt.load(os.path.join(TASKS_DIR, "theory_inequalities.txt"))
TASK_THEORY_FUNCTIONS = Prompt.load(os.path.join(TASKS_DIR, "theory_functions.txt"))
TASK_THEORY_PYTHAGOREAN_THEOREM = Prompt.load(os.path.join(TASKS_DIR, "theory_pythagorean_theorem.txt"))
TASK_THEORY_TRIGONOMETRY = Prompt.load(os.path.join(TASKS_DIR, "theory_trigonometry.txt"))
TASK_THEORY_AREAS = Prompt.load(os.path.join(TASKS_DIR, "theory_areas.txt"))
TASK_THEORY_VOLUMES = Prompt.load(os.path.join(TASKS_DIR, "theory_volumes.txt"))
TASK_THEORY_PROBABILITY = Prompt.load(os.path.join(TASKS_DIR, "theory_probability.txt"))

# ========================== ЗАГРУЗКА ЗАДАЧ EASY ==========================

TASK_TEST_EASY_LINEAR_EQUATIONS = Prompt.load(os.path.join(TASKS_DIR, "test_easy_linear_equations.txt"))
TASK_TEST_EASY_FRACTIONS = Prompt.load(os.path.join(TASKS_DIR, "test_easy_fractions.txt"))
TASK_TEST_EASY_PERCENTAGES = Prompt.load(os.path.join(TASKS_DIR, "test_easy_percentages.txt"))
TASK_TEST_EASY_POWERS = Prompt.load(os.path.join(TASKS_DIR, "test_easy_powers.txt"))
TASK_TEST_EASY_ROOTS = Prompt.load(os.path.join(TASKS_DIR, "test_easy_roots.txt"))
TASK_TEST_EASY_ARITHMETIC = Prompt.load(os.path.join(TASKS_DIR, "test_easy_arithmetic.txt"))

# ========================== ЗАГРУЗКА ЗАДАЧ STANDARD ==========================

TASK_TEST_STANDARD_LINEAR_EQUATIONS = Prompt.load(os.path.join(TASKS_DIR, "test_standard_linear_equations.txt"))
TASK_TEST_STANDARD_QUADRATIC_EQUATIONS = Prompt.load(os.path.join(TASKS_DIR, "test_standard_quadratic_equations.txt"))
TASK_TEST_STANDARD_FRACTIONS = Prompt.load(os.path.join(TASKS_DIR, "test_standard_fractions.txt"))
TASK_TEST_STANDARD_SYSTEMS_OF_EQUATIONS = Prompt.load(os.path.join(TASKS_DIR, "test_standard_systems_of_equations.txt"))
TASK_TEST_STANDARD_INEQUALITIES = Prompt.load(os.path.join(TASKS_DIR, "test_standard_inequalities.txt"))
TASK_TEST_STANDARD_WORD_PROBLEMS = Prompt.load(os.path.join(TASKS_DIR, "test_standard_word_problems.txt"))
TASK_TEST_STANDARD_GEOMETRY = Prompt.load(os.path.join(TASKS_DIR, "test_standard_geometry.txt"))
TASK_TEST_STANDARD_TRIGONOMETRY = Prompt.load(os.path.join(TASKS_DIR, "test_standard_trigonometry.txt"))
TASK_TEST_STANDARD_PROBABILITY = Prompt.load(os.path.join(TASKS_DIR, "test_standard_probability.txt"))

# ========================== ЗАГРУЗКА ЗАДАЧ HARD ==========================

TASK_TEST_HARD_ALGEBRA = Prompt.load(os.path.join(TASKS_DIR, "test_hard_algebra.txt"))
TASK_TEST_HARD_GEOMETRY = Prompt.load(os.path.join(TASKS_DIR, "test_hard_geometry.txt"))
TASK_TEST_HARD_COMBINATORICS = Prompt.load(os.path.join(TASKS_DIR, "test_hard_combinatorics.txt"))
TASK_TEST_HARD_NUMBER_THEORY = Prompt.load(os.path.join(TASKS_DIR, "test_hard_number_theory.txt"))
TASK_TEST_HARD_LOGIC = Prompt.load(os.path.join(TASKS_DIR, "test_hard_logic.txt"))
TASK_TEST_HARD_FUNCTIONS = Prompt.load(os.path.join(TASKS_DIR, "test_hard_functions.txt"))
TASK_TEST_HARD_INEQUALITIES = Prompt.load(os.path.join(TASKS_DIR, "test_hard_inequalities.txt"))
TASK_TEST_HARD_SEQUENCES = Prompt.load(os.path.join(TASKS_DIR, "test_hard_sequences.txt"))


class Math:
    """Промпты для математики."""
    
    class Theory:
        """Промпты для объяснения теории по конкретным темам."""
        linear_equations = Prompt(ROLE_MATH_TEACHER, TASK_THEORY_LINEAR_EQUATIONS, ANSWER_DETAILED)
        quadratic_equations = Prompt(ROLE_MATH_TEACHER, TASK_THEORY_QUADRATIC_EQUATIONS, ANSWER_DETAILED)
        fractions = Prompt(ROLE_MATH_TEACHER, TASK_THEORY_FRACTIONS, ANSWER_DETAILED)
        proportions = Prompt(ROLE_MATH_TEACHER, TASK_THEORY_PROPORTIONS, ANSWER_DETAILED)
        percentages = Prompt(ROLE_MATH_TEACHER, TASK_THEORY_PERCENTAGES, ANSWER_DETAILED)
        powers = Prompt(ROLE_MATH_TEACHER, TASK_THEORY_POWERS, ANSWER_DETAILED)
        roots = Prompt( ROLE_MATH_TEACHER, TASK_THEORY_ROOTS, ANSWER_DETAILED)
        systems_of_equations = Prompt(ROLE_MATH_TEACHER, TASK_THEORY_SYSTEMS_OF_EQUATIONS, ANSWER_DETAILED)
        inequalities = Prompt( ROLE_MATH_TEACHER, TASK_THEORY_INEQUALITIES, ANSWER_DETAILED)
        functions = Prompt(ROLE_MATH_TEACHER, TASK_THEORY_FUNCTIONS, ANSWER_DETAILED)
        pythagorean_theorem = Prompt( ROLE_MATH_TEACHER, TASK_THEORY_PYTHAGOREAN_THEOREM, ANSWER_DETAILED)
        trigonometry = Prompt(ROLE_MATH_TEACHER, TASK_THEORY_TRIGONOMETRY, ANSWER_DETAILED)
        areas = Prompt( ROLE_MATH_TEACHER, TASK_THEORY_AREAS, ANSWER_DETAILED)
        volumes = Prompt( ROLE_MATH_TEACHER, TASK_THEORY_VOLUMES, ANSWER_DETAILED)
        probability = Prompt( ROLE_MATH_TEACHER, TASK_THEORY_PROBABILITY, ANSWER_DETAILED)
    
    class Test:
        """Промпты для генерации заданий."""
        class Easy:
            """Лёгкий уровень - задания решаются в уме."""
            linear_equations = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_EASY_LINEAR_EQUATIONS, ANSWER_TASK_FORMAT)
            fractions = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_EASY_FRACTIONS, ANSWER_TASK_FORMAT)
            percentages = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_EASY_PERCENTAGES, ANSWER_TASK_FORMAT)
            powers = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_EASY_POWERS, ANSWER_TASK_FORMAT)
            roots = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_EASY_ROOTS, ANSWER_TASK_FORMAT)
            arithmetic = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_EASY_ARITHMETIC, ANSWER_TASK_FORMAT)
        
        class Standard:
            """Стандартный уровень - школьные задач"""
            linear_equations = Prompt( ROLE_TASK_GENERATOR, TASK_TEST_STANDARD_LINEAR_EQUATIONS, ANSWER_TASK_FORMAT)
            quadratic_equations = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_STANDARD_QUADRATIC_EQUATIONS, ANSWER_TASK_FORMAT)
            fractions = Prompt( ROLE_TASK_GENERATOR, TASK_TEST_STANDARD_FRACTIONS, ANSWER_TASK_FORMAT)
            systems_of_equations = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_STANDARD_SYSTEMS_OF_EQUATIONS, ANSWER_TASK_FORMAT)
            inequalities = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_STANDARD_INEQUALITIES, ANSWER_TASK_FORMAT)
            word_problems = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_STANDARD_WORD_PROBLEMS, ANSWER_TASK_FORMAT)
            geometry = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_STANDARD_GEOMETRY, ANSWER_TASK_FORMAT)
            trigonometry = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_STANDARD_TRIGONOMETRY, ANSWER_TASK_FORMAT)
            probability = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_STANDARD_PROBABILITY, ANSWER_TASK_FORMAT)
        
        class Hard:
            """Сложный уровень - олимпиадные задач"""
            algebra = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_HARD_ALGEBRA, ANSWER_TASK_FORMAT)
            geometry = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_HARD_GEOMETRY, ANSWER_TASK_FORMAT)
            combinatorics = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_HARD_COMBINATORICS, ANSWER_TASK_FORMAT)
            number_theory = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_HARD_NUMBER_THEORY, ANSWER_TASK_FORMAT)
            logic = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_HARD_LOGIC, ANSWER_TASK_FORMAT)
            functions = Prompt(ROLE_TASK_GENERATOR,TASK_TEST_HARD_FUNCTIONS,ANSWER_TASK_FORMAT)
            inequalities = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_HARD_INEQUALITIES, ANSWER_TASK_FORMAT)
            sequences = Prompt(ROLE_TASK_GENERATOR, TASK_TEST_HARD_SEQUENCES, ANSWER_TASK_FORMAT)
