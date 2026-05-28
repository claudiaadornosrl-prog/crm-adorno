@echo off
echo Instalando tarea programada "CRM_Adorno_SyncEncuestas"...
echo.

schtasks /create ^
  /tn "CRM_Adorno_SyncEncuestas" ^
  /tr "python C:\CRM_Adorno\rrhh-adorno\sync_anviz\sync_encuestas.py --aplicar" ^
  /sc daily ^
  /mo 2 ^
  /st 08:00 ^
  /ru "%USERDOMAIN%\%USERNAME%" ^
  /it ^
  /f

if %ERRORLEVEL% == 0 (
    echo.
    echo [OK] Tarea creada exitosamente.
    echo      Nombre:     CRM_Adorno_SyncEncuestas
    echo      Comando:    python ...\sync_anviz\sync_encuestas.py --aplicar
    echo      Frecuencia: cada 2 dias (48 hs) a las 08:00
    echo      Usuario:    %USERDOMAIN%\%USERNAME%
    echo.
    echo Corre solo mientras la PC este encendida.
    echo Para verificar: abri el Programador de tareas de Windows
    echo y busca "CRM_Adorno_SyncEncuestas" en la lista.
) else (
    echo.
    echo [ERROR] No se pudo crear la tarea. Ejecuta este .bat
    echo         como Administrador ^(clic derecho ^> Ejecutar como administrador^).
)

echo.
pause
