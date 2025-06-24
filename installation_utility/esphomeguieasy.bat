@echo off
cd /d "%~dp0"

:: Log file
echo Avvio ESPHomeGUIeasy... > "%TEMP%\esphomeguieasy_log.txt"

:: Lancia il programma usando il Python embedded rinominato
python\ESPHomeRunner.exe main.py >> "%TEMP%\esphomeguieasy_log.txt" 2>&1

:: Se c'è stato errore, mostra messaggio
if errorlevel 1 (
    echo Errore durante l'esecuzione. Controlla il file di log in %TEMP%\esphomeguieasy_log.txt
    pause
)
