from asyncio import threads
import streamlit as st
import time
import socket
from bot.settings import OPENAI_API_KEY
from langchain_ollama import OllamaLLM

class TheoryManager:
    """Класс для управления теоретическими материалами"""
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        # Структура предметов и их разделов
        self.SUBJECTS_STRUCTURE = {
            "Алгебра": {
                "icon": "🔢",
                "sections": {
                    "Уравнения": {
                        "topics": [
                            "Линейные уравнения",
                            "Квадратные уравнения", 
                            "Системы уравнений",
                            "Иррациональные уравнения",
                            "Показательные уравнения",
                            "Логарифмические уравнения"
                        ]
                    },
                    "Функции": {
                        "topics": [
                            "Линейная функция",
                            "Квадратичная функция",
                            "Степенная функция",
                            "Показательная функция",
                            "Логарифмическая функция",
                            "Тригонометрические функции"
                        ]
                    },
                    "Прогрессии": {
                        "topics": [
                            "Арифметическая прогрессия",
                            "Геометрическая прогрессия",
                            "Бесконечно убывающая прогрессия"
                        ]
                    }
                }
            },
            "Геометрия": {
                "icon": "📐",
                "sections": {
                    "Планиметрия": {
                        "topics": [
                            "Треугольники",
                            "Четырехугольники",
                            "Окружность",
                            "Многоугольники",
                            "Площади фигур",
                            "Подобие"
                        ]
                    },
                    "Стереометрия": {
                        "topics": [
                            "Прямые и плоскости",
                            "Многогранники",
                            "Призма",
                            "Пирамида",
                            "Цилиндр",
                            "Конус",
                            "Шар",
                            "Объемы тел"
                        ]
                    },
                    "Теоремы": {
                        "topics": [
                            "Теорема Пифагора",
                            "Теорема косинусов",
                            "Теорема синусов",
                            "Теорема о площади треугольника",
                            "Теоремы о параллельных прямых",
                            "Теоремы о подобии"
                        ]
                    }
                }
            },
            "Физика": {
                "icon": "⚡",
                "sections": {
                    "Механика": {
                        "topics": [
                            "Кинематика",
                            "Динамика", 
                            "Законы Ньютона",
                            "Импульс",
                            "Энергия",
                            "Колебания и волны"
                        ]
                    },
                    "Термодинамика": {
                        "topics": [
                            "Температура и теплота",
                            "Газовые законы",
                            "Первый закон термодинамики",
                            "Второй закон термодинамики",
                            "Тепловые машины"
                        ]
                    },
                    "Электричество": {
                        "topics": [
                            "Электростатика",
                            "Постоянный ток",
                            "Магнетизм",
                            "Электромагнитная индукция",
                            "Переменный ток"
                        ]
                    },
                    "Оптика": {
                        "topics": [
                            "Геометрическая оптика",
                            "Линзы",
                            "Волновая оптика",
                            "Интерференция",
                            "Дифракция"
                        ]
                    }
                }
            },
            "Английский язык": {
                "icon": "🇬🇧",
                "sections": {
                    "Грамматика": {
                        "topics": [
                            "Времена глаголов",
                            "Артикли",
                            "Местоимения",
                            "Модальные глаголы",
                            "Условные предложения",
                            "Пассивный залог"
                        ]
                    },
                    "Лексика": {
                        "topics": [
                            "Фразовые глаголы",
                            "Идиомы",
                            "Словообразование",
                            "Синонимы и антонимы",
                            "Устойчивые выражения"
                        ]
                    },
                    "Разговорная речь": {
                        "topics": [
                            "Повседневные диалоги",
                            "Описание людей и мест",
                            "Выражение мнения",
                            "Рассказ о событиях",
                            "Деловое общение"
                        ]
                    }
                }
            },
            "Химия": {
                "icon": "🧪",
                "sections": {
                    "Общая химия": {
                        "topics": [
                            "Атомное строение",
                            "Периодическая система",
                            "Химическая связь",
                            "Валентность",
                            "Степень окисления",
                            "Типы химических реакций"
                        ]
                    },
                    "Неорганическая химия": {
                        "topics": [
                            "Металлы",
                            "Неметаллы",
                            "Кислоты",
                            "Основания",
                            "Соли",
                            "Оксиды"
                        ]
                    },
                    "Органическая химия": {
                        "topics": [
                            "Углеводороды",
                            "Спирты",
                            "Альдегиды и кетоны",
                            "Карбоновые кислоты",
                            "Амины",
                            "Белки и углеводы"
                        ]
                    }
                }
            },
            "Русский язык": {
                "icon": "📝",
                "sections": {
                    "Морфология": {
                        "topics": [
                            "Имя существительное",
                            "Имя прилагательное",
                            "Глагол",
                            "Наречие",
                            "Местоимение",
                            "Числительное"
                        ]
                    },
                    "Синтаксис": {
                        "topics": [
                            "Простое предложение",
                            "Сложное предложение",
                            "Однородные члены",
                            "Обособленные члены",
                            "Вводные слова",
                            "Прямая и косвенная речь"
                        ]
                    },
                    "Орфография": {
                        "topics": [
                            "Правописание корней",
                            "Правописание приставок",
                            "Правописание суффиксов",
                            "Правописание окончаний",
                            "НЕ с разными частями речи",
                            "Н и НН в разных частях речи"
                        ]
                    }
                }
            },
            "История": {
                "icon": "🏛️",
                "sections": {
                    "Древний мир": {
                        "topics": [
                            "Первобытное общество",
                            "Древний Египет",
                            "Древняя Греция",
                            "Древний Рим",
                            "Древний Восток",
                            "Великое переселение народов"
                        ]
                    },
                    "Средние века": {
                        "topics": [
                            "Феодализм",
                            "Крестовые походы",
                            "Византийская империя",
                            "Арабские завоевания",
                            "Монгольские завоевания",
                            "Возрождение"
                        ]
                    },
                    "Новое время": {
                        "topics": [
                            "Великие географические открытия",
                            "Реформация",
                            "Промышленная революция",
                            "Французская революция",
                            "Наполеоновские войны",
                            "Колониализм"
                        ]
                    }
                }
            },
            "Обществознание": {
                "icon": "👥",
                "sections": {
                    "Человек и общество": {
                        "topics": [
                            "Природа человека",
                            "Социализация",
                            "Общество как система",
                            "Социальные институты",
                            "Культура",
                            "Глобализация"
                        ]
                    },
                    "Политика": {
                        "topics": [
                            "Государство",
                            "Формы правления",
                            "Политические режимы",
                            "Избирательные системы",
                            "Политические партии",
                            "Гражданское общество"
                        ]
                    },
                    "Экономика": {
                        "topics": [
                            "Рыночная экономика",
                            "Спрос и предложение",
                            "Конкуренция",
                            "Деньги и банки",
                            "Инфляция",
                            "Безработица"
                        ]
                    }
                }
            },
            "География": {
                "icon": "🌍",
                "sections": {
                    "Физическая география": {
                        "topics": [
                            "Литосфера",
                            "Атмосфера",
                            "Гидросфера",
                            "Биосфера",
                            "Климат",
                            "Природные зоны"
                        ]
                    },
                    "Экономическая география": {
                        "topics": [
                            "Население мира",
                            "Промышленность",
                            "Сельское хозяйство",
                            "Транспорт",
                            "Мировое хозяйство",
                            "Глобальные проблемы"
                        ]
                    },
                    "География России": {
                        "topics": [
                            "Географическое положение",
                            "Рельеф и недра",
                            "Климат России",
                            "Внутренние воды",
                            "Природные зоны России",
                            "Население России"
                        ]
                    }
                }
            },
            "Информатика": {
                "icon": "💻",
                "sections": {
                    "Основы программирования": {
                        "topics": [
                            "Алгоритмы",
                            "Переменные и типы данных",
                            "Условные операторы",
                            "Циклы",
                            "Функции",
                            "Массивы"
                        ]
                    },
                    "Информация и данные": {
                        "topics": [
                            "Системы счисления",
                            "Кодирование информации",
                            "Базы данных",
                            "Файловые системы",
                            "Сжатие данных",
                            "Защита информации"
                        ]
                    },
                    "Компьютерные сети": {
                        "topics": [
                            "Интернет",
                            "Протоколы передачи данных",
                            "Веб-технологии",
                            "Электронная почта",
                            "Безопасность в сети",
                            "Облачные технологии"
                        ]
                    }
                }
            },
            "Биология": {
                "icon": "🧬",
                "sections": {
                    "Общая биология": {
                        "topics": [
                            "Клеточная теория",
                            "Строение клетки",
                            "Обмен веществ",
                            "Размножение",
                            "Наследственность",
                            "Эволюция"
                        ]
                    },
                    "Ботаника": {
                        "topics": [
                            "Строение растений",
                            "Фотосинтез",
                            "Размножение растений",
                            "Систематика растений",
                            "Экология растений",
                            "Значение растений"
                        ]
                    },
                    "Зоология": {
                        "topics": [
                            "Простейшие",
                            "Беспозвоночные",
                            "Позвоночные",
                            "Поведение животных",
                            "Экология животных",
                            "Эволюция животного мира"
                        ]
                    }
                }
            }
        }
        self.init_theory_session()
        self._init_ollama_client()
    
    def _init_ollama_client(self):
        """Инициализация Ollama клиента для генерации теории"""
        # Проверяем доступность сервера перед инициализацией
        if not self._check_ollama_server_available():
            print("Ollama сервер недоступен (порт 11434 не отвечает), теория будет генерироваться через OpenAI или локально")
            self.ollama_client = None
            self.model_name = "deepseek-r1:7b"
            return
        
        # Список моделей для попытки инициализации (только deepseek-r1:7b)
        models_to_try = [
            ("deepseek-r1:7b", 0.7)
        ]
        
        for model_name, temperature in models_to_try:
            try:
                # Пробуем использовать модель напрямую
                print(f"Пробуем инициализировать модель {model_name}...")
                self.ollama_client = OllamaLLM(model=model_name, temperature=temperature)
                self.model_name = model_name
                
                # Делаем тестовый запрос, чтобы убедиться, что модель действительно доступна
                try:
                    test_response = self.ollama_client.invoke("test")
                    if test_response is not None:
                        print(f"✓ Генерация теории успешно использует модель: {model_name}")
                        return
                    else:
                        print(f"✗ Модель {model_name} вернула пустой ответ, пробуем следующую...")
                        self.ollama_client = None
                        continue
                except Exception as test_error:
                    error_str = str(test_error).lower()
                    if "not found" in error_str or "404" in error_str or "model" in error_str:
                        print(f"✗ Модель {model_name} не найдена при тестовом запросе, пробуем следующую...")
                    else:
                        print(f"✗ Ошибка при тестовом запросе к модели {model_name}: {test_error}")
                    self.ollama_client = None
                    continue
                    
            except Exception as e:
                error_str = str(e).lower()
                # Проверяем, является ли это ошибкой "модель не найдена"
                if "not found" in error_str or "404" in error_str or "model" in error_str and "not" in error_str:
                    print(f"✗ Модель {model_name} не найдена, пробуем следующую...")
                else:
                    print(f"✗ Ошибка при инициализации модели {model_name}: {e}")
                self.ollama_client = None
                continue
        
        # Если модель недоступна
        self.ollama_client = None
        self.model_name = "deepseek-r1:7b"
        print("⚠ Модель deepseek-r1:7b недоступна, теория будет генерироваться через OpenAI или локально")
        print("Для использования локальной модели выполните:")
        print("  ollama pull deepseek-r1:7b")
    
    def _check_ollama_server_available(self):
        """Проверка доступности Ollama сервера через проверку порта"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 11434))
            sock.close()
            return result == 0
        except Exception as e:
            print(f"Ошибка проверки доступности Ollama сервера: {e}")
            return False
    
    def _check_ollama_connection(self):
        """Проверка доступности Ollama и переподключение при необходимости"""
        try:
            # Сначала проверяем доступность сервера
            if not self._check_ollama_server_available():
                print("Ollama сервер недоступен (порт 11434 не отвечает)")
                print("Убедитесь, что Ollama запущен. Запустите: ollama serve")
                self.ollama_client = None
                return False
            
            if self.ollama_client is None:
                # Пробуем переинициализировать клиент
                print("Пробуем переподключиться к Ollama...")
                self._init_ollama_client()
                if self.ollama_client is not None:
                    print("Успешно переподключились к Ollama")
                    return True
                else:
                    print("Не удалось переподключиться к Ollama")
                    return False
            
            # Если клиент есть, считаем что он доступен (проверка будет при реальном запросе)
            # Это оптимизация - не делаем тестовый запрос каждый раз
            return True
        except Exception as e:
            print(f"Ошибка проверки подключения Ollama: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _try_fallback_model(self):
        """Попытка переподключиться к модели deepseek-r1:7b при ошибке"""
        try:
            # Сначала проверяем доступность Ollama сервера
            if not self._check_ollama_server_available():
                print("Ollama сервер недоступен, переподключение не поможет")
                self.ollama_client = None
                return False
            
            # Пробуем переподключиться к deepseek-r1:7b
            print("Пробуем переподключиться к deepseek-r1:7b...")
            self.ollama_client = OllamaLLM(model="deepseek-r1:7b", temperature=0.7)
            self.model_name = "deepseek-r1:7b"
            print("Успешно переподключились к deepseek-r1:7b")
            return True
        except Exception as e:
            print(f"Ошибка при переподключении к deepseek-r1:7b: {e}")
            self.ollama_client = None
            return False
    
    def _clean_text_from_cursor(self, text):
        """Очистить текст от курсора и лишних пробелов"""
        if not text:
            return ""
        # Убираем все возможные варианты курсора
        cleaned = str(text)
        # Убираем все варианты курсора
        cursor_variants = ["▌", "▋", "▊", "▉", "█", "▐", "▎", "▍"]
        for cursor in cursor_variants:
            cleaned = cleaned.replace(cursor, "")
        # Исправляем проблемы с пробелами в командах и тексте
        cleaned = cleaned.replace("ollamapull", "ollama pull")
        cleaned = cleaned.replace("ollamalist", "ollama list")
        cleaned = cleaned.replace("deepseek :7b", "deepseek:7b")
        cleaned = cleaned.replace("deepseek-r1 :7b", "deepseek-r1:7b")
        cleaned = cleaned.replace("deepseek:7bзагружена", "deepseek:7b загружена")
        cleaned = cleaned.replace("deepseek-r1:7b загружена", "deepseek-r1:7b загружена")
        cleaned = cleaned.replace("deepseek:7b загружена:", "deepseek:7b загружена:")
        cleaned = cleaned.replace("модельdeepseek", "модель deepseek")
        cleaned = cleaned.replace("модель deepseek:7b", "модель deepseek:7b")
        cleaned = cleaned.replace("неудалось сгенерировать", "не удалось сгенерировать")
        # Исправляем проблемы с форматированием команд (слипшиеся команды)
        cleaned = cleaned.replace(":ollama pull", ": `ollama pull")
        cleaned = cleaned.replace(":ollama list", ": `ollama list")
        cleaned = cleaned.replace("загружена:ollama", "загружена: `ollama")
        cleaned = cleaned.replace("доступна:ollama", "доступна: `ollama")
        cleaned = cleaned.strip()
        return cleaned
    
    def _save_explanation_text(self, text):
        """Безопасное сохранение текста объяснения с очисткой от курсора"""
        if not text:
            st.session_state.theory_state['explanation_text'] = None
            return None
        # Многократная очистка для надежности
        cleaned_text = self._clean_text_from_cursor(text)
        # Дополнительная проверка - если все еще есть курсор, очищаем еще раз
        if "▌" in cleaned_text or "▋" in cleaned_text or "▊" in cleaned_text or "▉" in cleaned_text:
            cursor_variants = ["▌", "▋", "▊", "▉", "█", "▐", "▎", "▍"]
            for cursor in cursor_variants:
                cleaned_text = cleaned_text.replace(cursor, "")
        # Исправляем проблемы с пробелами в командах перед сохранением
        cleaned_text = cleaned_text.replace("ollamapull", "ollama pull")
        cleaned_text = cleaned_text.replace("ollamalist", "ollama list")
        cleaned_text = cleaned_text.replace("deepseek :7b", "deepseek:7b")
        cleaned_text = cleaned_text.replace("deepseek-r1 :7b", "deepseek-r1:7b")
        cleaned_text = cleaned_text.replace("deepseek:7bзагружена", "deepseek:7b загружена")
        cleaned_text = cleaned_text.replace("deepseek-r1:7b загружена", "deepseek-r1:7b загружена")
        cleaned_text = cleaned_text.replace("deepseek:7b загружена:", "deepseek:7b загружена:")
        cleaned_text = cleaned_text.replace("модельdeepseek", "модель deepseek")
        cleaned_text = cleaned_text.replace("модель deepseek:7b", "модель deepseek:7b")
        # Исправляем "неудалось сгенерировать" (с пробелом, но слитно)
        cleaned_text = cleaned_text.replace("неудалось сгенерировать", "не удалось сгенерировать")
        # Исправляем проблемы с форматированием команд (слипшиеся команды)
        cleaned_text = cleaned_text.replace(":ollama pull", ": `ollama pull")
        cleaned_text = cleaned_text.replace(":ollama list", ": `ollama list")
        cleaned_text = cleaned_text.replace("загружена:ollama", "загружена: `ollama")
        cleaned_text = cleaned_text.replace("доступна:ollama", "доступна: `ollama")
        # НЕ используем strip() чтобы сохранить форматирование, только убираем лишние пробелы в начале/конце
        cleaned_text = cleaned_text.strip()
        st.session_state.theory_state['explanation_text'] = cleaned_text
        return cleaned_text
    
    def init_theory_session(self):
        """Инициализация сессии для теории"""
        if 'theory_state' not in st.session_state:
            st.session_state.theory_state = {
                'current_page': 'subjects',  # subjects, sections, topics, explanation
                'selected_subject': None,
                'selected_section': None,
                'selected_topic': None,
                'explanation_text': None
            }
    
    def show_theory_interface(self):
        """Главный интерфейс теории"""
        try:
            # Убеждаемся, что состояние инициализировано
            self.init_theory_session()
            
            st.header("📚 Теоретические материалы")
            
            # Навигационные кнопки
            self.show_navigation()
            
            # Отображение соответствующей страницы
            if st.session_state.theory_state['current_page'] == 'subjects':
                self.show_subjects()
            elif st.session_state.theory_state['current_page'] == 'sections':
                self.show_sections()
            elif st.session_state.theory_state['current_page'] == 'topics':
                self.show_topics()
            elif st.session_state.theory_state['current_page'] == 'explanation':
                self.show_explanation()
            
        except Exception as e:
            st.error(f"Ошибка в интерфейсе теории: {e}")
            print(f"Ошибка в интерфейсе теории: {e}")
    
    def show_navigation(self):
        """Показать навигационные кнопки"""
        try:
            state = st.session_state.theory_state
            
            # Хлебные крошки
            breadcrumbs = []
            if state['current_page'] != 'subjects':
                breadcrumbs.append("Предметы")
            if state['selected_subject'] and state['current_page'] not in ['subjects', 'sections']:
                breadcrumbs.append(state['selected_subject'])
            if state['selected_section'] and state['current_page'] not in ['subjects', 'sections', 'topics']:
                breadcrumbs.append(state['selected_section'])
            if state['selected_topic']:
                breadcrumbs.append(state['selected_topic'])
            
            if breadcrumbs:
                st.markdown(" → ".join(breadcrumbs))
                st.markdown("---")
            
            # Кнопка "Назад"
            if state['current_page'] != 'subjects':
                if st.button("⬅️ Назад", key="theory_back_button"):
                    self.navigate_back()
                    st.rerun()
            
        except Exception as e:
            st.error(f"Ошибка навигации: {e}")
            print(f"Ошибка навигации: {e}")
    
    def navigate_back(self):
        """Навигация назад"""
        try:
            state = st.session_state.theory_state
            
            if state['current_page'] == 'explanation':
                state['current_page'] = 'topics'
                state['selected_topic'] = None
                state['explanation_text'] = None
            elif state['current_page'] == 'topics':
                state['current_page'] = 'sections'
                state['selected_section'] = None
            elif state['current_page'] == 'sections':
                state['current_page'] = 'subjects'
                state['selected_subject'] = None
            
        except Exception as e:
            print(f"Ошибка навигации назад: {e}")
    
    def show_subjects(self):
        """Показать список предметов"""
        try:
            st.subheader("Выберите предмет:")
            
            # Создаем сетку кнопок для предметов (3 колонки для лучшего отображения)
            subjects = list(self.SUBJECTS_STRUCTURE.keys())
            
            # Отображаем предметы по 3 в ряду
            for i in range(0, len(subjects), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(subjects):
                        subject = subjects[i + j]
                        with cols[j]:
                            icon = self.SUBJECTS_STRUCTURE[subject]["icon"]
                            if st.button(f"{icon} {subject}", key=f"subject_{subject}", use_container_width=True):
                                st.session_state.theory_state['selected_subject'] = subject
                                st.session_state.theory_state['current_page'] = 'sections'
                                # Очищаем старые данные при выборе нового предмета
                                st.session_state.theory_state['selected_section'] = None
                                st.session_state.theory_state['selected_topic'] = None
                                st.session_state.theory_state['explanation_text'] = None
                                st.rerun()
            
        except Exception as e:
            st.error(f"Ошибка отображения предметов: {e}")
            print(f"Ошибка отображения предметов: {e}")
    
    def show_sections(self):
        """Показать разделы выбранного предмета"""
        try:
            subject = st.session_state.theory_state['selected_subject']
            if not subject:
                st.session_state.theory_state['current_page'] = 'subjects'
                st.rerun()
                return
            
            icon = self.SUBJECTS_STRUCTURE[subject]["icon"]
            st.subheader(f"{icon} {subject}")
            st.write("Выберите раздел:")
            
            sections = self.SUBJECTS_STRUCTURE[subject]["sections"]
            
            # Создаем кнопки для разделов
            for section_name in sections.keys():
                if st.button(f"📖 {section_name}", key=f"section_{section_name}", use_container_width=True):
                    st.session_state.theory_state['selected_section'] = section_name
                    st.session_state.theory_state['current_page'] = 'topics'
                    # Очищаем старое объяснение при выборе нового раздела
                    st.session_state.theory_state['selected_topic'] = None
                    st.session_state.theory_state['explanation_text'] = None
                    st.rerun()
            
        except Exception as e:
            st.error(f"Ошибка отображения разделов: {e}")
            print(f"Ошибка отображения разделов: {e}")
    
    def show_topics(self):
        """Показать темы выбранного раздела"""
        try:
            subject = st.session_state.theory_state['selected_subject']
            section = st.session_state.theory_state['selected_section']
            
            if not subject or not section:
                st.session_state.theory_state['current_page'] = 'subjects'
                st.rerun()
                return
            
            icon = self.SUBJECTS_STRUCTURE[subject]["icon"]
            st.subheader(f"{icon} {subject} → {section}")
            st.write("Выберите тему для изучения:")
            
            topics = self.SUBJECTS_STRUCTURE[subject]["sections"][section]["topics"]
            
            # Создаем кнопки для тем
            for topic in topics:
                if st.button(f"🎯 {topic}", key=f"topic_{topic}", use_container_width=True):
                    st.session_state.theory_state['selected_topic'] = topic
                    st.session_state.theory_state['current_page'] = 'explanation'
                    # Очищаем старое объяснение при выборе новой темы
                    st.session_state.theory_state['explanation_text'] = None
                    st.rerun()
            
        except Exception as e:
            st.error(f"Ошибка отображения тем: {e}")
            print(f"Ошибка отображения тем: {e}")
    
    def show_explanation(self):
        """Показать объяснение выбранной темы"""
        try:
            subject = st.session_state.theory_state['selected_subject']
            section = st.session_state.theory_state['selected_section']
            topic = st.session_state.theory_state['selected_topic']
            
            if not all([subject, section, topic]):
                st.session_state.theory_state['current_page'] = 'subjects'
                st.rerun()
                return
            
            icon = self.SUBJECTS_STRUCTURE[subject]["icon"]
            st.subheader(f"{icon} {subject} → {section} → {topic}")
            
            # Проверяем, изменилась ли тема - если да, сбрасываем флаг отображения
            current_topic_key = f"{subject}_{section}_{topic}"
            last_topic_key = st.session_state.theory_state.get('last_topic_key')
            if current_topic_key != last_topic_key:
                st.session_state.theory_state['explanation_displayed'] = False
                st.session_state.theory_state['last_topic_key'] = current_topic_key
            
            # Проверяем, есть ли уже объяснение (и это не шаблон ошибки)
            explanation_text = st.session_state.theory_state.get('explanation_text')
            # Очищаем от возможного курсора при загрузке из session_state
            if explanation_text:
                explanation_text = self._clean_text_from_cursor(explanation_text)
                # Обновляем в session_state очищенную версию
                self._save_explanation_text(explanation_text)
            # Проверяем, является ли текст старым сообщением об ошибке
            is_error_template = explanation_text and (
                "К сожалению, не удалось сгенерировать" in explanation_text or
                "К сожалению, неудалось сгенерировать" in explanation_text or
                "неудалось сгенерировать" in explanation_text or
                "не удалосьсгенерировать" in explanation_text or
                "неудалосьсгенерировать" in explanation_text or
                "Сервер Ollama доступен, но была ошибка" in explanation_text or
                "Сервер Ollama доступен, но возникла ошибка" in explanation_text or
                "Что можно сделать:" in explanation_text or
                "Убедитесь, что модель" in explanation_text
            )
            # Также проверяем на старое название модели
            is_old_error = explanation_text and "deepseek:7b" in explanation_text and "deepseek-r1:7b" not in explanation_text
            
            # Если есть сообщение об ошибке (особенно старое), очищаем его
            if is_error_template or is_old_error:
                print(f"Обнаружено сообщение об ошибке (старое: {is_old_error}), очищаем и пробуем получить объяснение для: {topic}")
                st.session_state.theory_state['explanation_text'] = None
                explanation_text = None
            
            if not explanation_text or is_error_template:
                # Используем spinner для индикации загрузки
                with st.spinner("🔄 Генерирую объяснение..."):
                    try:
                        # Используем НЕ-streaming метод для получения текста целиком
                        # Это полностью избегает проблем с DOM обновлениями
                        print(f"Начинаем генерацию объяснения для темы: {topic}")
                        full_text = self.get_topic_explanation(subject, section, topic, regenerate=False)
                        
                        # Проверяем и сохраняем финальный текст (без курсора)
                        full_text = self._clean_text_from_cursor(full_text)
                        # Исправляем проблемы с пробелами в командах
                        full_text = full_text.replace("ollamapull", "ollama pull")
                        full_text = full_text.replace("ollamalist", "ollama list")
                        full_text = full_text.replace("deepseek :7b", "deepseek:7b")
                        full_text = full_text.replace("deepseek:7bзагружена", "deepseek:7b загружена")
                        
                        if full_text and len(full_text) > 50:  # Проверяем, что текст не слишком короткий (минимум 50 символов)
                            # Проверяем, является ли это финальным сообщением об ошибке от _get_error_message
                            # Такие сообщения уже прошли все fallback варианты и должны быть отображены как есть
                            is_final_error_message = (
                                "## " + topic in full_text and
                                ("К сожалению, не удалось сгенерировать объяснение этой темы" in full_text or
                                 "К сожалению, неудалось сгенерировать объяснение этой темы" in full_text) and
                                ("**Предмет:**" in full_text or "**Раздел:**" in full_text)
                            )
                            
                            if is_final_error_message:
                                # Это финальное сообщение об ошибке, все варианты уже испробованы
                                # Просто сохраняем и отображаем его
                                print(f"Получено финальное сообщение об ошибке (длина: {len(full_text)} символов), отображаем как есть")
                                explanation_text = self._save_explanation_text(full_text)
                            elif len(full_text) > 200:
                                # Если ответ достаточно длинный (>200 символов), это скорее всего нормальное объяснение
                                # get_topic_explanation уже пробовал все варианты (Ollama -> OpenAI -> локальное -> ошибка)
                                # Поэтому просто принимаем ответ как есть
                                print(f"Получено объяснение длиной {len(full_text)} символов от get_topic_explanation, принимаем как есть")
                                explanation_text = self._save_explanation_text(full_text)
                            else:
                                # Для коротких ответов (50-200 символов) проверяем более тщательно
                                # Но только на явные признаки ошибок, а не на случайные совпадения
                                full_text_lower = full_text.lower()
                                full_text_start = full_text_lower[:100]  # Первые 100 символов
                                
                                # Только самые явные индикаторы ошибок в начале ответа
                                explicit_error_indicators = [
                                    "к сожалению, не удалось сгенерировать",
                                    "к сожалению, неудалось сгенерировать",
                                    "не удалось сгенерировать объяснение",
                                    "неудалось сгенерировать объяснение",
                                    "оллама сервер недоступен",
                                    "ollama сервер недоступен",
                                    "что можно сделать:",
                                    "убедитесь, что модель",
                                    "проверьте, доступна ли модель"
                                ]
                                
                                # Проверяем только явные индикаторы в начале ответа
                                is_explicit_error = any(indicator in full_text_start for indicator in explicit_error_indicators)
                                
                                # Проверяем команды (должны быть в начале)
                                is_command = (
                                    full_text.strip().startswith("ollama") or 
                                    full_text.strip().startswith("Ollama")
                                )
                                
                                if is_explicit_error or is_command:
                                    # Это явная ошибка или команда, пробуем fallback
                                    print(f"Обнаружено явное сообщение об ошибке или команда в коротком ответе (is_explicit_error={is_explicit_error}, is_command={is_command})")
                                    # Пробуем локальное объяснение
                                    local_explanation = self._get_local_explanation(subject, section, topic)
                                    if local_explanation:
                                        explanation_text = self._save_explanation_text(local_explanation)
                                    else:
                                        explanation_text = self._get_error_message(subject, section, topic)
                                        explanation_text = self._clean_text_from_cursor(explanation_text)
                                        self._save_explanation_text(explanation_text)
                                else:
                                    # Короткий ответ, но не явная ошибка - принимаем как есть
                                    print(f"Короткий ответ ({len(full_text)} символов), но не явная ошибка, принимаем как есть")
                                    explanation_text = self._save_explanation_text(full_text)
                        else:
                            # Если текст пустой или слишком короткий, показываем ошибку
                            print(f"Текст слишком короткий или пустой (длина: {len(full_text) if full_text else 0})")
                            raise Exception("Получен пустой или некорректный ответ от модели")
                    except Exception as e:
                        print(f"Ошибка генерации объяснения: {e}")
                        import traceback
                        traceback.print_exc()
                        
                        # Получаем сообщение об ошибке и очищаем его от курсора
                        explanation_text = self._get_error_message(subject, section, topic)
                        explanation_text = self._clean_text_from_cursor(explanation_text)
                        # Дополнительная проверка - убираем все возможные варианты курсора
                        explanation_text = explanation_text.replace("▌", "").replace("▋", "").replace("▊", "").replace("▉", "").strip()
                        # Финальная очистка перед отображением
                        explanation_text = self._clean_text_from_cursor(explanation_text)
                        # Исправляем проблемы с пробелами
                        explanation_text = explanation_text.replace("ollamapull", "ollama pull")
                        explanation_text = explanation_text.replace("ollamalist", "ollama list")
                        explanation_text = explanation_text.replace("deepseek :7b", "deepseek:7b")
                        explanation_text = explanation_text.replace("deepseek-r1 :7b", "deepseek-r1:7b")
                        explanation_text = explanation_text.replace("deepseek:7bзагружена", "deepseek:7b загружена")
                        explanation_text = explanation_text.replace("deepseek-r1:7b загружена", "deepseek-r1:7b загружена")
                        explanation_text = explanation_text.replace("deepseek:7b загружена:", "deepseek:7b загружена:")
                        explanation_text = explanation_text.replace("модельdeepseek", "модель deepseek")
                        explanation_text = explanation_text.replace("неудалось сгенерировать", "не удалось сгенерировать")
                        # Исправляем проблемы с форматированием команд (слипшиеся команды)
                        explanation_text = explanation_text.replace(":ollama pull", ": `ollama pull")
                        explanation_text = explanation_text.replace(":ollama list", ": `ollama list")
                        explanation_text = explanation_text.replace("загружена:ollama", "загружена: `ollama")
                        explanation_text = explanation_text.replace("доступна:ollama", "доступна: `ollama")
                        
                        # Сохраняем очищенное сообщение об ошибке
                        self._save_explanation_text(explanation_text)
            
            # Отображаем объяснение (если оно уже было сохранено)
            if explanation_text:
                # Очищаем от возможного курсора перед отображением (многократная очистка)
                clean_text = str(explanation_text)
                # Убираем все возможные варианты курсора
                cursor_variants = ["▌", "▋", "▊", "▉", "█", "▐", "▎", "▍"]
                for cursor in cursor_variants:
                    clean_text = clean_text.replace(cursor, "")
                # Исправляем проблемы с пробелами в командах
                clean_text = clean_text.replace("ollamapull", "ollama pull")
                clean_text = clean_text.replace("ollamalist", "ollama list")
                clean_text = clean_text.replace("deepseek :7b", "deepseek:7b")
                clean_text = clean_text.replace("deepseek-r1 :7b", "deepseek-r1:7b")
                clean_text = clean_text.replace("deepseek:7bзагружена", "deepseek:7b загружена")
                clean_text = clean_text.replace("deepseek-r1:7b загружена", "deepseek-r1:7b загружена")
                clean_text = clean_text.replace("deepseek:7b загружена:", "deepseek:7b загружена:")
                clean_text = clean_text.replace("модельdeepseek", "модель deepseek")
                clean_text = clean_text.replace("неудалось сгенерировать", "не удалось сгенерировать")
                # Исправляем проблемы с форматированием команд (слипшиеся команды)
                clean_text = clean_text.replace(":ollama pull", ": `ollama pull")
                clean_text = clean_text.replace(":ollama list", ": `ollama list")
                clean_text = clean_text.replace("загружена:ollama", "загружена: `ollama")
                clean_text = clean_text.replace("доступна:ollama", "доступна: `ollama")
                # Исправляем проблемы с форматированием списка
                clean_text = clean_text.replace("2.Проверьте", "2. Проверьте")
                clean_text = clean_text.replace("3.Настройте", "3. Настройте")
                clean_text = clean_text.replace("4. Обратиться", "4. Обратитесь")
                clean_text = clean_text.strip()
                # Дополнительная проверка через функцию очистки
                clean_text = self._clean_text_from_cursor(clean_text)
                if clean_text:
                    # Используем st.empty() для стабильного отображения и избежания ошибок DOM
                    explanation_container = st.empty()
                    try:
                        explanation_container.markdown(clean_text)
                    except Exception as dom_error:
                        # Если произошла ошибка DOM, пробуем отобразить еще раз
                        print(f"Ошибка DOM при отображении: {dom_error}")
                        try:
                            explanation_container.markdown(clean_text)
                        except:
                            # В крайнем случае используем обычный markdown
                            st.markdown(clean_text)
                    # Обновляем session_state очищенной версией на случай, если там был курсор
                    if clean_text != explanation_text:
                        self._save_explanation_text(clean_text)
            
            # Кнопка для нового объяснения
            if st.button("🔄 Получить другое объяснение", key="regenerate_explanation_button"):
                # Очищаем старое объяснение
                st.session_state.theory_state['explanation_text'] = None
                st.session_state.theory_state['explanation_displayed'] = False
                # Перезагружаем страницу для чистого состояния
                st.rerun()
            
        except Exception as e:
            st.error(f"Ошибка отображения объяснения: {e}")
            print(f"Ошибка отображения объяснения: {e}")
    
    def get_topic_explanation(self, subject, section, topic, regenerate=False):
        """Получить объяснение темы от LLM (Ollama или OpenAI)"""
        try:
            # Сначала проверяем, есть ли локальное объяснение в файле
            if not regenerate:
                local_explanation = self._get_local_explanation(subject, section, topic, generate_if_missing=False)
                if local_explanation:
                    return local_explanation
            
            # Приоритет: локальная LLM (Ollama) через deepseek, затем OpenAI
            # Проверяем, что ollama_client не только не None, но и действительно доступен
            if self.ollama_client is not None and self._check_ollama_connection():
                try:
                    return self.get_ollama_explanation(subject, section, topic, regenerate)
                except Exception as e:
                    print(f"Ошибка Ollama: {e}")
                    # Продолжаем к следующему варианту
            else:
                print("Ollama клиент недоступен, пробуем сгенерировать локальное объяснение через deepseek...")
                # Если Ollama недоступен, но сервер доступен, пробуем переподключиться
                if self._check_ollama_server_available():
                    try:
                        print("Ollama сервер доступен, пробуем переподключиться...")
                        self._init_ollama_client()
                        if self.ollama_client is not None and self._check_ollama_connection():
                            try:
                                return self.get_ollama_explanation(subject, section, topic, regenerate)
                            except Exception as e:
                                print(f"Ошибка Ollama после переподключения: {e}")
                    except Exception as reconnect_error:
                        print(f"Ошибка переподключения к Ollama: {reconnect_error}")
            
            # Если Ollama недоступен, сначала пробуем OpenAI (если доступен)
            # Это приоритетнее, чем генерация локального объяснения
            if self.api_key:
                try:
                    print("Ollama недоступен, пробуем использовать OpenAI...")
                    return self.get_openai_explanation(subject, section, topic, regenerate)
                except Exception as e2:
                    print(f"Ошибка OpenAI API: {e2}")
            
            # Если OpenAI тоже недоступен, пробуем сгенерировать локальное объяснение через deepseek
            # (если файла нет, оно будет сгенерировано и сохранено)
            # Перед генерацией пробуем переподключиться к Ollama
            print("OpenAI недоступен, пробуем сгенерировать локальное объяснение через deepseek (Ollama)...")
            if self._check_ollama_server_available():
                print("Ollama сервер доступен, пробуем переподключиться перед генерацией...")
                self._init_ollama_client()
            local_explanation = self._get_local_explanation(subject, section, topic, generate_if_missing=True)
            if local_explanation:
                print("Локальное объяснение успешно сгенерировано через deepseek")
                return local_explanation
            
            # Последняя попытка - получить локальное объяснение из файла (если оно было создано)
            local_explanation = self._get_local_explanation(subject, section, topic, generate_if_missing=False)
            if local_explanation:
                return local_explanation
            
            return self._get_error_message(subject, section, topic)
        except Exception as e:
            print(f"Ошибка получения объяснения: {e}")
            import traceback
            traceback.print_exc()
            
            # Пробуем OpenAI как fallback
            if self.api_key:
                try:
                    print("Пробуем OpenAI как fallback после ошибки...")
                    return self.get_openai_explanation(subject, section, topic, regenerate)
                except Exception as e2:
                    print(f"Ошибка OpenAI при fallback: {e2}")
            
            # Пробуем получить локальное объяснение
            local_explanation = self._get_local_explanation(subject, section, topic)
            if local_explanation:
                return local_explanation
            
            return self._get_error_message(subject, section, topic)
    
    def get_topic_explanation_stream(self, subject, section, topic, regenerate=False):
        """Получить объяснение темы от LLM с streaming (Ollama или OpenAI)"""
        try:
            # Сначала проверяем, есть ли локальное объяснение
            # Если не требуется регенерация, используем локальное объяснение
            if not regenerate:
                local_explanation = self._get_local_explanation(subject, section, topic)
                if local_explanation:
                    print(f"Используется локальное объяснение для темы: {topic}")
                    # Используем локальное объяснение с имитацией streaming
                    chunk_size = 10
                    for i in range(0, len(local_explanation), chunk_size):
                        chunk = local_explanation[i:i+chunk_size]
                        yield chunk
                        time.sleep(0.02)
                    return
                else:
                    print(f"Локальное объяснение не найдено для темы: {topic}")
            
            # Приоритет: локальная LLM (Ollama), затем OpenAI
            # Проверяем доступность Ollama перед использованием
            if self.ollama_client is not None:
                # Проверяем подключение перед использованием
                if self._check_ollama_connection():
                    try:
                        yield from self.get_ollama_explanation_stream(subject, section, topic, regenerate)
                        return
                    except Exception as e:
                        error_str = str(e).lower()
                        is_connection_error = any(keyword in error_str for keyword in [
                            'connection', 'подключение', 'refused', 'отверг', '10061', '10060'
                        ])
                        if is_connection_error:
                            print("Ошибка подключения к Ollama, пробуем OpenAI...")
                        else:
                            print(f"Ошибка Ollama: {e}")
            
            # Пробуем OpenAI как fallback
            if self.api_key:
                try:
                    yield from self.get_openai_explanation_stream(subject, section, topic, regenerate)
                    return
                except Exception as e2:
                    print(f"Ошибка OpenAI API (streaming): {e2}")
            
            # Только если и Ollama, и OpenAI недоступны, используем локальное объяснение
            local_explanation = self._get_local_explanation(subject, section, topic)
            if local_explanation:
                # Имитируем streaming для локального объяснения
                chunk_size = 10
                for i in range(0, len(local_explanation), chunk_size):
                    chunk = local_explanation[i:i+chunk_size]
                    yield chunk
                    time.sleep(0.02)
            else:
                error_msg = self._get_error_message(subject, section, topic)
                # Очищаем от курсора
                error_msg = self._clean_text_from_cursor(error_msg)
                # Возвращаем весь текст сразу, а не по частям
                yield error_msg
        except Exception as e:
            print(f"Ошибка получения объяснения (streaming): {e}")
            # Пробуем OpenAI как fallback, если Ollama не сработал
            if self.api_key:
                try:
                    yield from self.get_openai_explanation_stream(subject, section, topic, regenerate)
                    return
                except Exception as e2:
                    print(f"Ошибка OpenAI API (streaming): {e2}")
            
            # Только в крайнем случае используем локальное объяснение
            local_explanation = self._get_local_explanation(subject, section, topic)
            if local_explanation:
                chunk_size = 10
                for i in range(0, len(local_explanation), chunk_size):
                    chunk = local_explanation[i:i+chunk_size]
                    yield chunk
                    time.sleep(0.02)
            else:
                error_msg = self._get_error_message(subject, section, topic)
                # Очищаем от курсора
                error_msg = self._clean_text_from_cursor(error_msg)
                # Возвращаем весь текст сразу, а не по частям
                yield error_msg
    
    def get_ollama_explanation(self, subject, section, topic, regenerate=False):
        """Получить объяснение от локальной LLM (Ollama)"""
        # Создаем специальный промпт для учителя (выносим вне try для доступности в except)
        system_prompt = f"""Ты опытный учитель {subject.lower()}а с 20-летним стажем. 
