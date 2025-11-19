from asyncio import threads
import streamlit as st
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
        try:
            # Пробуем использовать deepseek:7b
            self.ollama_client = OllamaLLM(model="deepseek:7b", temperature=0.7)
            self.model_name = "deepseek:7b"
            print("Генерация теории использует модель: deepseek:7b")
        except Exception as e:
            try:
                # Fallback на deepseek-r1:7b
                print(f"Модель deepseek:7b недоступна для теории, пробуем deepseek-r1:7b: {e}")
                self.ollama_client = OllamaLLM(model="deepseek-r1:7b", temperature=0.7)
                self.model_name = "deepseek-r1:7b"
                print("Генерация теории использует модель: deepseek-r1:7b")
            except Exception as e2:
                try:
                    # Fallback на deepseek-coder:6.7b
                    print(f"Модель deepseek-r1:7b недоступна, пробуем deepseek-coder:6.7b: {e2}")
                    self.ollama_client = OllamaLLM(model="deepseek-coder:6.7b", temperature=0.7)
                    self.model_name = "deepseek-coder:6.7b"
                    print("Генерация теории использует модель: deepseek-coder:6.7b")
                except Exception as e3:
                    self.ollama_client = None
                    self.model_name = "deepseek:7b"
                    print(f"Ошибка инициализации Ollama клиента для теории: {e3}")
                    print("Убедитесь, что Ollama установлен и модель deepseek:7b загружена")
    
    def _try_fallback_model(self):
        """Попытка переключиться на резервную модель при ошибке"""
        try:
            if self.model_name == "deepseek:7b":
                print("Пробуем переключиться на deepseek-r1:7b...")
                self.ollama_client = OllamaLLM(model="deepseek-r1:7b", temperature=0.7)
                self.model_name = "deepseek-r1:7b"
                print("Успешно переключились на deepseek-r1:7b")
            elif self.model_name == "deepseek-r1:7b":
                print("Пробуем переключиться на deepseek-coder:6.7b...")
                self.ollama_client = OllamaLLM(model="deepseek-coder:6.7b", temperature=0.7)
                self.model_name = "deepseek-coder:6.7b"
                print("Успешно переключились на deepseek-coder:6.7b")
            else:
                # Если все модели не работают, отключаем клиент
                self.ollama_client = None
                print("Все модели недоступны, отключаем Ollama клиент")
        except Exception as e:
            print(f"Ошибка при переключении на резервную модель: {e}")
            self.ollama_client = None
    
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
            
            # Проверяем, есть ли уже объяснение (и это не шаблон ошибки)
            explanation_text = st.session_state.theory_state.get('explanation_text')
            is_error_template = explanation_text and "К сожалению, не удалось сгенерировать" in explanation_text
            
            if not explanation_text or is_error_template:
                with st.spinner("Генерирую объяснение темы с помощью LLM..."):
                    try:
                        explanation = self.get_topic_explanation(subject, section, topic)
                        st.session_state.theory_state['explanation_text'] = explanation
                        explanation_text = explanation
                    except Exception as e:
                        print(f"Ошибка генерации объяснения: {e}")
                        st.error(f"Ошибка генерации объяснения: {e}")
                        explanation_text = self._get_error_message(subject, section, topic)
                        st.session_state.theory_state['explanation_text'] = explanation_text
            
            # Отображаем объяснение
            if explanation_text:
                st.markdown(explanation_text)
            else:
                st.error("Не удалось загрузить объяснение. Попробуйте позже.")
            
            # Кнопка для нового объяснения
            if st.button("🔄 Получить другое объяснение", key="regenerate_explanation_button"):
                with st.spinner("Генерирую новое объяснение с помощью LLM..."):
                    try:
                        explanation = self.get_topic_explanation(subject, section, topic, regenerate=True)
                        st.session_state.theory_state['explanation_text'] = explanation
                    except Exception as e:
                        print(f"Ошибка регенерации объяснения: {e}")
                        st.error(f"Ошибка генерации объяснения: {e}")
                st.rerun()
            
        except Exception as e:
            st.error(f"Ошибка отображения объяснения: {e}")
            print(f"Ошибка отображения объяснения: {e}")
    
    def get_topic_explanation(self, subject, section, topic, regenerate=False):
        """Получить объяснение темы от LLM (Ollama или OpenAI)"""
        try:
            # Приоритет: локальная LLM (Ollama), затем OpenAI
            if self.ollama_client is not None:
                return self.get_ollama_explanation(subject, section, topic, regenerate)
            elif self.api_key:
                return self.get_openai_explanation(subject, section, topic, regenerate)
            else:
                return self._get_error_message(subject, section, topic)
        except Exception as e:
            print(f"Ошибка получения объяснения: {e}")
            # Пробуем OpenAI как fallback, если Ollama не сработал
            if self.api_key:
                try:
                    return self.get_openai_explanation(subject, section, topic, regenerate)
                except Exception as e2:
                    print(f"Ошибка OpenAI API: {e2}")
                    return self._get_error_message(subject, section, topic)
            return self._get_error_message(subject, section, topic)
    
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
            if self.ollama_client is None:
                print("Ollama клиент не инициализирован, пробуем OpenAI...")
                # Если Ollama недоступен, пробуем OpenAI
                if self.api_key:
                    return self.get_openai_explanation(subject, section, topic, regenerate)
                return self._get_error_message(subject, section, topic)
            
            print(f"Генерирую объяснение через Ollama (модель: {self.model_name})...")
            # Получаем ответ от модели
            response_text = self.ollama_client.invoke(full_prompt)
            
            if not response_text or len(response_text.strip()) == 0:
                print("Пустой ответ от Ollama, пробуем OpenAI...")
                # Если ответ пустой, пробуем OpenAI
                if self.api_key:
                    return self.get_openai_explanation(subject, section, topic, regenerate)
                return self._get_error_message(subject, section, topic)
            
            # Очищаем ответ от возможных префиксов
            response_text = response_text.strip()
            print(f"Успешно получено объяснение от Ollama (длина: {len(response_text)} символов)")
            
            return response_text
            
        except Exception as e:
            error_str = str(e)
            print(f"Ошибка Ollama API для теории: {e}")
            import traceback
            traceback.print_exc()
            
            # Если модель не найдена, пробуем переключиться на другую модель
            if "not found" in error_str.lower() or "404" in error_str or "connection" in error_str.lower():
                print(f"Модель {self.model_name} недоступна, пробуем переключиться на другую модель...")
                self._try_fallback_model()
                # Пробуем еще раз с новой моделью
                if self.ollama_client is not None:
                    try:
                        print(f"Пробуем с моделью {self.model_name}...")
                        response_text = self.ollama_client.invoke(full_prompt)
                        if response_text and len(response_text.strip()) > 0:
                            print(f"Успешно получено объяснение от fallback модели (длина: {len(response_text)} символов)")
                            return response_text.strip()
                    except Exception as e2:
                        print(f"Ошибка при повторной попытке с fallback моделью: {e2}")
            
            # В случае любой ошибки пробуем OpenAI как fallback
            if self.api_key:
                try:
                    print("Пробуем OpenAI как fallback...")
                    return self.get_openai_explanation(subject, section, topic, regenerate)
                except Exception as e3:
                    print(f"Ошибка OpenAI API при fallback: {e3}")
            
            return self._get_error_message(subject, section, topic)
    
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
    
    def _get_error_message(self, subject, section, topic):
        """Сообщение об ошибке, когда LLM недоступны"""
        return f"""
## {topic}

**К сожалению, не удалось сгенерировать объяснение этой темы.**

**Что можно сделать:**
1. Убедитесь, что Ollama установлен и запущен, или настройте API ключ OpenAI
2. Проверьте подключение к интернету (для OpenAI)
3. Обратитесь к учителю за дополнительной информацией
4. Используйте учебники и онлайн-ресурсы

**Предмет:** {subject}  
**Раздел:** {section}  
**Тема:** {topic}

Эта тема важна для понимания дальнейшего материала. Рекомендуем изучить её более подробно.
"""

# Создание экземпляра менеджера теории
theory_manager = TheoryManager()
