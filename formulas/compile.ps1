# Компиляция DLL с максимальной оптимизацией для PowerShell
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Компиляция DLL с максимальной оптимизацией" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка наличия компилятора
$gpp = Get-Command g++ -ErrorAction SilentlyContinue
if (-not $gpp) {
    Write-Host "ОШИБКА: g++ не найден в PATH!" -ForegroundColor Red
    Write-Host "Установите MinGW или добавьте его в PATH" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "Проверка компилятора..." -ForegroundColor Yellow
g++ --version
Write-Host ""

# Флаги для максимальной оптимизации и минимального размера
# -Os: оптимизация по размеру (меньше чем -O3, но лучше для размера)
# -flto: link-time optimization
# -ffunction-sections -fdata-sections: разделение функций и данных
# -Wl,--gc-sections: удаление неиспользуемых секций
# -Wl,--strip-all: удаление всех символов
# -s: удаление отладочной информации
# -fno-exceptions -fno-rtti: отключение исключений и RTTI
# -fvisibility=hidden: скрытие символов по умолчанию
# -march=native: оптимизация под текущий процессор
# -static-libgcc -static-libstdc++: статическая линковка для уменьшения зависимостей

$OPTIMIZE_FLAGS = @(
    "-shared", "-Os", "-flto",
    "-ffunction-sections", "-fdata-sections",
    "-fstack-protector-strong", "-D_FORTIFY_SOURCE=2",
    "-Wall", "-Wextra",
    "-fno-exceptions", "-fno-rtti",
    "-fvisibility=hidden",
    "-march=native", "-mtune=native",
    "-Wl,--gc-sections", "-Wl,--strip-all",
    "-s", "-static-libgcc", "-static-libstdc++"
)

$dllFiles = @("algebra", "geometry", "physics")

foreach ($dll in $dllFiles) {
    Write-Host "Компиляция ${dll}.dll..." -ForegroundColor Yellow
    & g++ $OPTIMIZE_FLAGS "${dll}.cpp" -o "${dll}.dll"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ОШИБКА при компиляции ${dll}.dll!" -ForegroundColor Red
        Read-Host "Нажмите Enter для выхода"
        exit 1
    }
    
    if (Test-Path "${dll}.dll") {
        $size = (Get-Item "${dll}.dll").Length
        Write-Host "  ✓ Размер: $size байт" -ForegroundColor Green
    } else {
        Write-Host "ОШИБКА: ${dll}.dll не создан!" -ForegroundColor Red
        Read-Host "Нажмите Enter для выхода"
        exit 1
    }
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Компиляция завершена успешно!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Созданные DLL файлы:" -ForegroundColor Yellow
Get-ChildItem *.dll | ForEach-Object {
    $size = $_.Length
    Write-Host "  $($_.Name): $size байт" -ForegroundColor Cyan
}
Write-Host ""
Read-Host "Нажмите Enter для выхода"

