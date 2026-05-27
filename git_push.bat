@echo off
cd /d C:\CRM_Adorno
del .git\index.lock 2>nul
git config user.email "claudiaadornosrl@gmail.com"
git config user.name "Claudia Adorno"
git add index.html
git commit -m "feat: mostrar sku_resuelto en pedidos y alertas"
git push
echo.
echo Listo! Presiona cualquier tecla para cerrar.
pause