Тебе необходимо просто и понятно объяснить тему "{topic}" из раздела "{section}".

Требования к объяснению:
1. Используй простой и доступный язык
2. Приводи конкретные примеры
3. Объясняй шаг за шагом
4. Используй аналогии из повседневной жизни
5. Структурируй материал логично
6. Выделяй ключевые моменты
7. Пиши на русском языке
8. Объем: 300-500 слов

Начни объяснение с краткого введения в тему, затем подробно разбери основные понятия и заверши практическими советами или примерами применения."""
        
        user_prompt = f"Объясни тему '{topic}' из раздела '{section}' предмета '{subject}'"
        
        # Формируем полный промпт
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        try:
            # Проверяем доступность Ollama перед использованием
            if self.ollama_client is None:
                # Пробуем переподключиться
                if self._check_ollama_server_available():
                    print("Ollama сервер доступен, пробуем переподключиться...")
                    self._init_ollama_client()
            
            if self.ollama_client is None or not self._check_ollama_connection():
                print(f"Ollama клиент недоступен (client={self.ollama_client is not None}, connection={self._check_ollama_connection() if self.ollama_client else False}), пробуем OpenAI...")
                # Если Ollama недоступен, пробуем OpenAI
                if self.api_key:
                    try:
                        print("Пробуем использовать OpenAI как fallback...")
                        return self.get_openai_explanation(subject, section, topic, regenerate)
                    except Exception as e:
                        print(f"Ошибка OpenAI при fallback: {e}")
                # Только если OpenAI тоже недоступен, используем локальное объяснение
                local_explanation = self._get_local_explanation(subject, section, topic)
                if local_explanation:
                    print("Используем локальное объяснение как fallback")
                    return local_explanation
                print("Все варианты исчерпаны, возвращаем сообщение об ошибке")
                return self._get_error_message(subject, section, topic)
            
            print(f"Генерирую объяснение через Ollama (модель: {self.model_name})...")
            # Получаем ответ от модели
            response_text = self.ollama_client.invoke(full_prompt)
            
            if not response_text or len(response_text.strip()) == 0:
                print("Пустой ответ от Ollama, пробуем OpenAI...")
                # Если ответ пустой, пробуем OpenAI
                if self.api_key:
                    try:
                        return self.get_openai_explanation(subject, section, topic, regenerate)
                    except Exception as e:
                        print(f"Ошибка OpenAI при fallback: {e}")
                # Только если OpenAI тоже недоступен, используем локальное объяснение
                local_explanation = self._get_local_explanation(subject, section, topic)
                if local_explanation:
                    return local_explanation
                return self._get_error_message(subject, section, topic)
            
            # Очищаем ответ от возможных префиксов
            response_text = response_text.strip()
            
            # Проверяем минимальную длину ответа (должен быть разумный объем)
            if len(response_text) < 50:
                print(f"Ответ от Ollama слишком короткий ({len(response_text)} символов), пробуем OpenAI...")
                if self.api_key:
                    try:
                        return self.get_openai_explanation(subject, section, topic, regenerate)
                    except Exception as e:
                        print(f"Ошибка OpenAI при fallback: {e}")
                local_explanation = self._get_local_explanation(subject, section, topic)
                if local_explanation:
                    return local_explanation
                return self._get_error_message(subject, section, topic)
            
            # Проверяем, не содержит ли ответ сообщение об ошибке (расширенный список)
            error_indicators = [
                "К сожалению, не удалось сгенерировать",
                "К сожалению, неудалось сгенерировать",
                "не удалосьсгенерировать",
                "не удалось сгенерировать",
                "неудалосьсгенерировать",
                "неудалось сгенерировать",
                "Оллама сервер недоступен",
                "Ollama сервер недоступен",
                "Сервер Ollama доступен, но была ошибка",
                "Сервер Ollama доступен, но возникла ошибка",
                "Генерация сервера Олламы доступна",
                "Генерация сервера Ollama доступна",
                "произошла ошибка при этом",
                "произошла ошибка при генерации",
                "ollama serve",
                "ollama pull",
                "ollamapull",
                "ollamalist",
                "какая модель",
                "модельdeepseek",
                "модель deepseek",
                "deepseek:7b загружена",
                "deepseek:7bзагружена",
                "deepseek :7b",
                "deepseek-r1 :7b",
                "deepseek-r1:7b загружена",
                "Что можно сделать:",
                "Убедитесь, что модель",
                "Проверьте, доступна ли модель",
                "проверьте доступна ли модель",
                "Установить API-ключ"
            ]
            response_lower = response_text.lower()
            if any(indicator.lower() in response_lower for indicator in error_indicators):
                print("Ответ от Ollama содержит сообщение об ошибке, пробуем OpenAI...")
                # Отключаем ollama_client, чтобы не пытаться использовать его снова
                self.ollama_client = None
                if self.api_key:
                    try:
                        return self.get_openai_explanation(subject, section, topic, regenerate)
                    except Exception as e:
                        print(f"Ошибка OpenAI при fallback: {e}")
                # Только если OpenAI тоже недоступен, используем локальное объяснение
                local_explanation = self._get_local_explanation(subject, section, topic)
                if local_explanation:
                    return local_explanation
                return self._get_error_message(subject, section, topic)
            
            # Проверяем, что ответ не является просто инструкцией или командой
            if response_text.startswith("ollama") or response_text.startswith("Ollama"):
                print("Ответ от Ollama похож на команду, а не на объяснение, пробуем OpenAI...")
                if self.api_key:
                    try:
                        return self.get_openai_explanation(subject, section, topic, regenerate)
                    except Exception as e:
                        print(f"Ошибка OpenAI при fallback: {e}")
                local_explanation = self._get_local_explanation(subject, section, topic)
                if local_explanation:
                    return local_explanation
                return self._get_error_message(subject, section, topic)
            
            print(f"Успешно получено объяснение от Ollama (длина: {len(response_text)} символов)")
            
            return response_text
            
        except Exception as e:
            error_str = str(e)
            print(f"Ошибка Ollama API для теории: {e}")
            import traceback
            traceback.print_exc()
            
            # Проверяем тип ошибки
            error_str_lower = error_str.lower()
            is_connection_error = any(keyword in error_str_lower for keyword in [
                'connection', 'подключение', 'refused', 'отверг', '10061', '10060'
            ])
            is_model_error = "not found" in error_str_lower or "404" in error_str
            
            # Если модель не найдена или ошибка подключения, пробуем переключиться на другую модель
            if (is_model_error or is_connection_error) and self._check_ollama_server_available():
                if is_connection_error:
                    print(f"Ошибка подключения к Ollama, проверяем доступность сервера...")
                else:
                    print(f"Модель {self.model_name} недоступна, пробуем переключиться на другую модель...")
                
                # Проверяем доступность сервера перед переключением модели
                if self._try_fallback_model():
                    # Пробуем еще раз с новой моделью
                    if self.ollama_client is not None:
                        try:
                            print(f"Пробуем с моделью {self.model_name}...")
                            response_text = self.ollama_client.invoke(full_prompt)
                            if response_text and len(response_text.strip()) > 50:
                                # Проверяем, не содержит ли ответ сообщение об ошибке (расширенный список)
                                error_indicators = [
                                    "К сожалению, не удалось сгенерировать",
                                    "К сожалению, неудалось сгенерировать",
                                    "не удалосьсгенерировать",
                                    "не удалось сгенерировать",
                                    "неудалосьсгенерировать",
                                    "неудалось сгенерировать",
                                    "Оллама сервер недоступен",
                                    "Ollama сервер недоступен",
                                    "Сервер Ollama доступен, но была ошибка",
                                    "Сервер Ollama доступен, но возникла ошибка",
                                    "ollama serve",
                                    "ollama pull",
                                    "ollamapull",
                                    "ollamalist",
                                    "какая модель",
                                    "модельdeepseek",
                                    "модель deepseek",
                                    "deepseek:7b загружена",
                                    "deepseek:7bзагружена",
                                    "deepseek :7b",
                                    "Что можно сделать:",
                                    "Убедитесь, что модель"
                                ]
                                response_lower = response_text.lower()
                                if not any(indicator.lower() in response_lower for indicator in error_indicators):
                                    # Проверяем, что ответ не является просто командой
                                    if not response_text.strip().startswith("ollama") and not response_text.strip().startswith("Ollama"):
                                        print(f"Успешно получено объяснение от fallback модели (длина: {len(response_text)} символов)")
                                        return response_text.strip()
                                    else:
                                        print("Ответ от fallback модели похож на команду, пробуем OpenAI...")
                                else:
                                    print("Ответ от fallback модели содержит сообщение об ошибке, пробуем OpenAI...")
                            else:
                                print(f"Ответ от fallback модели слишком короткий ({len(response_text.strip()) if response_text else 0} символов), пробуем OpenAI...")
                        except Exception as e2:
                            print(f"Ошибка при повторной попытке с fallback моделью: {e2}")
            
            # В случае ЛЮБОЙ ошибки пробуем OpenAI как fallback (приоритет выше локального объяснения)
            if self.api_key:
                try:
                    print("Пробуем OpenAI как fallback после ошибки Ollama...")
                    return self.get_openai_explanation(subject, section, topic, regenerate)
                except Exception as e3:
                    print(f"Ошибка OpenAI API при fallback: {e3}")
            
            # Только если и Ollama, и OpenAI недоступны, используем локальное объяснение
            local_explanation = self._get_local_explanation(subject, section, topic)
            if local_explanation:
                print("Используем локальное объяснение как последний fallback")
                return local_explanation
            
            print("Все варианты исчерпаны, возвращаем сообщение об ошибке")
            return self._get_error_message(subject, section, topic)
    
    def get_ollama_explanation_stream(self, subject, section, topic, regenerate=False):
        """Получить объяснение от локальной LLM (Ollama) с streaming"""
        system_prompt = f"""Ты опытный учитель {subject.lower()}а с 20-летним стажем. 
