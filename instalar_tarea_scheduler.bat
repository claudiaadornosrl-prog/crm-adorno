@echo off
echo Instalando tarea programada "CRM_Adorno_SyncStock"...
echo.

schtasks /create ^
  /tn "CRM_Adorno_SyncStock" ^
  /tr "python C:\CRM_Adorno\sync_dragonfish.py --modo todo" ^
  /sc minute ^
  /mo 15 ^
  /ru "%USERDOMAIN%\%USERNAME%" ^
  /it ^
  /f

if %ERRORLEVEL% == 0 (
    echo.
    echo [OK] Tarea creada exitosamente.
    echo      Nombre:    CRM_Adorno_SyncStock
    echo      Comando:   python C:\CRM_Adorno\sync_dragonfish.py --modo todo
    echo      Frecuencia: cada 15 minutos
    echo      Usuario:   %USERDOMAIN%\%USERNAME%
    echo.
    echo Para verificar: abri el Programador de tareas de Windows
    echo y busca "CRM_Adorno_SyncStock" en la lista.
) else (
    echo.
    echo [ERROR] No se pudo crear la tarea. Intenta ejecutar este .bat
    echo         como Administrador (clic derecho ^> Ejecutar como administrador).
)

echo.
pause
