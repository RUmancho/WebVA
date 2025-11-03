# -*- coding: utf-8 -*-
"""
Вспомогательные функции для сокращения кода и улучшения читаемости
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import streamlit as st

def format_datetime(dt: Optional[datetime], format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Форматирование datetime с безопасной обработкой None
    
    Args:
        dt: Объект datetime или None
        format_str: Строка формата
        
    Returns:
        str: Отформатированная дата или 'Не указано'
    """
    return dt.strftime(format_str) if dt else 'Не указано'

def safe_get(dictionary: Dict[str, Any], key: str, default: Any = '') -> Any:
    """
    Безопасное получение значения из словаря
    
    Args:
        dictionary: Словарь
        key: Ключ
        default: Значение по умолчанию
        
    Returns:
        Any: Значение или default
    """
    return dictionary.get(key, default) if dictionary else default

def create_user_display_name(user: Dict[str, Any]) -> str:
    """
    Создание отображаемого имени пользователя
    
    Args:
        user: Словарь с данными пользователя
        
    Returns:
        str: Полное имя пользователя
    """
    first_name = safe_get(user, 'first_name', '')
    last_name = safe_get(user, 'last_name', '')
    return f"{first_name} {last_name}".strip()

def create_status_icon(is_online: bool) -> str:
    """
    Создание иконки статуса онлайн
    
    Args:
        is_online: Статус онлайн
        
    Returns:
        str: Эмодзи статуса
    """
    return "🟢" if is_online else "🔴"

def format_user_location(user: Dict[str, Any]) -> str:
    """
    Форматирование местоположения пользователя
    
    Args:
        user: Словарь с данными пользователя
        
    Returns:
        str: Строка местоположения
    """
    city = safe_get(user, 'city', 'Не указан')
    school = safe_get(user, 'school', 'Не указана')
    return f"{city}, {school}"

def show_info_card(label: str, value: Any, help_text: Optional[str] = None) -> None:
    """
    Отображение информационной карточки
    
    Args:
        label: Метка
        value: Значение
        help_text: Текст подсказки
    """
    if help_text:
        st.info(f"**{label}:** {value}", icon="ℹ️")
    else:
        st.info(f"**{label}:** {value}")

def show_user_card(user: Dict[str, Any], show_status: bool = True, 
                   show_location: bool = True) -> None:
    """
    Отображение карточки пользователя
    
    Args:
        user: Данные пользователя
        show_status: Показывать статус онлайн
        show_location: Показывать местоположение
    """
    cols = st.columns([1, 3, 2])
    
    with cols[0]:
        if show_status:
            status_icon = create_status_icon(safe_get(user, 'is_online', False))
            st.write(status_icon)
    
    with cols[1]:
        st.write(f"**{create_user_display_name(user)}**")
        st.write(f"*{safe_get(user, 'role', 'Пользователь')}*")
    
    with cols[2]:
        if show_location:
            st.write(format_user_location(user))
        st.write(safe_get(user, 'email', ''))