Тебе необходимо просто и понятно объяснить тему "{topic}" из раздела "{section}".

Требования к объяснению:
1. Используй простой и доступный язык
2. Приводи конкретные примеры
3. Объясняй шаг за шагом
4. Используй аналогии из повседневной жизни
5. Структурируй материал логично
6. Выделяй ключевые моменты
7. Пиши на русском языке
8. Объем: 300-500 слов

Начни объяснение с краткого введения в тему, затем подробно разбери основные понятия и заверши практическими советами или примерами применения."""
        
        user_prompt = f"Объясни тему '{topic}' из раздела '{section}' предмета '{subject}'"
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        try:
            # Проверяем доступность Ollama перед использованием
            if self.ollama_client is None:
                # Пробуем переподключиться
                if self._check_ollama_server_available():
                    print("Ollama сервер доступен, пробуем переподключиться...")
                    self._init_ollama_client()
            
            if self.ollama_client is None or not self._check_ollama_connection():
                print("Ollama клиент недоступен, пробуем OpenAI...")
                if self.api_key:
                    yield from self.get_openai_explanation_stream(subject, section, topic, regenerate)
                else:
                    # Только если OpenAI тоже недоступен, используем локальное объяснение
                    local_explanation = self._get_local_explanation(subject, section, topic)
                    if local_explanation:
                        chunk_size = 10
                        for i in range(0, len(local_explanation), chunk_size):
                            chunk = local_explanation[i:i+chunk_size]
                            yield chunk
                            time.sleep(0.02)
                    else:
                        # Для сообщения об ошибке не используем streaming, возвращаем сразу весь текст
                        error_msg = self._get_error_message(subject, section, topic)
                        # Очищаем от курсора
                        error_msg = self._clean_text_from_cursor(error_msg)
                        # Возвращаем весь текст сразу, а не по словам
                        yield error_msg
                return
            
            # Для Ollama используем streaming через invoke с callback
            # Но OllamaLLM из langchain может не поддерживать streaming напрямую
            # Поэтому используем альтернативный подход - получаем поток и разбиваем на слова
            try:
                import ollama
                
                # Используем прямой вызов Ollama API для streaming
                try:
                    stream = ollama.chat(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        stream=True
                    )
                except Exception as chat_error:
                    error_str = str(chat_error).lower()
                    is_model_error = any(keyword in error_str for keyword in [
                        'not found', '404', 'model', 'не найдена', 'не найдена модель'
                    ])
                    
                    if is_model_error:
                        print(f"Модель {self.model_name} не найдена при вызове ollama.chat(), пробуем переключиться...")
                        if self._try_fallback_model():
                            # Пробуем еще раз с новой моделью
                            try:
                                stream = ollama.chat(
                                    model=self.model_name,
                                    messages=[
                                        {"role": "system", "content": system_prompt},
                                        {"role": "user", "content": user_prompt}
                                    ],
                                    stream=True
                                )
                            except Exception as e_retry:
                                print(f"Ошибка при повторной попытке с fallback моделью: {e_retry}")
                                raise chat_error  # Пробрасываем исходную ошибку для дальнейшей обработки
                        else:
                            raise chat_error  # Пробрасываем ошибку для дальнейшей обработки
                    else:
                        raise chat_error  # Пробрасываем ошибку для дальнейшей обработки
                
                full_response = ""
                chunks_to_yield = []
                for chunk in stream:
                    if chunk.get('message') and chunk['message'].get('content'):
                        content = chunk['message']['content']
                        full_response += content
                        chunks_to_yield.append(content)
                
                # Проверяем финальный ответ на наличие сообщения об ошибке перед отправкой
                error_indicators = [
                    "К сожалению, не удалось сгенерировать",
                    "К сожалению, неудалось сгенерировать",
                    "не удалосьсгенерировать",
                    "не удалось сгенерировать",
                    "неудалосьсгенерировать",
                    "неудалось сгенерировать",
                    "Оллама сервер недоступен",
                    "Ollama сервер недоступен",
                    "Сервер Ollama доступен, но была ошибка",
                    "Сервер Ollama доступен, но возникла ошибка",
                    "ollama serve",
                    "ollama pull",
                    "ollamapull",
                    "ollamalist",
                    "порт 114343",
                    "порт 11434",
                    "какая модель",
                    "модельdeepseek",
                    "модель deepseek",
                    "deepseek:7b загружена",
                    "deepseek:7bзагружена",
                    "deepseek :7b",
                    "Что можно сделать:",
                    "Убедитесь, что модель"
                ]
                full_response_lower = full_response.lower() if full_response else ""
                if full_response and (len(full_response.strip()) < 50 or any(indicator.lower() in full_response_lower for indicator in error_indicators) or full_response.strip().startswith("ollama") or full_response.strip().startswith("Ollama")):
                    print("Ответ от Ollama содержит сообщение об ошибке, пробуем OpenAI...")
                    if self.api_key:
                        try:
                            yield from self.get_openai_explanation_stream(subject, section, topic, regenerate)
                            return
                        except Exception as e:
                            print(f"Ошибка OpenAI при fallback: {e}")
                    # Только если OpenAI тоже недоступен, используем локальное объяснение
                    local_explanation = self._get_local_explanation(subject, section, topic)
                    if local_explanation:
                        chunk_size = 10
                        for i in range(0, len(local_explanation), chunk_size):
                            chunk = local_explanation[i:i+chunk_size]
                            yield chunk
                            time.sleep(0.02)
                        return
                    error_msg = self._get_error_message(subject, section, topic)
                    # Очищаем от курсора
                    error_msg = self._clean_text_from_cursor(error_msg)
                    # Возвращаем весь текст сразу, а не по частям
                    yield error_msg
                    return
                
                # Если ответ нормальный, отдаем все чанки
                for content in chunks_to_yield:
                    if content.strip():
                        yield content
                        time.sleep(0.02)  # Небольшая задержка для плавности
                
            except ImportError:
                # Если ollama не установлен, используем обычный метод
                print("Библиотека ollama не установлена, используем обычный метод...")
                response_text = self.ollama_client.invoke(full_prompt)
                if response_text:
                    # Имитируем streaming, отдавая текст по частям
                    chunk_size = 10  # Отдаем по 10 символов за раз
                    for i in range(0, len(response_text), chunk_size):
                        chunk = response_text[i:i+chunk_size]
                        yield chunk
                        time.sleep(0.02)
                else:
                    if self.api_key:
                        yield from self.get_openai_explanation_stream(subject, section, topic, regenerate)
                    else:
                        error_msg = self._get_error_message(subject, section, topic)
                        # Очищаем от курсора
                        error_msg = self._clean_text_from_cursor(error_msg)
                        # Возвращаем весь текст сразу, а не по частям
                        yield error_msg
            except Exception as e:
                # Проверяем тип ошибки
                error_str = str(e).lower()
                is_connection_error = any(keyword in error_str for keyword in [
                    'connection', 'подключение', 'refused', 'отверг', '10061', '10060', 'timeout'
                ])
                is_model_error = any(keyword in error_str for keyword in [
                    'not found', '404', 'model', 'не найдена', 'не найдена модель'
                ])
                
                print(f"Ошибка Ollama streaming: {e}")
                import traceback
                traceback.print_exc()
                
                # Если модель не найдена, пробуем переключиться на другую модель
                if is_model_error and self._check_ollama_server_available():
                    print(f"Модель {self.model_name} не найдена, пробуем переключиться на другую модель...")
                    if self._try_fallback_model():
                        # Пробуем еще раз с новой моделью через обычный invoke
                        try:
                            print(f"Пробуем с моделью {self.model_name} через обычный метод...")
                            response_text = self.ollama_client.invoke(full_prompt)
                            if response_text and len(response_text.strip()) > 50:
                                # Проверяем, не содержит ли ответ сообщение об ошибке (расширенный список)
                                error_indicators = [
                                    "К сожалению, не удалось сгенерировать",
                                    "К сожалению, неудалось сгенерировать",
                                    "не удалосьсгенерировать",
                                    "не удалось сгенерировать",
                                    "неудалосьсгенерировать",
                                    "неудалось сгенерировать",
                                    "Оллама сервер недоступен",
                                    "Ollama сервер недоступен",
                                    "Сервер Ollama доступен, но была ошибка",
                                    "Сервер Ollama доступен, но возникла ошибка",
                                    "ollama serve",
                                    "ollama pull",
                                    "ollamapull",
                                    "ollamalist",
                                    "какая модель",
                                    "модельdeepseek",
                                    "модель deepseek",
                                    "deepseek:7b загружена",
                                    "deepseek:7bзагружена",
                                    "deepseek :7b",
                                    "Что можно сделать:",
                                    "Убедитесь, что модель"
                                ]
                                response_lower = response_text.lower()
                                if not any(indicator.lower() in response_lower for indicator in error_indicators) and not response_text.strip().startswith("ollama") and not response_text.strip().startswith("Ollama"):
                                    # Имитируем streaming
                                    chunk_size = 10
                                    for i in range(0, len(response_text), chunk_size):
                                        chunk = response_text[i:i+chunk_size]
                                        yield chunk
                                        time.sleep(0.02)
                                    return
                        except Exception as e3:
                            print(f"Ошибка при повторной попытке с fallback моделью: {e3}")
                
                # Если ошибка подключения, пробуем переподключиться
                if is_connection_error and self._check_ollama_server_available():
                    print("Ошибка подключения к Ollama, пробуем переподключиться...")
                    if self._try_fallback_model():
                        # Пробуем еще раз с новой моделью
                        try:
                            response_text = self.ollama_client.invoke(full_prompt)
                            if response_text and len(response_text.strip()) > 0:
                                # Имитируем streaming
                                chunk_size = 10
                                for i in range(0, len(response_text), chunk_size):
                                    chunk = response_text[i:i+chunk_size]
                                    yield chunk
                                    time.sleep(0.02)
                                return
                        except Exception as e3:
                            print(f"Ошибка при повторной попытке: {e3}")
                
                # При ЛЮБОЙ ошибке пробуем OpenAI как fallback (приоритет выше локального объяснения)
                if self.api_key:
                    try:
                        print("Пробуем OpenAI как fallback после ошибки Ollama streaming...")
                        yield from self.get_openai_explanation_stream(subject, section, topic, regenerate)
                        return
                    except Exception as e4:
                        print(f"Ошибка OpenAI при fallback: {e4}")
                
                # Только если все AI недоступны, используем локальное объяснение
                local_explanation = self._get_local_explanation(subject, section, topic)
                if local_explanation:
                    print("Используем локальное объяснение как последний fallback")
                    # Имитируем streaming для локального объяснения
                    chunk_size = 10
                    for i in range(0, len(local_explanation), chunk_size):
                        chunk = local_explanation[i:i+chunk_size]
                        yield chunk
                        time.sleep(0.02)
                else:
                    print("Все варианты исчерпаны, возвращаем сообщение об ошибке")
                    error_msg = self._get_error_message(subject, section, topic)
                    # Очищаем от курсора
                    error_msg = self._clean_text_from_cursor(error_msg)
                    # Возвращаем весь текст сразу, а не по частям
                    yield error_msg
            
        except Exception as e:
            # Проверяем тип ошибки - если это ошибка подключения, не выводим traceback
            error_str = str(e).lower()
            is_connection_error = any(keyword in error_str for keyword in [
                'connection', 'подключение', 'refused', 'отверг', '10061', '10060', 'timeout'
            ])
            is_model_error = any(keyword in error_str for keyword in [
                'not found', '404', 'model', 'не найдена', 'не найдена модель'
            ])
            
            print(f"Ошибка Ollama streaming API: {e}")
            if not is_connection_error:
                import traceback
                traceback.print_exc()
            
            # Если модель не найдена, пробуем переключиться на другую модель
            if is_model_error and self._check_ollama_server_available():
                print(f"Модель {self.model_name} не найдена во внешнем обработчике, пробуем переключиться...")
                if self._try_fallback_model():
                    try:
                        print(f"Пробуем с моделью {self.model_name}...")
                        response_text = self.ollama_client.invoke(full_prompt)
                        if response_text and len(response_text.strip()) > 50:
                            # Проверяем, не содержит ли ответ сообщение об ошибке (расширенный список)
                            error_indicators = [
                                "К сожалению, не удалось сгенерировать",
                                "К сожалению, неудалось сгенерировать",
                                "не удалосьсгенерировать",
                                "не удалось сгенерировать",
                                "неудалосьсгенерировать",
                                "неудалось сгенерировать",
                                "Оллама сервер недоступен",
                                "Ollama сервер недоступен",
                                "Сервер Ollama доступен, но была ошибка",
                                "Сервер Ollama доступен, но возникла ошибка",
                                "ollama serve",
                                "ollama pull",
                                "ollamapull",
                                "ollamalist",
                                "какая модель",
                                "модельdeepseek",
                                "модель deepseek",
                                "deepseek:7b загружена",
                                "deepseek:7bзагружена",
                                "deepseek :7b",
                                "Что можно сделать:",
                                "Убедитесь, что модель"
                            ]
                            response_lower = response_text.lower()
                            if not any(indicator.lower() in response_lower for indicator in error_indicators) and not response_text.strip().startswith("ollama") and not response_text.strip().startswith("Ollama"):
                                # Имитируем streaming
                                chunk_size = 10
                                for i in range(0, len(response_text), chunk_size):
                                    chunk = response_text[i:i+chunk_size]
                                    yield chunk
                                    time.sleep(0.02)
                                return
                    except Exception as e_fallback:
                        print(f"Ошибка при повторной попытке с fallback моделью: {e_fallback}")
            
            if self.api_key:
                try:
                    print("Пробуем OpenAI как fallback после ошибки Ollama (внешний обработчик)...")
                    yield from self.get_openai_explanation_stream(subject, section, topic, regenerate)
                    return
                except Exception as e3:
                    error_msg = self._get_error_message(subject, section, topic)
                    # Очищаем от курсора
                    error_msg = self._clean_text_from_cursor(error_msg)
                    # Возвращаем весь текст сразу, а не по частям
                    yield error_msg
            else:
                error_msg = self._get_error_message(subject, section, topic)
                # Очищаем от курсора
                error_msg = self._clean_text_from_cursor(error_msg)
                # Возвращаем весь текст сразу, а не по частям
                yield error_msg
    
    def get_openai_explanation(self, subject, section, topic, regenerate=False):
        """Получить объяснение от OpenAI"""
        try:
            from openai import OpenAI
            
            if not self.api_key:
                print("OpenAI API ключ не установлен")
                return self._get_error_message(subject, section, topic)
            
            print(f"Генерирую объяснение через OpenAI (модель: gpt-4o-mini)...")
            client = OpenAI(api_key=self.api_key)
            
            # Создаем специальный промпт для учителя
            system_prompt = f"""Ты опытный учитель {subject.lower()}а с 20-летним стажем. 
