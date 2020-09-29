::Deploys the code.py file when changes happen to the source file
::
@echo off
setlocal

xcopy /y /c /i /v /s /e "E:\Dev\CirciutPython\projects\LED Controller WiFi Slave\led_controller_wifi_salve\src" "H:\"
taskkill /F /IM "putty.exe"
::taskkill /F /IM "cmd.exe"
start E:\Dev\CirciutPython\projects\"LED Controller WiFi Slave"\led_controller_wifi_salve\build_scripts\connect_serial.bat

endlocal

