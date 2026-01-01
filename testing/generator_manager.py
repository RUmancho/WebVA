"""
Менеджер генераторов заданий.
Диспетчеризует генерацию между DLL и AI в зависимости от конфигурации.
"""

import os
import sys
import json
import re
import random
from typing import Optional, Dict, List, Any

# Настройка путей
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from testing.config import (
    GeneratorType,
    get_generator_type,
    get_dll_method
)
from logger.stats import log_info, log_warning, log_error

PYTHON_FILENAME = "generator_manager"


class GeneratorManager:
    """Менеджер генерации заданий"""
    
    def __init__(self):
        self.algebra_generator = None
        self._init_dll_generators()
    
    def _init_dll_generators(self):
        """Инициализация DLL генераторов"""
        try:
            from generator.generator import Algebra
            self.algebra_generator = Algebra
            log_info("Algebra DLL генератор загружен", PYTHON_FILENAME)
        except Exception as e:
            log_warning(f"Не удалось загрузить Algebra DLL: {e}", PYTHON_FILENAME)
            self.algebra_generator = None
    
    def get_generator_info(self, subject: str, section: str, topic: str) -> Dict[str, Any]:
        """
        Получить информацию о генераторе для темы.
        
        Returns:
            Dict с ключами: type, available, method (для DLL)
        """
        gen_type = get_generator_type(subject, section, topic)
        
        info = {
            "type": gen_type.value,
            "available": True,
            "method": None
        }
        
        if gen_type == GeneratorType.DLL:
            method = get_dll_method(topic)
            info["method"] = method
            info["available"] = self.algebra_generator is not None and bool(method)
        
        return info
    
    def generate_question(
        self,
        subject: str,
        section: str,
        topic: str,
        difficulty: int = 2
    ) -> Optional[Dict[str, Any]]:
        """
        Генерация одного вопроса.
        
        Args:
            subject: Название предмета
            section: Название раздела
            topic: Название темы
            difficulty: Уровень сложности (1-3)
        
        Returns:
            Dict с ключами: question, correct_answer, options (опционально)
        """
        gen_type = get_generator_type(subject, section, topic)
        
        if gen_type == GeneratorType.DLL:
            result = self._generate_dll_question(topic, difficulty)
            if result:
                return result
            # Fallback на AI если DLL не сработал
            log_warning(f"DLL fallback на AI для темы: {topic}", PYTHON_FILENAME)
        
        # AI генерация
        return self._generate_ai_question(subject, section, topic, difficulty)
    
    def generate_test(
        self,
        subject: str,
        section: str,
        topic: str,
        difficulty: int = 2,
        num_questions: int = 5,
        with_options: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Генерация полного теста.
        
        Args:
            subject: Название предмета
            section: Название раздела
            topic: Название темы
            difficulty: Уровень сложности (1-3)
            num_questions: Количество вопросов
            with_options: Генерировать варианты ответов
        
        Returns:
            Dict с ключами: questions, generator, test_type
        """
        gen_type = get_generator_type(subject, section, topic)
        
        log_info(
            f"Генерация теста: {subject}/{section}/{topic}, "
            f"генератор={gen_type.value}, вопросов={num_questions}",
            PYTHON_FILENAME
        )
        
        # Попытка DLL генерации
        if gen_type == GeneratorType.DLL:
            result = self._generate_dll_test(topic, difficulty, num_questions, with_options)
            if result and result.get("questions"):
                return result
        
        # AI генерация
        try:
            return self._generate_ai_test(
                subject, section, topic, difficulty, num_questions, with_options
            )
        except Exception as e:
            log_error(f"AI генерация не удалась: {e}", PYTHON_FILENAME)
            return self._generate_local_test(topic, num_questions, with_options)
    
    def _generate_dll_question(self, topic: str, difficulty: int) -> Optional[Dict[str, Any]]:
        """Генерация вопроса через DLL"""
        try:
            if not self.algebra_generator:
                return None
            
            method_name = get_dll_method(topic)
            if not method_name:
                return None
            
            method = getattr(self.algebra_generator, method_name, None)
            if not method:
                log_warning(f"Метод {method_name} не найден в DLL", PYTHON_FILENAME)
                return None
            
            result = method(difficulty)
            if not result:
                return None
            
            # Парсим результат: "уравнение|ответ"
            parts = result.split("|")
            if len(parts) >= 2:
                equation = parts[0].strip()
                answer = parts[1].strip()
                
                return {
                    "question": f"Решите: {equation}",
                    "correct_answer": answer,
                    "raw_equation": equation
                }
            
            return None
            
        except Exception as e:
            log_error(f"Ошибка DLL генерации: {e}", PYTHON_FILENAME)
            return None
    
    def _generate_dll_test(
        self,
        topic: str,
        difficulty: int,
        num_questions: int,
        with_options: bool
    ) -> Optional[Dict[str, Any]]:
        """Генерация теста через DLL"""
        questions = []
        attempts = 0
        max_attempts = num_questions * 3
        
        while len(questions) < num_questions and attempts < max_attempts:
            attempts += 1
            question_data = self._generate_dll_question(topic, difficulty)
            
            if question_data:
                question = {
                    "question": question_data["question"],
                    "correct_answer": question_data["correct_answer"]
                }
                
                if with_options:
                    question["options"] = self._generate_options(question_data["correct_answer"])
                
                questions.append(question)
        
        if not questions:
            log_warning(f"DLL не создал вопросов для: {topic}", PYTHON_FILENAME)
            return None
        
        return {
            "questions": questions[:num_questions],
            "generator": "DLL",
            "test_type": "with_options" if with_options else "without_options"
        }
    
    def _generate_ai_question(
        self,
        subject: str,
        section: str,
        topic: str,
        difficulty: int
    ) -> Optional[Dict[str, Any]]:
        """Генерация одного вопроса через AI"""
        # Генерируем мини-тест из 1 вопроса
        test = self._generate_ai_test(subject, section, topic, difficulty, 1, True)
        if test and test.get("questions"):
            return test["questions"][0]
        return None
    
    def _generate_ai_test(
        self,
        subject: str,
        section: str,
        topic: str,
        difficulty: int,
        num_questions: int,
        with_options: bool
    ) -> Optional[Dict[str, Any]]:
        """Генерация теста через AI (LLM)"""
        from bot.prompt import Prompt
        from bot import chat
        
        difficulty_names = {1: "лёгкий", 2: "средний", 3: "сложный"}
        diff_name = difficulty_names.get(difficulty, "средний")
        
        if with_options:
            format_desc = '"options": ["A", "B", "C", "D"], "correct_answer": "A"'
            format_instruction = 'с 4 вариантами ответов'
        else:
            format_desc = '"correct_answer": "точный ответ"'
            format_instruction = 'с точным ответом (без вариантов)'
        
        prompt = Prompt(
            role=f"Ты преподаватель предмета {subject}. Создаёшь тесты {format_instruction}.",
            task=f"""Создай {num_questions} тестовых вопросов по теме "{topic}" (раздел "{section}").
Сложность: {diff_name}.
Ответь СТРОГО в формате JSON: {{"questions": [{{"question": "Текст вопроса", {format_desc}}}]}}
Все вопросы на русском языке. Только JSON, без пояснений.""",
            answer="Верни только валидный JSON с вопросами."
        )
        
        response = chat.academic.ask(prompt)
        
        # Очистка от тегов <think>
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
        
        # Очистка markdown
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        data = json.loads(response)
        if "questions" in data and len(data["questions"]) > 0:
            return {
                "questions": data["questions"][:num_questions],
                "generator": "AI",
                "test_type": "with_options" if with_options else "without_options"
            }
        
        raise ValueError("Пустой ответ от AI")
    
    def _generate_local_test(
        self,
        topic: str,
        num_questions: int,
        with_options: bool
    ) -> Dict[str, Any]:
        """Локальная генерация (fallback)"""
        questions = []
        
        for i in range(num_questions):
            question = {
                "question": f"Вопрос {i+1} по теме '{topic}'",
                "correct_answer": "А"
            }
            if with_options:
                question["options"] = ["А", "Б", "В", "Г"]
            questions.append(question)
        
        return {
            "questions": questions,
            "generator": "LOCAL",
            "test_type": "with_options" if with_options else "without_options"
        }
    
    def _generate_options(self, correct: str) -> List[str]:
        """Генерация вариантов ответов для числового ответа"""
        options = [correct]
        numbers = re.findall(r'-?\d+\.?\d*', correct)
        
        if numbers:
            base = float(numbers[0])
            variants = [
                base + random.randint(1, 3),
                base - random.randint(1, 3),
                base * 2 if abs(base) < 10 else base + 5
            ]
            
            for v in variants:
                v_str = str(int(v)) if v == int(v) else str(round(v, 2))
                new_opt = correct.replace(str(numbers[0]), v_str)
                if new_opt not in options:
                    options.append(new_opt)
        
        while len(options) < 4:
            options.append(f"x = {random.randint(-10, 10)}")
        
        random.shuffle(options)
        return options[:4]


# Синглтон экземпляр
generator_manager = GeneratorManager()