Тебе необходимо просто и понятно объяснить тему "{topic}" из раздела "{section}".

Требования к объяснению:
1. Используй простой и доступный язык
2. Приводи конкретные примеры
3. Объясняй шаг за шагом
4. Используй аналогии из повседневной жизни
5. Структурируй материал логично
6. Выделяй ключевые моменты
7. Пиши на русском языке
8. Объем: 300-500 слов

Начни объяснение с краткого введения в тему, затем подробно разбери основные понятия и заверши практическими советами или примерами применения."""
            
            user_prompt = f"Объясни тему '{topic}' из раздела '{section}' предмета '{subject}'"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                print(f"Успешно получено объяснение от OpenAI (длина: {len(content)} символов)")
                return content
            else:
                print("Пустой ответ от OpenAI")
                return self._get_error_message(subject, section, topic)
            
        except ImportError:
            print("Библиотека openai не установлена")
            return self._get_error_message(subject, section, topic)
        except Exception as e:
            print(f"Ошибка OpenAI API: {e}")
            import traceback
            traceback.print_exc()
            return self._get_error_message(subject, section, topic)
    
    def get_openai_explanation_stream(self, subject, section, topic, regenerate=False):
        """Получить объяснение от OpenAI с streaming"""
        try:
            from openai import OpenAI
            
            if not self.api_key:
                print("OpenAI API ключ не установлен")
                error_msg = self._get_error_message(subject, section, topic)
                # Очищаем от курсора
                error_msg = self._clean_text_from_cursor(error_msg)
                # Возвращаем весь текст сразу, а не по частям
                yield error_msg
                return
            
            print(f"Генерирую объяснение через OpenAI (streaming, модель: gpt-4o-mini)...")
            client = OpenAI(api_key=self.api_key)
            
            system_prompt = f"""Ты опытный учитель {subject.lower()}а с 20-летним стажем. 
