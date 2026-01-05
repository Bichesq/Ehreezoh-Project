New-NetFirewallRule -DisplayName "Allow Port 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
Write-Host "Firewall rule successfully added for Port 8000."
pause
