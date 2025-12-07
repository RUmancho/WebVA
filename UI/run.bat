@echo off
echo ========================================
echo Запуск Flask приложения
echo ========================================
echo.

cd /d "%~dp0"

REM Получаем локальный IP-адрес
echo Определение IP-адреса...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set LOCAL_IP=%%a
    goto :found_ip
)
:found_ip
set LOCAL_IP=%LOCAL_IP:~1%

echo.
echo ========================================
echo Приложение будет доступно по адресам:
echo ========================================
echo   Локально:  http://localhost:5000
echo   Локально:  http://127.0.0.1:5000
if defined LOCAL_IP (
    echo   В сети:    http://%LOCAL_IP%:5000
) else (
    echo   В сети:    http://<ваш-IP>:5000
)
echo.
echo ========================================
echo ВАЖНО: НЕ используйте http://0.0.0.0:5000
echo        0.0.0.0 - это служебный адрес!
echo ========================================
echo.
echo Запуск сервера...
echo Для остановки нажмите Ctrl+C
echo.

python.exe app.py

pause

