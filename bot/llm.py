import re, os, sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from logger import console

python_filename = "llm"

# Пути к папкам промптов
PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
ROLES_DIR = os.path.join(PROMPTS_DIR, "roles")
TASKS_DIR = os.path.join(PROMPTS_DIR, "tasks")
ANSWERS_DIR = os.path.join(PROMPTS_DIR, "answers")

class Commands:
    class Student:
        PROFILE = "профиль"
        APPLICATIONS = "заявки"
        MY_TEACHERS = "мои учителя"
        TASKS = "задания"
        GET_TASKS = "получить задания"
        SUBMIT_SOLUTION = "отправить решение"
        DELETE_PROFILE = "удалить профиль"
        AI_ASSISTANT = "ai помощник"
        AI_HELP_WITH_PROBLEM = "помощь с задачей"
        AI_EXPLAIN_THEORY = "объяснить теорию"
        AI_TIPS = "получить советы"
        AI_STUDY_PLAN = "план обучения"
        AI_CHECK_SOLUTION = "проверить решение"
        AI_PRACTICE = "практика"

    class Teacher:
        PROFILE = "профиль"
        ATTACH_CLASS = "прикрепить класс"
        MY_STUDENTS = "мои учащиеся"
        SEND_TASK = "отправить задание"
        CHECK_TASKS = "проверить задания"
        SEND_INDIVIDUAL_TASK = "отправить индивидуальное задание"
        SEND_CLASS_TASK = "отправить задание классу"
        CHECK_INDIVIDUAL_TASKS = "проверить индивидуальные задания"
        CLASS_TASKS = "задания для класса"
        DELETE_PROFILE = "удалить профиль"
        AI_ASSISTANT = "ai помощник"
        AI_CREATE_EXPLANATION = "создать объяснение"
        AI_ANALYZE_STUDENT = "анализ студента"
        AI_PERSONALIZED_TASK = "персонализированное задание"
        AI_GENERATE_TASK = "сгенерировать задание"
        AI_GENERATE_FOR_CLASS = "сгенерировать для класса"
        AI_CHECK = "ai проверка"
        ANALYZE_PROGRESS = "анализ прогресса"
        ATTACH_ALL = "прикрепить всех"


class Prompt:
    def __init__(self, role: str = "", task: str = "", answer: str = ""):
        self.__prompt_template = "role: {role}\ntask: {task}\nanswer: {answer}"
        self._prompt = ""
        
        # Инициализируем все атрибуты
        self.__role = ""
        self.__task = ""
        self.__answer = ""
        
        # Устанавливаем значения через сеттеры
        if role:
            self.set_role(role)
        if task:
            self.set_task(task)
        if answer:
            self.set_answer(answer)
    
    def __validator(self, description: str) -> bool:
        if not isinstance(description, str):
            raise TypeError("description must be a string")
        elif len(description) <= 2:
            raise ValueError("description must be longer than 2 characters")
        return True
    
    def set_role(self, description: str) -> None:
        if self.__validator(description):
            self.__role = description
    
    def set_task(self, description: str) -> None:
        if self.__validator(description):
            self.__task = description
    
    def set_answer(self, description: str) -> None:
        if self.__validator(description):
            self.__answer = description
    
    def get_role(self) -> str:
        return self.__role
    
    def get_task(self) -> str:
        return self.__task
    
    def get_answer(self) -> str:
        return self.__answer
    
    def prompt(self) -> str:
        if not all([self.__role, self.__task, self.__answer]):
            raise ValueError("Role, task and answer must be set before generating prompt")
        
        self._prompt = self.__prompt_template.format(
            role=self.__role,
            task=self.__task,
            answer=self.__answer
        )
        return self._prompt
    
    def save(self, filepath: str) -> None:
        with open(filepath, 'w', encoding="utf-8") as file:
            file.write(self.prompt())
    
    @staticmethod
    def load(filepath: str) -> str:
        try:
            with open(filepath, 'r', encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filepath}")
    
    def create_prompt(self, role_path: str, task_path: str, answer_path: str) -> str:
        self.set_role(self.load(role_path))
        self.set_task(self.load(task_path))
        self.set_answer(self.load(answer_path))
        return self.prompt()


