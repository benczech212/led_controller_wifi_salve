::@echo off
setlocal

taskkill /F /IM putty.exe
cd C:\"Program Files"\PuTTY\
C:\"Program Files"\PuTTY\putty.exe -load "Metro M4 AirLift"
pause
endlocal
exit /B