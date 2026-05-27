"""
Test script: read Chrome cookies for znube.com.ar and make authenticated request.
Run from Windows PowerShell: python C:/CRM_Adorno/test_znube_cookies.py
"""
import sys
import os
import json
import sqlite3
import tempfile
import base64
import ctypes
import ctypes.wintypes

TOKEN = "ee086f9b-6b7c-4e40-80a1-456679fb55d2"
URL   = f"https://www.znube.com.ar/Omnichannel/OnlineReportPartial?appToken={TOKEN}"

# ── Step 1: check required packages ──────────────────────────────────────────
missing = []
for pkg in ['win32crypt', 'Crypto', 'requests', 'bs4']:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print(f"Missing packages: {missing}")
    print("Run: pip install pywin32 pycryptodome requests beautifulsoup4")
    sys.exit(1)

import win32crypt
from Crypto.Cipher import AES
import requests
from bs4 import BeautifulSoup

# ── Step 2: get Chrome AES key from Local State ───────────────────────────────
local_state_path = os.path.join(
    os.environ.get('LOCALAPPDATA', ''),
    r'Google\Chrome\User Data\Local State'
)
with open(local_state_path, 'r', encoding='utf-8') as f:
    local_state = json.load(f)

enc_key_b64 = local_state['os_crypt']['encrypted_key']
enc_key = base64.b64decode(enc_key_b64)[5:]   # strip "DPAPI" prefix
aes_key = win32crypt.CryptUnprotectData(enc_key, None, None, None, 0)[1]
print(f"[OK] AES key decrypted ({len(aes_key)} bytes)")

# ── Step 3: copy & query the Cookies SQLite file ─────────────────────────────
cookie_db = os.path.join(
    os.environ.get('LOCALAPPDATA', ''),
    r'Google\Chrome\User Data\Default\Network\Cookies'
)
print(f"[OK] Cookie DB: {cookie_db}")
print(f"[OK] Exists: {os.path.exists(cookie_db)}")

# Use CreateFileW with all share flags to bypass Chrome's exclusive lock
GENERIC_READ           = 0x80000000
FILE_SHARE_READ        = 0x00000001
FILE_SHARE_WRITE       = 0x00000002
FILE_SHARE_DELETE      = 0x00000004
OPEN_EXISTING          = 3
FILE_ATTRIBUTE_NORMAL  = 0x00000080
INVALID_HANDLE_VALUE   = ctypes.wintypes.HANDLE(-1).value

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
kernel32.CreateFileW.restype  = ctypes.wintypes.HANDLE
kernel32.CreateFileW.argtypes = [
    ctypes.c_wchar_p,           # lpFileName
    ctypes.wintypes.DWORD,      # dwDesiredAccess
    ctypes.wintypes.DWORD,      # dwShareMode
    ctypes.c_void_p,            # lpSecurityAttributes
    ctypes.wintypes.DWORD,      # dwCreationDisposition
    ctypes.wintypes.DWORD,      # dwFlagsAndAttributes
    ctypes.wintypes.HANDLE,     # hTemplateFile
]

h = kernel32.CreateFileW(
    cookie_db,
    GENERIC_READ,
    FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
    None,
    OPEN_EXISTING,
    FILE_ATTRIBUTE_NORMAL,
    None,
)

if h == INVALID_HANDLE_VALUE or h == 0xFFFFFFFF:
    err = ctypes.get_last_error()
    raise PermissionError(f"CreateFileW failed: WinError {err}")

print(f"[OK] CreateFileW handle: {h}")

# Get file size
size_hi = ctypes.wintypes.DWORD(0)
size_lo = kernel32.GetFileSize(h, ctypes.byref(size_hi))
total_size = (size_hi.value << 32) | size_lo
print(f"[OK] Cookie DB size: {total_size} bytes")

# Read entire file
buf        = ctypes.create_string_buffer(total_size)
bytes_read = ctypes.wintypes.DWORD(0)
ok = kernel32.ReadFile(h, buf, total_size, ctypes.byref(bytes_read), None)
kernel32.CloseHandle(h)
data = buf.raw[:bytes_read.value]
print(f"[OK] Read {bytes_read.value} bytes from Cookies DB")

tmp = tempfile.mktemp(suffix='.db')
with open(tmp, 'wb') as dst:
    dst.write(data)

conn = sqlite3.connect(tmp)
cur  = conn.cursor()
cur.execute(
    "SELECT name, encrypted_value FROM cookies WHERE host_key LIKE '%znube%'"
)
rows = cur.fetchall()
conn.close()
os.unlink(tmp)
print(f"[OK] Found {len(rows)} cookie rows for znube.com.ar")

# ── Step 4: decrypt each cookie ───────────────────────────────────────────────
def decrypt(enc_val):
    if enc_val[:3] == b'v10':
        nonce      = enc_val[3:15]
        ciphertext = enc_val[15:-16]
        tag        = enc_val[-16:]
        cipher     = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8', errors='replace')
    else:
        # Old DPAPI path (Chrome < 80)
        return win32crypt.CryptUnprotectData(enc_val, None, None, None, 0)[1].decode('utf-8', errors='replace')

cookies = {}
for name, enc_val in rows:
    try:
        cookies[name] = decrypt(enc_val)
    except Exception as e:
        print(f"  [WARN] could not decrypt '{name}': {e}")

print(f"[OK] Decrypted cookies: {list(cookies.keys())}")

# ── Step 5: make authenticated GET to ZNube ──────────────────────────────────
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
    'Referer': 'https://www.znube.com.ar/',
}
resp = requests.get(URL, cookies=cookies, headers=headers, timeout=30)
print(f"[OK] Response: {resp.status_code}, {len(resp.text)} chars")

# ── Step 6: parse response ────────────────────────────────────────────────────
soup = BeautifulSoup(resp.text, 'html.parser')
tr_rows = soup.find_all('tr')
hash_rows = [tr for tr in tr_rows if tr.find('td') and tr.find('td').get_text(strip=True).endswith('##')]
print(f"[OK] Total <tr>: {len(tr_rows)}, data rows (##): {len(hash_rows)}")

if hash_rows:
    # Show first 3 rows
    for tr in hash_rows[:3]:
        tds = tr.find_all('td')
        texts = [td.get_text(strip=True) for td in tds]
        print(f"  SKU: {texts[0]}, Alcorta: {texts[7] if len(texts)>7 else '?'}, Unicenter: {texts[9] if len(texts)>9 else '?'}")
    print(f"\n[SUCCESS] Cookie approach works! {len(hash_rows)} rows found.")
else:
    print(f"\n[FAIL] Still got spinner HTML. Raw start:\n{resp.text[:500]}")
