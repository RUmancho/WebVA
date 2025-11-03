# -*- coding: utf-8 -*-
"""
Планировщик задач для автоматического прикрепления учеников
"""
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config_manager import get_config_value, log_info, log_error
import os

# Глобальный планировщик
SCHEDULER: Optional[BackgroundScheduler] = None
CHECK_INTERVAL_MINUTES = 3

def init_scheduler() -> BackgroundScheduler:
    """
    Инициализация планировщика задач
    
    Returns:
        BackgroundScheduler: Экземпляр планировщика
    """
    global SCHEDULER, CHECK_INTERVAL_MINUTES
    
    try:
        if SCHEDULER is not None and SCHEDULER.running:
            log_info("scheduler.py", "Планировщик уже запущен")
            return SCHEDULER
        
        # Получаем настройки из конфига
        scheduler_enabled = get_config_value("scheduler.enabled", True)
        CHECK_INTERVAL_MINUTES = get_config_value("scheduler.class_attachment_check_interval_minutes", 3)
        
        if not scheduler_enabled:
            log_info("scheduler.py", "Планировщик отключен в конфигурации")
            return None
        
        SCHEDULER = BackgroundScheduler(
            timezone="UTC",
            daemon=True,
            job_defaults={
                'coalesce': True,  # Объединять пропущенные задачи
                'max_instances': 1  # Только одна задача может выполняться одновременно
            }
        )
        
        log_info("scheduler.py", f"Планировщик успешно инициализирован (интервал: {CHECK_INTERVAL_MINUTES} мин)")
        return SCHEDULER
        
    except Exception as e:
        log_error("scheduler.py", f"Ошибка инициализации планировщика: {e}")
        return None

def start_scheduler() -> bool:
    """
    Запуск планировщика задач
    
    Returns:
        bool: True если успешно запущен
    """
    global SCHEDULER
    
    try:
        if SCHEDULER is None:
            SCHEDULER = init_scheduler()
        
        if SCHEDULER is None:
            return False
        
        if not SCHEDULER.running:
            SCHEDULER.start()
            log_info("scheduler.py", "Планировщик запущен")
            return True
        
        return True
        
    except Exception as e:
        log_error("scheduler.py", f"Ошибка запуска планировщика: {e}")
        return False

def stop_scheduler() -> bool:
    """
    Остановка планировщика задач
    
    Returns:
        bool: True если успешно остановлен
    """
    global SCHEDULER
    
    try:
        if SCHEDULER and SCHEDULER.running:
            SCHEDULER.shutdown(wait=False)
            log_info("scheduler.py", "Планировщик остановлен")
            return True
        return False
        
    except Exception as e:
        log_error("scheduler.py", f"Ошибка остановки планировщика: {e}")
        return False

def add_class_attachment_job(db_instance) -> bool:
    """
    Добавление задачи периодической проверки прикрепления учеников
    
    Args:
        db_instance: Экземпляр базы данных
        
    Returns:
        bool: True если задача успешно добавлена
    """
    global SCHEDULER, CHECK_INTERVAL_MINUTES
    
    try:
        if SCHEDULER is None:
            SCHEDULER = init_scheduler()
            
        if SCHEDULER is None:
            return False
        
        # Удаляем существующую задачу если есть
        try:
            SCHEDULER.remove_job('class_attachment_check')
        except:
            pass
        
        # Добавляем новую задачу
        SCHEDULER.add_job(
            func=lambda: process_class_attachment_tasks(db_instance),
            trigger=IntervalTrigger(minutes=CHECK_INTERVAL_MINUTES),
            id='class_attachment_check',
            name='Class Attachment Check',
            replace_existing=True
        )
        
        if not SCHEDULER.running:
            start_scheduler()
        
        log_info("scheduler.py", f"Задача автоприкрепления добавлена (каждые {CHECK_INTERVAL_MINUTES} мин)")
        return True
        
    except Exception as e:
        log_error("scheduler.py", f"Ошибка добавления задачи прикрепления: {e}")
        return False

def process_class_attachment_tasks(db_instance) -> None:
    """
    Обработка всех активных задач прикрепления классов
    
    Args:
        db_instance: Экземпляр базы данных
    """
    try:
        log_info("scheduler.py", "Начало обработки задач прикрепления")
        
        # Получаем активные задачи
        active_tasks = db_instance.get_active_attachment_tasks()
        
        if not active_tasks:
            log_info("scheduler.py", "Нет активных задач прикрепления")
            return
        
        log_info("scheduler.py", f"Найдено активных задач: {len(active_tasks)}")
        
        # Обрабатываем каждую задачу
        for task in active_tasks:
            try:
                # Проверяем, не завершена ли задача
                if task['current_student_count'] >= task['target_student_count']:
                    db_instance.complete_attachment_task(task['id'])
                    log_info("scheduler.py", f"Задача {task['id']} завершена (достигнут лимит учеников)")
                    continue
                
                # Проверяем время последней проверки
                last_check = task.get('last_check_time')
                if last_check:
                    time_diff = datetime.utcnow() - datetime.fromisoformat(last_check)
                    if time_diff < timedelta(minutes=CHECK_INTERVAL_MINUTES - 0.5):
                        # Еще рано проверять
                        continue
                
                # Выполняем прикрепление учеников для этой задачи
                result = db_instance.process_single_attachment_task(task['id'])
                
                if result['success']:
                    log_info("scheduler.py", 
                            f"Задача {task['id']}: прикреплено {result['attached_count']} учеников")
                else:
                    log_error("scheduler.py", 
                             f"Задача {task['id']}: ошибка - {result.get('message', 'Unknown')}")
                
            except Exception as e:
                log_error("scheduler.py", f"Ошибка обработки задачи {task.get('id', 'unknown')}: {e}")
                
        log_info("scheduler.py", "Обработка задач прикрепления завершена")
        
    except Exception as e:
        log_error("scheduler.py", f"Критическая ошибка обработки задач: {e}")

def get_scheduler_status() -> Dict[str, Any]:
    """
    Получение статуса планировщика
    
    Returns:
        Dict: Информация о статусе планировщика
    """
    global SCHEDULER
    
    try:
        if SCHEDULER is None:
            return {
                'running': False,
                'jobs_count': 0,
                'message': 'Планировщик не инициализирован'
            }
        
        jobs = SCHEDULER.get_jobs()
        
        return {
            'running': SCHEDULER.running,
            'jobs_count': len(jobs),
            'jobs': [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run': str(job.next_run_time) if job.next_run_time else None
                }
                for job in jobs
            ],
            'message': 'Планировщик работает нормально' if SCHEDULER.running else 'Планировщик остановлен'
        }
        
    except Exception as e:
        log_error("scheduler.py", f"Ошибка получения статуса планировщика: {e}")
        return {
            'running': False,
            'jobs_count': 0,
            'error': str(e)
        }

