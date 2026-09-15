@echo off
chcp 65001 > nul
title Сборка W11LatencyFixer в EXE...

echo ==============================================
echo 1. Проверка и обновление зависимостей...
echo ==============================================
pip install --upgrade pyinstaller customtkinter psutil

echo.
echo ==============================================
echo 2. Запуск компиляции PyInstaller...
echo ==============================================
:: --clean гарантирует пересборку без использования старого кэша
pyinstaller --clean ^
            --icon=w11fix.ico ^
            --noconsole ^
            --onefile ^
            --uac-admin ^
            --collect-all customtkinter ^
            --name "W11LatencyFixer" ^
            W11LatencyFixer.py

echo.
if %errorlevel% equ 0 (
    echo ==============================================
    echo [УСПЕХ] Сборка завершена!
    echo Исполняемый файл: dist\W11LatencyFixer.exe
    echo ==============================================
) else (
    echo ==============================================
    echo [ОШИБКА] Произошел сбой при компиляции!
    echo Проверьте текст ошибки выше.
    echo ==============================================
)

pause