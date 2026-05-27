@echo off
echo === Installing required packages ===
pip install pywin32 pycryptodome requests beautifulsoup4 -q 2>&1
echo === Running ZNube cookie test ===
python "C:\Users\Usuario\AppData\Roaming\Claude\local-agent-mode-sessions\6a2423f3-4b2e-4c8e-9c2d-70f007f97568\8ad96112-164d-4e02-bfc9-bcecad85b7c5\local_4a504643-3f3a-4f30-875a-09e1059c8a11\outputs\test_znube_cookies.py" 2>&1
pause
