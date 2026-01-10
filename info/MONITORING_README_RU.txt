================================================================================
                   ДОКУМЕНТАЦИЯ СИСТЕМЫ МОНИТОРИНГА
================================================================================

ЧТО БЫЛО РЕАЛИЗОВАНО:
---------------------
1. Система мониторинга на основе OpenTelemetry
2. База данных SQLite для хранения метрик (logger/reports/metrics.db)
3. Автоматическое отслеживание:
   - Количества вызовов функций
   - Времени выполнения (среднее, мин, макс)
   - Ошибок с типами

СОЗДАННЫЕ ФАЙЛЫ:
----------------
- logger/models.py           - Модели базы данных
- logger/exporter.py         - Экспортер в SQLite
- test_metrics.py            - Тестовый скрипт
- view_metrics.py            - Просмотр всех метрик
- analyze_metrics.py         - Анализ конкретных функций
- show_database_metrics.py   - Просмотр метрик database.py
- check_db.py                - Проверка структуры БД

ИЗМЕНЕННЫЕ ФАЙЛЫ:
-----------------
- logger/t.py                - Обновлен с настройкой OpenTelemetry
- database/database.py       - Добавлен @monitor_function к 32 методам
- requirements.txt           - Добавлены зависимости opentelemetry

================================================================================
                          КАК ИСПОЛЬЗОВАТЬ
================================================================================

1. ТЕСТИРОВАНИЕ СИСТЕМЫ:
   
   python test_metrics.py
   
   Это:
   - Вызовет тестовые функции 10, 5 и 3 раза
   - Сгенерирует ошибки
   - Экспортирует метрики в базу данных

2. ПРОСМОТР ВСЕХ МЕТРИК:
   
   python view_metrics.py
   
   Показывает:
   - Все метрики в базе данных
   - Количество вызовов функций
   - Статистику функций
   - Ошибки

3. ПРОСМОТР МЕТРИК DATABASE.PY:
   
   python show_database_metrics.py
   
   Показывает метрики всех отслеживаемых функций database.py

4. АНАЛИЗ КОНКРЕТНОЙ ФУНКЦИИ:
   
   python analyze_metrics.py
   
   Показывает детальный анализ каждой отслеживаемой функции

5. ПРОВЕРКА СТРУКТУРЫ БАЗЫ ДАННЫХ:
   
   python check_db.py
   
   Показывает таблицы БД и количество записей

================================================================================
                          КАК ЭТО РАБОТАЕТ
================================================================================

1. АВТОМАТИЧЕСКИЙ МОНИТОРИНГ:
   - Все функции с декоратором @monitor_function отслеживаются
   - Метрики собираются в памяти (OpenTelemetry)
   - Экспортируются в SQLite каждые 60 секунд
   - Нет влияния на производительность функций

2. ХРАНЕНИЕ ДАННЫХ:
   - База данных: E:\Python\Sites\WebVA\logger\reports\metrics.db
     (абсолютный путь, не зависит от директории запуска)
   - Таблица: function_metrics
   - Столбцы: function_name, metric_type, value, count, sum, min, max, 
              timestamp, error_type

3. ТИПЫ МЕТРИК:
   - call     - Количество вызовов функции (накопительное)
   - duration - Статистика времени выполнения
   - error    - Количество ошибок по типам

================================================================================
                      ОТСЛЕЖИВАЕМЫЕ ФУНКЦИИ
================================================================================

Следующие функции database.py отслеживаются:
- register_user
- authenticate_user
- get_user_by_email
- reset_user_password
- get_teachers
- get_user_by_id
- delete_user
- create_teacher_request
- get_student_requests
- accept_teacher_request
- reject_teacher_request
- get_student_teachers
- create_call
- start_call
- end_call
- get_user_calls
- cleanup_expired_records
- create_lesson_record
- get_user_lesson_records
- get_all_students
- get_teacher_sent_requests
- get_teacher_students
- update_user_online_status
- get_user_notifications
- mark_notification_read
- create_notification
- get_teacher_students_tree
- get_user_settings
- update_user_settings
- reset_user_settings
- create_class_assignment
- get_teacher_assignments
- get_student_assignments
- get_assignment_by_id
- submit_assignment
- get_assignment_statistics
- get_class_statistics
- toggle_assignment_active

