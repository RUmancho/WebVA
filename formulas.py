# -*- coding: utf-8 -*-
import streamlit as st
import math
from typing import Dict, List, Optional

# Константы
G_CONSTANT = 9.80665
PI = 3.14159265359

class FormulaManager:
    """Класс для управления формулами и вычислениями"""
    
    def __init__(self):
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
    
    def show_formula_interface(self):
        """Отображение интерфейса калькулятора формул"""
        try:
            st.header("📐 Калькулятор Формул")
            st.info("💡 Выберите категорию и формулу для вычисления. Калькулятор автоматически найдет неизвестную величину!")
            
            # Инициализация состояния
            if 'formula_state' not in st.session_state:
                st.session_state.formula_state = {
                    'current_category': None,
                    'current_subcategory': None
                }
            
            # Выбор категории
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📐 МАТЕМАТИКА", use_container_width=True):
                    st.session_state.formula_state['current_category'] = "📐 МАТЕМАТИКА"
                    st.session_state.formula_state['current_subcategory'] = None
                    st.rerun()
            
            with col2:
                if st.button("⚡ ФИЗИКА", use_container_width=True):
                    st.session_state.formula_state['current_category'] = "⚡ ФИЗИКА"
                    st.session_state.formula_state['current_subcategory'] = None
                    st.rerun()
            
            # Если выбрана категория, показываем подкатегории
            if st.session_state.formula_state['current_category']:
                self.show_subcategories()
            
        except Exception as e:
            st.error(f"Ошибка интерфейса формул: {e}")
            print(f"Ошибка интерфейса формул: {e}")
    
    def show_subcategories(self):
        """Показать подкатегории и формулы"""
        try:
            category = st.session_state.formula_state['current_category']
            
            st.markdown("---")
            st.subheader(f"{category}")
            
            # Выбор подкатегории
            subcategories = self.categories[category]['subcategories']
            selected_subcategory = st.selectbox(
                "Выберите раздел:",
                subcategories,
                key="subcategory_selector"
            )
            
            st.session_state.formula_state['current_subcategory'] = selected_subcategory
            
            # Показываем формулы выбранной подкатегории
            if selected_subcategory:
                formulas = self.get_formulas(category, selected_subcategory)
                
                if formulas:
                    st.markdown("---")
                    st.subheader(f"Формулы раздела: {selected_subcategory}")
                    
                    for formula_data in formulas:
                        self.render_formula_calculator(formula_data, category, selected_subcategory)
                        st.markdown("---")
                else:
                    st.info("Формулы для этой подкатегории пока не добавлены.")
            
        except Exception as e:
            st.error(f"Ошибка отображения подкатегорий: {e}")
            print(f"Ошибка отображения подкатегорий: {e}")
    
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
                {"name": "Вес тела", "formula": "F = m × g", "fields": [("m", "Масса (m)", "кг"), ("F", "Вес (F)", "Н")]},
                {"name": "Скорость", "formula": "v = s / t", "fields": [("s", "Путь (s)", "м"), ("t", "Время (t)", "с"), ("v", "Скорость (v)", "м/с")]},
                {"name": "Механическая работа", "formula": "A = F × s", "fields": [("F", "Сила (F)", "Н"), ("s", "Путь (s)", "м"), ("A", "Работа (A)", "Дж")]},
            ]
        
        return formulas
    
    def render_formula_calculator(self, formula_data: Dict, category: str, subcategory: str):
        """Отображает калькулятор для конкретной формулы"""
        try:
            with st.expander(f"🧮 {formula_data['name']} - {formula_data['formula']}", expanded=False):
                # Выбор целевой переменной
                st.markdown("**Что нужно найти:**")
                target_options = []
                for field_id, field_name, unit in formula_data['fields']:
                    label = f"{field_name}" + (f" [{unit}]" if unit else "")
                    target_options.append((field_id, label))
                
                target_field = st.radio(
                    "Выберите неизвестную величину:",
                    options=[opt[0] for opt in target_options],
                    format_func=lambda x: dict(target_options)[x],
                    horizontal=True,
                    key=f"target_{formula_data['name']}_{category}_{subcategory}"
                )
                
                st.markdown("**Введите известные значения:**")
                
                # Поля ввода
                values = {}
                cols = st.columns(len(formula_data['fields']))
                
                for idx, (field_id, field_name, unit) in enumerate(formula_data['fields']):
                    with cols[idx]:
                        label = f"{field_name}" + (f" [{unit}]" if unit else "")
                        
                        if field_id == target_field:
                            st.text_input(
                                label,
                                value="❓ Найти",
                                disabled=True,
                                key=f"{formula_data['name']}_{field_id}_disabled_{category}"
                            )
                        else:
                            value = st.number_input(
                                label,
                                value=None,
                                format="%.4f",
                                key=f"{formula_data['name']}_{field_id}_{category}"
                            )
                            if value is not None:
                                values[field_id] = value
                
                # Кнопка вычисления
                if st.button(f"🧮 ВЫЧИСЛИТЬ", key=f"calc_{formula_data['name']}_{category}"):
                    try:
                        required_fields = [f[0] for f in formula_data['fields'] if f[0] != target_field]
                        missing_fields = [f for f in required_fields if f not in values]
                        
                        if missing_fields:
                            st.warning(f"⚠️ Пожалуйста, заполните все поля")
                        else:
                            result = self.calculate_formula(
                                formula_data['name'],
                                category,
                                subcategory,
                                values,
                                target_field
                            )
                            
                            if result is not None:
                                field_name_full = ""
                                unit_text = ""
                                for field_id, fname, unit in formula_data['fields']:
                                    if field_id == target_field:
                                        field_name_full = fname
                                        unit_text = f" {unit}" if unit else ""
                                        break
                                
                                st.success(f"✅ **Результат:** {field_name_full} = {result:.4f}{unit_text}")
                            else:
                                st.error("❌ Не удалось вычислить результат")
                    except Exception as e:
                        st.error(f"❌ Ошибка: {str(e)}")
                        
        except Exception as e:
            st.error(f"Ошибка отображения калькулятора: {e}")
            print(f"Ошибка отображения калькулятора: {e}")
    
    def calculate_formula(self, formula_name: str, category: str, subcategory: str, 
                         values: Dict[str, float], target: str) -> Optional[float]:
        """Вычисляет значение по формуле"""
        try:
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
                        return (2 * values['S']) / values['h']
                    elif target == "h":
                        return (2 * values['S']) / values['a']
                    else:  # S
                        return (values['a'] * values['h']) / 2
                
                elif formula_name == "Площадь прямоугольника":
                    if target == "a":
                        return values['S'] / values['b']
                    elif target == "b":
                        return values['S'] / values['a']
                    else:  # S
                        return values['a'] * values['b']
            
            # ФИЗИКА - Механика
            elif category == "⚡ ФИЗИКА" and subcategory == "Механика":
                if formula_name == "Вес тела":
                    if target == "m":
                        return values['F'] / G_CONSTANT
                    else:  # F
                        return values['m'] * G_CONSTANT
                
                elif formula_name == "Скорость":
                    if target == "s":
                        return values['v'] * values['t']
                    elif target == "t":
                        return values['s'] / values['v']
                    else:  # v
                        return values['s'] / values['t']
                
                elif formula_name == "Механическая работа":
                    if target == "F":
                        return values['A'] / values['s']
                    elif target == "s":
                        return values['A'] / values['F']
                    else:  # A
                        return values['F'] * values['s']
            
            return None
            
        except Exception as e:
            print(f"Ошибка вычисления: {e}")
            return None

# Создание экземпляра менеджера формул
formula_manager = FormulaManager()

