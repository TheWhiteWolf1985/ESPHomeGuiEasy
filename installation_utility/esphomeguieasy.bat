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
::Zh4grVQjdCyDJGyX8VAjFDEadgWMOWe2B4k47fvw++WXnmguZMowdYr8752LIfMK1kzqZoIs2nZbjMIDAiRNahunZxstlWtRpmyKOsKbpgbkS1uQqE4oHgU=
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off
cd /d "%~dp0"

:: Log file
echo Avvio ESPHomeGUIeasy... > "%TEMP%\esphomeguieasy_log.txt"

:: Lancia il programma usando il Python nel venv
venv\Scripts\python.exe main.py >> "%TEMP%\esphomeguieasy_log.txt" 2>&1

:: Se c'è stato errore, mostra messaggio
if errorlevel 1 (
    echo Errore durante l'esecuzione. Controlla il file di log in %TEMP%\esphomeguieasy_log.txt
    pause
)

