@echo off
schtasks /create /tn "CRM_Adorno_SyncEncuestas" /tr "python C:\CRM_Adorno\rrhh-adorno\sync_anviz\sync_encuestas.py --aplicar" /sc daily /mo 2 /st 08:00 /ru "%USERDOMAIN%\%USERNAME%" /it /f > C:\CRM_Adorno\_verif_tarea.txt 2>&1
echo ----- QUERY ----- >> C:\CRM_Adorno\_verif_tarea.txt
schtasks /query /tn "CRM_Adorno_SyncEncuestas" /fo LIST /v >> C:\CRM_Adorno\_verif_tarea.txt 2>&1
