@echo off
echo Adding firewall rule for Ehreezoh Backend...
netsh advfirewall firewall add rule name="Ehreezoh Backend" dir=in action=allow protocol=TCP localport=8000
if %errorlevel% neq 0 (
    echo Failed to add firewall rule. Please run this script as Administrator.
    pause
    exit /b 1
)
echo Firewall rule added successfully.
pause