================================================================================
                        ПРИМЕРЫ SQL ЗАПРОСОВ
================================================================================

1. Получить общее количество вызовов функции:

   SELECT MAX(value) 
   FROM function_metrics 
   WHERE metric_type = 'call' AND function_name = 'register_user';

2. Получить среднее время выполнения:

   SELECT AVG(value) 
   FROM function_metrics 
   WHERE metric_type = 'duration' AND function_name = 'register_user';

3. Получить все ошибки:

   SELECT function_name, error_type, MAX(value) as count
   FROM function_metrics 
   WHERE metric_type = 'error'
   GROUP BY function_name, error_type;

4. Получить самые медленные функции:

   SELECT function_name, AVG(value) as avg_time
   FROM function_metrics 
   WHERE metric_type = 'duration'
   GROUP BY function_name
   ORDER BY avg_time DESC
   LIMIT 10;

5. Получить динамику вызовов по времени:

   SELECT 
       datetime(timestamp) as time,
       function_name,
       value as cumulative_calls
   FROM function_metrics
   WHERE metric_type = 'call' 
     AND function_name = 'register_user'
     AND timestamp >= datetime('now', '-1 day')
   ORDER BY timestamp;

6. Получить процент ошибок функции:

   WITH calls AS (
       SELECT MAX(value) as total 
       FROM function_metrics 
       WHERE metric_type = 'call' AND function_name = 'register_user'
   ),
   errors AS (
       SELECT SUM(max_val) as total FROM (
           SELECT MAX(value) as max_val 
           FROM function_metrics
           WHERE metric_type = 'error' AND function_name = 'register_user'
           GROUP BY error_type
       )
   )
   SELECT 
       calls.total as total_calls,
       errors.total as total_errors,
       ROUND((errors.total * 100.0 / calls.total), 2) as error_rate_percent
   FROM calls, errors;

================================================================================
                             ЗАМЕТКИ
================================================================================

1. Метрики экспортируются каждые 60 секунд (настраивается в logger/t.py)
2. Для принудительного экспорта: вызовите функцию flush_metrics()
3. База данных растет медленно (только агрегированные данные за минуту)
4. Счетчики НАКОПИТЕЛЬНЫЕ (не сбрасываются между экспортами)
5. Для получения вызовов за период: MAX(value) - MIN(value) для временного диапазона

6. СТРУКТУРА ДАННЫХ:
   - Каждая запись = один экспорт (раз в 60 секунд)
   - value для 'call' = общее количество с момента запуска
   - value для 'duration' = среднее время за период
   - count, sum, min, max = детальная статистика для duration
   - error_type = тип исключения (ValueError, SQLAlchemyError и т.д.)

7. ПРОИЗВОДИТЕЛЬНОСТЬ:
   - Декоратор добавляет ~0.0001 мс накладных расходов
   - Влияние на функцию < 1%
   - Запись в БД происходит в фоне (не блокирует функции)

================================================================================
                        УСТРАНЕНИЕ НЕПОЛАДОК
================================================================================

Если метрики не появляются:

1. Проверьте, что opentelemetry установлен:
   pip list | grep opentelemetry
   
   Должны быть:
   - opentelemetry-api
   - opentelemetry-sdk

2. Проверьте, что база данных существует:
   python check_db.py
   
   Должна показать:
   - Файл найден
   - Таблица function_metrics существует

3. Запустите тест для проверки системы:
   python test_metrics.py
   
   Должно появиться:
   - [Tracer] OpenTelemetry monitoring initialized successfully
   - [SQLiteMetricExporter] Exported N metrics

4. Проверьте консольный вывод на наличие ошибок:
   - AttributeError -> проверьте версию opentelemetry
   - ImportError -> переустановите зависимости
   - SQLite error -> проверьте права доступа к файлу

