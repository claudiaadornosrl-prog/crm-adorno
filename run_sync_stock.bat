@echo off
cd /d C:\CRM_Adorno
echo === Ejecutando sync_dragonfish.py --modo stock ===
python sync_dragonfish.py --modo stock
echo.
echo === Listo ===
pause
