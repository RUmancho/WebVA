@echo off
echo ========================================
echo Компиляция DLL с максимальной оптимизацией
echo ========================================
echo.

REM Проверка наличия компилятора
where g++ >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА: g++ не найден в PATH!
    echo Установите MinGW или добавьте его в PATH
    pause
    exit /b 1
)

echo Проверка компилятора...
g++ --version
echo.

REM Флаги для максимальной оптимизации и минимального размера
REM -Os: оптимизация по размеру (вместо -O3 для скорости)
REM -flto: link-time optimization
REM -ffunction-sections -fdata-sections: разделение функций и данных для лучшей оптимизации
REM -Wl,--gc-sections: удаление неиспользуемых секций
REM -Wl,--strip-all: удаление всех символов
REM -s: удаление отладочной информации
REM -fno-exceptions -fno-rtti: отключение исключений и RTTI для уменьшения размера
REM -fvisibility=hidden: скрытие символов по умолчанию
REM -march=native: оптимизация под текущий процессор
REM -mtune=native: настройка под текущий процессор

set OPTIMIZE_FLAGS=-shared -Os -flto -ffunction-sections -fdata-sections -fstack-protector-strong -D_FORTIFY_SOURCE=2 -Wall -Wextra -fno-exceptions -fno-rtti -fvisibility=hidden -march=native -mtune=native -Wl,--gc-sections -Wl,--strip-all -s -static-libgcc -static-libstdc++

echo Компиляция algebra.dll...
g++ %OPTIMIZE_FLAGS% algebra.cpp -o algebra.dll
if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА при компиляции algebra.dll!
    pause
    exit /b 1
)
if exist algebra.dll (
    for %%A in (algebra.dll) do echo   Размер: %%~zA байт
) else (
    echo ОШИБКА: algebra.dll не создан!
    pause
    exit /b 1
)

echo.
echo Компиляция geometry.dll...
g++ %OPTIMIZE_FLAGS% geometry.cpp -o geometry.dll
if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА при компиляции geometry.dll!
    pause
    exit /b 1
)
if exist geometry.dll (
    for %%A in (geometry.dll) do echo   Размер: %%~zA байт
) else (
    echo ОШИБКА: geometry.dll не создан!
    pause
    exit /b 1
)

echo.
echo Компиляция physics.dll...
g++ %OPTIMIZE_FLAGS% physics.cpp -o physics.dll
if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА при компиляции physics.dll!
    pause
    exit /b 1
)
if exist physics.dll (
    for %%A in (physics.dll) do echo   Размер: %%~zA байт
) else (
    echo ОШИБКА: physics.dll не создан!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Компиляция завершена успешно!
echo ========================================
echo.
echo Созданные DLL файлы:
dir *.dll /b
echo.
pause

