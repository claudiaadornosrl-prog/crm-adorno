"""
test_znube_login.py  —  verifica login + paginación ZNube
Ejecutar: python C:\CRM_Adorno\test_znube_login.py
"""
import requests, re, sys
from bs4 import BeautifulSoup

ZNUBE_TOKEN    = "ee086f9b-6b7c-4e40-80a1-456679fb55d2"
ZNUBE_STOCK_URL = "https://www.znube.com.ar/Omnichannel/OnlineReportPartial"
ZNUBE_USER     = "juansimonelli@claudiaadorno.com"
ZNUBE_PASS     = "lola2205"

def _parse_float_es(text):
    if not text: return 0.0
    try: return float(str(text).strip().replace(".", "").replace(",", "."))
    except: return 0.0

print("="*60)
print("TEST 1: Login en ZNube")
print("="*60)
session = requests.Session()
session.headers.update({
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
    "Referer":         "https://www.znube.com.ar/",
})
resp = session.post("https://www.znube.com.ar/Account/LogOn", data={
    "UserName": ZNUBE_USER, "Password": ZNUBE_PASS,
    "RememberMeString": "true", "recaptchaResponse": "",
    "returnUrl": "/", "returnDomain": "www.znube.com.ar",
}, timeout=30, allow_redirects=True)
print(f"  HTTP {resp.status_code} | URL final: {resp.url}")
if "/Account/LogOn" in resp.url:
    print("  [FAIL] Login rechazado — credenciales incorrectas")
    sys.exit(1)
print("  [OK] Login exitoso")

print()
print("="*60)
print("TEST 2: Página 0 (GET)")
print("="*60)
base_url = f"{ZNUBE_STOCK_URL}?appToken={ZNUBE_TOKEN}"
r0 = session.get(base_url, timeout=45)
html0 = r0.text
print(f"  HTTP {r0.status_code} | {len(html0):,} chars")

# Detectar total páginas
pn  = [int(x) for x in re.findall(r"['\"]PN(\d+)['\"]", html0)]
pbn = [int(x) for x in re.findall(r"['\"]PBN(\d+)['\"]", html0)]
if pn:
    print(f"  Pager PN: max={max(pn)}  → total_pages={max(pn)+1}")
elif pbn:
    print(f"  Pager PBN: max={max(pbn)}  → total_pages={max(pbn)+1}")
else:
    print("  [WARN] No se detectó pager — total_pages desconocido")

# Parsear filas
soup = BeautifulSoup(html0, "html.parser")
rows = [tr for tr in soup.find_all("tr")
        if tr.find_all("td") and tr.find_all("td")[0].get_text(strip=True).endswith("##")]
print(f"  Filas de datos (##): {len(rows)}")
if rows:
    tds = [td.get_text(strip=True) for td in rows[0].find_all("td")]
    sku = tds[0][:-2].strip()
    alco = _parse_float_es(tds[7]) if len(tds) > 7 else "N/A"
    uni  = _parse_float_es(tds[9]) if len(tds) > 9 else "N/A"
    print(f"  Primera fila — SKU={sku}, Alcorta={alco}, Unicenter={uni}")
    print(f"  Columnas totales: {len(tds)}")
    print(f"  Todas las columnas: {tds}")

print()
print("="*60)
print("TEST 3: Página 1 (POST PN1)")
print("="*60)
r1 = session.post(base_url, data={
    "__CALLBACKID": "gridView", "__CALLBACKPARAM": "PN1"
}, headers={
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Requested-With": "XMLHttpRequest",
}, timeout=45)
html1 = r1.text
print(f"  HTTP {r1.status_code} | {len(html1):,} chars")
soup1 = BeautifulSoup(html1, "html.parser")
rows1 = [tr for tr in soup1.find_all("tr")
         if tr.find_all("td") and tr.find_all("td")[0].get_text(strip=True).endswith("##")]
print(f"  Filas de datos (##): {len(rows1)}")
if rows1:
    tds1 = [td.get_text(strip=True) for td in rows1[0].find_all("td")]
    sku1 = tds1[0][:-2].strip()
    alco1 = _parse_float_es(tds1[7]) if len(tds1) > 7 else "N/A"
    uni1  = _parse_float_es(tds1[9]) if len(tds1) > 9 else "N/A"
    print(f"  Primera fila — SKU={sku1}, Alcorta={alco1}, Unicenter={uni1}")

print()
print("="*60)
if rows and rows1:
    print("[SUCCESS] ZNube login + paginación funcionando correctamente")
else:
    print("[FAIL] Ver detalles arriba")
print("="*60)
input("\nPresioná Enter para cerrar...")
