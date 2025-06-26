::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAjk
::fBw5plQjdCyDJGyX8VAjFDEadgWMOWe2B4k47fvw++WXnmguZMowdYr8752LIfMK1kT3ZpM5xUZTm8QCMB5LbhqkYwozvGdHt3ecec6fvG8=
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSzk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSDk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+JeA==
::cxY6rQJ7JhzQF1fEqQJQ
::ZQ05rAF9IBncCkqN+0xwdVs0
::ZQ05rAF9IAHYFVzEqQJQ
::eg0/rx1wNQPfEVWB+kM9LVsJDGQ=
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWDk=
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATElA==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdCyDJGyX8VAjFDEadgWMOWe2B4k47fvw++WXnkgOROowdYrcz72LIfMKpED8cPY=
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off
cd /d "%~dp0"

:: Percorso file di log in APPDATA
set LOGDIR=%APPDATA%\ESPHomeGUIeasy
set LOGFILE=%LOGDIR%\esphomeguieasy_log.txt

:: Crea la cartella log se non esiste
if not exist "%LOGDIR%" (
    mkdir "%LOGDIR%"
)

:: Intestazione log
echo ------------------------------------------ > "%LOGFILE%"
echo AVVIO ESPHomeGUIeasy - %DATE% %TIME% >> "%LOGFILE%"
echo Cartella corrente: %CD% >> "%LOGFILE%"
echo Utente: %USERNAME% >> "%LOGFILE%"
echo ------------------------------------------ >> "%LOGFILE%"

:: Controllo file Python
if not exist "python\ESPHomeRunner.exe" (
    echo ❌ ERRORE: ESPHomeRunner.exe non trovato. >> "%LOGFILE%"
    echo ESPHomeRunner.exe mancante nella sottocartella 'python\'. >> "%LOGFILE%"
    echo ESPHomeRunner.exe mancante nella sottocartella 'python\'.
    pause
    exit /b 1
)

:: Controllo file main.py
if not exist "main.py" (
    echo ❌ ERRORE: main.py non trovato. >> "%LOGFILE%"
    echo main.py mancante nella cartella corrente. >> "%LOGFILE%"
    echo main.py mancante nella cartella corrente.
    pause
    exit /b 1
)

:: Avvio del programma
python\ESPHomeRunner.exe main.py >> "%LOGFILE%" 2>&1

:: Verifica errori di esecuzione
if errorlevel 1 (
    echo ❌ Errore durante l'esecuzione. >> "%LOGFILE%"
    echo Errore durante l'esecuzione. Controlla il file di log in %LOGFILE%
    pause
)