Тебе необходимо просто и понятно объяснить тему "{topic}" из раздела "{section}".

Требования к объяснению:
1. Используй простой и доступный язык
2. Приводи конкретные примеры
3. Объясняй шаг за шагом
4. Используй аналогии из повседневной жизни
5. Структурируй материал логично
6. Выделяй ключевые моменты
7. Пиши на русском языке
8. Объем: 300-500 слов

Начни объяснение с краткого введения в тему, затем подробно разбери основные понятия и заверши практическими советами или примерами применения."""
            
            user_prompt = f"Объясни тему '{topic}' из раздела '{section}' предмета '{subject}'"
            
            # Используем streaming
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    # Отдаем текст по мере поступления с небольшой задержкой
                    if content.strip():
                        yield content
                        time.sleep(0.01)  # Небольшая задержка для плавности
            
        except ImportError:
            print("Библиотека openai не установлена")
            error_msg = self._get_error_message(subject, section, topic)
            chunk_size = 10
            for i in range(0, len(error_msg), chunk_size):
                chunk = error_msg[i:i+chunk_size]
                yield chunk
                time.sleep(0.02)
        except Exception as e:
            print(f"Ошибка OpenAI API (streaming): {e}")
            import traceback
            traceback.print_exc()
            error_msg = self._get_error_message(subject, section, topic)
            chunk_size = 10
            for i in range(0, len(error_msg), chunk_size):
                chunk = error_msg[i:i+chunk_size]
                yield chunk
                time.sleep(0.02)
    
    def _get_local_explanation(self, subject, section, topic, generate_if_missing=True):
        """Получить локальное объяснение темы, если оно доступно.
        Если файла нет и generate_if_missing=True, генерирует через deepseek (Ollama) и сохраняет."""
        try:
            from pathlib import Path
            
            # Транслитерация кириллицы в латиницу
            translit_map = {
                'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
                'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm',
                'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
                'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
            }
            
            # Создаем имя файла из темы (транслитерация + замена пробелов)
            topic_lower = topic.lower()
            topic_filename = ''
            for char in topic_lower:
                if char in translit_map:
                    topic_filename += translit_map[char]
                elif char.isalnum() or char == '_':
                    topic_filename += char
                elif char == ' ':
                    topic_filename += '_'
            
            # Путь к файлу с объяснением
            explanations_dir = Path(__file__).parent / "explanations"
            explanations_dir.mkdir(exist_ok=True)  # Создаем папку, если её нет
            explanation_file = explanations_dir / f"{topic_filename}.txt"
            
            # Если файл существует, читаем его
            if explanation_file.exists():
                with open(explanation_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Заменяем плейсхолдеры, если они есть
                    content = content.replace('{topic}', topic)
                    content = content.replace('{subject}', subject)
                    content = content.replace('{section}', section)
                    # Очищаем от возможного курсора
                    content = self._clean_text_from_cursor(content)
                    return content
            
            # Если файла нет и нужно генерировать, пробуем через deepseek (Ollama)
            if generate_if_missing:
                try:
                    # Проверяем доступность Ollama и переподключаемся при необходимости
                    if self.ollama_client is None or not self._check_ollama_connection():
                        # Пробуем проверить доступность сервера
                        if self._check_ollama_server_available():
                            print("Ollama сервер доступен, пробуем переподключиться...")
                            self._init_ollama_client()
                        else:
                            print("Ollama сервер недоступен. Убедитесь, что сервер запущен: ollama serve")
                            # Пробуем еще раз переподключиться (на случай если сервер только что запустился)
                            if self._check_ollama_server_available():
                                print("Ollama сервер теперь доступен, пробуем переподключиться...")
                                self._init_ollama_client()
                    
                    if self.ollama_client is not None and self._check_ollama_connection():
                        print(f"Генерирую локальное объяснение через deepseek (Ollama) для темы: {topic}")
                        
                        # Создаем промпт для генерации объяснения
                        system_prompt = f"""Ты опытный учитель {subject.lower()}а с 20-летним стажем. 