class LLM:
    def __init__(self, provider, model: str, **kwargs):
        self.client = provider(model=model, **kwargs)
    
    @console.debug(python_filename)
    def ask(self, prompt: Prompt) -> str:
        """Отправить промпт и получить ответ."""
        try:
            response = self.client.invoke(prompt.prompt())
            return response
        except Exception as e:
            print(f"[ERROR] Ошибка при запросе к LLM: {e}")
            return ""
    
    @console.debug(python_filename)
    def calculate(self, expression: str) -> str:
        normalized = self._normalize_expression(expression)
        prompt = f"Вычисли следующее выражение и дай только числовой ответ: {normalized}"
        
        response = self.ask(prompt)
        result = self._extract_number(response)
        return result
    
    @console.debug(python_filename)
    def _normalize_expression(self, expr: str) -> str:
        expr = expr.lower().strip()
        replacements = {
            "squared": "^2",
            "cubed": "^3",
            "to the power of": "^",
            "square root of": "sqrt",
            "divided by": "/",
            "times": "*",
            "в квадрате": "^2",
            "в кубе": "^3",
            "в степени": "^",
            "корень из": "sqrt",
            "делить на": "/",
            "умножить на": "*",
            "плюс": "+",
            "минус": "-"
        }
        for k, v in replacements.items():
            expr = expr.replace(k, v)
        return expr
    
    @console.debug(python_filename)
    def _extract_number(self, text: str) -> str:
        """Извлекает число из текста ответа."""
        matches = re.findall(r"-?\d+\.?\d*", text)
        return matches[0] if matches else text

class AcademicLLM(LLM):
    """LLM для академических задач с предзагруженными промптами."""
    
    class Tasks:
        """Пути к файлам задач."""
        HELP_PROBLEM = os.path.join(TASKS_DIR, "help_problem.txt")
        EXPLAIN = os.path.join(TASKS_DIR, "explain.txt")
        TIPS = os.path.join(TASKS_DIR, "tips.txt")
        PLAN = os.path.join(TASKS_DIR, "plan.txt")
        CHECK_SOLUTION = os.path.join(TASKS_DIR, "check_solution.txt")
        PRACTICE = os.path.join(TASKS_DIR, "practice.txt")
        GENERATE_TASK = os.path.join(TASKS_DIR, "generate_task.txt")
        COMPUTATIONAL_SKILLS = os.path.join(TASKS_DIR, "computational_skills.txt")
        EXPRESSION_VALUE = os.path.join(TASKS_DIR, "expression_value.txt")
        FORMULAS_WORK = os.path.join(TASKS_DIR, "formulas_work.txt")
        SHORTHAND_FORMULAS = os.path.join(TASKS_DIR, "shorthand_formulas.txt")
        EQUATIONS = os.path.join(TASKS_DIR, "equations.txt")
        INEQUALITIES = os.path.join(TASKS_DIR, "inequalities.txt")
        GRAPHS = os.path.join(TASKS_DIR, "graphs.txt")
        TRIGONOMETRY = os.path.join(TASKS_DIR, "trigonometry.txt")
        PROBABILITY = os.path.join(TASKS_DIR, "probability.txt")
        TRIANGLES = os.path.join(TASKS_DIR, "triangles.txt")
        QUADRILATERALS = os.path.join(TASKS_DIR, "quadrilaterals.txt")
        CIRCLES = os.path.join(TASKS_DIR, "circles.txt")
        AREAS_VOLUMES = os.path.join(TASKS_DIR, "areas_volumes.txt")
        COORDINATE_GEOMETRY = os.path.join(TASKS_DIR, "coordinate_geometry.txt")
    
    class Roles:
        """Пути к файлам ролей."""
        MATH_TEACHER = os.path.join(ROLES_DIR, "math_teacher.txt")
        CHAT_HELPER = os.path.join(ROLES_DIR, "chat_helper.txt")
    
    class Answers:
        """Пути к файлам форматов ответа."""
        CALCULATION = os.path.join(ANSWERS_DIR, "calculation.txt")
        CONCISE = os.path.join(ANSWERS_DIR, "concise.txt")
        DETAILED = os.path.join(ANSWERS_DIR, "detailed.txt")

    def __init__(self, provider, model: str, **kwargs):
        super().__init__(provider, model, **kwargs)
