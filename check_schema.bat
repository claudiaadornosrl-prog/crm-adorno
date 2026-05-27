@echo off
python -c "
import requests, json
url = 'https://kwwiykssrpabncpqtmwi.supabase.co/rest/v1/pedidos'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3d2l5a3NzcnBhYm5jcHF0bXdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzNjI1NTQsImV4cCI6MjA5NDkzODU1NH0.O1VhKdjPahnJJ9qXcQuSKQbnKGhsEZqYmjDEfRuRpkc'
h = {'apikey': key, 'Authorization': 'Bearer '+key, 'Prefer': 'return=representation'}
r = requests.get(url, headers=h, params={'limit':'1','select':'*'})
rows = r.json()
if rows: print('COLUMNAS:', list(rows[0].keys())); print('EJEMPLO:', json.dumps(rows[0], indent=2, default=str))
else: print('Sin filas. Status:', r.status_code, r.text[:200])
"
pause