Тебе необходимо просто и понятно объяснить тему "{topic}" из раздела "{section}".

Требования к объяснению:
1. Используй простой и доступный язык
2. Приводи конкретные примеры
3. Объясняй шаг за шагом
4. Используй аналогии из повседневной жизни
5. Структурируй материал логично
6. Выделяй ключевые моменты
7. Пиши на русском языке
8. Объем: 300-500 слов

Начни объяснение с краткого введения в тему, затем подробно разбери основные понятия и заверши практическими советами или примерами применения."""
                        
                        user_prompt = f"Объясни тему '{topic}' из раздела '{section}' предмета '{subject}'"
                        full_prompt = f"{system_prompt}\n\n{user_prompt}"
                        
                        # Генерируем объяснение через Ollama
                        response_text = self.ollama_client.invoke(full_prompt)
                        
                        if response_text and len(response_text.strip()) > 50:
                            # Очищаем ответ
                            content = response_text.strip()
                            content = self._clean_text_from_cursor(content)
                            
                            # Сохраняем в файл для будущего использования
                            try:
                                with open(explanation_file, 'w', encoding='utf-8') as f:
                                    f.write(content)
                                print(f"Локальное объяснение сохранено в файл: {explanation_file}")
                            except Exception as save_error:
                                print(f"Ошибка сохранения локального объяснения: {save_error}")
                            
                            return content
                        else:
                            print(f"Ответ от Ollama слишком короткий или пустой ({len(response_text.strip()) if response_text else 0} символов)")
                    else:
                        print("Ollama недоступен для генерации локального объяснения")
                except Exception as gen_error:
                    print(f"Ошибка генерации локального объяснения через Ollama: {gen_error}")
                    import traceback
                    traceback.print_exc()
            
            return None
        except Exception as e:
            print(f"Ошибка загрузки локального объяснения: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_error_message(self, subject, section, topic):
        """Сообщение об ошибке, когда LLM недоступны"""
        # Сначала пробуем получить локальное объяснение
        local_explanation = self._get_local_explanation(subject, section, topic)
        if local_explanation:
            # Очищаем от возможного курсора
            local_explanation = self._clean_text_from_cursor(local_explanation)
            return local_explanation
        
        # Если локального объяснения нет, возвращаем сообщение об ошибке
        # Проверяем, доступен ли Ollama сервер
        ollama_available = self._check_ollama_server_available()
        
        if not ollama_available:
            error_msg = f"""
