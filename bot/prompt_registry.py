"""
Реестр готовых промптов.
Комбинирует пути, загрузчик и модель Prompt.
"""

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from bot.prompt import Prompt
from bot.prompt_loader import PromptLoader, load_prompt_safe
from bot.prompt_paths import RolePaths, AnswerPaths, TheoryPaths, TestPaths


class PromptFactory:
    """
    Фабрика для создания промптов.
    Загружает компоненты из файлов и собирает Prompt.
    """
    
    @staticmethod
    def create(role_path: str, task_path: str, answer_path: str) -> Prompt:
        """
        Создаёт Prompt из трёх файлов.
        
        Args:
            role_path: Путь к файлу роли
            task_path: Путь к файлу задачи
            answer_path: Путь к файлу формата ответа
            
        Returns:
            Prompt: Готовый промпт
        """
        role = load_prompt_safe(role_path)
        task = load_prompt_safe(task_path)
        answer = load_prompt_safe(answer_path)
        return Prompt(role=role, task=task, answer=answer)
    
    @staticmethod
    def create_from_strings(role: str, task: str, answer: str) -> Prompt:
        """Создаёт Prompt из строк напрямую."""
        return Prompt(role=role, task=task, answer=answer)


# ========================== ГОТОВЫЕ РОЛИ (загруженные строки) ==========================

class Roles:
    """Загруженные роли для использования в промптах."""
    
    @staticmethod
    def math_teacher() -> str:
        return load_prompt_safe(RolePaths.MATH_TEACHER)
    
    @staticmethod
    def task_generator() -> str:
        return load_prompt_safe(RolePaths.TASK_GENERATOR)
    
    @staticmethod
    def chat_helper() -> str:
        return load_prompt_safe(RolePaths.CHAT_HELPER)
    
    @staticmethod
    def theory_teacher() -> str:
        return load_prompt_safe(RolePaths.THEORY_TEACHER)
    
    @staticmethod
    def universal_teacher() -> str:
        return load_prompt_safe(RolePaths.UNIVERSAL_TEACHER)


# ========================== ГОТОВЫЕ ФОРМАТЫ ОТВЕТОВ ==========================

class Answers:
    """Загруженные форматы ответов."""
    
    @staticmethod
    def detailed() -> str:
        return load_prompt_safe(AnswerPaths.DETAILED)
    
    @staticmethod
    def concise() -> str:
        return load_prompt_safe(AnswerPaths.CONCISE)
    
    @staticmethod
    def calculation() -> str:
        return load_prompt_safe(AnswerPaths.CALCULATION)
    
    @staticmethod
    def task_format() -> str:
        return load_prompt_safe(AnswerPaths.TASK_FORMAT)


# ========================== ПРОМПТЫ ДЛЯ МАТЕМАТИКИ ==========================

