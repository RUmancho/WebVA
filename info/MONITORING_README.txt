================================================================================
                     SYSTEM MONITORING DOCUMENTATION
================================================================================

WHAT WAS IMPLEMENTED:
---------------------
1. OpenTelemetry-based monitoring system
2. SQLite database for storing metrics (logger/reports/metrics.db)
3. Automatic tracking of:
   - Function call counts
   - Execution time (average, min, max)
   - Errors with types

FILES CREATED:
--------------
- logger/models.py           - Database models
- logger/exporter.py         - SQLite exporter
- test_metrics.py            - Test script
- view_metrics.py            - View all metrics
- analyze_metrics.py         - Analyze specific functions
- show_database_metrics.py   - View database.py functions
- check_db.py                - Database structure checker

FILES MODIFIED:
---------------
- logger/tracer.py (renamed from t.py) - OpenTelemetry setup with @trace decorator
- database/database.py       - Added @trace to 32 methods
- requirements.txt           - Added opentelemetry dependencies
- bot/llm.py, bot/testing.py, bot/theory.py, bot/chat.py, bot/prompt_loader.py - Updated decorators

================================================================================
                          HOW TO USE
================================================================================

1. TESTING THE SYSTEM:
   
   python test_metrics.py
   
   This will:
   - Call test functions 10, 5, and 3 times
   - Generate errors
   - Export metrics to database

2. VIEWING ALL METRICS:
   
   python view_metrics.py
   
   Shows:
   - All metrics in database
   - Function call counts
   - Function statistics
   - Errors

3. VIEWING DATABASE.PY METRICS:
   
   python show_database_metrics.py
   
   Shows metrics for all monitored database.py functions

4. ANALYZING SPECIFIC FUNCTION:
   
   python analyze_metrics.py
   
   Shows detailed analysis of each monitored function

5. CHECKING DATABASE STRUCTURE:
   
   python check_db.py
   
   Shows database tables and record counts

================================================================================
                          HOW IT WORKS
================================================================================

1. AUTOMATIC MONITORING:
   - All functions with @trace decorator are monitored
   - Metrics collected in memory (OpenTelemetry)
   - Exported to SQLite every 60 seconds
   - Execution time rounded to 4 decimal places
   - Minimal performance impact

2. DATA STORAGE:
   - Database: logger/reports/metrics.db
   - Table: function_metrics (no ID column - composite primary key)
   - Columns: function (full path), metric_type, timestamp (composite PK),
              calls, avg_time, total_time, min_time, max_time,
              errors, error_type
   - Function format: folder.module.function (e.g., database.database.register_user)

3. METRIC TYPES:
   - call - Number of function calls
   - time - Execution time statistics (avg, min, max, total)
   - error - Error counts with error type

================================================================================
                          MONITORED FUNCTIONS
================================================================================

The following database.py functions are monitored:
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
                          SQL QUERIES EXAMPLES
================================================================================

1. Get total calls for a function:

   SELECT SUM(calls) 
   FROM function_metrics 
   WHERE metric_type = 'call' AND function = 'database.database.register_user';

2. Get average execution time:

   SELECT AVG(avg_time), MIN(min_time), MAX(max_time)
   FROM function_metrics 
   WHERE metric_type = 'time' AND function = 'database.database.register_user';

3. Get all errors:

   SELECT function, error_type, SUM(errors) as total_errors
   FROM function_metrics 
   WHERE metric_type = 'error'
   GROUP BY function, error_type
   ORDER BY total_errors DESC;

4. Get slowest functions:

   SELECT function, AVG(avg_time) as avg_time, MAX(max_time) as max_time
   FROM function_metrics 
   WHERE metric_type = 'time' AND avg_time > 0
   GROUP BY function
   ORDER BY avg_time DESC
   LIMIT 10;

================================================================================
                          NOTES
================================================================================

1. Metrics are exported every 60 seconds (configurable in logger/tracer.py)
2. To force export immediately: call flush() function
3. Database grows slowly (only aggregated data per minute)
4. Execution times are rounded to 4 decimal places
5. No ID column - uses composite primary key (function, metric_type, timestamp)
6. Function names include full path: folder.module.function
7. Migration script available: migrate_metrics_db.py

================================================================================
                          TROUBLESHOOTING
================================================================================

If metrics not appearing:
1. Check that opentelemetry is installed:
   pip list | grep opentelemetry
   
2. Check database exists:
   python check_db.py
   
3. Run test to verify system:
   python test_metrics.py
   
4. Check for errors in console output

================================================================================