## {topic}

**К сожалению, не удалось сгенерировать объяснение этой темы.**

**Ollama сервер недоступен!**

**Чтобы использовать локальную модель deepseek-r1:7b, выполните следующие шаги:**

1. **Убедитесь, что Ollama установлен:**
   - Скачайте с https://ollama.ai
   - Установите на ваш компьютер

2. **Запустите Ollama сервер:**
   - Откройте командную строку (терминал)
   - Выполните команду: `ollama serve`
   - Сервер должен запуститься на порту 11434

3. **Загрузите модель deepseek-r1:7b:**
   - В другом окне терминала выполните: `ollama pull deepseek-r1:7b`
   - Дождитесь завершения загрузки

4. **После этого обновите страницу** и попробуйте снова

**Альтернативные варианты:**
- Настройте API ключ OpenAI для использования облачной модели
- Обратитесь к учителю за дополнительной информацией
- Используйте учебники и онлайн-ресурсы

**Предмет:** {subject}  
**Раздел:** {section}  
**Тема:** {topic}

Эта тема важна для понимания дальнейшего материала. Рекомендуем изучить её более подробно.
"""
        else:
            # Проверяем наличие API ключа OpenAI
            has_openai_key = bool(self.api_key)
            
            # Используем только deepseek-r1:7b
            model_name = "deepseek-r1:7b"
            
            if has_openai_key:
                error_msg = f"""## {topic}