def validate_form_fields(fields: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
    """
    Валидация полей формы
    
    Args:
        fields: Словарь полей
        required_fields: Список обязательных полей
        
    Returns:
        Tuple[bool, List[str]]: (валидна ли форма, список ошибок)
    """
    errors = []
    
    for field in required_fields:
        value = fields.get(field)
        if not value or (isinstance(value, str) and not value.strip()):
            errors.append(f"Поле '{field}' обязательно для заполнения")
    
    return len(errors) == 0, errors

def show_errors(errors: List[str]) -> None:
    """
    Отображение списка ошибок
    
    Args:
        errors: Список ошибок
    """
    if errors:
        st.error("Обнаружены ошибки:")
        for error in errors:
            st.error(f"• {error}")

def create_progress_bar(current: int, total: int, label: Optional[str] = None) -> None:
    """
    Создание прогресс-бара
    
    Args:
        current: Текущее значение
        total: Максимальное значение
        label: Метка
    """
    if total == 0:
        percentage = 0
    else:
        percentage = (current / total) * 100
    
    if label:
        st.write(f"{label}: {current}/{total} ({percentage:.1f}%)")
    else:
        st.write(f"{current}/{total} ({percentage:.1f}%)")
    
    st.progress(percentage / 100.0)

def format_list_display(items: List[str], separator: str = ", ", 
                        empty_text: str = "Не указано") -> str:
    """
    Форматирование списка для отображения
    
    Args:
        items: Список элементов
        separator: Разделитель
        empty_text: Текст если список пустой
        
    Returns:
        str: Отформатированная строка
    """
    if not items:
        return empty_text
    return separator.join(str(item) for item in items if item)

def create_two_column_form(left_fields: List[Tuple[str, Any]], 
                           right_fields: List[Tuple[str, Any]]) -> Dict[str, Any]:
    """
    Создание формы с двумя колонками
    
    Args:
        left_fields: Поля левой колонки (label, widget)
        right_fields: Поля правой колонки (label, widget)
        
    Returns:
        Dict: Значения полей
    """
    col1, col2 = st.columns(2)
    values = {}
    
    with col1:
        for label, widget in left_fields:
            values[label] = widget
    
    with col2:
        for label, widget in right_fields:
            values[label] = widget
    
    return values

def confirm_action(message: str, button_text: str = "Подтвердить", 
                   danger: bool = False) -> bool:
    """
    Диалог подтверждения действия
    
    Args:
        message: Сообщение для подтверждения
        button_text: Текст кнопки
        danger: Опасное действие (красная кнопка)
        
    Returns:
        bool: True если пользователь подтвердил
    """
    st.warning(message)
    button_type = "primary" if not danger else "primary"
    
    if danger:
        st.error("⚠️ Это действие необратимо!")
    
    return st.button(button_text, type=button_type)

def show_success_message(message: str, with_balloons: bool = False) -> None:
    """
    Отображение сообщения об успехе
    
    Args:
        message: Сообщение
        with_balloons: Показать анимацию шариков
    """
    st.success(f"✅ {message}")
    if with_balloons:
        st.balloons()

def show_error_message(message: str, details: Optional[str] = None) -> None:
    """
    Отображение сообщения об ошибке
    
    Args:
        message: Сообщение
        details: Дополнительные детали
    """
    st.error(f"❌ {message}")
    if details:
        with st.expander("Подробности ошибки"):
            st.code(details)

def batch_dict_to_list(dicts: List[Dict[str, Any]], key: str) -> List[Any]:
    """
    Извлечение значений ключа из списка словарей
    
    Args:
        dicts: Список словарей
        key: Ключ для извлечения
        
    Returns:
        List: Список значений
    """
    return [d.get(key) for d in dicts if key in d]

def group_by_key(items: List[Dict[str, Any]], key: str) -> Dict[Any, List[Dict[str, Any]]]:
    """
    Группировка элементов по ключу
    
    Args:
        items: Список элементов
        key: Ключ для группировки
        
    Returns:
        Dict: Сгруппированные элементы
    """
    groups = {}
    for item in items:
        group_key = item.get(key)
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(item)
    return groups

def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Обрезка строки с добавлением суффикса
    
    Args:
        text: Исходная строка
        max_length: Максимальная длина
        suffix: Суффикс для обрезанной строки
        
    Returns:
        str: Обрезанная строка
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def calculate_time_difference(dt1: datetime, dt2: datetime) -> str:
    """
    Вычисление разницы во времени в читаемом формате
    
    Args:
        dt1: Первая дата
        dt2: Вторая дата
        
    Returns:
        str: Разница во времени
    """
    diff = abs((dt2 - dt1).total_seconds())
    
    if diff < 60:
        return f"{int(diff)} сек"
    elif diff < 3600:
        return f"{int(diff / 60)} мин"
    elif diff < 86400:
        return f"{int(diff / 3600)} ч"
    else:
        return f"{int(diff / 86400)} дн"

def create_table_from_dicts(data: List[Dict[str, Any]], columns: List[str]) -> None:
    """
    Создание таблицы из списка словарей
    
    Args:
        data: Данные
        columns: Колонки для отображения
    """
    if not data:
        st.info("Нет данных для отображения")
        return
    
    # Создаем таблицу
    table_data = []
    for item in data:
        row = [item.get(col, '') for col in columns]
        table_data.append(row)
    
    # Отображаем
    st.table({col: [row[i] for row in table_data] 
             for i, col in enumerate(columns)})

