from flask import session as flask_session
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional

CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from formulas.physics_wrapper import Force, Energy, PhysicsUtils
    DLL_AVAILABLE = True
except Exception as e:
    print(f"Предупреждение: Не удалось загрузить DLL wrapper: {e}")
    DLL_AVAILABLE = False
    Force = None
    Energy = None
    PhysicsUtils = None

# Физические константы
g = 9.80665  # Ускорение свободного падения, м/с²
G = 6.67430e-11  # Гравитационная постоянная, Н·м²/кг²
k = 8.987551789e9  # Постоянная Кулона, Н·м²/Кл²
c = 299792458.0  # Скорость света, м/с
h = 6.62607015e-34  # Постоянная Планка, Дж·с
R = 8.314462618  # Универсальная газовая постоянная, Дж/(моль·К)
PI = math.pi  # Число π


class FormulaManager:
    """Класс для управления формулами и вычислениями"""
    
    def __init__(self):
        # Словарь для определения, какие поля могут быть делителями
        self.divisor_fields = {
            # Математика
            "h": "Высота не может быть равна нулю",
            "a": "Длина не может быть равна нулю",
            "b": "Ширина не может быть равна нулю",
            # Физика - силы
            "m": "Масса не может быть равна нулю",
            "g": "Ускорение свободного падения не может быть равно нулю",
            "N": "Сила реакции опоры не может быть равна нулю",
            "u": "Коэффициент трения не может быть равен нулю",
            "r": "Расстояние/радиус не может быть равно нулю",
            "P": "Давление не может быть равно нулю",
            "S": "Площадь не может быть равна нулю",
            "V": "Скорость не может быть равна нулю",
            "I": "Сила тока не может быть равна нулю",
            "L": "Длина/Индуктивность не может быть равна нулю",
            "B": "Магнитная индукция не может быть равна нулю",
            "q": "Заряд не может быть равен нулю",
            "q1": "Заряд 1 не может быть равен нулю",
            "q2": "Заряд 2 не может быть равен нулю",
            "k": "Жесткость/константа не может быть равна нулю",
            "c": "Удельная теплоемкость не может быть равна нулю",
            "dt": "Изменение температуры не может быть равно нулю",
            "s": "Путь не может быть равен нулю",
            "F": "Сила не может быть равна нулю",
            "F_friction": "Сила трения не может быть равна нулю",
            "F_initial": "Начальная сила не может быть равна нулю",
            "F_final": "Конечная сила не может быть равна нулю",
            "efficiency": "КПД не может быть равен нулю",
            "total_work": "Полная работа не может быть равна нулю",
            "U": "Напряжение не может быть равно нулю",
            "dV": "Изменение объема не может быть равно нулю",
            "power": "Мощность не может быть равна нулю",
            "time": "Время не может быть равно нулю",
            "work": "Работа не может быть равна нулю",
            "C": "Емкость не может быть равна нулю",
            "bond_energy_per_mole": "Энергия связи на моль не может быть равна нулю",
            "moles": "Количество вещества не может быть равно нулю",
            "rate_constant": "Константа скорости не может быть равна нулю",
            "pre_exponential": "Предэкспоненциальный множитель не может быть равен нулю",
            "T": "Температура не может быть равна нулю",
        }
        
        self.categories = {
            "📐 МАТЕМАТИКА": {
                "subcategories": ["Планиметрия", "Стереометрия", "Тригонометрия", "Алгебра", "Теория вероятности"],
                "icon": "📐"
            },
            "⚡ ФИЗИКА": {
                "subcategories": ["Механика", "Электродинамика", "Термодинамика", "Оптика"],
                "icon": "⚡"
            }
        }
    
    def _validate_divisor(self, field_id: str, value: float) -> None:
        """Проверяет, что значение не равно нулю, если оно используется как делитель"""
        if field_id in self.divisor_fields and abs(value) < 1e-10:
            error_msg = self.divisor_fields.get(field_id, f"{field_id} не может быть равно нулю")
            raise ValueError(error_msg)
    
    def _validate_all_divisors(self, values: Dict[str, float], target: str) -> None:
        """Проверяет все значения, которые могут быть делителями"""
        for field_id, value in values.items():
            if field_id != target:  # Не проверяем целевую переменную
                self._validate_divisor(field_id, value)
    
    def init_formula_state(self):
        """Инициализация состояния формул"""
        session = flask_session
        if 'formula_state' not in session:
            session['formula_state'] = {
                'current_category': None,
                'current_subcategory': None
            }
    
    def show_formula_interface(self):
        """Интерфейс формул - ТРЕБУЕТ АДАПТАЦИИ ДЛЯ FLASK"""
        # TODO: UI теперь в Flask шаблонах (templates/dashboard/formulas.html)
        # Этот метод возвращает данные для шаблона вместо отображения UI
        try:
            # Инициализация состояния
            self.init_formula_state()
            session = flask_session
            
            # Возвращаем данные для Flask шаблона
            return {
                'categories': self.categories,
                'current_category': session.get('formula_state', {}).get('current_category'),
                'current_subcategory': session.get('formula_state', {}).get('current_subcategory')
            }
            
        except Exception as e:
            print(f"Ошибка интерфейса формул: {e}")
            return {'error': str(e)}
    
    def show_subcategories(self):
        """Показать подкатегории и формулы - ТРЕБУЕТ АДАПТАЦИИ ДЛЯ FLASK"""
        # TODO: Этот метод использует Streamlit UI и требует адаптации
        try:
            session = flask_session
            category = session.get('formula_state', {}).get('current_category', '')
            
            if not category or category not in self.categories:
                return {'error': 'Категория не выбрана'}
            
            # Возвращаем данные для Flask шаблона
            subcategories = self.categories[category]['subcategories']
            current_subcategory = session.get('formula_state', {}).get('current_subcategory')
            
            # Получаем формулы для текущей подкатегории
            formulas = []
            if current_subcategory:
                formulas_list = self.get_formulas(category, current_subcategory)
                if formulas_list:
                    # Преобразуем в список если это словарь
                    if isinstance(formulas_list, list):
                        formulas = formulas_list
                    elif isinstance(formulas_list, dict):
                        formulas = list(formulas_list.values())
                    else:
                        formulas = formulas_list if formulas_list else []
            
            return {
                'category': category,
                'subcategories': subcategories,
                'current_subcategory': current_subcategory,
                'formulas': formulas
            }
            
        except Exception as e:
            print(f"Ошибка отображения подкатегорий: {e}")
            return {'error': str(e)}
    
    def get_formulas(self, category: str, subcategory: str) -> List[Dict]:
        """Возвращает список формул для категории и подкатегории"""
        formulas = []
        
        # МАТЕМАТИКА - Планиметрия
        if category == "📐 МАТЕМАТИКА" and subcategory == "Планиметрия":
            formulas = [
                {"name": "Площадь круга", "formula": "S = π × r²", "fields": [("r", "Радиус (r)", "м"), ("S", "Площадь (S)", "м²")]},
                {"name": "Длина окружности", "formula": "C = 2 × π × r", "fields": [("r", "Радиус (r)", "м"), ("C", "Длина окружности (C)", "м")]},
                {"name": "Площадь треугольника", "formula": "S = (a × h) / 2", "fields": [("a", "Основание (a)", "м"), ("h", "Высота (h)", "м"), ("S", "Площадь (S)", "м²")]},
                {"name": "Площадь прямоугольника", "formula": "S = a × b", "fields": [("a", "Длина (a)", "м"), ("b", "Ширина (b)", "м"), ("S", "Площадь (S)", "м²")]},
            ]
        
        # ФИЗИКА - Механика
        elif category == "⚡ ФИЗИКА" and subcategory == "Механика":
            formulas = [
                {"name": "Сила тяжести", "formula": "F = m × g", "fields": [("m", "Масса (m)", "кг"), ("g", "Ускорение свободного падения (g)", "м/с²"), ("F", "Сила тяжести (F)", "Н")]},
                {"name": "Второй закон Ньютона", "formula": "F = m × a", "fields": [("m", "Масса (m)", "кг"), ("a", "Ускорение (a)", "м/с²"), ("F", "Сила (F)", "Н")]},
                {"name": "Закон всемирного тяготения", "formula": "F = G × m1 × m2 / r²", "fields": [("m1", "Масса 1 (m1)", "кг"), ("m2", "Масса 2 (m2)", "кг"), ("r", "Расстояние (r)", "м"), ("F", "Сила (F)", "Н")]},
                {"name": "Сила трения", "formula": "F = μ × N", "fields": [("u", "Коэффициент трения (μ)", ""), ("N", "Сила реакции опоры (N)", "Н"), ("F", "Сила трения (F)", "Н")]},
                {"name": "Сила Архимеда", "formula": "F = ρ × V × g", "fields": [("p", "Плотность (ρ)", "кг/м³"), ("V", "Объем (V)", "м³"), ("g", "Ускорение свободного падения (g)", "м/с²"), ("F", "Сила Архимеда (F)", "Н")]},
                {"name": "Центростремительная сила", "formula": "F = m × V² / r", "fields": [("m", "Масса (m)", "кг"), ("V", "Скорость (V)", "м/с"), ("r", "Радиус (r)", "м"), ("F", "Центростремительная сила (F)", "Н")]},
                {"name": "Сила давления", "formula": "F = P × S", "fields": [("P", "Давление (P)", "Па"), ("S", "Площадь (S)", "м²"), ("F", "Сила давления (F)", "Н")]},
                {"name": "Гидростатическое давление", "formula": "F = ρ × g × h × S", "fields": [("p", "Плотность (ρ)", "кг/м³"), ("h", "Высота столба (h)", "м"), ("S", "Площадь (S)", "м²"), ("g", "Ускорение свободного падения (g)", "м/с²"), ("F", "Сила (F)", "Н")]},
                {"name": "Кинетическая энергия", "formula": "E = m × V² / 2", "fields": [("m", "Масса (m)", "кг"), ("V", "Скорость (V)", "м/с"), ("E", "Кинетическая энергия (E)", "Дж")]},
                {"name": "Потенциальная энергия", "formula": "E = m × g × h", "fields": [("m", "Масса (m)", "кг"), ("h", "Высота (h)", "м"), ("g", "Ускорение свободного падения (g)", "м/с²"), ("E", "Потенциальная энергия (E)", "Дж")]},
                {"name": "Потенциальная энергия упругости", "formula": "E = k × x² / 2", "fields": [("k", "Жесткость (k)", "Н/м"), ("x", "Деформация (x)", "м"), ("E", "Потенциальная энергия (E)", "Дж")]},
                {"name": "Кинетическая энергия вращения", "formula": "E = I × ω² / 2", "fields": [("I", "Момент инерции (I)", "кг·м²"), ("w", "Угловая скорость (ω)", "рад/с"), ("E", "Кинетическая энергия (E)", "Дж")]},
                {"name": "Тепловая энергия", "formula": "Q = m × c × ΔT", "fields": [("m", "Масса (m)", "кг"), ("c", "Удельная теплоемкость (c)", "Дж/(кг·К)"), ("dt", "Изменение температуры (ΔT)", "К"), ("Q", "Тепловая энергия (Q)", "Дж")]},
                {"name": "Энергия сгорания", "formula": "Q = m × q", "fields": [("m", "Масса (m)", "кг"), ("q", "Удельная теплота сгорания (q)", "Дж/кг"), ("Q", "Энергия сгорания (Q)", "Дж")]},
                {"name": "Работа постоянной силы", "formula": "A = F × s × cos(α)", "fields": [("F", "Сила (F)", "Н"), ("s", "Путь (s)", "м"), ("angle_degrees", "Угол (α)", "град"), ("A", "Работа (A)", "Дж")]},
                {"name": "Работа переменной силы", "formula": "A = (F₁ + F₂) × s / 2", "fields": [("F_initial", "Начальная сила (F₁)", "Н"), ("F_final", "Конечная сила (F₂)", "Н"), ("s", "Путь (s)", "м"), ("A", "Работа (A)", "Дж")]},
                {"name": "Работа газа (изобарный процесс)", "formula": "A = P × ΔV", "fields": [("P", "Давление (P)", "Па"), ("dV", "Изменение объема (ΔV)", "м³"), ("A", "Работа (A)", "Дж")]},
                {"name": "Работа электрического поля", "formula": "A = q × U", "fields": [("q", "Заряд (q)", "Кл"), ("U", "Напряжение (U)", "В"), ("A", "Работа (A)", "Дж")]},
                {"name": "Работа против трения", "formula": "A = F_friction × s", "fields": [("F_friction", "Сила трения (F)", "Н"), ("s", "Путь (s)", "м"), ("A", "Работа (A)", "Дж")]},
                {"name": "Полезная работа", "formula": "A_useful = A_total × η", "fields": [("total_work", "Полная работа (A_total)", "Дж"), ("efficiency", "КПД (η)", ""), ("A_useful", "Полезная работа (A_useful)", "Дж")]},
                {"name": "Работа через изменение кинетической энергии", "formula": "A = m × (V₂² - V₁²) / 2", "fields": [("m", "Масса (m)", "кг"), ("V_initial", "Начальная скорость (V₁)", "м/с"), ("V_final", "Конечная скорость (V₂)", "м/с"), ("A", "Работа (A)", "Дж")]},
                {"name": "Работа через изменение потенциальной энергии", "formula": "A = m × g × (h₂ - h₁)", "fields": [("m", "Масса (m)", "кг"), ("h_initial", "Начальная высота (h₁)", "м"), ("h_final", "Конечная высота (h₂)", "м"), ("g", "Ускорение свободного падения (g)", "м/с²"), ("A", "Работа (A)", "Дж")]},
                {"name": "Работа упругой силы", "formula": "A = k × (x₂² - x₁²) / 2", "fields": [("k", "Жесткость (k)", "Н/м"), ("x_initial", "Начальная деформация (x₁)", "м"), ("x_final", "Конечная деформация (x₂)", "м"), ("A", "Работа (A)", "Дж")]},
                {"name": "Энергия покоя", "formula": "E = m × c²", "fields": [("m", "Масса (m)", "кг"), ("E", "Энергия покоя (E)", "Дж")]},
                {"name": "Энергия фотона", "formula": "E = h × f", "fields": [("frequency", "Частота (f)", "Гц"), ("E", "Энергия фотона (E)", "Дж")]},
                {"name": "Энергия магнитного поля", "formula": "E = L × I² / 2", "fields": [("L", "Индуктивность (L)", "Гн"), ("I", "Сила тока (I)", "А"), ("E", "Энергия магнитного поля (E)", "Дж")]},
                {"name": "Химическая энергия", "formula": "E = n × E_bond", "fields": [("moles", "Количество вещества (n)", "моль"), ("bond_energy_per_mole", "Энергия связи на моль (E_bond)", "Дж/моль"), ("E", "Химическая энергия (E)", "Дж")]},
                {"name": "Энергия активации", "formula": "E_a = -R × T × ln(k / A)", "fields": [("pre_exponential", "Предэкспоненциальный множитель (A)", ""), ("rate_constant", "Константа скорости (k)", ""), ("T", "Температура (T)", "К"), ("E_a", "Энергия активации (E_a)", "Дж")]},
                {"name": "КПД", "formula": "η = A_useful / A_total", "fields": [("useful_work", "Полезная работа (A_useful)", "Дж"), ("total_work", "Полная работа (A_total)", "Дж"), ("efficiency", "КПД (η)", "")]},
                {"name": "Мощность", "formula": "P = A / t", "fields": [("work", "Работа (A)", "Дж"), ("time", "Время (t)", "с"), ("P", "Мощность (P)", "Вт")]},
                {"name": "Работа из мощности", "formula": "A = P × t", "fields": [("power", "Мощность (P)", "Вт"), ("time", "Время (t)", "с"), ("A", "Работа (A)", "Дж")]},
            ]
        
        # ФИЗИКА - Электродинамика
        elif category == "⚡ ФИЗИКА" and subcategory == "Электродинамика":
            formulas = [
                {"name": "Закон Кулона", "formula": "F = k × q1 × q2 / r²", "fields": [("q1", "Заряд 1 (q1)", "Кл"), ("q2", "Заряд 2 (q2)", "Кл"), ("r", "Расстояние (r)", "м"), ("F", "Сила (F)", "Н")]},
                {"name": "Сила Лоренца", "formula": "F = q × V × B × sin(α)", "fields": [("q", "Заряд (q)", "Кл"), ("V", "Скорость (V)", "м/с"), ("B", "Магнитная индукция (B)", "Тл"), ("angle", "Угол (α)", "град"), ("F", "Сила Лоренца (F)", "Н")]},
                {"name": "Сила Ампера", "formula": "F = B × I × L × sin(α)", "fields": [("B", "Магнитная индукция (B)", "Тл"), ("I", "Сила тока (I)", "А"), ("L", "Длина проводника (L)", "м"), ("angle", "Угол (α)", "град"), ("F", "Сила Ампера (F)", "Н")]},
                {"name": "Энергия конденсатора", "formula": "E = C × U² / 2", "fields": [("C", "Емкость (C)", "Ф"), ("U", "Напряжение (U)", "В"), ("E", "Энергия конденсатора (E)", "Дж")]},
            ]
        
        return formulas
    
    def render_formula_calculator(self, formula_data: Dict, category: str, subcategory: str):
        """Отображает калькулятор для конкретной формулы - ТРЕБУЕТ АДАПТАЦИИ ДЛЯ FLASK"""
        # TODO: Этот метод использует Streamlit UI и требует полной адаптации для Flask
        # UI теперь находится в Flask шаблонах (templates/dashboard/formulas.html)
        # Метод можно удалить или адаптировать для возврата данных вместо отображения UI
        try:
            # Возвращаем данные формулы для Flask шаблона
            return {
                'formula_name': formula_data['name'],
                'formula': formula_data['formula'],
                'fields': formula_data['fields'],
                'category': category,
                'subcategory': subcategory
            }
        except Exception as e:
            print(f"Ошибка отображения калькулятора: {e}")
            return {'error': str(e)}
    
    def calculate_formula(self, formula_name: str, category: str, subcategory: str, 
                         values: Dict[str, float], target: str) -> Optional[float]:
        """Вычисляет значение по формуле, используя DLL функции"""
        try:
            if not DLL_AVAILABLE:
                print("⚠️ DLL не доступна, используются стандартные расчеты")
            
            # МАТЕМАТИКА - Планиметрия
            if category == "📐 МАТЕМАТИКА" and subcategory == "Планиметрия":
                if formula_name == "Площадь круга":
                    if target == "r":
                        return math.sqrt(values['S'] / PI)
                    else:  # S
                        return PI * values['r'] ** 2
                
                elif formula_name == "Длина окружности":
                    if target == "r":
                        return values['C'] / (2 * PI)
                    else:  # C
                        return 2 * PI * values['r']
                
                elif formula_name == "Площадь треугольника":
                    if target == "a":
                        if abs(values['h']) < 1e-10:
                            raise ValueError("Высота не может быть равна нулю")
                        return (2 * values['S']) / values['h']
                    elif target == "h":
                        if abs(values['a']) < 1e-10:
                            raise ValueError("Основание не может быть равно нулю")
                        return (2 * values['S']) / values['a']
                    else:  # S
                        return (values['a'] * values['h']) / 2
                
                elif formula_name == "Площадь прямоугольника":
                    if target == "a":
                        if abs(values['b']) < 1e-10:
                            raise ValueError("Ширина не может быть равна нулю")
                        return values['S'] / values['b']
                    elif target == "b":
                        if abs(values['a']) < 1e-10:
                            raise ValueError("Длина не может быть равна нулю")
                        return values['S'] / values['a']
                    else:  # S
                        return values['a'] * values['b']
            
            # ФИЗИКА - Механика
            elif category == "⚡ ФИЗИКА" and subcategory == "Механика":
                if DLL_AVAILABLE and Force:
                    if formula_name == "Сила тяжести":
                        if target == "m":
                            # F = m * g => m = F / g
                            g_val = values.get('g', g)
                            return values['F'] / g_val
                        elif target == "g":
                            # F = m * g => g = F / m
                            return values['F'] / values['m']
                        else:  # F
                            g_val = values.get('g', g)
                            return Force.gravity(values['m'], g_val)
                    
                    elif formula_name == "Второй закон Ньютона":
                        if target == "m":
                            # F = m * a => m = F / a
                            return Force.newton_mass(values['F'], values['a'])
                        elif target == "a":
                            # F = m * a => a = F / m
                            return Force.newton_acceleration(values['F'], values['m'])
                        else:  # F
                            return Force.newton_second_law(values['m'], values['a'])
                    
                    elif formula_name == "Закон всемирного тяготения":
                        if target == "m1":
                            # F = G * m1 * m2 / r² => m1 = F * r² / (G * m2)
                            G_val = values.get('G', G)
                            return (values['F'] * values['r'] ** 2) / (G_val * values['m2'])
                        elif target == "m2":
                            # F = G * m1 * m2 / r² => m2 = F * r² / (G * m1)
                            G_val = values.get('G', G)
                            return (values['F'] * values['r'] ** 2) / (G_val * values['m1'])
                        elif target == "r":
                            # F = G * m1 * m2 / r² => r = sqrt(G * m1 * m2 / F)
                            G_val = values.get('G', G)
                            return math.sqrt((G_val * values['m1'] * values['m2']) / values['F'])
                        else:  # F
                            G_val = values.get('G', G)
                            return Force.universal_gravitation(values['m1'], values['m2'], values['r'], G_val)
                    
                    elif formula_name == "Сила трения":
                        if target == "u":
                            # F = μ * N => μ = F / N
                            return values['F'] / values['N']
                        elif target == "N":
                            # F = μ * N => N = F / μ
                            return values['F'] / values['u']
                        else:  # F
                            return Force.friction(values['u'], values['N'])
                    
                    elif formula_name == "Сила Архимеда":
                        if target == "p":
                            # F = ρ * V * g => ρ = F / (V * g)
                            g_val = values.get('g', g)
                            return values['F'] / (values['V'] * g_val)
                        elif target == "V":
                            # F = ρ * V * g => V = F / (ρ * g)
                            g_val = values.get('g', g)
                            return values['F'] / (values['p'] * g_val)
                        elif target == "g":
                            # F = ρ * V * g => g = F / (ρ * V)
                            return values['F'] / (values['p'] * values['V'])
                        else:  # F
                            g_val = values.get('g', g)
                            return Force.archimedes(values['p'], values['V'], g_val)
                    
                    elif formula_name == "Центростремительная сила":
                        if target == "m":
                            # F = m * V² / r => m = F * r / V²
                            return Force.centripetal_mass(values['F'], values['V'], values['r'])
                        elif target == "V":
                            # F = m * V² / r => V = sqrt(F * r / m)
                            return Force.centripetal_velocity(values['F'], values['m'], values['r'])
                        elif target == "r":
                            # F = m * V² / r => r = m * V² / F
                            return Force.centripetal_radius(values['F'], values['m'], values['V'])
                        else:  # F
                            return Force.centripetal(values['m'], values['V'], values['r'])
                    
                    elif formula_name == "Сила давления":
                        if target == "P":
                            # F = P * S => P = F / S
                            return values['F'] / values['S']
                        elif target == "S":
                            # F = P * S => S = F / P
                            return values['F'] / values['P']
                        else:  # F
                            return Force.pressure(values['P'], values['S'])
                    
                    elif formula_name == "Гидростатическое давление":
                        if target == "p":
                            # F = ρ * g * h * S => ρ = F / (g * h * S)
                            g_val = values.get('g', g)
                            return values['F'] / (g_val * values['h'] * values['S'])
                        elif target == "h":
                            # F = ρ * g * h * S => h = F / (ρ * g * S)
                            g_val = values.get('g', g)
                            return values['F'] / (values['p'] * g_val * values['S'])
                        elif target == "S":
                            # F = ρ * g * h * S => S = F / (ρ * g * h)
                            g_val = values.get('g', g)
                            return values['F'] / (values['p'] * g_val * values['h'])
                        elif target == "g":
                            # F = ρ * g * h * S => g = F / (ρ * h * S)
                            return values['F'] / (values['p'] * values['h'] * values['S'])
                        else:  # F
                            g_val = values.get('g', g)
                            return Force.hydrostatic(values['p'], values['h'], values['S'], g_val)
                    
                    elif formula_name == "Кинетическая энергия":
                        if target == "m":
                            # E = m * V² / 2 => m = 2 * E / V²
                            return Energy.kinetic_mass(values['E'], values['V'])
                        elif target == "V":
                            # E = m * V² / 2 => V = sqrt(2 * E / m)
                            return Energy.kinetic_velocity(values['E'], values['m'])
                        else:  # E
                            return Energy.kinetic(values['m'], values['V'])
                    
                    elif formula_name == "Потенциальная энергия":
                        if target == "m":
                            # E = m * g * h => m = E / (g * h)
                            g_val = values.get('g', g)
                            return Energy.potential_mass(values['E'], values['h'], g_val)
                        elif target == "h":
                            # E = m * g * h => h = E / (m * g)
                            g_val = values.get('g', g)
                            return Energy.potential_height(values['E'], values['m'], g_val)
                        elif target == "g":
                            # E = m * g * h => g = E / (m * h)
                            return values['E'] / (values['m'] * values['h'])
                        else:  # E
                            g_val = values.get('g', g)
                            return Energy.potential(values['m'], values['h'], g_val)
                    
                    elif formula_name == "Потенциальная энергия упругости":
                        if target == "k":
                            # E = k * x² / 2 => k = 2 * E / x²
                            return Energy.elastic_potential_k(values['E'], values['x'])
                        elif target == "x":
                            # E = k * x² / 2 => x = sqrt(2 * E / k)
                            return Energy.elastic_potential_x(values['E'], values['k'])
                        else:  # E
                            return Energy.elastic_potential(values['k'], values['x'])
                    
                    elif formula_name == "Кинетическая энергия вращения":
                        if target == "I":
                            # E = I * ω² / 2 => I = 2 * E / ω²
                            return (2 * values['E']) / (values['w'] ** 2)
                        elif target == "w":
                            # E = I * ω² / 2 => ω = sqrt(2 * E / I)
                            return math.sqrt((2 * values['E']) / values['I'])
                        else:  # E
                            return Energy.rotational_kinetic(values['I'], values['w'])
                    
                    elif formula_name == "Тепловая энергия":
                        if target == "m":
                            # Q = m * c * ΔT => m = Q / (c * ΔT)
                            return values['Q'] / (values['c'] * values['dt'])
                        elif target == "c":
                            # Q = m * c * ΔT => c = Q / (m * ΔT)
                            return values['Q'] / (values['m'] * values['dt'])
                        elif target == "dt":
                            # Q = m * c * ΔT => ΔT = Q / (m * c)
                            return values['Q'] / (values['m'] * values['c'])
                        else:  # Q
                            return Energy.thermal(values['m'], values['c'], values['dt'])
                    
                    elif formula_name == "Энергия сгорания":
                        if target == "m":
                            # Q = m * q => m = Q / q
                            return values['Q'] / values['q']
                        elif target == "q":
                            # Q = m * q => q = Q / m
                            return values['Q'] / values['m']
                        else:  # Q
                            return Energy.combustion(values['m'], values['q'])
                    
                    elif formula_name == "Работа постоянной силы":
                        if target == "F":
                            # A = F * s * cos(α) => F = A / (s * cos(α))
                            angle_rad = math.radians(values.get('angle_degrees', 0))
                            return values['A'] / (values['s'] * math.cos(angle_rad))
                        elif target == "s":
                            # A = F * s * cos(α) => s = A / (F * cos(α))
                            angle_rad = math.radians(values.get('angle_degrees', 0))
                            return values['A'] / (values['F'] * math.cos(angle_rad))
                        elif target == "angle_degrees":
                            # A = F * s * cos(α) => α = arccos(A / (F * s))
                            cos_angle = values['A'] / (values['F'] * values['s'])
                            return math.degrees(math.acos(cos_angle))
                        else:  # A
                            angle_degrees = values.get('angle_degrees', 0)
                            return Energy.work_constant_force(values['F'], values['s'], angle_degrees)
                    
                    elif formula_name == "Работа переменной силы":
                        if target == "F_initial":
                            # A = (F₁ + F₂) * s / 2 => F₁ = 2 * A / s - F₂
                            return (2 * values['A'] / values['s']) - values['F_final']
                        elif target == "F_final":
                            # A = (F₁ + F₂) * s / 2 => F₂ = 2 * A / s - F₁
                            return (2 * values['A'] / values['s']) - values['F_initial']
                        elif target == "s":
                            # A = (F₁ + F₂) * s / 2 => s = 2 * A / (F₁ + F₂)
                            return (2 * values['A']) / (values['F_initial'] + values['F_final'])
                        else:  # A
                            return Energy.work_variable_force_linear(values['F_initial'], values['F_final'], values['s'])
                    
                    elif formula_name == "Работа газа (изобарный процесс)":
                        if target == "P":
                            # A = P * ΔV => P = A / ΔV
                            return values['A'] / values['dV']
                        elif target == "dV":
                            # A = P * ΔV => ΔV = A / P
                            return values['A'] / values['P']
                        else:  # A
                            return Energy.work_gas_isobaric(values['P'], values['dV'])
                    
                    elif formula_name == "Работа электрического поля":
                        if target == "q":
                            # A = q * U => q = A / U
                            return values['A'] / values['U']
                        elif target == "U":
                            # A = q * U => U = A / q
                            return values['A'] / values['q']
                        else:  # A
                            return Energy.work_electric_field(values['q'], values['U'])
                    
                    elif formula_name == "Работа против трения":
                        if target == "F_friction":
                            # A = F * s => F = A / s
                            return values['A'] / values['s']
                        elif target == "s":
                            # A = F * s => s = A / F
                            return values['A'] / values['F_friction']
                        else:  # A
                            return Energy.work_against_friction(values['F_friction'], values['s'])
                    
                    elif formula_name == "Полезная работа":
                        if target == "total_work":
                            # A_useful = A_total * η => A_total = A_useful / η
                            return values['A_useful'] / values['efficiency']
                        elif target == "efficiency":
                            # A_useful = A_total * η => η = A_useful / A_total
                            return values['A_useful'] / values['total_work']
                        else:  # A_useful
                            return Energy.useful_work(values['total_work'], values['efficiency'])
                    
                    elif formula_name == "Работа через изменение кинетической энергии":
                        if target == "m":
                            # A = m * (V₂² - V₁²) / 2 => m = 2 * A / (V₂² - V₁²)
                            return (2 * values['A']) / (values['V_final'] ** 2 - values['V_initial'] ** 2)
                        elif target == "V_initial":
                            # A = m * (V₂² - V₁²) / 2 => V₁ = sqrt(V₂² - 2 * A / m)
                            return math.sqrt(values['V_final'] ** 2 - (2 * values['A'] / values['m']))
                        elif target == "V_final":
                            # A = m * (V₂² - V₁²) / 2 => V₂ = sqrt(V₁² + 2 * A / m)
                            return math.sqrt(values['V_initial'] ** 2 + (2 * values['A'] / values['m']))
                        else:  # A
                            return Energy.work_kinetic_energy_change(values['m'], values['V_initial'], values['V_final'])
                    
                    elif formula_name == "Работа через изменение потенциальной энергии":
                        if target == "m":
                            # A = m * g * (h₂ - h₁) => m = A / (g * (h₂ - h₁))
                            g_val = values.get('g', g)
                            return values['A'] / (g_val * (values['h_final'] - values['h_initial']))
                        elif target == "h_initial":
                            # A = m * g * (h₂ - h₁) => h₁ = h₂ - A / (m * g)
                            g_val = values.get('g', g)
                            return values['h_final'] - (values['A'] / (values['m'] * g_val))
                        elif target == "h_final":
                            # A = m * g * (h₂ - h₁) => h₂ = h₁ + A / (m * g)
                            g_val = values.get('g', g)
                            return values['h_initial'] + (values['A'] / (values['m'] * g_val))
                        elif target == "g":
                            # A = m * g * (h₂ - h₁) => g = A / (m * (h₂ - h₁))
                            return values['A'] / (values['m'] * (values['h_final'] - values['h_initial']))
                        else:  # A
                            g_val = values.get('g', g)
                            return Energy.work_potential_energy_change(values['m'], values['h_initial'], values['h_final'], g_val)
                    
                    elif formula_name == "Работа упругой силы":
                        if target == "k":
                            # A = k * (x₂² - x₁²) / 2 => k = 2 * A / (x₂² - x₁²)
                            return (2 * values['A']) / (values['x_final'] ** 2 - values['x_initial'] ** 2)
                        elif target == "x_initial":
                            # A = k * (x₂² - x₁²) / 2 => x₁ = sqrt(x₂² - 2 * A / k)
                            return math.sqrt(values['x_final'] ** 2 - (2 * values['A'] / values['k']))
                        elif target == "x_final":
                            # A = k * (x₂² - x₁²) / 2 => x₂ = sqrt(x₁² + 2 * A / k)
                            return math.sqrt(values['x_initial'] ** 2 + (2 * values['A'] / values['k']))
                        else:  # A
                            return Energy.work_elastic_force(values['k'], values['x_initial'], values['x_final'])
                    
                    elif formula_name == "Энергия покоя":
                        if target == "m":
                            # E = m * c² => m = E / c²
                            return values['E'] / (c ** 2)
                        else:  # E
                            return Energy.rest_energy(values['m'])
                    
                    elif formula_name == "Энергия фотона":
                        if target == "frequency":
                            # E = h * f => f = E / h
                            return values['E'] / h
                        else:  # E
                            return Energy.photon_energy(values['frequency'])
                    
                    elif formula_name == "Энергия магнитного поля":
                        if target == "L":
                            # E = L * I² / 2 => L = 2 * E / I²
                            return (2 * values['E']) / (values['I'] ** 2)
                        elif target == "I":
                            # E = L * I² / 2 => I = sqrt(2 * E / L)
                            return math.sqrt((2 * values['E']) / values['L'])
                        else:  # E
                            return Energy.magnetic_energy(values['L'], values['I'])
                    
                    elif formula_name == "Химическая энергия":
                        if target == "moles":
                            # E = n * E_bond => n = E / E_bond
                            return values['E'] / values['bond_energy_per_mole']
                        elif target == "bond_energy_per_mole":
                            # E = n * E_bond => E_bond = E / n
                            return values['E'] / values['moles']
                        else:  # E
                            return Energy.chemical_energy(values['moles'], values['bond_energy_per_mole'])
                    
                    elif formula_name == "Энергия активации":
                        if target == "pre_exponential":
                            # E_a = -R * T * ln(k / A) => A = k / exp(-E_a / (R * T))
                            return values['rate_constant'] / math.exp(-values['E_a'] / (R * values['T']))
                        elif target == "rate_constant":
                            # E_a = -R * T * ln(k / A) => k = A * exp(-E_a / (R * T))
                            return values['pre_exponential'] * math.exp(-values['E_a'] / (R * values['T']))
                        elif target == "T":
                            # E_a = -R * T * ln(k / A) => T = -E_a / (R * ln(k / A))
                            return -values['E_a'] / (R * math.log(values['rate_constant'] / values['pre_exponential']))
                        else:  # E_a
                            return Energy.activation_energy(values['pre_exponential'], values['rate_constant'], values['T'])
                    
                    elif formula_name == "КПД":
                        if target == "useful_work":
                            # η = A_useful / A_total => A_useful = η * A_total
                            return values['efficiency'] * values['total_work']
                        elif target == "total_work":
                            # η = A_useful / A_total => A_total = A_useful / η
                            return values['useful_work'] / values['efficiency']
                        else:  # efficiency
                            return PhysicsUtils.calculate_efficiency(values['useful_work'], values['total_work'])
                    
                    elif formula_name == "Мощность":
                        if target == "work":
                            # P = A / t => A = P * t
                            return values['P'] * values['time']
                        elif target == "time":
                            # P = A / t => t = A / P
                            return values['work'] / values['P']
                        else:  # P
                            return PhysicsUtils.calculate_power(values['work'], values['time'])
                    
                    elif formula_name == "Работа из мощности":
                        if target == "power":
                            # A = P * t => P = A / t
                            return values['A'] / values['time']
                        elif target == "time":
                            # A = P * t => t = A / P
                            return values['A'] / values['power']
                        else:  # A
                            return PhysicsUtils.calculate_work_from_power(values['power'], values['time'])
            
            # ФИЗИКА - Электродинамика
            elif category == "⚡ ФИЗИКА" and subcategory == "Электродинамика":
                if DLL_AVAILABLE and Force and Energy:
                    if formula_name == "Закон Кулона":
                        if target == "q1":
                            # F = k * q1 * q2 / r² => q1 = F * r² / (k * q2)
                            k_val = values.get('k', k)
                            return (values['F'] * values['r'] ** 2) / (k_val * values['q2'])
                        elif target == "q2":
                            # F = k * q1 * q2 / r² => q2 = F * r² / (k * q1)
                            k_val = values.get('k', k)
                            return (values['F'] * values['r'] ** 2) / (k_val * values['q1'])
                        elif target == "r":
                            # F = k * q1 * q2 / r² => r = sqrt(k * q1 * q2 / F)
                            k_val = values.get('k', k)
                            return math.sqrt((k_val * values['q1'] * values['q2']) / values['F'])
                        else:  # F
                            k_val = values.get('k', k)
                            return Force.coulomb(values['q1'], values['q2'], values['r'], k_val)
                    
                    elif formula_name == "Сила Лоренца":
                        if target == "q":
                            # F = q * V * B * sin(α) => q = F / (V * B * sin(α))
                            angle_rad = math.radians(values['angle'])
                            return values['F'] / (values['V'] * values['B'] * math.sin(angle_rad))
                        elif target == "V":
                            # F = q * V * B * sin(α) => V = F / (q * B * sin(α))
                            angle_rad = math.radians(values['angle'])
                            return values['F'] / (values['q'] * values['B'] * math.sin(angle_rad))
                        elif target == "B":
                            # F = q * V * B * sin(α) => B = F / (q * V * sin(α))
                            angle_rad = math.radians(values['angle'])
                            return values['F'] / (values['q'] * values['V'] * math.sin(angle_rad))
                        elif target == "angle":
                            # F = q * V * B * sin(α) => α = arcsin(F / (q * V * B))
                            sin_angle = values['F'] / (values['q'] * values['V'] * values['B'])
                            return math.degrees(math.asin(sin_angle))
                        else:  # F
                            return Force.lorentz(values['q'], values['V'], values['B'], values['angle'])
                    
                    elif formula_name == "Сила Ампера":
                        if target == "B":
                            # F = B * I * L * sin(α) => B = F / (I * L * sin(α))
                            angle_rad = math.radians(values['angle'])
                            return values['F'] / (values['I'] * values['L'] * math.sin(angle_rad))
                        elif target == "I":
                            # F = B * I * L * sin(α) => I = F / (B * L * sin(α))
                            angle_rad = math.radians(values['angle'])
                            return values['F'] / (values['B'] * values['L'] * math.sin(angle_rad))
                        elif target == "L":
                            # F = B * I * L * sin(α) => L = F / (B * I * sin(α))
                            angle_rad = math.radians(values['angle'])
                            return values['F'] / (values['B'] * values['I'] * math.sin(angle_rad))
                        elif target == "angle":
                            # F = B * I * L * sin(α) => α = arcsin(F / (B * I * L))
                            sin_angle = values['F'] / (values['B'] * values['I'] * values['L'])
                            return math.degrees(math.asin(sin_angle))
                        else:  # F
                            return Force.ampere(values['B'], values['I'], values['L'], values['angle'])
                    
                    elif formula_name == "Энергия конденсатора":
                        if target == "C":
                            # E = C * U² / 2 => C = 2 * E / U²
                            return (2 * values['E']) / (values['U'] ** 2)
                        elif target == "U":
                            # E = C * U² / 2 => U = sqrt(2 * E / C)
                            return math.sqrt((2 * values['E']) / values['C'])
                        else:  # E
                            return Energy.capacitor(values['C'], values['U'])
            
            return None
            
        except Exception as e:
            print(f"Ошибка вычисления: {e}")
            import traceback
            traceback.print_exc()
            return None

# Создание экземпляра менеджера формул
formula_manager = FormulaManager()