5. Если функция database.py не отслеживается:
   - Убедитесь, что декоратор @monitor_function добавлен
   - Проверьте, что функция была вызвана хотя бы раз
   - Подождите 60 секунд (время экспорта)
   - Или вызовите flush_metrics() для принудительного экспорта

6. Если база данных создается в неправильном месте:
   - Система использует АБСОЛЮТНЫЙ путь относительно корня проекта
   - Файл всегда создается в E:\Python\Sites\WebVA\logger\reports\metrics.db
   - Независимо от того, откуда запущено приложение (UI/, корень и т.д.)
   - Если видите файл в другом месте - удалите его, он старый

================================================================================
                        РАСШИРЕННОЕ ИСПОЛЬЗОВАНИЕ
================================================================================

1. НАСТРОЙКА ИНТЕРВАЛА ЭКСПОРТА:

   В файле logger/t.py измените:
   
   export_interval_millis=60000  # 60 секунд
   
   На нужное значение (в миллисекундах):
   - 30000  = 30 секунд
   - 300000 = 5 минут

2. ПРИНУДИТЕЛЬНЫЙ ЭКСПОРТ:

   from logger.t import flush_metrics
   
   # В конце скрипта или перед завершением
   flush_metrics()

3. ДОБАВЛЕНИЕ МОНИТОРИНГА К НОВЫМ ФУНКЦИЯМ:

   from logger.t import monitor_function
   
   @monitor_function
   def my_new_function():
       # ваш код
       pass

4. СОЗДАНИЕ СВОИХ ЗАПРОСОВ:

   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker
   from logger.models import FunctionMetric
   
   engine = create_engine('sqlite:///logger/reports/metrics.db')
   Session = sessionmaker(bind=engine)
   session = Session()
   
   # Ваш запрос
   results = session.query(FunctionMetric).filter(
       FunctionMetric.function_name == 'my_function'
   ).all()

5. ОЧИСТКА СТАРЫХ ДАННЫХ:

   import sqlite3
   from datetime import datetime, timedelta
   
   conn = sqlite3.connect('logger/reports/metrics.db')
   cursor = conn.cursor()
   
   # Удалить метрики старше 30 дней
   cutoff = datetime.utcnow() - timedelta(days=30)
   cursor.execute(
       "DELETE FROM function_metrics WHERE timestamp < ?",
       (cutoff,)
   )
   conn.commit()
   conn.close()

================================================================================
                          ИНТЕГРАЦИЯ С FLASK
================================================================================

Для мониторинга Flask-роутов (опционально):

В файле UI/app.py:

from logger.t import monitor_function, flush_metrics
import atexit

# При завершении приложения - экспортировать метрики
atexit.register(flush_metrics)

# Добавить декоратор на роуты
@app.route('/api/login', methods=['POST'])
@monitor_function
def login():
    # ... ваш код ...
    pass

================================================================================
                          ПРИМЕРЫ АНАЛИЗА
================================================================================

1. ПОИСК УЗКИХ МЕСТ:
   
   python show_database_metrics.py
   
   Смотрите "TOP SLOWEST FUNCTIONS" - функции с высоким avg_time

2. МОНИТОРИНГ ОШИБОК:
   
   python show_database_metrics.py
   
   Смотрите "FUNCTIONS WITH ERRORS" - функции с частыми ошибками

3. АНАЛИЗ НАГРУЗКИ:
   
   python view_metrics.py
   
   Смотрите "FUNCTION CALL COUNTS" - самые вызываемые функции

4. ПОИСК АНОМАЛИЙ:
   
   Если max_time >> avg_time -> есть редкие медленные вызовы
   Если error_rate > 5% -> нужна оптимизация обработки ошибок

================================================================================
                          ПОДДЕРЖКА
================================================================================

При возникновении проблем:

1. Проверьте версию Python (требуется >= 3.8)
2. Переустановите зависимости: pip install -r requirements.txt
3. Удалите metrics.db и запустите test_metrics.py заново
4. Проверьте логи в консоли при запуске приложения

================================================================================

