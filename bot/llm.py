import re, os, sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from logger import console

python_filename = "llm"

class Mode:
    HELP_PROBLEM = "help_problem"
    EXPLAIN = "explain"
    TIPS = "tips"
    PLAN = "plan"
    CHECK_SOLUTION = "check_solution"
    PRACTICE = "practice"
    GENERATE_TASK = "generate_task"
    
    COMPUTATIONAL_SKILLS = "computational_skills"
    EXPRESSION_VALUE = "expression_value"
    FORMULAS_WORK = "formulas_work"
    SHORTHAND_FORMULAS = "shorthand_formulas"
    EQUATIONS = "equations"
    INEQUALITIES = "inequalities"
    GRAPHS = "graphs"
    TRIGONOMETRY = "trigonometry"
    PROBABILITY = "probability"
    
    TRIANGLES = "triangles"
    QUADRILATERALS = "quadrilaterals"
    CIRCLES = "circles"
    AREAS_VOLUMES = "areas_volumes"
    COORDINATE_GEOMETRY = "coordinate_geometry"


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


MODE_TO_FILE = {
    Mode.HELP_PROBLEM: "help_problem.txt",
    Mode.EXPLAIN: "explain.txt",
    Mode.TIPS: "tips.txt",
    Mode.PLAN: "plan.txt",
    Mode.CHECK_SOLUTION: "check_solution.txt",
    Mode.PRACTICE: "practice.txt",
    Mode.GENERATE_TASK: "generate_task.txt",
    Mode.COMPUTATIONAL_SKILLS: "computational_skills.txt",
    Mode.EXPRESSION_VALUE: "expression_value.txt",
    Mode.FORMULAS_WORK: "formulas_work.txt",
    Mode.SHORTHAND_FORMULAS: "shorthand_formulas.txt",
    Mode.EQUATIONS: "equations.txt",
    Mode.INEQUALITIES: "inequalities.txt",
    Mode.GRAPHS: "graphs.txt",
    Mode.TRIGONOMETRY: "trigonometry.txt",
    Mode.PROBABILITY: "probability.txt",
    Mode.TRIANGLES: "triangles.txt",
    Mode.QUADRILATERALS: "quadrilaterals.txt",
    Mode.CIRCLES: "circles.txt",
    Mode.AREAS_VOLUMES: "areas_volumes.txt",
    Mode.COORDINATE_GEOMETRY: "coordinate_geometry.txt"
}

class Prompt:
    def __init__(self):
        self.__prompt_template = "role: {role}\ntask: {task}\nanswer: {answer}"
        self._prompt = ""
        self.__role = ""
        self.__task = ""
        self.__answer = ""

    @console.debug(python_filename)
    def set_role(self, descripton: str) -> None:
        self.__role = descripton

    @console.debug(python_filename)
    def set_task(self, description: str) -> None:
        self.__task = description
    
    @console.debug(python_filename)
    def set_answer(self, description: str) -> None:
        self.__answer = description

    @console.debug(python_filename)
    def prompt(self):
        self.__prompt = self.__prompt_template.format(role = self.__role, task = self.__task, answer = self.__answer)
        return self.__prompt

    @console.debug(python_filename)
    def save(self, filepath):
        with open(filepath, 'w', encoding="utf-8") as file:
            file.write(self.prompt())

    @console.debug(python_filename)
    def load_role(self, filepath: str) -> None:
        self.__role = self.__load(filepath)

    @console.debug(python_filename)
    def load_task(self, filepath: str) -> None:
        self.__task = self.__load(filepath)

    @console.debug(python_filename)
    def load_answer(self, filepath: str) -> None:
        self.__task = self.__load(filepath)

    @console.debug(python_filename)
    def __load(filepath: str) -> str:
        with open(filepath, 'r', encoding="utf-8") as file:
            return file.read()

class LLM:
    def __init__(self, provider, model: str, **kwargs):
        self.client = provider(model=model, **kwargs)
        self.prompt = Prompt()
    
    @console.debug(python_filename)
    def ask(self) -> str:
        response = self.client.invoke(self.prompt)
        return response
    
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
    def __init__(self, provider, model: str, **kwargs):
        super().__init__(provider, model, )