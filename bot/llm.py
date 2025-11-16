from langchain_ollama import OllamaLLM 
from openai import OpenAI
import re
import enum
import datetime
import time
from bot.prompt_loader import load_prompt, load_prompt_with_format

class AIMode(enum.Enum):
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

class StudentCommands(enum.Enum):
    """Команды меню ученика (текстовые ярлыки на кнопках)."""
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

class TeacherCommands(enum.Enum):
    """Команды меню учителя (текстовые ярлыки на кнопках)."""
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



class ResponseType(enum.Enum):
    """Тип запрашиваемого ответа от модели."""
    CALCULATION = enum.auto()  # Только числовой ответ
    EXPLANATION = enum.auto()  # Развернутое объяснение
    CONCISE = enum.auto()      # Краткий ответ

class LLM:
    def _load_roles(self):
        """Загружает роли из файлов промптов."""
        return {
            "math teacher": {
                "base": load_prompt("role_base.txt"),
                "calculation": load_prompt("role_calculation.txt"),
                "explanation": load_prompt("role_explanation.txt"),
                "concise": load_prompt("role_concise.txt")
            }
        }
    
    @property
    def ROLES(self):
        """Свойство для получения ролей (загружает из файлов при первом обращении)."""
        if not hasattr(self, '_roles_cache'):
            self._roles_cache = self._load_roles()
        return self._roles_cache

    def __init__(self):
        try:
            # self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            self.client = OllamaLLM(model="deepseek-r1:7b", temperature=0.3)
            
            self.model_name = "deepseek-r1:7b"
        except Exception as e:
            try:
                # Fallback на другую модель если deepseek-r1:7b недоступна
                self.client = OllamaLLM(model="deepseek-coder:6.7b", temperature=0.3)
                self.model_name = "deepseek-coder:6.7b"
            except Exception as e2:
                self.client = None
                self.model_name = "deepseek-r1:7b"
                print(f"Ошибка инициализации Ollama клиента: {e2}")

        self.role = ""
        self.task = ""
        self.prompt = ""
        self.response_type = ResponseType.EXPLANATION  # По умолчанию объяснение
        self.request_id = None  # Уникальный ID для отслеживания запросов

    def _generate_request_id(self) -> str:
        """Генерирует уникальный ID для запроса."""
        return f"{int(time.time() * 1000)}"

    def set_role(self, role: str) -> None:
        """Устанавливает роль подсказки (поддерживается только 'math teacher')."""
        if role not in self.ROLES:
            raise ValueError("Unsupported model role selected")
        self.role = self.ROLES[role]["base"]

    def set_response_type(self, response_type: ResponseType) -> None:
        """Меняет тип ответа модели (влияет на формирование промпта)."""
        self.response_type = response_type

    def calculate(self, expression: str) -> str:
        """Возвращает только числовой результат выражения, без пояснений."""
        self.response_type = ResponseType.CALCULATION
        expression = self._normalize_expression(expression)
        self.task = f"Calculate: {expression}"
        self._update_prompt()
        return self.run()

    def explain(self, topic: str) -> str:
        """Пишет развернутое объяснение темы с примерами и шагами."""
        self.response_type = ResponseType.EXPLANATION
        self.task = f"Explain: {topic}"
        self._update_prompt()
        return self.run()

    def ask(self, question: str) -> str:
        """Даёт краткий ответ на вопрос."""
        self.response_type = ResponseType.CONCISE
        self.task = question
        self._update_prompt()
        return self.run()


    def _update_prompt(self):
        if self.response_type == ResponseType.CALCULATION:
            instruction = self.ROLES["math teacher"]["calculation"]
        elif self.response_type == ResponseType.EXPLANATION:
            instruction = self.ROLES["math teacher"]["explanation"]
        else:
            instruction = self.ROLES["math teacher"]["concise"]
        
        # Обновляем роль с инструкцией для лучшего контекста
        self.role = f"{self.ROLES['math teacher']['base']} {instruction}"

    def _normalize_expression(self, expr: str) -> str:
        """Нормализует текстовые описания операций в форму, понятную модели."""
        expr = expr.lower().strip()
        replacements = {
            "squared": "^2",
            "cubed": "^3",
            "to the power of": "^",
            "square root of": "sqrt",
            "divided by": "/",
            "times": "*"
        }
        for k, v in replacements.items():
            expr = expr.replace(k, v)
        return expr

    def run(self) -> str:
        self.request_id = self._generate_request_id()
        
        try:
            if self.client is None:
                return "Ollama клиент недоступен. Проверьте настройки."
            
            full_prompt = f"{self.role}\n\nЗадача: {self.task}"
            
            request_params = {
                "model": self.model_name,
                "temperature": 0.3,
                "prompt_length": len(full_prompt)
            }
            
            start_time = datetime.datetime.now()
            
            # Используем метод invoke для OllamaLLM
            response_text = self.client.invoke(full_prompt)
            
            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Проверяем что ответ получен
            if not response_text:
                return "Получен пустой ответ от модели"
            
            if self.response_type == ResponseType.CALCULATION:
                extracted = self._extract_number(response_text)
                return extracted
                
            return response_text
            
        except Exception as e:
            error_msg = f"Произошла ошибка при обращении к AI: {e}"
            return error_msg

    def _extract_number(self, text: str) -> str:
        """Извлекает число из текста ответа"""
        matches = re.findall(r"-?\d+\.?\d*", text)
        return matches[0] if matches else "Could not extract number"

    def respond(self, mode: AIMode | None, user_text: str) -> str:
        """Формирует промпт по режиму и возвращает ответ модели."""
        
        try:
            prompt = self._build_prompt(mode, user_text)
            
            answer = self.ask(prompt)
            
            if mode == AIMode.GENERATE_TASK:
                sanitized = self._sanitize_generated_task(answer)
                return sanitized
            
            return answer
        except Exception as e:
            return "Произошла ошибка при обработке запроса AI"

    @staticmethod
    def _build_prompt(mode: AIMode | None, text: str) -> str:
        """Создаёт промпт к LLM на основе выбранного режима AI."""
        try:
            # Маппинг режимов на имена файлов промптов
            mode_to_file = {
                AIMode.HELP_PROBLEM: "help_problem.txt",
                AIMode.EXPLAIN: "explain.txt",
                AIMode.TIPS: "tips.txt",
                AIMode.PLAN: "plan.txt",
                AIMode.CHECK_SOLUTION: "check_solution.txt",
                AIMode.PRACTICE: "practice.txt",
                AIMode.GENERATE_TASK: "generate_task.txt",
                AIMode.COMPUTATIONAL_SKILLS: "computational_skills.txt",
                AIMode.EXPRESSION_VALUE: "expression_value.txt",
                AIMode.FORMULAS_WORK: "formulas_work.txt",
                AIMode.SHORTHAND_FORMULAS: "shorthand_formulas.txt",
                AIMode.EQUATIONS: "equations.txt",
                AIMode.INEQUALITIES: "inequalities.txt",
                AIMode.GRAPHS: "graphs.txt",
                AIMode.TRIGONOMETRY: "trigonometry.txt",
                AIMode.PROBABILITY: "probability.txt",
                AIMode.TRIANGLES: "triangles.txt",
                AIMode.QUADRILATERALS: "quadrilaterals.txt",
                AIMode.CIRCLES: "circles.txt",
                AIMode.AREAS_VOLUMES: "areas_volumes.txt",
                AIMode.COORDINATE_GEOMETRY: "coordinate_geometry.txt"
            }
            
            if mode and mode in mode_to_file:
                filename = mode_to_file[mode]
                return load_prompt_with_format(filename, text=text)
            
            return text
        except Exception as e:
            print(f"Ошибка формирования промпта в LLM: {e}")
            return text

    @staticmethod
    def _sanitize_generated_task(raw_text: str) -> str:
        """Возвращает из ответа LLM только условие задачи.

        - Если есть строка, начинающаяся с 'Задача:', берём её и последующие строки до пустой строки.
        - Удаляем блоки, начинающиеся с 'Решение', 'Пример', 'Вид', 'Answer', 'Program', 'Программа', 'Ответ'.
        - Если 'Задача:' не найдено — берём первую содержательную строку и добавляем префикс 'Задача: '.
        - Обрезаем до 3–4 строк максимум, чтобы избежать лишнего текста.
        """
        try:
            if not isinstance(raw_text, str):
                return "Не удалось сгенерировать задачу"
            lines = [ln.strip() for ln in raw_text.strip().splitlines()]
            drop_prefixes = (
                "решение", "пример", "вид", "answer", "program", "программа", "ответ"
            )
            filtered = []
            skip = False
            for ln in lines:
                low = ln.lower()
                if any(low.startswith(pfx) for pfx in drop_prefixes):
                    skip = True
                if skip:
                    if ln == "":
                        skip = False
                    continue
                filtered.append(ln)

            start_idx = next((i for i, ln in enumerate(filtered) if ln.lower().startswith("задача:")), None)
            if start_idx is not None:
                result_block = []
                for ln in filtered[start_idx:]:
                    if ln == "":
                        break
                    result_block.append(ln)
                result_block = result_block[:4]
                return "\n".join(result_block) if result_block else filtered[start_idx]

            first = next((ln for ln in filtered if ln), "")
            if not first:
                return "Не удалось сгенерировать задачу"
            if not first.lower().startswith("задача:"):
                first = f"Задача: {first}"
            return first
        except Exception as e:
            print(f"Ошибка санитизации текста задачи в LLM: {e}")
            return "Не удалось сгенерировать задачу"