class Math:
    """Промпты для математики."""
    
    class Theory:
        """Промпты для объяснения теории."""
        
        @staticmethod
        def linear_equations() -> Prompt:
            return PromptFactory.create(
                RolePaths.MATH_TEACHER,
                TheoryPaths.LINEAR_EQUATIONS,
                AnswerPaths.DETAILED
            )
        
        @staticmethod
        def quadratic_equations() -> Prompt:
            return PromptFactory.create(
                RolePaths.MATH_TEACHER,
                TheoryPaths.QUADRATIC_EQUATIONS,
                AnswerPaths.DETAILED
            )
        
        @staticmethod
        def fractions() -> Prompt:
            return PromptFactory.create(
                RolePaths.MATH_TEACHER,
                TheoryPaths.FRACTIONS,
                AnswerPaths.DETAILED
            )
        
        @staticmethod
        def proportions() -> Prompt:
            return PromptFactory.create(
                RolePaths.MATH_TEACHER,
                TheoryPaths.PROPORTIONS,
                AnswerPaths.DETAILED
            )
        
        @staticmethod
        def percentages() -> Prompt:
            return PromptFactory.create(
                RolePaths.MATH_TEACHER,
                TheoryPaths.PERCENTAGES,
                AnswerPaths.DETAILED
            )
        
        @staticmethod
        def powers() -> Prompt:
            return PromptFactory.create(
                RolePaths.MATH_TEACHER,
                TheoryPaths.POWERS,
                AnswerPaths.DETAILED
            )
        
        @staticmethod
        def roots() -> Prompt:
            return PromptFactory.create(
                RolePaths.MATH_TEACHER,
                TheoryPaths.ROOTS,
                AnswerPaths.DETAILED
            )
        
        @staticmethod
        def systems_of_equations() -> Prompt:
            return PromptFactory.create(
                RolePaths.MATH_TEACHER,
                TheoryPaths.SYSTEMS_OF_EQUATIONS,
                AnswerPaths.DETAILED
            )
        
        @staticmethod
        def inequalities() -> Prompt:
            return PromptFactory.create(
                RolePaths.MATH_TEACHER,
                TheoryPaths.INEQUALITIES,
                AnswerPaths.DETAILED
            )
        
        @staticmethod
        def functions() -> Prompt:
            return PromptFactory.create(
                RolePaths.MATH_TEACHER,
                TheoryPaths.FUNCTIONS,
                AnswerPaths.DETAILED
            )
        
        @staticmethod
        def pythagorean_theorem() -> Prompt:
            return PromptFactory.create(
                RolePaths.MATH_TEACHER,
                TheoryPaths.PYTHAGOREAN_THEOREM,
                AnswerPaths.DETAILED
            )
        
        @staticmethod
        def trigonometry() -> Prompt:
            return PromptFactory.create(
                RolePaths.MATH_TEACHER,
                TheoryPaths.TRIGONOMETRY,
                AnswerPaths.DETAILED
            )
        
        @staticmethod
        def areas() -> Prompt:
            return PromptFactory.create(
                RolePaths.MATH_TEACHER,
                TheoryPaths.AREAS,
                AnswerPaths.DETAILED
            )
        
        @staticmethod
        def volumes() -> Prompt:
            return PromptFactory.create(
                RolePaths.MATH_TEACHER,
                TheoryPaths.VOLUMES,
                AnswerPaths.DETAILED
            )
        
        @staticmethod
        def probability() -> Prompt:
            return PromptFactory.create(
                RolePaths.MATH_TEACHER,
                TheoryPaths.PROBABILITY,
                AnswerPaths.DETAILED
            )
    
    class Test:
        """Промпты для генерации тестов."""
        
        class Easy:
            """Лёгкий уровень."""
            
            @staticmethod
            def linear_equations() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Easy.LINEAR_EQUATIONS,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def fractions() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Easy.FRACTIONS,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def percentages() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Easy.PERCENTAGES,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def powers() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Easy.POWERS,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def roots() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Easy.ROOTS,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def arithmetic() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Easy.ARITHMETIC,
                    AnswerPaths.TASK_FORMAT
                )
        
        class Standard:
            """Стандартный уровень."""
            
            @staticmethod
            def linear_equations() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Standard.LINEAR_EQUATIONS,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def quadratic_equations() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Standard.QUADRATIC_EQUATIONS,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def fractions() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Standard.FRACTIONS,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def systems_of_equations() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Standard.SYSTEMS_OF_EQUATIONS,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def inequalities() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Standard.INEQUALITIES,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def word_problems() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Standard.WORD_PROBLEMS,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def geometry() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Standard.GEOMETRY,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def trigonometry() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Standard.TRIGONOMETRY,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def probability() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Standard.PROBABILITY,
                    AnswerPaths.TASK_FORMAT
                )
        
        class Hard:
            """Олимпиадный уровень."""
            
            @staticmethod
            def algebra() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Hard.ALGEBRA,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def geometry() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Hard.GEOMETRY,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def combinatorics() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Hard.COMBINATORICS,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def number_theory() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Hard.NUMBER_THEORY,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def logic() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Hard.LOGIC,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def functions() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Hard.FUNCTIONS,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def inequalities() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Hard.INEQUALITIES,
                    AnswerPaths.TASK_FORMAT
                )
            
            @staticmethod
            def sequences() -> Prompt:
                return PromptFactory.create(
                    RolePaths.TASK_GENERATOR,
                    TestPaths.Hard.SEQUENCES,
                    AnswerPaths.TASK_FORMAT
                )

