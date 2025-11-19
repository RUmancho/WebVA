import streamlit as st
import json
import random
from bot.settings import OPENAI_API_KEY
from bot.theory import TheoryManager
from langchain_ollama import OllamaLLM

class TestingManager:
    """Класс для управления системой тестирования"""
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.theory_manager = TheoryManager()
        self.SUBJECTS_STRUCTURE = self.theory_manager.SUBJECTS_STRUCTURE
        self.init_testing_session()
        self._init_ollama_client()
    
    def _init_ollama_client(self):
        """Инициализация Ollama клиента для генерации тестов"""
        try:
            # Пробуем использовать deepseek:7b
            self.ollama_client = OllamaLLM(model="deepseek:7b", temperature=0.7)
            self.model_name = "deepseek:7b"
            print("Генерация тестов использует модель: deepseek:7b")
        except Exception as e:
            try:
                # Fallback на deepseek-r1:7b
                print(f"Модель deepseek:7b недоступна для тестов, пробуем deepseek-r1:7b: {e}")
                self.ollama_client = OllamaLLM(model="deepseek-r1:7b", temperature=0.7)
                self.model_name = "deepseek-r1:7b"
                print("Генерация тестов использует модель: deepseek-r1:7b")
            except Exception as e2:
                try:
                    # Fallback на deepseek-coder:6.7b
                    print(f"Модель deepseek-r1:7b недоступна, пробуем deepseek-coder:6.7b: {e2}")
                    self.ollama_client = OllamaLLM(model="deepseek-coder:6.7b", temperature=0.7)
                    self.model_name = "deepseek-coder:6.7b"
                    print("Генерация тестов использует модель: deepseek-coder:6.7b")
                except Exception as e3:
                    self.ollama_client = None
                    self.model_name = "deepseek:7b"
                    print(f"Ошибка инициализации Ollama клиента для тестов: {e3}")
                    print("Убедитесь, что Ollama установлен и модель deepseek:7b загружена")
        
        # Уровни сложности
        self.DIFFICULTY_LEVELS = {
            "Лёгкий": {
                "icon": "🟢",
                "description": "Базовые вопросы, подходят для начального изучения темы",
                "questions_style": "простые вопросы с очевидными ответами"
            },
            "Средний": {
                "icon": "🟡", 
                "description": "Вопросы среднего уровня, требуют понимания материала",
                "questions_style": "вопросы среднего уровня сложности, требующие анализа"
            },
            "Хардкор": {
                "icon": "🔴",
                "description": "Сложные вопросы для глубокого понимания темы",
                "questions_style": "сложные аналитические вопросы, требующие глубокого понимания"
            }
        }
        
        # Тематические стикеры и анимации для каждого предмета
        self.SUBJECT_STICKERS = {
            "Алгебра": {
                "stickers": ["🔢", "➕", "➖", "✖️", "➗", "🧮", "📊", "📈", "📉", "🔣"],
                "animation_emojis": "🔢➕➖✖️➗🧮📊📈📉🔣💯✨",
                "funny_comments": [
                    "Икс найден! Он больше не скрывается! 🕵️",
                    "Формулы покорены! Математика сдается! 🏳️",
                    "Уравнение решено! Алгебра не устоит! 💪",
                    "Переменные под контролем! 🎯"
                ],
                "topic_stickers": {
                    "Линейные уравнения": "📏➡️",
                    "Квадратные уравнения": "2️⃣🔢",
                    "Функции": "📈📉"
                }
            },
            "Геометрия": {
                "stickers": ["📐", "📏", "🔺", "⬜", "🔴", "📊", "📋", "✏️", "🎯", "🏗️"],
                "animation_emojis": "📐📏🔺⬜🔴📊📋✏️🎯🏗️📏✨",
                "funny_comments": [
                    "Углы покорены! Треугольники сдались! 🔺",
                    "Теорема Пифагора одобряет! 👑",
                    "Окружности в восторге от ваших знаний! ⭕",
                    "Площади и объемы вычислены! 📊"
                ],
                "topic_stickers": {
                    "Треугольники": "🔺📐",
                    "Окружность": "⭕🔴",
                    "Площади фигур": "📊📏"
                }
            },
            "Физика": {
                "stickers": ["⚡", "🔬", "🌊", "🎭", "⚛️", "🔋", "💡", "🌟", "🚀", "⭐"],
                "animation_emojis": "⚡🔬🌊🎭⚛️🔋💡🌟🚀⭐🔥✨",
                "funny_comments": [
                    "Ньютон бы гордился! Яблоко падает правильно! 🍎",
                    "Электроны танцуют от радости! ⚡💃",
                    "Законы физики соблюдены! Порядок во вселенной! 🌌",
                    "Энергия сохранена! Физика покорена! 🔋"
                ],
                "topic_stickers": {
                    "Механика": "⚙️🔧",
                    "Электричество": "⚡🔌",
                    "Оптика": "💡🔍"
                }
            },
            "Химия": {
                "stickers": ["🧪", "⚗️", "🔬", "💊", "🌡️", "🧬", "💎", "🔥", "💧", "💨"],
                "animation_emojis": "🧪⚗️🔬💊🌡️🧬💎🔥💧💨⚛️✨",
                "funny_comments": [
                    "Реакция прошла успешно! Без взрывов! 💥😅",
                    "Менделеев аплодирует! Таблица довольна! 👏",
                    "Молекулы в восторге! Атомы ликуют! ⚛️",
                    "Химия покорена без противогаза! 🥽"
                ],
                "topic_stickers": {
                    "Атомное строение": "⚛️🔬",
                    "Кислоты": "🧪💧",
                    "Органическая химия": "🧬💊"
                }
            },
            "Биология": {
                "stickers": ["🧬", "🔬", "🌱", "🐛", "🦋", "🌸", "🍃", "🧫", "🔍", "🌿"],
                "animation_emojis": "🧬🔬🌱🐛🦋🌸🍃🧫🔍🌿🌺✨",
                "funny_comments": [
                    "Дарвин бы восхитился! Эволюция знаний! 🐒➡️🧑‍🎓",
                    "Клетки делятся... знаниями! 🧫",
                    "ДНК расшифрована! Код жизни взломан! 🧬",
                    "Биосфера покорена! Природа сдается! 🌍"
                ],
                "topic_stickers": {
                    "Клеточная теория": "🧫🔬",
                    "Эволюция": "🐒➡️🧑",
                    "Фотосинтез": "🌱☀️"
                }
            },
            "География": {
                "stickers": ["🌍", "🗺️", "🏔️", "🌊", "🏝️", "🌋", "🧭", "📍", "🛰️", "🌐"],
                "animation_emojis": "🌍🗺️🏔️🌊🏝️🌋🧭📍🛰️🌐🗾✨",
                "funny_comments": [
                    "Колумб бы позавидовал! Все континенты найдены! 🗺️",
                    "GPS не нужен! Вы знаете все координаты! 🧭",
                    "Экватор покорен! Полюса сдались! 🌍",
                    "Атлас плачет от восторга! 📚"
                ],
                "topic_stickers": {
                    "Климат": "🌡️🌦️",
                    "Океаны": "🌊🐋",
                    "Горы": "🏔️⛰️"
                }
            },
            "История": {
                "stickers": ["🏛️", "👑", "⚔️", "📜", "🏺", "🗿", "🏰", "📚", "⏳", "🎭"],
                "animation_emojis": "🏛️👑⚔️📜🏺🗿🏰📚⏳🎭🏺✨",
                "funny_comments": [
                    "Цезарь бы гордился! История покорена! 👑",
                    "Машина времени не нужна! Вы знаете все эпохи! ⏳",
                    "Летописи переписаны! Историки аплодируют! 📜",
                    "Прошлое раскрыто! Тайны веков разгаданы! 🔍"
                ],
                "topic_stickers": {
                    "Древний Рим": "🏛️👑",
                    "Средние века": "🏰⚔️",
                    "Новое время": "📚⏳"
                }
            },
            "Обществознание": {
                "stickers": ["👥", "🏛️", "⚖️", "🗳️", "💰", "📈", "🌐", "🤝", "📊", "💼"],
                "animation_emojis": "👥🏛️⚖️🗳️💰📈🌐🤝📊💼🌍✨",
                "funny_comments": [
                    "Общество покорено! Социум под контролем! 👥",
                    "Политологи в восторге! Демократия ликует! 🗳️",
                    "Экономика сдается! Рынок побежден! 📈",
                    "Социальные науки аплодируют! 👏"
                ],
                "topic_stickers": {
                    "Политика": "🏛️🗳️",
                    "Экономика": "💰📈",
                    "Социология": "👥🤝"
                }
            },
            "Русский язык": {
                "stickers": ["📝", "📚", "✒️", "📖", "🎭", "📜", "💬", "🔤", "📄", "✍️"],
                "animation_emojis": "📝📚✒️📖🎭📜💬🔤📄✍️📓✨",
                "funny_comments": [
                    "Пушкин аплодирует! Язык покорен! 👏",
                    "Орфография сдается! Пунктуация побеждена! ✍️",
                    "Словари переписаны! Грамматика покорена! 📚",
                    "Великий и могучий подчинился! 🇷🇺"
                ],
                "topic_stickers": {
                    "Орфография": "✍️📝",
                    "Синтаксис": "📖📄",
                    "Морфология": "🔤📚"
                }
            },
            "Английский язык": {
                "stickers": ["🇬🇧", "🇺🇸", "💬", "📖", "🎭", "✈️", "🌐", "📱", "🎤", "📺"],
                "animation_emojis": "🇬🇧🇺🇸💬📖🎭✈️🌐📱🎤📺🗣️✨",
                "funny_comments": [
                    "Шекспир бы восхитился! English is conquered! 🎭",
                    "Биг Бен звонит в честь ваших знаний! 🔔",
                    "Британская королева одобряет! 👑",
                    "Welcome to the club! You speak English! 🎉"
                ],
                "topic_stickers": {
                    "Грамматика": "📖✍️",
                    "Лексика": "💬🗣️",
                    "Разговорная речь": "🎤💭"
                }
            },
            "Информатика": {
                "stickers": ["💻", "🖥️", "⌨️", "🖱️", "💾", "🔌", "📱", "🌐", "🤖", "💿"],
                "animation_emojis": "💻🖥️⌨️🖱️💾🔌📱🌐🤖💿⚡✨",
                "funny_comments": [
                    "Код работает! Баги побеждены! 🐛❌",
                    "Алгоритм оптимизирован! Процессор ликует! 🔥",
                    "Hello World! Программирование покорено! 👋",
                    "Сеть настроена! Интернет подключен! 🌐"
                ],
                "topic_stickers": {
                    "Программирование": "💻⌨️",
                    "Алгоритмы": "🤖🔢",
                    "Сети": "🌐🔌"
                }
            }
        }
    
    def init_testing_session(self):
        """Инициализация сессии для тестирования"""
        if 'testing_state' not in st.session_state:
            st.session_state.testing_state = {
                'current_page': 'subjects',  # subjects, sections, topics, difficulty, test, results
                'selected_subject': None,
                'selected_section': None, 
                'selected_topic': None,
                'selected_difficulty': None,
                'current_test': None,
                'user_answers': {},
                'test_results': None,
                'current_question': 0
            }
    
    def play_sound_effect(self, sound_type, subject=None):
        """Воспроизведение звуковых эффектов"""
        try:
            # Звуковые эффекты через HTML audio с веб-звуками
            sound_urls = {
                'start_test': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LLfSgEs3k=',
                'correct_answer': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LLfSgEs3k=',
                'wrong_answer': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LLfSgEs3k=',
                'excellent_result': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LLfSgEs3k=',
                'good_result': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LLfSgEs3k=',
                'try_again': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LLfSgEs3k='
            }
            
            # Предметные звуки (забавные описания)
            subject_sounds = {
                'Алгебра': ['🔢 *звук калькулятора*', '➕ *щелчок счетов*'],
                'Геометрия': ['📐 *скрип циркуля*', '📏 *стук линейки*'],
                'Физика': ['⚡ *треск электричества*', '🔬 *булькание в пробирке*'],
                'Химия': ['🧪 *шипение реакции*', '💥 *небольшой взрыв*'],
                'Биология': ['🧬 *шуршание листьев*', '🐛 *жужжание насекомых*'],
                'География': ['🌍 *шум океана*', '🏔️ *эхо в горах*'],
                'История': ['⚔️ *звон мечей*', '📜 *шуршание пергамента*'],
                'Обществознание': ['🏛️ *гул парламента*', '💰 *звон монет*'],
                'Русский язык': ['📝 *скрип пера*', '📚 *шелест страниц*'],
                'Английский язык': ['🇬🇧 *Big Ben*', '☕ *чаепитие*'],
                'Информатика': ['⌨️ *стук клавиш*', '💾 *писк модема*']
            }
            
            # Отображаем звуковой эффект как текст (поскольку реальные звуки требуют аудиофайлы)
            if sound_type in ['start_test', 'excellent_result', 'good_result']:
                st.info("🎵 *воспроизводится торжественная мелодия* 🎶")
            elif sound_type == 'correct_answer':
                st.success("🎉 *звон успеха* ✨")
            elif sound_type == 'wrong_answer':
                st.info("🤔 *мягкий звук 'упс'* 💭")
            elif sound_type == 'try_again':
                st.info("🚀 *звук старта* 💫")
            
            # Добавляем предметный звук
            if subject and subject in subject_sounds:
                subject_sound = random.choice(subject_sounds[subject])
                st.caption(f"🎧 {subject_sound}")
            
        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")
    
    def show_subject_stickers(self, subject, topic=None):
        """Показать тематические стикеры для предмета"""
        try:
            if subject not in self.SUBJECT_STICKERS:
                return
            
            subject_data = self.SUBJECT_STICKERS[subject]
            
            # Большие стикеры предмета
            stickers = subject_data['stickers']
            selected_stickers = random.sample(stickers, min(5, len(stickers)))
            
            # Отображаем стикеры
            st.markdown(f"### {''.join(selected_stickers)}")
            
            # Специальные стикеры для конкретной темы
            if topic and topic in subject_data.get('topic_stickers', {}):
                topic_stickers = subject_data['topic_stickers'][topic]
                st.markdown(f"#### {topic_stickers} {topic} {topic_stickers}")
            
        except Exception as e:
            print(f"Ошибка отображения стикеров: {e}")
    
    def show_animated_celebration(self, subject, grade_percentage):
        """Показать анимированное празднование с тематическими элементами"""
        try:
            if subject not in self.SUBJECT_STICKERS:
                return
            
            subject_data = self.SUBJECT_STICKERS[subject]
            
            # Анимированные эмодзи
            animation_emojis = subject_data['animation_emojis']
            st.markdown(f"## {animation_emojis}")
            
            # Тематические комментарии
            funny_comments = subject_data['funny_comments']
            selected_comment = random.choice(funny_comments)
            
            # Специальные анимации в зависимости от результата
            if grade_percentage >= 90:
                st.balloons()  # Шарики для отличных результатов
                st.success(f"🎊 {selected_comment}")
                # Дополнительные стикеры для отличного результата
                if subject == "Алгебра":
                    st.markdown("### 🏆➕➖✖️➗🧮💯🎯")
                elif subject == "Физика":
                    st.markdown("### ⚡🚀🌟💫🔥⚛️🏆")
                elif subject == "Химия":
                    st.markdown("### 🧪⚗️💎🔬🏆✨💫")
                elif subject == "Биология":
                    st.markdown("### 🧬🌱🦋🌸🏆🌺✨")
                elif subject == "География":
                    st.markdown("### 🌍🗺️🏔️🌊🏆⭐✨")
                elif subject == "История":
                    st.markdown("### 👑⚔️🏛️📜🏆✨💫")
                elif subject == "Информатика":
                    st.markdown("### 💻🤖⚡🏆💫✨🚀")
                else:
                    st.markdown("### 🏆🎉🌟💫✨🎊🎯")
                    
            elif grade_percentage >= 70:
                st.info(f"🌟 {selected_comment}")
                # Стикеры для хорошего результата
                if subject == "Алгебра":
                    st.markdown("### 🔢➕📊📈👍")
                elif subject == "Физика":
                    st.markdown("### ⚡🔬💡🌟👍")
                else:
                    st.markdown("### 🌟👍💪📚✨")
                    
            elif grade_percentage >= 50:
                st.info(f"💪 {selected_comment}")
                # Мотивирующие стикеры
                st.markdown("### 🌱💪📚🎯🚀")
                
            else:
                st.snow()  # Снежинки как символ нового начала
                st.info(f"🌟 {selected_comment}")
                # Поддерживающие стикеры
                st.markdown("### 💪🌟📚🚀💡🌱")
            
        except Exception as e:
            print(f"Ошибка анимации: {e}")
    
    def get_funny_subject_comment(self, subject, context='general'):
        """Получить смешной комментарий для предмета"""
        try:
            if subject not in self.SUBJECT_STICKERS:
                return "Отлично! Продолжайте в том же духе! 🎉"
            
            funny_comments = self.SUBJECT_STICKERS[subject]['funny_comments']
            return random.choice(funny_comments)
            
        except Exception as e:
            print(f"Ошибка получения комментария: {e}")
            return "Замечательно! 🌟"
    
    def show_testing_interface(self):
        """Главный интерфейс тестирования"""
        try:
            st.header("📝 Система тестирования")
            
            # Навигационные кнопки
            self.show_navigation()
            
            # Отображение соответствующей страницы
            state = st.session_state.testing_state
            
            if state['current_page'] == 'subjects':
                self.show_subjects()
            elif state['current_page'] == 'sections':
                self.show_sections()
            elif state['current_page'] == 'topics':
                self.show_topics()
            elif state['current_page'] == 'difficulty':
                self.show_difficulty_selection()
            elif state['current_page'] == 'test':
                self.show_test()
            elif state['current_page'] == 'results':
                self.show_results()
            
        except Exception as e:
            st.error(f"Ошибка в интерфейсе тестирования: {e}")
            print(f"Ошибка в интерфейсе тестирования: {e}")
    
    def show_navigation(self):
        """Показать навигационные кнопки"""
        try:
            state = st.session_state.testing_state
            
            # Хлебные крошки
            breadcrumbs = []
            if state['current_page'] != 'subjects':
                breadcrumbs.append("Предметы")
            if state['selected_subject'] and state['current_page'] not in ['subjects', 'sections']:
                breadcrumbs.append(state['selected_subject'])
            if state['selected_section'] and state['current_page'] not in ['subjects', 'sections', 'topics']:
                breadcrumbs.append(state['selected_section'])
            if state['selected_topic'] and state['current_page'] not in ['subjects', 'sections', 'topics', 'difficulty']:
                breadcrumbs.append(state['selected_topic'])
            if state['selected_difficulty'] and state['current_page'] in ['test', 'results']:
                breadcrumbs.append(f"Уровень: {state['selected_difficulty']}")
            
            if breadcrumbs:
                st.markdown(" → ".join(breadcrumbs))
                st.markdown("---")
            
            # Кнопка "Назад"
            if state['current_page'] not in ['subjects', 'test']:
                if st.button("⬅️ Назад", key="testing_back_button"):
                    self.navigate_back()
                    st.rerun()
            
        except Exception as e:
            st.error(f"Ошибка навигации: {e}")
            print(f"Ошибка навигации: {e}")
    
    def navigate_back(self):
        """Навигация назад"""
        try:
            state = st.session_state.testing_state
            
            if state['current_page'] == 'results':
                state['current_page'] = 'difficulty'
                state['test_results'] = None
                state['user_answers'] = {}
                state['current_test'] = None
            elif state['current_page'] == 'difficulty':
                state['current_page'] = 'topics'
                state['selected_difficulty'] = None
            elif state['current_page'] == 'topics':
                state['current_page'] = 'sections'
                state['selected_topic'] = None
            elif state['current_page'] == 'sections':
                state['current_page'] = 'subjects'
                state['selected_section'] = None
            
        except Exception as e:
            print(f"Ошибка навигации назад: {e}")
    
    def show_subjects(self):
        """Показать список предметов"""
        try:
            st.subheader("Выберите предмет для тестирования:")
            st.success("🎓 Добро пожаловать в систему тестирования! Выберите предмет и проверьте свои знания!")
            
            # Звуковой эффект при входе
            self.play_sound_effect('start_test')
            
            subjects = list(self.SUBJECTS_STRUCTURE.keys())
            
            # Отображаем предметы по 3 в ряду
            for i in range(0, len(subjects), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(subjects):
                        subject = subjects[i + j]
                        with cols[j]:
                            icon = self.SUBJECTS_STRUCTURE[subject]["icon"]
                            if st.button(f"{icon} {subject}", key=f"test_subject_{subject}", use_container_width=True):
                                st.session_state.testing_state['selected_subject'] = subject
                                st.session_state.testing_state['current_page'] = 'sections'
                                
                                # Показываем тематические стикеры
                                self.show_subject_stickers(subject)
                                
                                # Смешной комментарий для предмета
                                funny_comment = self.get_funny_subject_comment(subject)
                                st.success(f"🎯 {funny_comment}")
                                
                                # Звуковой эффект предмета
                                self.play_sound_effect('correct_answer', subject)
                                
                                st.rerun()
            
        except Exception as e:
            st.error(f"Ошибка отображения предметов: {e}")
            print(f"Ошибка отображения предметов: {e}")
    
    def show_sections(self):
        """Показать разделы выбранного предмета"""
        try:
            subject = st.session_state.testing_state['selected_subject']
            if not subject:
                st.session_state.testing_state['current_page'] = 'subjects'
                st.rerun()
                return
            
            icon = self.SUBJECTS_STRUCTURE[subject]["icon"]
            st.subheader(f"{icon} {subject}")
            st.info(f"🎪 Отлично! Теперь выберите раздел {subject.lower()}а для тестирования!")
            
            sections = self.SUBJECTS_STRUCTURE[subject]["sections"]
            
            for section_name in sections.keys():
                if st.button(f"📖 {section_name}", key=f"test_section_{section_name}", use_container_width=True):
                    st.session_state.testing_state['selected_section'] = section_name
                    st.session_state.testing_state['current_page'] = 'topics'
                    st.success(f"✨ Прекрасно! Вы выбрали раздел '{section_name}'!")
                    st.rerun()
            
        except Exception as e:
            st.error(f"Ошибка отображения разделов: {e}")
            print(f"Ошибка отображения разделов: {e}")
    
    def show_topics(self):
        """Показать темы выбранного раздела"""
        try:
            subject = st.session_state.testing_state['selected_subject']
            section = st.session_state.testing_state['selected_section']
            
            if not subject or not section:
                st.session_state.testing_state['current_page'] = 'subjects'
                st.rerun()
                return
            
            icon = self.SUBJECTS_STRUCTURE[subject]["icon"]
            st.subheader(f"{icon} {subject} → {section}")
            st.info(f"🚀 Потрясающе! Теперь выберите конкретную тему из раздела '{section}'!")
            
            topics = self.SUBJECTS_STRUCTURE[subject]["sections"][section]["topics"]
            
            for topic in topics:
                if st.button(f"🎯 {topic}", key=f"test_topic_{topic}", use_container_width=True):
                    st.session_state.testing_state['selected_topic'] = topic
                    st.session_state.testing_state['current_page'] = 'difficulty'
                    
                    # Показываем тематические стикеры для конкретной темы
                    self.show_subject_stickers(subject, topic)
                    
                    st.success(f"🌟 Великолепно! Вы выбрали тему '{topic}'! Переходим к выбору сложности!")
                    
                    # Звуковой эффект
                    self.play_sound_effect('correct_answer', subject)
                    
                    st.rerun()
            
        except Exception as e:
            st.error(f"Ошибка отображения тем: {e}")
            print(f"Ошибка отображения тем: {e}")
    
    def show_difficulty_selection(self):
        """Показать выбор уровня сложности"""
        try:
            subject = st.session_state.testing_state['selected_subject']
            section = st.session_state.testing_state['selected_section']
            topic = st.session_state.testing_state['selected_topic']
            
            if not all([subject, section, topic]):
                st.session_state.testing_state['current_page'] = 'subjects'
                st.rerun()
                return
            
            icon = self.SUBJECTS_STRUCTURE[subject]["icon"]
            st.subheader(f"{icon} {subject} → {section} → {topic}")
            
            # Позитивное вступление
            st.success("🎯 Отлично! Теперь выберите уровень сложности, который подходит именно вам!")
            st.info("💡 Совет: Начните с лёгкого уровня, если изучаете тему впервые!")
            
            # Показываем уровни сложности
            for difficulty, info in self.DIFFICULTY_LEVELS.items():
                with st.container():
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button(f"{info['icon']} {difficulty}", 
                                   key=f"difficulty_{difficulty}", 
                                   use_container_width=True):
                            st.session_state.testing_state['selected_difficulty'] = difficulty
                            st.session_state.testing_state['current_page'] = 'test'
                            
                            # Позитивные сообщения при выборе сложности
                            if difficulty == "Лёгкий":
                                st.success("🌟 Отличный выбор для начала! Удачи!")
                            elif difficulty == "Средний":
                                st.success("💪 Прекрасно! Вызов принят!")
                            else:
                                st.success("🔥 Вау! Настоящий смельчак! Покорите этот уровень!")
                                
                            st.rerun()
                    with col2:
                        st.write(f"**{difficulty}:** {info['description']}")
                    
                st.markdown("---")
            
        except Exception as e:
            st.error(f"Ошибка выбора сложности: {e}")
            print(f"Ошибка выбора сложности: {e}")
    
    def show_test(self):
        """Показать тест"""
        try:
            state = st.session_state.testing_state
            
            if not all([state['selected_subject'], state['selected_section'], 
                       state['selected_topic'], state['selected_difficulty']]):
                state['current_page'] = 'subjects'
                st.rerun()
                return
            
            # Генерируем тест если его еще нет
            if not state['current_test']:
                # Позитивные сообщения при генерации
                motivational_messages = [
                    "🎯 Готовлю для вас увлекательные вопросы!",
                    "🧠 Создаю интересные задания!",
                    "✨ Почти готово! Сейчас будет весело!",
                    "🎪 Подготавливаю захватывающий тест!",
                    "🚀 Запускаю генератор знаний!"
                ]
                selected_message = random.choice(motivational_messages)
                
                with st.spinner(selected_message):
                    test = self.generate_test(
                        state['selected_subject'],
                        state['selected_section'], 
                        state['selected_topic'],
                        state['selected_difficulty']
                    )
                    state['current_test'] = test
                    state['user_answers'] = {}
                    state['current_question'] = 0
                
                # Позитивное сообщение после генерации
                st.success("🎉 Отлично! Тест готов к прохождению!")
                st.info("💡 Совет: внимательно читайте вопросы и не торопитесь с ответами!")
            
            if not state['current_test']:
                st.error("Не удалось сгенерировать тест. Попробуйте позже.")
                return
            
            self.display_test()
            
        except Exception as e:
            st.error(f"Ошибка отображения теста: {e}")
            print(f"Ошибка отображения теста: {e}")
    
    def display_test(self):
        """Отображение теста"""
        try:
            state = st.session_state.testing_state
            test = state['current_test']
            
            icon = self.SUBJECTS_STRUCTURE[state['selected_subject']]["icon"]
            difficulty_icon = self.DIFFICULTY_LEVELS[state['selected_difficulty']]["icon"]
            
            st.subheader(f"{icon} Тест: {state['selected_topic']}")
            st.write(f"{difficulty_icon} Уровень сложности: {state['selected_difficulty']}")
            
            # Прогресс с позитивными сообщениями
            progress = len(state['user_answers']) / len(test['questions'])
            answered_count = len(state['user_answers'])
            total_count = len(test['questions'])
            
            # Мотивирующие сообщения в зависимости от прогресса
            if progress == 0:
                progress_message = "🌟 Начинаем! Вы справитесь!"
            elif progress < 0.3:
                progress_message = "💪 Отличное начало! Продолжайте!"
            elif progress < 0.6:
                progress_message = "🔥 Вы на правильном пути!"
            elif progress < 0.9:
                progress_message = "⚡ Почти финиш! Так держать!"
            else:
                progress_message = "🏆 Последний рывок! Вы молодец!"
            
            st.progress(progress, text=f"{progress_message} ({answered_count}/{total_count})")
            
            st.markdown("---")
            
            # Отображаем все вопросы
            all_answered = True
            
            for i, question in enumerate(test['questions']):
                st.write(f"**Вопрос {i+1}:** {question['question']}")
                
                # Варианты ответов
                answer_key = f"question_{i}"
                selected_answer = st.radio(
                    "Выберите ответ:",
                    options=question['options'],
                    key=answer_key,
                    index=None
                )
                
                # Сохраняем ответ
                if selected_answer:
                    state['user_answers'][i] = selected_answer
                else:
                    all_answered = False
                
                st.markdown("---")
            
            # Кнопка завершения теста
            if all_answered:
                # Показываем стикеры предмета при завершении
                self.show_subject_stickers(state['selected_subject'], state['selected_topic'])
                
                st.success("🎊 Поздравляем! Все вопросы отвечены!")
                if st.button("✅ Завершить тест и узнать результат", type="primary", key="finish_test_button"):
                    self.calculate_results()
                    state['current_page'] = 'results'
                    
                    # Добавляем праздничную анимацию при завершении
                    st.balloons()
                    
                    # Звуковой эффект завершения
                    self.play_sound_effect('excellent_result', state['selected_subject'])
                    
                    st.rerun()
            else:
                remaining = len(test['questions']) - len(state['user_answers'])
                st.info(f"📝 Осталось ответить на {remaining} вопрос(ов). Вы уже на финишной прямой!")
            
            st.markdown("---")
            
            # Кнопка генерации нового теста
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Сгенерировать новый тест", key="regenerate_test_button"):
                    state['current_test'] = None
                    state['user_answers'] = {}
                    
                    # Звуковой эффект и стикеры для нового теста
                    self.play_sound_effect('start_test', state['selected_subject'])
                    funny_comment = self.get_funny_subject_comment(state['selected_subject'])
                    st.success(f"🚀 {funny_comment} Готовим новые вопросы!")
                    
                    st.rerun()
            
            with col2:
                if st.button("🎯 Другая тема", key="different_topic_button"):
                    state['current_test'] = None
                    state['user_answers'] = {}
                    state['current_page'] = 'topics'
                    
                    # Звук перехода
                    self.play_sound_effect('try_again', state['selected_subject'])
                    st.info("🌟 Переходим к выбору новой темы!")
                    
                    st.rerun()
            
        except Exception as e:
            st.error(f"Ошибка отображения теста: {e}")
            print(f"Ошибка отображения теста: {e}")
    
    def generate_test(self, subject, section, topic, difficulty):
        """Генерация теста"""
        try:
            # Приоритет: локальная LLM (Ollama), затем OpenAI, затем локальные тесты
            if self.ollama_client is not None:
                return self.generate_ollama_test(subject, section, topic, difficulty)
            elif self.api_key:
                return self.generate_openai_test(subject, section, topic, difficulty)
            else:
                return self.generate_local_test(subject, section, topic, difficulty)
        except Exception as e:
            print(f"Ошибка генерации теста: {e}")
            return self.generate_local_test(subject, section, topic, difficulty)
    
    def generate_ollama_test(self, subject, section, topic, difficulty):
        """Генерация теста через локальную LLM (Ollama)"""
        try:
            if self.ollama_client is None:
                return self.generate_local_test(subject, section, topic, difficulty)
            
            difficulty_info = self.DIFFICULTY_LEVELS[difficulty]
            
            system_prompt = f"""Ты опытный преподаватель {subject.lower()}а. 
Создай тест из 5 вопросов по теме "{topic}" из раздела "{section}".

Требования:
1. Уровень сложности: {difficulty} ({difficulty_info['questions_style']})
2. Каждый вопрос должен иметь 4 варианта ответа (A, B, C, D)
3. Только один правильный ответ
4. Вопросы должны проверять понимание темы
5. Ответь СТРОГО в формате JSON без дополнительного текста:

{{
    "questions": [
        {{
            "question": "Текст вопроса",
            "options": ["Вариант A", "Вариант B", "Вариант C", "Вариант D"],
            "correct_answer": "Вариант A"
        }}
    ]
}}

Вопросы должны быть на русском языке."""
            
            user_prompt = f"Создай тест уровня '{difficulty}' по теме '{topic}' из раздела '{section}' предмета '{subject}'"
            
            # Формируем полный промпт
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Получаем ответ от модели
            response_text = self.ollama_client.invoke(full_prompt)
            
            if not response_text:
                return self.generate_local_test(subject, section, topic, difficulty)
            
            # Очищаем ответ от возможных префиксов и markdown
            response_text = response_text.strip()
            
            # Удаляем markdown код блоки если есть
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Парсим JSON ответ
            try:
                test_data = json.loads(response_text)
                # Проверяем структуру
                if "questions" not in test_data or not isinstance(test_data["questions"], list):
                    raise ValueError("Неверная структура JSON")
                return test_data
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Ошибка парсинга JSON от Ollama: {e}")
                print(f"Ответ модели: {response_text[:200]}...")
                return self.generate_local_test(subject, section, topic, difficulty)
            
        except Exception as e:
            print(f"Ошибка Ollama API для тестов: {e}")
            return self.generate_local_test(subject, section, topic, difficulty)
    
    def generate_openai_test(self, subject, section, topic, difficulty):
        """Генерация теста через OpenAI"""
        try:
            import openai
            
            openai.api_key = self.api_key
            
            difficulty_info = self.DIFFICULTY_LEVELS[difficulty]
            
            system_prompt = f"""Ты опытный преподаватель {subject.lower()}а. 
            Создай тест из 5 вопросов по теме "{topic}" из раздела "{section}".
            
            Требования:
            1. Уровень сложности: {difficulty} ({difficulty_info['questions_style']})
            2. Каждый вопрос должен иметь 4 варианта ответа (A, B, C, D)
            3. Только один правильный ответ
            4. Вопросы должны проверять понимание темы
            5. Ответь СТРОГО в формате JSON без дополнительного текста:
            
            {{
                "questions": [
                    {{
                        "question": "Текст вопроса",
                        "options": ["Вариант A", "Вариант B", "Вариант C", "Вариант D"],
                        "correct_answer": "Вариант A"
                    }}
                ]
            }}
            
            Вопросы должны быть на русском языке."""
            
            user_prompt = f"Создай тест уровня '{difficulty}' по теме '{topic}' из раздела '{section}' предмета '{subject}'"
            
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            # Парсим JSON ответ
            test_json = response.choices[0].message.content
            test_data = json.loads(test_json)
            
            return test_data
            
        except ImportError:
            return self.generate_local_test(subject, section, topic, difficulty)
        except json.JSONDecodeError:
            print("Ошибка парсинга JSON от OpenAI")
            return self.generate_local_test(subject, section, topic, difficulty)
        except Exception as e:
            print(f"Ошибка OpenAI API: {e}")
            return self.generate_local_test(subject, section, topic, difficulty)
    
    def generate_local_test(self, subject, section, topic, difficulty):
        """Локальная генерация теста"""
        
        # Базовые тесты для демонстрации
        sample_tests = {
            "Линейные уравнения": {
                "questions": [
                    {
                        "question": "Решите уравнение: 2x + 5 = 11",
                        "options": ["x = 3", "x = 8", "x = -3", "x = 16"],
                        "correct_answer": "x = 3"
                    },
                    {
                        "question": "Какой коэффициент при x в уравнении 3x - 7 = 0?",
                        "options": ["3", "-7", "0", "10"],
                        "correct_answer": "3"
                    },
                    {
                        "question": "Сколько решений имеет уравнение 0x + 5 = 5?",
                        "options": ["Одно", "Два", "Бесконечно много", "Ни одного"],
                        "correct_answer": "Бесконечно много"
                    },
                    {
                        "question": "Решите уравнение: x/2 = 6",
                        "options": ["x = 3", "x = 12", "x = 8", "x = 4"],
                        "correct_answer": "x = 12"
                    },
                    {
                        "question": "В уравнении ax + b = 0, чему равен x при a ≠ 0?",
                        "options": ["x = -b/a", "x = b/a", "x = a/b", "x = -a/b"],
                        "correct_answer": "x = -b/a"
                    }
                ]
            },
            "Треугольники": {
                "questions": [
                    {
                        "question": "Чему равна сумма углов треугольника?",
                        "options": ["90°", "180°", "270°", "360°"],
                        "correct_answer": "180°"
                    },
                    {
                        "question": "Как называется треугольник с тремя равными сторонами?",
                        "options": ["Равнобедренный", "Прямоугольный", "Равносторонний", "Тупоугольный"],
                        "correct_answer": "Равносторонний"
                    },
                    {
                        "question": "По какой формуле вычисляется площадь треугольника?",
                        "options": ["S = a×h", "S = (1/2)×a×h", "S = a²", "S = 2×a×h"],
                        "correct_answer": "S = (1/2)×a×h"
                    },
                    {
                        "question": "Какое неравенство выполняется для сторон треугольника?",
                        "options": ["a + b = c", "a + b < c", "a + b > c", "a = b = c"],
                        "correct_answer": "a + b > c"
                    },
                    {
                        "question": "Как называется треугольник с углом 90°?",
                        "options": ["Острый", "Тупой", "Прямоугольный", "Равнобедренный"],
                        "correct_answer": "Прямоугольный"
                    }
                ]
            }
        }
        
        # Возвращаем готовый тест если есть, иначе создаем базовый
        if topic in sample_tests:
            return sample_tests[topic]
        else:
            return {
                "questions": [
                    {
                        "question": f"Базовый вопрос по теме '{topic}' из раздела '{section}' предмета '{subject}'",
                        "options": ["Вариант А", "Вариант Б", "Вариант В", "Вариант Г"],
                        "correct_answer": "Вариант А"
                    },
                    {
                        "question": f"Второй вопрос по теме '{topic}' (уровень: {difficulty})",
                        "options": ["Ответ 1", "Ответ 2", "Ответ 3", "Ответ 4"],
                        "correct_answer": "Ответ 1"
                    },
                    {
                        "question": f"Третий вопрос по теме '{topic}'",
                        "options": ["Опция A", "Опция B", "Опция C", "Опция D"],
                        "correct_answer": "Опция A"
                    },
                    {
                        "question": f"Четвертый вопрос по теме '{topic}'",
                        "options": ["Выбор 1", "Выбор 2", "Выбор 3", "Выбор 4"],
                        "correct_answer": "Выбор 1"
                    },
                    {
                        "question": f"Пятый вопрос по теме '{topic}'",
                        "options": ["Решение А", "Решение Б", "Решение В", "Решение Г"],
                        "correct_answer": "Решение А"
                    }
                ]
            }
    
    def calculate_results(self):
        """Подсчет результатов теста"""
        try:
            state = st.session_state.testing_state
            test = state['current_test']
            answers = state['user_answers']
            
            correct_count = 0
            total_questions = len(test['questions'])
            
            detailed_results = []
            
            for i, question in enumerate(test['questions']):
                user_answer = answers.get(i, "")
                correct_answer = question['correct_answer']
                is_correct = user_answer == correct_answer
                
                if is_correct:
                    correct_count += 1
                
                detailed_results.append({
                    'question': question['question'],
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_correct': is_correct
                })
            
            percentage = (correct_count / total_questions) * 100
            
            # Определяем оценку с позитивными сообщениями
            if percentage >= 90:
                grade = "Отлично"
                grade_icon = "🏆"
                congratulations = random.choice([
                    "Невероятно! Вы настоящий знаток!",
                    "Фантастика! Блестящий результат!",
                    "Браво! Вы просто великолепны!",
                    "Потрясающе! Вы мастер этой темы!",
                    "Восхитительно! Вы на высоте!"
                ])
                celebration_emojis = "🎉🎊✨🌟💫🎯🏆👑"
            elif percentage >= 70:
                grade = "Хорошо"
                grade_icon = "👍"
                congratulations = random.choice([
                    "Отлично справились! Хороший результат!",
                    "Молодец! Вы на правильном пути!",
                    "Здорово! Продолжайте в том же духе!",
                    "Хорошая работа! Есть к чему стремиться!",
                    "Замечательно! Вы показали хорошие знания!"
                ])
                celebration_emojis = "👏🎈🌟💪🎯📚"
            elif percentage >= 50:
                grade = "Удовлетворительно"
                grade_icon = "👌"
                congratulations = random.choice([
                    "Неплохо! Есть база для роста!",
                    "Хорошее начало! Продолжайте изучать!",
                    "Достойно! Немного практики и будет лучше!",
                    "Справились! Есть над чем поработать!",
                    "Молодец, что не сдались! Вперед к новым высотам!"
                ])
                celebration_emojis = "🌱💪📖🎓✊"
            else:
                grade = "Нужно подучить"
                grade_icon = "📚"
                congratulations = random.choice([
                    "Не расстраивайтесь! Это отличная возможность учиться!",
                    "Все проходили через это! Главное не сдаваться!",
                    "Ошибки - это ступеньки к знаниям!",
                    "Не беда! Повторите материал и попробуйте снова!",
                    "Каждый эксперт когда-то был новичком! Вперед!"
                ])
                celebration_emojis = "💪🌟📚🚀💡"
            
            state['test_results'] = {
                'correct_count': correct_count,
                'total_questions': total_questions,
                'percentage': percentage,
                'grade': grade,
                'grade_icon': grade_icon,
                'congratulations': congratulations,
                'celebration_emojis': celebration_emojis,
                'detailed_results': detailed_results
            }
            
        except Exception as e:
            st.error(f"Ошибка подсчета результатов: {e}")
            print(f"Ошибка подсчета результатов: {e}")
    
    def show_results(self):
        """Показать результаты теста"""
        try:
            state = st.session_state.testing_state
            results = state['test_results']
            
            if not results:
                state['current_page'] = 'subjects'
                st.rerun()
                return
            
            # Заголовок результатов с анимацией
            icon = self.SUBJECTS_STRUCTURE[state['selected_subject']]["icon"]
            st.subheader(f"{icon} Результаты тестирования")
            
            # Показываем анимированное празднование с тематическими элементами
            self.show_animated_celebration(state['selected_subject'], results['percentage'])
            
            # Воспроизводим звуковые эффекты
            if results['percentage'] >= 90:
                self.play_sound_effect('excellent_result', state['selected_subject'])
            elif results['percentage'] >= 70:
                self.play_sound_effect('good_result', state['selected_subject'])
            elif results['percentage'] >= 50:
                self.play_sound_effect('try_again', state['selected_subject'])
            else:
                self.play_sound_effect('try_again', state['selected_subject'])
            
            # Основные результаты в красивом оформлении
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Правильных ответов",
                    f"{results['correct_count']}/{results['total_questions']}",
                    delta=f"{results['correct_count']} из {results['total_questions']}"
                )
            
            with col2:
                st.metric(
                    "Процент правильных",
                    f"{results['percentage']:.1f}%",
                    delta="Ваш результат"
                )
            
            with col3:
                st.metric(
                    "Итоговая оценка",
                    f"{results['grade_icon']} {results['grade']}",
                    delta="Поздравляем!"
                )
            
            st.markdown("---")
            
            # Детальные результаты с позитивными комментариями
            st.subheader("📋 Разбор вопросов:")
            
            positive_comments = [
                "Великолепно! 🌟", "Превосходно! ✨", "Блестяще! 💫", 
                "Отлично! 🎯", "Замечательно! 🎉", "Молодец! 👏"
            ]
            
            encouraging_comments = [
                "Ничего страшного! Теперь вы знаете правильный ответ! 💪",
                "Хорошая попытка! Запомните этот момент! 📝",
                "Не беда! Это отличный урок! 🌱",
                "Теперь вы точно запомните! 🧠",
                "Ошибка - путь к знаниям! 🚀",
                "Так учатся все эксперты! 💡"
            ]
            
            for i, result in enumerate(results['detailed_results']):
                emoji = "✅" if result['is_correct'] else "📝"
                with st.expander(f"Вопрос {i+1} {emoji}"):
                    st.write(f"**Вопрос:** {result['question']}")
                    st.write(f"**Ваш ответ:** {result['user_answer']}")
                    st.write(f"**Правильный ответ:** {result['correct_answer']}")
                    
                    if result['is_correct']:
                        comment = random.choice(positive_comments)
                        st.success(f"{comment}")
                        # Небольшой звуковой эффект для правильного ответа (только текст)
                        if i == 0:  # Только для первого вопроса, чтобы не спамить
                            st.caption("🎵 *звон успеха* ✨")
                    else:
                        comment = random.choice(encouraging_comments)
                        st.info(f"{comment}")
                        # Мягкий звук для неправильного ответа
                        if i == 0:  # Только для первого вопроса
                            st.caption("🤔 *мягкий звук обучения* 💭")
            
            st.markdown("---")
            
            # Мотивирующие рекомендации
            if results['percentage'] >= 90:
                st.success("🏆 Вы показали выдающиеся знания! Попробуйте более сложные темы или помогите другим!")
            elif results['percentage'] >= 70:
                st.info("📈 Отличная работа! Можете попробовать повысить уровень сложности!")
            elif results['percentage'] >= 50:
                st.info("📚 Хорошая база! Рекомендуем повторить теорию и попробовать еще раз!")
            else:
                st.info("🎯 Не расстраивайтесь! Изучите теорию по этой теме и возвращайтесь за новыми знаниями!")
            
            # Кнопки действий с веселыми эмодзи
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Попробовать снова", use_container_width=True, key="try_again_results_button"):
                    state['current_test'] = None
                    state['user_answers'] = {}
                    state['test_results'] = None
                    state['current_page'] = 'test'
                    st.rerun()
            
            with col2:
                if st.button("🎯 Другая тема", use_container_width=True, key="different_topic_results_button"):
                    state['current_test'] = None
                    state['user_answers'] = {}
                    state['test_results'] = None
                    state['selected_topic'] = None
                    state['selected_difficulty'] = None
                    state['current_page'] = 'topics'
                    st.rerun()
            
            with col3:
                if st.button("📚 Изучить теорию", use_container_width=True, key="study_theory_button"):
                    # Переключаемся на вкладку теории с той же темой
                    if 'theory_state' not in st.session_state:
                        st.session_state.theory_state = {}
                    
                    st.session_state.theory_state.update({
                        'current_page': 'explanation',
                        'selected_subject': state['selected_subject'],
                        'selected_section': state['selected_section'],
                        'selected_topic': state['selected_topic']
                    })
                    
                    st.info("🚀 Переключаемся на изучение теории! Перейдите на вкладку 'Теория'")
                    st.balloons()
                    
                    # Звук перехода к теории
                    self.play_sound_effect('start_test', state['selected_subject'])
            
            st.markdown("---")
            
            # Дополнительная кнопка для веселья
            if st.button("🎪 Хочу еще анимацию!", use_container_width=True, key="more_animation_button"):
                # Дополнительное празднование
                self.show_animated_celebration(state['selected_subject'], results['percentage'])
                self.play_sound_effect('excellent_result', state['selected_subject'])
                
                # Смешной комментарий
                funny_comment = self.get_funny_subject_comment(state['selected_subject'])
                st.success(f"🎉 {funny_comment}")
                
                # Случайная анимация
                animations = [st.balloons, st.snow]
                random.choice(animations)()
            
        except Exception as e:
            st.error(f"Ошибка отображения результатов: {e}")
            print(f"Ошибка отображения результатов: {e}")

# Создание экземпляра менеджера тестирования
testing_manager = TestingManager()
