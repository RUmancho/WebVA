Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Запуск Flask приложения" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Переход в директорию скрипта
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Получение локального IP-адреса
Write-Host "Определение IP-адреса..." -ForegroundColor Yellow
try {
    $localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*"} | Select-Object -First 1).IPAddress
} catch {
    $localIP = $null
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Приложение будет доступно по адресам:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Локально:  http://localhost:5000" -ForegroundColor Green
Write-Host "  Локально:  http://127.0.0.1:5000" -ForegroundColor Green
if ($localIP) {
    Write-Host "  В сети:    http://$localIP:5000" -ForegroundColor Green
} else {
    Write-Host "  В сети:    http://<ваш-IP>:5000" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ВАЖНО: НЕ используйте http://0.0.0.0:5000" -ForegroundColor Red
Write-Host "       0.0.0.0 - это служебный адрес!" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Запуск сервера..." -ForegroundColor Yellow
Write-Host "Для остановки нажмите Ctrl+C" -ForegroundColor Yellow
Write-Host ""

python.exe app.py

Read-Host "Нажмите Enter для выхода"

