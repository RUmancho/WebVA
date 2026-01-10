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
            print("Algebra DLL генератор загружен")
        except Exception as e:
            print(f"Не удалось загрузить Algebra DLL: {e}")
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
        # ПРИОРИТЕТ 1: AI генерация
        try:
            result = self._generate_ai_question(subject, section, topic, difficulty)
            if result:
                return result
        except Exception as e:
            print(f"AI генерация вопроса не удалась: {e}")
        
        # ПРИОРИТЕТ 2: DLL генерация (fallback)
        gen_type = get_generator_type(subject, section, topic)
        if gen_type == GeneratorType.DLL:
            result = self._generate_dll_question(topic, difficulty)
            if result:
                print(f"Использован DLL fallback для темы: {topic}")
                return result
        
        # Fallback на локальные данные
        return None
    
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
        print(
            f"Генерация теста: {subject}/{section}/{topic}, "
            f"вопросов={num_questions}, приоритет=AI/LLM"
        )
        
        # ПРИОРИТЕТ 1: AI генерация через LLM
        try:
            print(f"[1/3] Попытка AI генерации через LLM...")
            result = self._generate_ai_test(
                subject, section, topic, difficulty, num_questions, with_options
            )
            if result and result.get("questions"):
                print(f"✅ AI успешно сгенерировал {len(result['questions'])} вопросов")
                return result
        except Exception as e:
            print(f"❌ AI генерация не удалась: {e}")
        
        # ПРИОРИТЕТ 2: DLL генерация (только для математических тем)
        gen_type = get_generator_type(subject, section, topic)
        if gen_type == GeneratorType.DLL:
            try:
                print(f"[2/3] Попытка DLL генерации (fallback)...")
                result = self._generate_dll_test(topic, difficulty, num_questions, with_options)
                if result and result.get("questions"):
                    print(f"✅ DLL успешно сгенерировал {len(result['questions'])} вопросов")
                    return result
            except Exception as e:
                print(f"❌ DLL генерация не удалась: {e}")
        
        # ПРИОРИТЕТ 3: Локальные тесты (последний fallback)
        print(f"[3/3] Использование локальных тестов (fallback)")
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
                print(f"Метод {method_name} не найден в DLL")
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
            print(f"Ошибка DLL генерации: {e}")
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
            print(f"DLL не создал вопросов для: {topic}")
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
        
        difficulty_names = {1: "базовый/лёгкий", 2: "средний", 3: "продвинутый/сложный"}
        diff_name = difficulty_names.get(difficulty, "средний")
        
        # Детальные контексты для разных предметов
        subject_contexts = {
            "Алгебра": {
                "context": "математические задачи по алгебре",
                "examples": "решение уравнений, работа с формулами, преобразования выражений",
                "format": "числовые ответы, уравнения, математические выражения"
            },
            "Геометрия": {
                "context": "геометрические задачи",
                "examples": "вычисление площадей, объёмов, углов, применение теорем",
                "format": "числовые ответы с единицами измерения (градусы, см², м³)"
            },
            "Физика": {
                "context": "физические задачи",
                "examples": "расчёт скорости, силы, энергии, применение физических законов",
                "format": "числовые ответы с единицами измерения (м/с, Н, Дж)"
            },
            "Химия": {
                "context": "химические задачи и теоретические вопросы",
                "examples": "уравнения реакций, расчёты по формулам, свойства веществ",
                "format": "названия веществ, химические формулы, числовые ответы"
            },
            "Биология": {
                "context": "биологические вопросы",
                "examples": "строение организмов, процессы жизнедеятельности, экосистемы",
                "format": "термины, названия, краткие описания"
            },
            "Русский язык": {
                "context": "вопросы по правилам русского языка",
                "examples": "орфография, пунктуация, морфология, синтаксис",
                "format": "слова, правила, краткие формулировки"
            },
            "Литература": {
                "context": "вопросы по литературным произведениям и теории литературы",
                "examples": "авторы, произведения, жанры, средства выразительности",
                "format": "имена, названия, литературные термины"
            },
            "История": {
                "context": "исторические вопросы",
                "examples": "даты, события, личности, причинно-следственные связи",
                "format": "даты, имена, названия событий"
            },
            "Обществознание": {
                "context": "вопросы по обществознанию",
                "examples": "понятия, социальные процессы, законы, экономика",
                "format": "термины, определения, краткие объяснения"
            },
            "Английский язык": {
                "context": "вопросы по английскому языку",
                "examples": "грамматика, лексика, перевод, употребление",
                "format": "слова, фразы, грамматические формы"
            },
            "Информатика": {
                "context": "вопросы по информатике",
                "examples": "алгоритмы, программирование, системы счисления",
                "format": "числа, код, термины"
            },
            "География": {
                "context": "географические вопросы",
                "examples": "страны, столицы, рельеф, климат, природные ресурсы",
                "format": "названия, числовые данные, географические термины"
            }
        }
        
        context_data = subject_contexts.get(subject, {
            "context": "учебные вопросы",
            "examples": "теоретические и практические задачи",
            "format": "точные краткие ответы"
        })
        
        if with_options:
            format_desc = '"options": ["A", "B", "C", "D"], "correct_answer": "A"'
            format_instruction = 'с 4 вариантами ответов'
            example = """
Пример правильного формата:
{
  "questions": [
    {
      "question": "Сколько будет 2 + 2?",
      "options": ["3", "4", "5", "6"],
      "correct_answer": "4"
    }
  ]
}"""
        else:
            format_desc = '"correct_answer": "точный краткий ответ"'
            format_instruction = 'с точным кратким ответом (без вариантов)'
            example = """
Пример правильного формата:
{
  "questions": [
    {
      "question": "Сколько будет 2 + 2?",
      "correct_answer": "4"
    }
  ]
}"""
        
        prompt = Prompt(
            role=f"""Ты опытный преподаватель предмета '{subject}' с 20-летним стажем.
Специализируешься на создании качественных тестовых заданий {format_instruction}.
Твои вопросы всегда точные, понятные и соответствуют программе обучения.""",
            task=f"""Создай {num_questions} тестовых вопросов по теме "{topic}" из раздела "{section}" предмета {subject}.

📚 КОНТЕКСТ ПРЕДМЕТА:
- Тип задач: {context_data['context']}
- Примеры: {context_data['examples']}
- Формат ответов: {context_data['format']}

⚙️ ТРЕБОВАНИЯ:
1. Уровень сложности: {diff_name} (важно!)
2. Все вопросы на русском языке
3. Вопросы должны быть РАЗНООБРАЗНЫМИ:
   - Проверять разные аспекты темы
   - Использовать разные типы задач
   - Иметь разную степень детализации
4. Ответы должны быть:
   - Точными и однозначными
   - Без лишних пояснений
   - В правильном формате
5. Вопросы должны быть:
   - Практичными и применимыми
   - Соответствовать указанному уровню сложности
   - Проверять понимание, а не только память

{example}

⚠️ ВАЖНО: Ответь СТРОГО в формате JSON!
Формат: {{"questions": [{{"question": "Текст вопроса", {format_desc}}}]}}
НЕ добавляй пояснений, рассуждений или комментариев - ТОЛЬКО валидный JSON.""",
            answer="Верни ТОЛЬКО чистый валидный JSON с массивом questions. Без тегов, без пояснений."
        )
        
        try:
            print(f"🤖 Отправка запроса к LLM...")
            response = chat.academic.ask(prompt)
            print(f"📥 Получен ответ от LLM (длина: {len(response)} символов)")
            
            # ШАГ 1: Очистка от служебных тегов deepseek-r1
            response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL | re.IGNORECASE).strip()
            response = re.sub(r'<reasoning>.*?</reasoning>', '', response, flags=re.DOTALL | re.IGNORECASE).strip()
            print(f"🧹 После очистки тегов: {len(response)} символов")
            
            # ШАГ 2: Очистка markdown блоков кода
            if "```" in response:
                # Пытаемся извлечь JSON из markdown блоков
                json_blocks = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', response, flags=re.DOTALL | re.IGNORECASE)
                if json_blocks:
                    response = json_blocks[0]
                    print(f"📦 Извлечён JSON из markdown блока")
                else:
                    # Удаляем markdown теги вручную
                    parts = re.split(r'```(?:json)?', response, flags=re.IGNORECASE)
                    for part in parts:
                        part = part.strip()
                        if part and (part.startswith('{') or part.startswith('[')):
                            response = part
                            break
            
            # ШАГ 3: Извлечение JSON объекта
            response = response.strip()
            
            # Удаляем всё до первой {
            if '{' in response:
                start_pos = response.find('{')
                response = response[start_pos:]
            
            # Удаляем всё после последней }
            if '}' in response:
                end_pos = response.rfind('}') + 1
                response = response[:end_pos]
            
            print(f"🔍 Финальный JSON (первые 300 символов): {response[:300]}")
            
            # ШАГ 4: Парсинг JSON
            data = json.loads(response)
            print(f"✅ JSON успешно распарсен")
            
            # ШАГ 5: Валидация структуры данных
            if "questions" not in data:
                print(f"❌ Ключ 'questions' не найден в ответе")
                raise ValueError("Отсутствует ключ 'questions' в ответе от AI")
            
            if not isinstance(data["questions"], list):
                print(f"❌ 'questions' не является массивом")
                raise ValueError("'questions' должен быть массивом")
            
            if len(data["questions"]) == 0:
                print(f"❌ Массив 'questions' пустой")
                raise ValueError("AI вернул пустой массив вопросов")
            
            print(f"📊 Получено вопросов от AI: {len(data['questions'])}")
            
            # ШАГ 6: Детальная валидация каждого вопроса
            valid_questions = []
            for idx, q in enumerate(data["questions"]):
                # Проверка обязательных полей
                if "question" not in q:
                    print(f"⚠️ Вопрос {idx+1}: отсутствует поле 'question'")
                    continue
                
                if "correct_answer" not in q:
                    print(f"⚠️ Вопрос {idx+1}: отсутствует поле 'correct_answer'")
                    continue
                
                # Проверка что вопрос не пустой
                if not q["question"].strip():
                    print(f"⚠️ Вопрос {idx+1}: пустой текст вопроса")
                    continue
                
                if not str(q["correct_answer"]).strip():
                    print(f"⚠️ Вопрос {idx+1}: пустой правильный ответ")
                    continue
                
                # Дополнительная проверка для тестов с вариантами
                if with_options:
                    if "options" not in q:
                        print(f"⚠️ Вопрос {idx+1}: отсутствуют варианты ответов")
                        continue
                    if not isinstance(q["options"], list):
                        print(f"⚠️ Вопрос {idx+1}: 'options' не массив")
                        continue
                    if len(q["options"]) < 2:
                        print(f"⚠️ Вопрос {idx+1}: слишком мало вариантов ({len(q['options'])})")
                        continue
                    if q["correct_answer"] not in q["options"]:
                        print(f"⚠️ Вопрос {idx+1}: правильный ответ отсутствует в вариантах")
                        # Добавим правильный ответ в варианты
                        q["options"].append(q["correct_answer"])
                
                valid_questions.append(q)
                print(f"✅ Вопрос {idx+1}: валиден")
            
            if not valid_questions:
                print(f"❌ Ни один вопрос не прошёл валидацию")
                raise ValueError("Все вопросы от AI невалидны")
            
            print(f"✅ AI сгенерировал {len(valid_questions)} валидных вопросов из {len(data['questions'])}")
            
            return {
                "questions": valid_questions[:num_questions],
                "generator": "AI (LLM)",
                "test_type": "with_options" if with_options else "without_options"
            }
            
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON от AI: {e}")
            print(f"📄 Проблемный ответ (первые 500 символов): {response[:500]}")
            print(f"📄 Проблемный ответ (последние 100 символов): ...{response[-100:]}")
            raise ValueError(f"AI вернул некорректный JSON: {e}")
        except ValueError as e:
            print(f"❌ Ошибка валидации данных от AI: {e}")
            raise
        except Exception as e:
            print(f"❌ Неожиданная ошибка AI генерации: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
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