**К сожалению, не удалось сгенерировать объяснение этой темы.**

**Ollama сервер доступен, но возникла ошибка при генерации. OpenAI также не смог сгенерировать объяснение.**

**Что можно сделать:**

1. Убедитесь, что модель {model_name} загружена: `ollama pull {model_name}`
2. Проверьте, что модель доступна: `ollama list`
3. Проверьте подключение к интернету (для OpenAI)
4. Обратитесь к учителю за дополнительной информацией
5. Используйте учебники и онлайн-ресурсы

**Предмет:** {subject}  
**Раздел:** {section}  
**Тема:** {topic}

Эта тема важна для понимания дальнейшего материала. Рекомендуем изучить её более подробно.
"""
            else:
                error_msg = f"""## {topic}

**К сожалению, не удалось сгенерировать объяснение этой темы.**

**Ollama сервер доступен, но возникла ошибка при генерации.**

**Что можно сделать:**

1. Убедитесь, что модель {model_name} загружена: `ollama pull {model_name}`
2. Проверьте, что модель доступна: `ollama list`
3. Настройте API ключ OpenAI для использования облачной модели (рекомендуется)
4. Обратитесь к учителю за дополнительной информацией
5. Используйте учебники и онлайн-ресурсы

**Предмет:** {subject}  
**Раздел:** {section}  
**Тема:** {topic}

Эта тема важна для понимания дальнейшего материала. Рекомендуем изучить её более подробно.
"""
        # Очищаем от возможного курсора (многократная очистка)
        error_msg = self._clean_text_from_cursor(error_msg)
        # Дополнительная проверка
        cursor_variants = ["▌", "▋", "▊", "▉", "█", "▐", "▎", "▍"]
        for cursor in cursor_variants:
            error_msg = error_msg.replace(cursor, "")
        # Убеждаемся, что пробелы в командах сохранены
        error_msg = error_msg.replace("ollamapull", "ollama pull")
        error_msg = error_msg.replace("ollamalist", "ollama list")
        error_msg = error_msg.replace("deepseek :7b", "deepseek:7b")
        error_msg = error_msg.replace("deepseek-r1 :7b", "deepseek-r1:7b")
        error_msg = error_msg.replace("deepseek:7bзагружена", "deepseek:7b загружена")
        error_msg = error_msg.replace("deepseek-r1:7b загружена", "deepseek-r1:7b загружена")
        error_msg = error_msg.replace("deepseek:7b загружена:", "deepseek:7b загружена:")
        error_msg = error_msg.replace("модельdeepseek", "модель deepseek")
        error_msg = error_msg.replace("неудалось сгенерировать", "не удалось сгенерировать")
        # Исправляем проблемы с форматированием команд (слипшиеся команды)
        error_msg = error_msg.replace(":ollama pull", ": `ollama pull")
        error_msg = error_msg.replace(":ollama list", ": `ollama list")
        error_msg = error_msg.replace("загружена:ollama", "загружена: `ollama")
        error_msg = error_msg.replace("доступна:ollama", "доступна: `ollama")
        # Исправляем проблемы с форматированием списка
        error_msg = error_msg.replace("1.", "\n1.")
        error_msg = error_msg.replace("2.", "\n2.")
        error_msg = error_msg.replace("3.", "\n3.")
        error_msg = error_msg.replace("4.", "\n4.")
        error_msg = error_msg.replace("5.", "\n5.")
        error_msg = error_msg.replace("6.", "\n6.")
        # Исправляем слипшиеся пункты списка
        error_msg = error_msg.replace("2.Проверьте", "2. Проверьте")
        error_msg = error_msg.replace("3.Настройте", "3. Настройте")
        error_msg = error_msg.replace("4. Обратиться", "4. Обратитесь")
        error_msg = error_msg.replace("Убедитесь, что модель", "\nУбедитесь, что модель")
        error_msg = error_msg.replace("Проверьте, доступна ли модель", "\nПроверьте, доступна ли модель")
        error_msg = error_msg.replace("Установить API-ключ", "\nУстановить API-ключ")
        return error_msg.strip()

# Создание экземпляра менеджера теории
theory_manager = TheoryManager()
