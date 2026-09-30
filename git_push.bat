@echo off
cd /d C:\CRM_Adorno
del .git\index.lock 2>nul
git config user.email "claudiaadornosrl@gmail.com"
git config user.name "Claudia Adorno"
REM Solo sube cambios de archivos YA publicados (index, manual, SW, manifest, iconos, fuentes).
REM "git add -u" nunca agrega archivos nuevos: el repo es publico.
git add -u
git commit -m "update %date% %time:~0,5%"
git push
echo.
echo Listo! Presiona cualquier tecla para cerrar.
pause
