"""
sync_dragonfish.py
==================
Script de sincronización Dragon Fish → Supabase CRM
Claudia Adorno — Ejecutar con Windows Task Scheduler cada 15 min

Funciones:
  1. sync_skus()         — lee artículos activos de Dragon Fish y los sube a Supabase
  2. sync_znube_stock()  — consulta stock real desde ZNube y marca pedidos "Listo para avisar"
  3. sync_stock()        — (FALLBACK) detecta ingresos vía MSTOCK si ZNube no está disponible

Requisitos:
  pip install pyodbc requests beautifulsoup4

Configuración:
  Editar la sección CONFIG al inicio del archivo.
"""

import os
import pickle
import pyodbc
import requests
import json
import logging
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from dateutil import parser as dateparser
from concurrent.futures import ThreadPoolExecutor, as_completed

# ══════════════════════════════════════════════════════════════════
#  CONFIG — editar estos valores
# ══════════════════════════════════════════════════════════════════

SUPABASE_URL = "https://kwwiykssrpabncpqtmwi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3d2l5a3NzcnBhYm5jcHF0bXdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzNjI1NTQsImV4cCI6MjA5NDkzODU1NH0.O1VhKdjPahnJJ9qXcQuSKQbnKGhsEZqYmjDEfRuRpkc"

# ZNube: token de acceso para consultar stock online en tiempo real
ZNUBE_TOKEN = "ee086f9b-6b7c-4e40-80a1-456679fb55d2"
ZNUBE_STOCK_URL = "https://www.znube.com.ar/Omnichannel/OnlineReportPartial"
ZNUBE_USER = "juansimonelli@claudiaadorno.com"
ZNUBE_PASS = "lola2205"
ZNUBE_SESSION_PKL = r"C:\CRM_Adorno\znube_session.pkl"

# SQL Server: string de conexión ODBC a la instancia de Dragon Fish en tu PC
SQL_SERVER_CONN = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-CI3MV5J\\ZOOLOGIC2026;"
    "Trusted_Connection=yes;"              # Windows auth
)

# Locales y sus bases de datos Dragon Fish
LOCALES = {
    "unicenter": ["DRAGONFISH_UNI1", "DRAGONFISH_UNI2"],
    "alcorta":   ["DRAGONFISH_ALCO1", "DRAGONFISH_ALCO2"],
}

# Ventana de tiempo para buscar ingresos MSTOCK (solo usado si ZNube falla)
STOCK_LOOKBACK_HOURS = 2

# Logging
LOG_FILE = r"C:\CRM_Adorno\sync_dragonfish.log"
LOG_LEVEL = logging.INFO

# ══════════════════════════════════════════════════════════════════
#  Setup logging
# ══════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
#  Supabase helpers
# ══════════════════════════════════════════════════════════════════

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}


def supa_get(table, params=None):
    """SELECT de Supabase vía REST."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = dict(HEADERS)
    headers["Prefer"] = "return=representation"
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def supa_upsert(table, rows, retries=3):
    """UPSERT batch en Supabase. Con retry exponencial y captura de body en error."""
    if not rows:
        return 0
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = dict(HEADERS)
    headers["Prefer"] = "resolution=merge-duplicates,return=minimal"
    last_err = None
    for attempt in range(retries):
        try:
            resp = requests.post(url, headers=headers, json=rows, timeout=120)
            if resp.ok:
                return len(rows)
            # No-OK: capturar body para logging
            body_snippet = resp.text[:500] if resp.text else "(empty)"
            last_err = f"HTTP {resp.status_code} on {table}: {body_snippet}"
            log.warning(f"  upsert {table} fallo attempt {attempt+1}/{retries}: {last_err}")
            if resp.status_code in (400, 403, 404, 422):
                # Errores no recuperables: abortar
                resp.raise_for_status()
            time.sleep(2 ** attempt)  # 1s, 2s, 4s
        except requests.exceptions.RequestException as e:
            last_err = f"Network error: {e}"
            log.warning(f"  upsert {table} network err attempt {attempt+1}/{retries}: {e}")
            time.sleep(2 ** attempt)
    raise RuntimeError(f"upsert {table} fallido tras {retries} intentos. Último error: {last_err}")


def supa_patch(table, match_params, data):
    """UPDATE filtrado en Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = requests.patch(url, headers=HEADERS, params=match_params, json=data, timeout=30)
    resp.raise_for_status()


def log_sync(tipo, locales, registros, matches, error=None):
    """Registrar ejecución en sync_log."""
    try:
        url = f"{SUPABASE_URL}/rest/v1/sync_log"
        payload = {
            "tipo":       tipo,
            "locales":    locales,
            "registros":  registros,
            "matches":    matches,
            "error":      error,
        }
        requests.post(url, headers=HEADERS, json=payload, timeout=15)
    except Exception as e:
        log.warning(f"No se pudo guardar sync_log: {e}")


# ══════════════════════════════════════════════════════════════════
#  Dragon Fish helpers
# ══════════════════════════════════════════════════════════════════

def get_sql_conn(database):
    """Abrir conexión ODBC a una base de datos específica."""
    conn_str = SQL_SERVER_CONN + f"DATABASE={database};"
    return pyodbc.connect(conn_str, timeout=10)


def df_query(database, sql):
    """Ejecutar una consulta SELECT en Dragon Fish y devolver lista de dicts."""
    conn = get_sql_conn(database)
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        cols = [col[0] for col in cursor.description]
        rows = []
        for row in cursor.fetchall():
            rows.append(dict(zip(cols, row)))
        return rows
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════
#  1. sync_skus — actualiza catálogo de artículos
# ══════════════════════════════════════════════════════════════════

def sync_skus():
    """
    Lee todos los artículos activos de Dragon Fish y los sube a Supabase.
    Se puede correr 1 vez al día (ej: 6:00 AM).
    """
    log.info("=== sync_skus: iniciando ===")
    total_registros = 0
    locales_ok = []
    error_global = None

    for local_id, databases in LOCALES.items():
        skus_local = {}

        for db_name in databases:
            try:
                rows = df_query(db_name, """
                    SELECT
                        RTRIM(ARTCOD) AS sku,
                        RTRIM(ARTDES) AS descripcion
                    FROM ZooLogic.ART
                    WHERE BLOQREG = 0
                      AND IMPORTADO = 0
                """)
                for r in rows:
                    sku = (r.get("sku") or "").strip()
                    if sku:
                        skus_local[sku] = r.get("descripcion", "").strip()
                log.info(f"  {db_name}: {len(rows)} artículos leídos")

            except Exception as e:
                log.warning(f"  {db_name}: error al leer SKUs — {e}")
                continue

        if not skus_local:
            log.warning(f"  {local_id}: sin artículos, saltando")
            continue

        batch = [
            {
                "sku":         sku,
                "descripcion": desc,
                "local_id":    local_id,
                "activo":      True,
            }
            for sku, desc in skus_local.items()
        ]

        batch_size = 500
        for i in range(0, len(batch), batch_size):
            supa_upsert("articulos", batch[i : i + batch_size])

        total_registros += len(batch)
        locales_ok.append(local_id)
        log.info(f"  {local_id}: {len(batch)} artículos sincronizados")

    log_sync("skus", locales_ok, total_registros, 0, error_global)
    log.info(f"=== sync_skus: fin — {total_registros} artículos totales ===")


# ══════════════════════════════════════════════════════════════════
#  2. sync_znube_stock — stock en tiempo real desde ZNube (PRINCIPAL)
# ══════════════════════════════════════════════════════════════════

def _parse_float_es(text):
    """Convierte número en formato español a float. '1.234,00' → 1234.0"""
    if not text:
        return 0.0
    clean = str(text).strip().replace(".", "").replace(",", ".")
    try:
        return float(clean)
    except ValueError:
        return 0.0


def _znube_login(username=None, password=None):
    """
    Autentica en ZNube con credenciales y retorna requests.Session con cookies activas.
    Lanza RuntimeError si las credenciales son incorrectas o el login falla.
    """
    username = username or ZNUBE_USER
    password = password or ZNUBE_PASS
    session = requests.Session()
    session.headers.update({
        "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
        "Referer":         "https://www.znube.com.ar/",
    })
    login_url = "https://www.znube.com.ar/Account/LogOn"
    resp = session.post(login_url, data={
        "UserName":          username,
        "Password":          password,
        "RememberMeString":  "true",
        "recaptchaResponse": "",
        "returnUrl":         "/",
        "returnDomain":      "www.znube.com.ar",
    }, timeout=30, allow_redirects=True)
    resp.raise_for_status()
    # Login exitoso → servidor redirige fuera de /Account/LogOn
    if "/Account/LogOn" in resp.url:
        raise RuntimeError(f"Login ZNube falló — verificar credenciales. URL final: {resp.url}")
    log.info(f"  Login ZNube OK (URL final: {resp.url})")
    return session


def _znube_get_session():
    """
    Devuelve una requests.Session autenticada en ZNube.
    Intenta reutilizar cookies guardadas en ZNUBE_SESSION_PKL.
    Si la sesión expiró o no existe, hace login fresco y guarda las nuevas cookies.
    """
    # Intentar cargar sesión previa
    if os.path.exists(ZNUBE_SESSION_PKL):
        try:
            with open(ZNUBE_SESSION_PKL, "rb") as f:
                saved = pickle.load(f)
            session = requests.Session()
            session.headers.update(saved["headers"])
            session.cookies.update(saved["cookies"])
            # Verificar que la sesión sigue activa
            test_url = f"{ZNUBE_STOCK_URL}?appToken={ZNUBE_TOKEN}"
            resp = session.get(test_url, timeout=20, allow_redirects=True)
            if "/Account/LogOn" not in resp.url and resp.status_code == 200:
                log.info("  Sesión ZNube reutilizada desde caché")
                return session
            log.info("  Sesión ZNube expirada — re-autenticando")
        except Exception as e:
            log.warning(f"  No se pudo cargar sesión ZNube guardada: {e}")

    # Login fresco
    session = _znube_login()

    # Guardar cookies para próxima ejecución
    try:
        with open(ZNUBE_SESSION_PKL, "wb") as f:
            pickle.dump({
                "headers": dict(session.headers),
                "cookies": dict(session.cookies),
            }, f)
        log.info(f"  Sesión ZNube guardada en {ZNUBE_SESSION_PKL}")
    except Exception as e:
        log.warning(f"  No se pudo guardar sesión ZNube: {e}")

    return session


def _fetch_znube_page(session, base_url, page_idx):
    """
    Obtiene una página del grid de ZNube.
      page_idx=0  → GET simple (primera página, HTML completo)
      page_idx>0  → POST callback DevExpress PN{n} (0-indexed)
    El grid ID es siempre 'gridView' (confirmado en producción).
    """
    if page_idx == 0:
        resp = session.get(base_url, timeout=45)
    else:
        resp = session.post(base_url, data={
            "__CALLBACKID":    "gridView",
            "__CALLBACKPARAM": f"PN{page_idx}",
        }, headers={
            "Content-Type":     "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
        }, timeout=45)
    resp.raise_for_status()
    return resp.text


def _parse_znube_html_page(html):
    """
    Parsea una página del HTML de ZNube OnlineReportPartial.

    Columnas fijas (confirmadas en producción):
      Col 0:  {SKU}##   ← clave DevExpress (termina en ##)
      Col 1:  SKU limpio
      Col 2:  Descripción
      Col 7:  Alcorta
      Col 8:  Oficina
      Col 9:  Unicenter
      Col 10: Total

    Retorna (items, total_pages):
      items      = list de dicts {sku, alcorta, unicenter}
      total_pages = int (1 si el pager no es detectable)
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        log.error("BeautifulSoup no instalado. Ejecutar: pip install beautifulsoup4")
        return [], 1

    soup = BeautifulSoup(html, "html.parser")
    items = []
    total_pages = 1

    # ── Detectar total de páginas desde el pager DevExpress ──────────
    # Formato v11+: 'PN{n}' (usado en producción)
    pn_nums = re.findall(r"['\"]PN(\d+)['\"]", html)
    if not pn_nums:
        # Fallback: formato antiguo 'PBN{n}'
        pn_nums = re.findall(r"['\"]PBN(\d+)['\"]", html)
    if pn_nums:
        max_pn = max(int(x) for x in pn_nums)
        total_pages = max_pn + 1  # PN es 0-indexed

    # ── Parsear filas de datos ────────────────────────────────────────
    ALCORTA_IDX   = 7
    UNICENTER_IDX = 9

    for tr in soup.find_all("tr"):
        cells = tr.find_all("td")
        if not cells:
            continue
        texts = [c.get_text(strip=True) for c in cells]

        # DevExpress marca la primera celda de cada fila de datos con "{SKU}##"
        if not texts[0].endswith("##"):
            continue

        sku = texts[0][:-2].strip().upper()
        if not sku:
            continue

        n = len(texts)
        alco = _parse_float_es(texts[ALCORTA_IDX])   if n > ALCORTA_IDX   else 0.0
        uni  = _parse_float_es(texts[UNICENTER_IDX]) if n > UNICENTER_IDX else 0.0

        items.append({"sku": sku, "alcorta": alco, "unicenter": uni})

    return items, total_pages


def sync_znube_stock():
    """
    Consulta stock en tiempo real desde ZNube y actualiza pedidos pendientes.

    Flujo:
    1. Lee pedidos 'Pendiente' con SKU desde Supabase
    2. Autentica en ZNube (reutiliza sesión guardada si es válida)
    3. Descarga todas las páginas de OnlineReportPartial (~385 págs, 10 SKUs c/u)
    4. Construye dict {sku → {alcorta, unicenter}}
    5. Para cada pedido, verifica stock en su local correspondiente
    6. Marca como 'Listo para avisar' si stock > 0

    Requisitos: pip install beautifulsoup4
    """
    log.info("=== sync_znube_stock: iniciando ===")
    total_matches = 0
    error_global = None

    # ── 1. Cargar pedidos pendientes ──────────────────────────────────
    try:
        pedidos_pendientes = supa_get("pedidos", {
            "estado": "eq.Pendiente",
            "sku":    "not.is.null",
            "select": "id,local_id,sku",
        })
        log.info(f"  {len(pedidos_pendientes)} pedidos pendientes con SKU")
    except Exception as e:
        log.error(f"  Error al leer pedidos de Supabase: {e}")
        log_sync("znube_stock", [], 0, 0, str(e))
        return False

    if not pedidos_pendientes:
        log.info("  Sin pedidos pendientes — nada que hacer")
        log_sync("znube_stock", list(LOCALES.keys()), 0, 0, None)
        return True

    # ── 2. Autenticar en ZNube ────────────────────────────────────────
    try:
        session = _znube_get_session()
    except Exception as e:
        log.error(f"  No se pudo autenticar en ZNube: {e}")
        log_sync("znube_stock", [], 0, 0, str(e))
        return False

    # ── 3. Descargar stock desde ZNube ────────────────────────────────
    base_url           = f"{ZNUBE_STOCK_URL}?appToken={ZNUBE_TOKEN}"
    stock_dict         = {}   # sku_upper → {"alcorta": float, "unicenter": float}
    total_pages        = 999  # Valor inicial amplio; se actualiza con la primera respuesta
    page               = 0
    consecutive_errors = 0

    log.info("  Descargando stock de ZNube...")

    while page < total_pages:
        try:
            html = _fetch_znube_page(session, base_url, page)

            items, detected_pages = _parse_znube_html_page(html)

            # Primera página: actualizar total de páginas
            if page == 0:
                if detected_pages > 1:
                    total_pages = detected_pages
                    log.info(f"  Total páginas detectado: {total_pages}")
                else:
                    log.warning("  No se pudo detectar total de páginas — búsqueda exhaustiva hasta página vacía")

            # Acumular stock (primer registro de cada SKU gana)
            for item in items:
                sku = item["sku"]
                if sku not in stock_dict:
                    stock_dict[sku] = {
                        "alcorta":   item["alcorta"],
                        "unicenter": item["unicenter"],
                    }

            # Página vacía → fin real de los datos
            if len(items) == 0:
                log.info(f"  Página {page} sin datos — fin de stock ZNube")
                break

            if page % 50 == 0 or page == total_pages - 1:
                log.info(f"  Página {page}/{total_pages - 1} — {len(stock_dict)} SKUs acumulados")

            consecutive_errors = 0

        except Exception as e:
            consecutive_errors += 1
            log.warning(f"  Error en página {page}: {e}")

            if page == 0:
                log.error("  Error en primera página — abortando sync_znube_stock")
                error_global = str(e)
                log_sync("znube_stock", [], 0, 0, error_global)
                return False

            if consecutive_errors >= 3:
                log.error(f"  {consecutive_errors} errores consecutivos — deteniendo descarga")
                break

        page += 1

    log.info(f"  Stock ZNube cargado: {len(stock_dict)} SKUs únicos")

    if not stock_dict:
        log.error("  No se pudo cargar ningún SKU de ZNube")
        log_sync("znube_stock", [], 0, 0, "stock_dict vacío")
        return False

    # ── 4. Cruzar con pedidos pendientes ──────────────────────────────
    pedidos_idx = {}
    for p in pedidos_pendientes:
        key = (p["local_id"], (p["sku"] or "").strip().upper())
        pedidos_idx.setdefault(key, []).append(p["id"])

    now_iso = datetime.now(timezone.utc).isoformat()
    matched_ids_by_local = {}

    for (local_id, sku), ids in pedidos_idx.items():
        stock_info = stock_dict.get(sku)
        if stock_info is None:
            log.debug(f"  SKU {sku} no encontrado en ZNube")
            continue

        stock_local = stock_info.get(local_id, 0.0)
        if stock_local > 0:
            log.info(f"  ✓ {sku} @ {local_id}: stock={stock_local:.0f} — {len(ids)} pedido(s)")
            matched_ids_by_local.setdefault(local_id, []).extend(ids)

    # ── 5. Marcar pedidos como "Listo para avisar" ────────────────────
    for local_id, ids in matched_ids_by_local.items():
        for pedido_id in ids:
            try:
                supa_patch(
                    "pedidos",
                    {"id": f"eq.{pedido_id}"},
                    {
                        "estado":              "Listo para avisar",
                        "stock_ingreso_fecha": now_iso,
                        "stock_ingreso_local": local_id,
                    },
                )
                total_matches += 1
            except Exception as e:
                log.warning(f"  Error al actualizar pedido {pedido_id}: {e}")

    log_sync("znube_stock", list(LOCALES.keys()), len(stock_dict), total_matches, error_global)
    log.info(f"=== sync_znube_stock: fin — {total_matches} pedidos marcados ===")
    return True


# ══════════════════════════════════════════════════════════════════
#  3. sync_stock — stock vía MSTOCK (Dragon Fish directo, PRINCIPAL)
# ══════════════════════════════════════════════════════════════════

def sync_stock():
    """
    Detecta ingresos de mercadería en Dragon Fish (MSTOCK) y notifica pedidos pendientes.

    Lógica: para cada pedido pendiente, verifica si hubo un ingreso (DIRMOV=1,
    ORIGDEST=ADMIN) del SKU en cuestión en la base del local correspondiente,
    DESDE la fecha en que se creó el pedido.

    Esto elimina la ventana fija de 2hs y es robusto ante cortes del scheduler:
    si el script no corrió por horas/días, igual detecta todos los ingresos
    acumulados desde que cada pedido fue registrado.

    Dragon Fish no registra ventas POS en MSTOCK (solo movimientos de depósito),
    por eso usamos ingresos de mercadería como señal de reposición.
    """
    log.info("=== sync_stock (MSTOCK): iniciando ===")
    total_matches = 0
    locales_ok    = []
    error_global  = None

    # ── 1. Cargar pedidos pendientes con fecha de creación ────────────
    # Intentamos obtener la fecha de creación del pedido (prueba varios nombres de columna)
    pedidos_pendientes = None
    fecha_col = None
    for col_fecha in ("creado_en", "created_at", "fecha_pedido", "fecha"):
        try:
            pedidos_pendientes = supa_get("pedidos", {
                "estado":  "eq.Pendiente",
                "motivo":  "eq.Avisar cuando ingrese",
                "sku":     "not.is.null",
                "select":  f"id,local_id,sku,{col_fecha}",
            })
            fecha_col = col_fecha
            log.info(f"  Columna fecha detectada: '{col_fecha}'")
            break
        except Exception:
            continue

    if pedidos_pendientes is None:
        # Último intento: sin columna de fecha (usaremos fallback de 30 días)
        try:
            pedidos_pendientes = supa_get("pedidos", {
                "estado":  "eq.Pendiente",
                "motivo":  "eq.Avisar cuando ingrese",
                "sku":     "not.is.null",
                "select":  "id,local_id,sku",
            })
            fecha_col = None
            log.warning("  No se encontró columna de fecha — usando fallback 30 días")
        except Exception as e:
            log.error(f"  Error al leer pedidos de Supabase: {e}")
            log_sync("stock_mstock", [], 0, 0, str(e))
            return

    log.info(f"  {len(pedidos_pendientes)} pedidos pendientes con SKU")

    if not pedidos_pendientes:
        log.info("  Sin pedidos pendientes — nada que hacer")
        log_sync("stock_mstock", list(LOCALES.keys()), 0, 0, None)
        return

    # ── 2. Indexar por (local_id, sku_upper) → [{id, desde}] ─────────
    # "desde" = fecha de creación del pedido (punto de corte para MSTOCK)
    fallback_desde = datetime.now(timezone.utc) - timedelta(days=30)
    pedidos_idx = {}  # (local_id, sku) → [{"id": ..., "desde": datetime}]
    for p in pedidos_pendientes:
        sku      = (p.get("sku") or "").strip().upper()
        local_id = p.get("local_id", "")
        if not sku or not local_id:
            continue
        try:
            val_fecha = p.get(fecha_col) if fecha_col else None
            desde_dt  = dateparser.parse(val_fecha) if val_fecha else fallback_desde
        except Exception:
            desde_dt = fallback_desde

        key = (local_id, sku)
        pedidos_idx.setdefault(key, []).append({"id": p["id"], "desde": desde_dt})

    # ── 3. Consultar MSTOCK por local ─────────────────────────────────
    for local_id, databases in LOCALES.items():
        # Filtrar solo los pedidos de este local
        pedidos_local = {
            sku: entries
            for (lid, sku), entries in pedidos_idx.items()
            if lid == local_id
        }
        if not pedidos_local:
            locales_ok.append(local_id)
            continue

        # Fecha más antigua entre los pedidos de este local
        fecha_minima = min(
            e["desde"]
            for entries in pedidos_local.values()
            for e in entries
        )
        # Dragon Fish guarda FECHA en hora local Argentina (UTC-3).
        # Supabase guarda created_at en UTC → restamos 3hs para comparar correctamente.
        ARG_OFFSET = timedelta(hours=3)
        fecha_minima_local = fecha_minima - ARG_OFFSET
        desde_str = fecha_minima_local.strftime("%Y-%m-%d %H:%M:%S")

        # Lista de SKUs a consultar (para acotar la query)
        skus_set    = set(pedidos_local.keys())
        skus_sql    = ",".join(f"'{s}'" for s in skus_set)

        # Ingresos desde la fecha mínima para los SKUs relevantes
        skus_ingresados = {}  # sku_upper → fecha_ingreso más reciente

        for db_name in databases:
            try:
                rows = df_query(db_name, f"""
                    SELECT RTRIM(d.MART) AS sku, MAX(m.FECHA) AS ultima_fecha
                    FROM ZooLogic.MSTOCK m
                    INNER JOIN ZooLogic.DETMSTOCK d ON d.NUMR = m.CODIGO
                    WHERE m.DIRMOV = 1
                      AND ISNULL(m.ANULADO, 0) = 0
                      AND m.FECHA >= '{desde_str}'
                      AND RTRIM(m.ORIGDEST) = 'ADMIN'
                      AND d.MART IS NOT NULL
                      AND RTRIM(d.MART) <> ''
                      AND RTRIM(d.MART) IN ({skus_sql})
                    GROUP BY RTRIM(d.MART)
                """)
                for r in rows:
                    sku = (r.get("sku") or "").strip().upper()
                    if sku:
                        fecha = r.get("ultima_fecha")
                        # Guardar la fecha más reciente entre todas las DBs del local
                        if sku not in skus_ingresados or (fecha and fecha > skus_ingresados[sku]):
                            skus_ingresados[sku] = fecha
                log.info(f"  {db_name}: {len(rows)} SKUs con ingreso desde {desde_str}")

            except Exception as e:
                log.warning(f"  {db_name}: error al leer movimientos — {e}")
                continue

        # ── 4. Cruzar con pedidos: solo marcar si el ingreso fue DESPUÉS ──
        # de la fecha de creación del pedido específico
        now_iso      = datetime.now(timezone.utc).isoformat()
        matched_ids  = []

        for sku, entries in pedidos_local.items():
            fecha_ingreso = skus_ingresados.get(sku)
            if fecha_ingreso is None:
                continue
            # fecha_ingreso viene de Dragon Fish (hora local Argentina, naive).
            # desde_pedido viene de Supabase (UTC). Convertimos desde_pedido a hora
            # local Argentina (UTC-3) para que la comparación sea en la misma zona.
            for entry in entries:
                desde_pedido_utc   = entry["desde"]
                desde_pedido_local = desde_pedido_utc - ARG_OFFSET
                # Asegurar ambos naive para comparar
                if hasattr(desde_pedido_local, 'tzinfo') and desde_pedido_local.tzinfo is not None:
                    desde_pedido_local = desde_pedido_local.replace(tzinfo=None)
                fi = fecha_ingreso if not (hasattr(fecha_ingreso, 'tzinfo') and fecha_ingreso.tzinfo is not None) \
                     else fecha_ingreso.replace(tzinfo=None)

                if fi >= desde_pedido_local:
                    matched_ids.append(entry["id"])
                    log.info(f"  ✓ {sku} @ {local_id}: ingreso {fi.date()} >= pedido {desde_pedido_local.date()}")

        for pedido_id in matched_ids:
            try:
                supa_patch(
                    "pedidos",
                    {"id": f"eq.{pedido_id}"},
                    {
                        "estado":              "Listo para avisar",
                        "stock_ingreso_fecha": now_iso,
                        "stock_ingreso_local": local_id,
                    },
                )
                total_matches += 1
            except Exception as e:
                log.warning(f"  Error al actualizar pedido {pedido_id}: {e}")

        locales_ok.append(local_id)

    log_sync("stock_mstock", locales_ok, 0, total_matches, error_global)
    log.info(f"=== sync_stock (MSTOCK): fin — {total_matches} pedidos marcados ===")




# ══════════════════════════════════════════════════════════════════
#  4. sync_clientes — espejo del maestro de clientes Dragonfish
# ══════════════════════════════════════════════════════════════════

# Mapeo de bases Dragonfish → local_id del CRM
BASE_TO_LOCAL = {
    "DRAGONFISH_UNI1":  "unicenter",
    "DRAGONFISH_UNI2":  "unicenter",
    "DRAGONFISH_ALCO1": "alcorta",
    "DRAGONFISH_ALCO2": "alcorta",
}


def _safe(value):
    """Strip de strings, None si está vacío. Numéricos tal cual."""
    if value is None:
        return None
    if isinstance(value, str):
        s = value.strip()
        return s if s else None
    return value


def _to_iso(dt):
    """Convierte datetime SQL Server a ISO string."""
    if dt is None:
        return None
    if hasattr(dt, "isoformat"):
        return dt.isoformat()
    return str(dt)


def _safe_fecha_nac(dt):
    """Valida que la fecha de nacimiento sea razonable (1920-2015) y devuelve YYYY-MM-DD."""
    if not dt or not hasattr(dt, 'year'):
        return None
    if dt.year < 1920 or dt.year > 2015:
        return None
    return dt.strftime('%Y-%m-%d')


def _clean_cuit(s):
    """Limpia un CUIT/CUIL: deja solo dígitos. None si está vacío o es uno de los placeholders comunes."""
    if not s:
        return None
    c = ''.join(ch for ch in str(s) if ch.isdigit())
    if not c:
        return None
    # Placeholders típicos que aparecen cuando no se identifica al cliente
    PLACEHOLDERS = {'0', '00', '00000000000', '99999999999', '99999999', '999999999', '11111111111', '22222222222'}
    if c in PLACEHOLDERS:
        return None
    return c


def _merge_cliente(existing, new_row, base_origen):
    """Combina datos de un cliente que aparece en múltiples bases. Primer dato no-vacío gana."""
    if existing is None:
        existing = {
            "globalid":          new_row["GLOBALID"].strip() if isinstance(new_row["GLOBALID"], str) else new_row["GLOBALID"],
            "clcod_unicenter":   None, "clcod_alcorta": None,
            "apellido":          None, "nombre": None, "nombre_completo": None,
            "cuit":              None, "dni": None, "tipo_doc": None,
            "email":             None, "telefono": None, "celular": None,
            "direccion":         None, "piso": None, "depto": None,
            "localidad":         None, "provincia": None, "codigo_postal": None, "pais": None,
            "fecha_alta":        None, "fecha_nacimiento": None,
            "vendedora_habitual":None, "sexo": None, "hijos": None, "observaciones": None,
            "estado":            None, "activo": True,
            "locales_presentes": [],
        }

    local_id = BASE_TO_LOCAL.get(base_origen)
    if local_id and local_id not in existing["locales_presentes"]:
        existing["locales_presentes"].append(local_id)

    if local_id == "unicenter" and not existing["clcod_unicenter"]:
        existing["clcod_unicenter"] = _safe(new_row.get("CLCOD"))
    elif local_id == "alcorta" and not existing["clcod_alcorta"]:
        existing["clcod_alcorta"] = _safe(new_row.get("CLCOD"))

    prinom = _safe(new_row.get("CLPRINOM")) or ""
    segnom = _safe(new_row.get("CLSEGNOM")) or ""
    nombre = (prinom + " " + segnom).strip() or None

    candidates = {
        "apellido":          _safe(new_row.get("CLAPELL")),
        "nombre":            nombre,
        "nombre_completo":   _safe(new_row.get("CLNOM")),
        "cuit":              _safe(new_row.get("CLCUIT")),
        "dni":               _safe(new_row.get("CLNRODOC")),
        "tipo_doc":          _safe(new_row.get("CLTIPODOC")),
        "email":             _safe(new_row.get("CLEMAIL")),
        "telefono":          _safe(new_row.get("CLTLF")),
        "celular":           _safe(new_row.get("CLMOVIL")),
        "direccion":         _safe(new_row.get("CLCALLE")),
        "piso":              _safe(new_row.get("CLPISO")),
        "depto":             _safe(new_row.get("CLDEPTO")),
        "localidad":         _safe(new_row.get("CLLOC")),
        "provincia":         _safe(new_row.get("CLPROV")),
        "codigo_postal":     _safe(new_row.get("CLCP")),
        "pais":              _safe(new_row.get("CLPAIS")),
        "fecha_alta":        new_row.get("CLFING"),
        "fecha_nacimiento":  _safe_fecha_nac(new_row.get("CLFECHA")),
        "vendedora_habitual":_safe(new_row.get("CLVEND")),
        "sexo":              _safe(new_row.get("SEXO")),
        "hijos":             int(new_row["HIJOS"]) if new_row.get("HIJOS") is not None else None,
        "observaciones":     _safe(new_row.get("CLOBS")),
        "estado":            _safe(new_row.get("ESTADO")),
        "activo":            not bool(new_row.get("INACTIVOFW")),
    }
    for k, v in candidates.items():
        if (not existing.get(k)) and v is not None:
            existing[k] = v

    return existing


def sync_clientes():
    """Lee CLI de las 4 bases, deduplica por GLOBALID y los upsertea a `clientes`."""
    log.info("=== sync_clientes: iniciando ===")
    error_global = None

    SQL_CLIENTES = """
        SELECT
            RTRIM(GLOBALID) AS GLOBALID, RTRIM(CLCOD) AS CLCOD,
            CLAPELL, CLPRINOM, CLSEGNOM, CLNOM,
            CLCUIT, CLNRODOC, CLTIPODOC,
            CLEMAIL, CLTLF, CLMOVIL,
            CLCALLE, CLPISO, CLDEPTO, CLLOC, CLPROV, CLCP, CLPAIS,
            CLFING, CLFECHA, CLVEND, SEXO, HIJOS, CLOBS, ESTADO, INACTIVOFW
        FROM ZooLogic.CLI
        WHERE GLOBALID IS NOT NULL AND RTRIM(GLOBALID) <> \'\'
    """

    bucket = {}  # globalid → dict mergeado

    for db_name in BASE_TO_LOCAL.keys():
        try:
            rows = df_query(db_name, SQL_CLIENTES)
            log.info(f"  {db_name}: {len(rows)} clientes leídos")
            for r in rows:
                gid = _safe(r.get("GLOBALID"))
                if not gid:
                    continue
                bucket[gid] = _merge_cliente(bucket.get(gid), r, db_name)
        except Exception as e:
            log.warning(f"  {db_name}: error al leer clientes — {e}")
            continue

    log.info(f"  Total clientes únicos (por GLOBALID): {len(bucket)}")

    batch = []
    for c in bucket.values():
        c2 = dict(c)
        c2["fecha_alta"] = _to_iso(c2.get("fecha_alta"))
        batch.append(c2)

    subido = 0
    for i in range(0, len(batch), 500):
        try:
            supa_upsert("clientes", batch[i:i+500])
            subido += len(batch[i:i+500])
            if i % 5000 == 0:
                log.info(f"  Subidos {subido}/{len(batch)}...")
        except Exception as e:
            log.error(f"  Error subiendo bloque {i}-{i+500}: {e}")
            error_global = str(e)
            break

    log.info(f"=== sync_clientes: fin — {subido} clientes en Supabase ===")
    log_sync("clientes", list(BASE_TO_LOCAL.values()), subido, 0, error_global)
    return subido


# ══════════════════════════════════════════════════════════════════
#  5. sync_compras — espejo de comprobantes de venta + detalle
# ══════════════════════════════════════════════════════════════════

def sync_compras(year_lookback=1):
    """Lee comprobantes último(s) año(s) + detalle. Calcula métricas y actualiza clientes."""
    log.info(f"=== sync_compras: iniciando (últimos {year_lookback} año/s) ===")
    error_global = None
    total_cabeceras = 0
    total_detalles  = 0
    fecha_desde = datetime.now() - timedelta(days=year_lookback*365 + 5)
    fecha_desde_str = fecha_desde.strftime("%Y-%m-%d")

    # Solo facturas (FACTTIPO=27). Notas de crédito (28) y remitos (11) no van por ahora.
    SQL_CABECERAS = f"""
        SELECT
            RTRIM(CODIGO) AS CODIGO, RTRIM(RECEPTOR) AS RECEPTOR, FFCH, FLETRA,
            FPTOVEN, FNUMCOMP, FACTTIPO, FVEN, FCUIT, FCLIENTE,
            FTOTAL, FSUBTOT, TOTDESC, TOTIMPUE, TOTALCANT,
            ISNULL(ANULADO, 0) AS ANULADO, FOBS
        FROM ZooLogic.COMPROBANTEV
        WHERE FFCH >= '{fecha_desde_str}'
          AND FACTTIPO = 27
    """

    SQL_DETALLE = f"""
        SELECT
            RTRIM(d.CODIGO) AS CODIGO, d.NROITEM, RTRIM(d.FART) AS FART, d.FTXT,
            d.FCANT, d.FPRECIO, d.FMONTO, d.TALLE, d.CCOLOR
        FROM ZooLogic.COMPROBANTEVDET d
        INNER JOIN ZooLogic.COMPROBANTEV c ON c.CODIGO = d.CODIGO
        WHERE c.FFCH >= '{fecha_desde_str}'
          AND c.FACTTIPO = 27
    """

    SQL_CLI_MAP = """
        SELECT RTRIM(CLCUIT) AS cuit, RTRIM(GLOBALID) AS GLOBALID
        FROM ZooLogic.CLI
        WHERE GLOBALID IS NOT NULL
          AND RTRIM(GLOBALID) <> ''
          AND CLCUIT IS NOT NULL
          AND RTRIM(CLCUIT) <> ''
    """

    # Acumulador de métricas por cliente: globalid → {total, count, max_fecha, min_fecha, locales}
    metricas_por_gid = {}

    for db_name, local_id in BASE_TO_LOCAL.items():
        try:
            mapping_rows = df_query(db_name, SQL_CLI_MAP)
            cuit_to_gid = {}
            for mr in mapping_rows:
                cuit_clean = _clean_cuit(mr.get("cuit"))
                gid_clean = (mr.get("GLOBALID") or "").strip()
                # Solo incluir si AMBOS, CUIT y GLOBALID, son válidos
                if cuit_clean and gid_clean and cuit_clean not in cuit_to_gid:
                    cuit_to_gid[cuit_clean] = gid_clean
            log.info(f"  {db_name}: {len(cuit_to_gid)} CUITs únicos en CLI para matchear")

            cabeceras = df_query(db_name, SQL_CABECERAS)
            log.info(f"  {db_name}: {len(cabeceras)} cabeceras leídas")

            ids_cab = set()
            batch_cab = []
            matched_count = 0
            for r in cabeceras:
                codigo = (r.get("CODIGO") or "").strip()
                if not codigo:
                    continue
                compra_id = f"{db_name}:{codigo}"
                ids_cab.add(compra_id)

                # Matching por CUIT (RECEPTOR está vacío en todas las facturas)
                cuit_factura = _clean_cuit(r.get("FCUIT"))
                gid = cuit_to_gid.get(cuit_factura) if cuit_factura else None
                if gid:
                    matched_count += 1
                # cliente_clcod queda como RECEPTOR (vacío en B2C) o None
                receptor = (r.get("RECEPTOR") or "").strip()
                fecha = r.get("FFCH")
                total = float(r.get("FTOTAL") or 0)
                anulado = bool(r.get("ANULADO"))

                batch_cab.append({
                    "id":               compra_id,
                    "cliente_globalid": gid,
                    "cliente_clcod":    receptor or None,
                    "local_id":         local_id,
                    "base_origen":      db_name,
                    "fecha":            _to_iso(fecha),
                    "letra":            _safe(r.get("FLETRA")),
                    "punto_venta":      int(r.get("FPTOVEN") or 0),
                    "numero":           int(r.get("FNUMCOMP") or 0),
                    "tipo_comprobante": int(r.get("FACTTIPO") or 0),
                    "vendedora":        _safe(r.get("FVEN")),
                    "cuit_factura":     _safe(r.get("FCUIT")),
                    "cliente_factura":  _safe(r.get("FCLIENTE")),
                    "total":            total,
                    "subtotal":         float(r.get("FSUBTOT") or 0),
                    "total_descuento":  float(r.get("TOTDESC") or 0),
                    "total_iva":        float(r.get("TOTIMPUE") or 0),
                    "cantidad_items":   float(r.get("TOTALCANT") or 0),
                    "anulado":          anulado,
                    "observaciones":    _safe(r.get("FOBS")),
                })

                if gid and not anulado and total > 0:
                    m = metricas_por_gid.setdefault(gid, {
                        "total": 0.0, "count": 0,
                        "max_fecha": None, "min_fecha": None,
                        "locales": {},
                    })
                    m["total"] += total
                    m["count"] += 1
                    if fecha:
                        if m["max_fecha"] is None or fecha > m["max_fecha"]:
                            m["max_fecha"] = fecha
                        if m["min_fecha"] is None or fecha < m["min_fecha"]:
                            m["min_fecha"] = fecha
                    m["locales"][local_id] = m["locales"].get(local_id, 0) + 1

            log.info(f"  {db_name}: {matched_count}/{len(batch_cab)} cabeceras matcheadas a cliente por CUIT")
            for i in range(0, len(batch_cab), 500):
                supa_upsert("compras", batch_cab[i:i+500])
            total_cabeceras += len(batch_cab)

            # Detalle
            detalle = df_query(db_name, SQL_DETALLE)
            batch_det = []
            for r in detalle:
                codigo = (r.get("CODIGO") or "").strip()
                if not codigo:
                    continue
                compra_id = f"{db_name}:{codigo}"
                if compra_id not in ids_cab:
                    continue
                batch_det.append({
                    "compra_id":       compra_id,
                    "nro_item":        int(r.get("NROITEM") or 0),
                    "sku":             _safe(r.get("FART")),
                    "descripcion":     _safe(r.get("FTXT")),
                    "cantidad":        float(r.get("FCANT") or 0),
                    "precio_unitario": float(r.get("FPRECIO") or 0),
                    "monto_total":     float(r.get("FMONTO") or 0),
                    "talle":           _safe(r.get("TALLE")),
                    "color":           _safe(r.get("CCOLOR")),
                })

            for i in range(0, len(batch_det), 500):
                supa_upsert("compras_detalle", batch_det[i:i+500])
            total_detalles += len(batch_det)
            log.info(f"  {db_name}: {len(batch_cab)} cabeceras + {len(batch_det)} detalles subidos")

        except Exception as e:
            log.error(f"  {db_name}: error procesando compras — {e}")
            error_global = str(e)
            continue

    # Actualizar métricas agregadas en clientes (paralelo, 10 workers)
    log.info(f"  Actualizando métricas en {len(metricas_por_gid)} clientes (10 workers paralelos)...")
    actualizados = 0
    fallidos = 0

    def _patch_metricas(gid_m):
        gid, m = gid_m
        ticket_promedio = m["total"] / m["count"] if m["count"] > 0 else 0
        sucursal_favorita = max(m["locales"].items(), key=lambda x: x[1])[0] if m["locales"] else None
        try:
            supa_patch("clientes", {"globalid": f"eq.{gid}"}, {
                "total_compras":        round(m["total"], 2),
                "cantidad_compras":     m["count"],
                "ticket_promedio":      round(ticket_promedio, 2),
                "ultima_compra_fecha":  _to_iso(m["max_fecha"]),
                "primera_compra_fecha": _to_iso(m["min_fecha"]),
                "sucursal_favorita":    sucursal_favorita,
                "actualizado_en":       datetime.now(timezone.utc).isoformat(),
            })
            return True, None
        except Exception as e:
            return False, str(e)

    with ThreadPoolExecutor(max_workers=10) as executor:
        items = list(metricas_por_gid.items())
        futures = {executor.submit(_patch_metricas, item): item[0] for item in items}
        for i, future in enumerate(as_completed(futures)):
            ok, err = future.result()
            if ok:
                actualizados += 1
            else:
                fallidos += 1
            if (i + 1) % 500 == 0:
                log.info(f"  Métricas procesadas: {i+1}/{len(items)} ({actualizados} ok, {fallidos} fail)")

    log.info(f"=== sync_compras: fin — {total_cabeceras} cabeceras + {total_detalles} detalles + {actualizados} clientes con métricas ===")
    log_sync("compras", list(BASE_TO_LOCAL.values()), total_cabeceras, total_detalles, error_global)
    return total_cabeceras, total_detalles




# ══════════════════════════════════════════════════════════════════
#  6. sync_conversiones — conectar pedidos del CRM con sus facturas
# ══════════════════════════════════════════════════════════════════

def _norm_nombre_tokens(s):
    """Normaliza un nombre: sin acentos, lowercase, tokens únicos sin stopwords."""
    if not s:
        return set()
    import unicodedata
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode('ascii').lower()
    for ch in ',.-_/&':
        s = s.replace(ch, ' ')
    STOPWORDS = {'de', 'la', 'el', 'los', 'las', 'y', 'o', 'a', 'del', 'sr', 'sra', 'srta', 'sa', 'srl'}
    return {t for t in s.split() if len(t) > 1 and t not in STOPWORDS}


def _nombres_matchean(pedido_nombre, factura_nombre):
    """True si todas las palabras del pedido están en la factura (>= 2 tokens)."""
    p = _norm_nombre_tokens(pedido_nombre)
    f = _norm_nombre_tokens(factura_nombre)
    # Requiere al menos 2 tokens significativos en el pedido para evitar falsos positivos
    if len(p) < 2:
        return False
    return p.issubset(f)


def sync_conversiones(ventana_dias=90):
    """
    Para cada pedido del CRM del último año con SKU, busca si existe una compra asociada.
    Estrategia de matching (en orden de confianza):
      1. DNI exacto del pedido vs DNI/CUIT del cliente en compra (cuando ambos disponibles)
      2. Nombre del pedido normalizado matchea cliente_factura de la compra
    Filtros comunes: mismo SKU, mismo local, fecha de compra dentro de ventana_dias, no anulada.
    NO cambia el estado del pedido.
    """
    log.info(f"=== sync_conversiones: iniciando (ventana {ventana_dias} días) ===")
    error_global = None
    actualizados = 0
    matches_por_dni = 0
    matches_por_nombre = 0

    try:
        un_anio = (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()
        pedidos = supa_get("pedidos", {
            "select": "id,created_at,local_id,sku,celular,dni,nombre_cliente,compra_id",
            "sku":    "not.is.null",
            "created_at": "gte." + un_anio,
            "order":  "created_at.desc",
        })
    except Exception as e:
        log.error(f"  Error al leer pedidos: {e}")
        log_sync("conversiones", [], 0, 0, str(e))
        return

    log.info(f"  {len(pedidos)} pedidos a evaluar")
    pedidos_pendientes = [p for p in pedidos if not p.get("compra_id")]
    log.info(f"  {len(pedidos_pendientes)} sin conversión previa")

    if not pedidos_pendientes:
        log_sync("conversiones", list(BASE_TO_LOCAL.values()), 0, 0, None)
        return

    # Para cada pedido, buscar candidatos: compras del mismo SKU/local/ventana, no anuladas
    # Hacemos un fetch por pedido (limit 50 candidatos) y filtramos en código
    now_iso = datetime.now(timezone.utc).isoformat()
    batch_updates = []

    for idx, p in enumerate(pedidos_pendientes):
        try:
            fecha_ped = dateparser.parse(p["created_at"])
            fecha_desde = fecha_ped.isoformat()
            fecha_hasta = (fecha_ped + timedelta(days=ventana_dias)).isoformat()
            sku_ped = p["sku"]
            local_ped = p["local_id"]
            dni_ped = (p.get("dni") or "").strip()
            nombre_ped = p.get("nombre_cliente")

            # 1. Buscar compras candidatas por SKU + local + ventana (no anuladas)
            detalles = supa_get("compras_detalle", {
                "select": "compra_id,monto_total,compras!inner(id,fecha,local_id,anulado,cliente_factura,cuit_factura)",
                "sku": "eq." + sku_ped,
                "compras.anulado": "eq.false",
                "compras.local_id": "eq." + local_ped,
                "compras.fecha": f"gte.{fecha_desde}",
                "order": "compras(fecha).asc",
                "limit": "50",
            })

            # Filtro en código por fecha_hasta + matching de cliente
            compra_match = None
            metodo = None
            for d in detalles:
                co = d.get("compras")
                if not co or co["fecha"] > fecha_hasta:
                    continue

                # Intento 1: DNI/CUIT exacto
                cuit_factura = (co.get("cuit_factura") or "").strip()
                if dni_ped and cuit_factura:
                    # CUIT en Argentina contiene el DNI (ej. CUIT 20-12345678-3 contiene DNI 12345678)
                    cuit_clean = ''.join(ch for ch in cuit_factura if ch.isdigit())
                    if dni_ped in cuit_clean:
                        compra_match = {"compra_id": co["id"], "factura_fecha": co["fecha"], "factura_monto": float(d.get("monto_total") or 0)}
                        metodo = "dni"
                        break

                # Intento 2: nombre matched (cliente del pedido aparece en cliente_factura)
                if nombre_ped and co.get("cliente_factura"):
                    if _nombres_matchean(nombre_ped, co["cliente_factura"]):
                        compra_match = {"compra_id": co["id"], "factura_fecha": co["fecha"], "factura_monto": float(d.get("monto_total") or 0)}
                        metodo = "nombre"
                        break

            update = {"id": p["id"], "conversion_checked_at": now_iso}
            if compra_match:
                update.update(compra_match)
                actualizados += 1
                if metodo == "dni":    matches_por_dni += 1
                elif metodo == "nombre": matches_por_nombre += 1
            batch_updates.append(update)

            if (idx + 1) % 100 == 0:
                log.info(f"  Evaluados: {idx+1}/{len(pedidos_pendientes)} ({actualizados} matches)")
        except Exception as e:
            log.warning(f"  Error evaluando pedido {p.get('id')}: {e}")
            continue

    log.info(f"  {actualizados}/{len(batch_updates)} matches encontrados (DNI: {matches_por_dni}, Nombre: {matches_por_nombre})")
    log.info(f"  Aplicando updates en paralelo...")

    def _patch_pedido(u):
        pid = u.pop("id")
        try:
            supa_patch("pedidos", {"id": f"eq.{pid}"}, u)
            return True, None
        except Exception as e:
            return False, str(e)

    aplicados = 0
    fallidos = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(_patch_pedido, dict(u)) for u in batch_updates]
        for i, fut in enumerate(as_completed(futures)):
            ok, err = fut.result()
            if ok: aplicados += 1
            else:  fallidos += 1

    log_sync("conversiones", list(BASE_TO_LOCAL.values()), len(batch_updates), actualizados, error_global)
    log.info(f"=== sync_conversiones: fin — {actualizados} conversiones detectadas, {aplicados} updates aplicados ===")
    return actualizados




# ══════════════════════════════════════════════════════════════════
#  7. sync_backup — exporta Supabase a JSON comprimido (nightly)
# ══════════════════════════════════════════════════════════════════

BACKUP_DIR = r"C:\Users\Usuario\OneDrive - Claudia Adorno SRL\ARCHIVOS JUAN PABLO\backups_crm"
BACKUP_RETENTION_DAYS = 30  # mantener N días de backups, borrar los más viejos
BACKUP_TABLES = [
    "articulos",
    "clientes",
    "pedidos",
    "compras",
    "compras_detalle",
    "locales",
    "vendedoras",
    "sku_map",
    "sync_log",
]


def supa_get_all(table, batch_size=1000):
    """Trae TODA la tabla paginando (PostgREST limita a 1000 por request)."""
    all_rows = []
    offset = 0
    while True:
        url = f"{SUPABASE_URL}/rest/v1/{table}"
        headers = dict(HEADERS)
        headers["Prefer"] = "return=representation"
        headers["Range-Unit"] = "items"
        headers["Range"] = f"{offset}-{offset + batch_size - 1}"
        try:
            resp = requests.get(url, headers=headers, timeout=120)
            if resp.status_code in (404, 400):
                # Tabla no existe → saltar
                return None
            resp.raise_for_status()
            batch = resp.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error leyendo {table} offset {offset}: {e}")
        all_rows.extend(batch)
        if len(batch) < batch_size:
            break
        offset += batch_size
    return all_rows


def sync_backup():
    """
    Exporta todas las tablas críticas de Supabase a un archivo JSON gzip-comprimido.
    Guarda en BACKUP_DIR/backup_YYYY-MM-DD_HHMM.json.gz.
    Rota: borra backups > BACKUP_RETENTION_DAYS días.
    """
    import gzip
    import json as _json

    log.info("=== sync_backup: iniciando ===")
    os.makedirs(BACKUP_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}.json.gz")

    snapshot = {
        "_meta": {
            "fecha":          datetime.now(timezone.utc).isoformat(),
            "supabase_url":   SUPABASE_URL,
            "version":        1,
        }
    }
    total_rows = 0
    errores = []
    for table in BACKUP_TABLES:
        try:
            rows = supa_get_all(table)
            if rows is None:
                log.warning(f"  {table}: tabla no existe (404/400), saltando")
                continue
            snapshot[table] = rows
            log.info(f"  {table}: {len(rows)} filas")
            total_rows += len(rows)
        except Exception as e:
            log.error(f"  {table}: error — {e}")
            errores.append(f"{table}: {e}")

    # Escribir comprimido
    try:
        with gzip.open(backup_path, "wt", encoding="utf-8") as f:
            _json.dump(snapshot, f, ensure_ascii=False, default=str)
        size_mb = os.path.getsize(backup_path) / 1024 / 1024
        log.info(f"  Backup escrito: {backup_path} ({size_mb:.1f} MB, {total_rows} filas totales)")
    except Exception as e:
        log.error(f"  Error escribiendo backup: {e}")
        log_sync("backup", [], total_rows, 0, str(e))
        return False

    # Rotación: borrar backups con más de BACKUP_RETENTION_DAYS días
    cutoff = datetime.now() - timedelta(days=BACKUP_RETENTION_DAYS)
    borrados = 0
    for fname in os.listdir(BACKUP_DIR):
        if not fname.startswith("backup_") or not fname.endswith(".json.gz"):
            continue
        fpath = os.path.join(BACKUP_DIR, fname)
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
            if mtime < cutoff:
                os.remove(fpath)
                borrados += 1
        except Exception as e:
            log.warning(f"  No se pudo evaluar {fname}: {e}")
    if borrados:
        log.info(f"  Rotación: {borrados} backup(s) viejo(s) eliminado(s) (>{BACKUP_RETENTION_DAYS} días)")

    error_global = "; ".join(errores) if errores else None
    log_sync("backup", [], total_rows, 0, error_global)
    log.info(f"=== sync_backup: fin — {total_rows} filas en {len(BACKUP_TABLES)} tablas ===")
    return True


# ══════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sync Dragon Fish → Supabase CRM")
    parser.add_argument(
        "--modo",
        choices=["skus", "stock", "znube", "clientes", "compras", "conversiones", "backup", "crm", "todo"],
        default="todo",
        help=(
            "skus     = solo catálogo de artículos\n"
            "stock    = sync stock vía MSTOCK Dragonfish\n"
            "znube    = sync stock vía ZNube (alternativo)\n"
            "clientes = espejo de maestro de clientes a Supabase\n"
            "compras  = espejo de comprobantes de venta (último año) + métricas\n"
            "conversiones = matchear pedidos del CRM con sus facturas\n"
            "backup   = exportar Supabase a JSON gzip (rotacion 30 dias)\n"
            "crm      = clientes + compras + conversiones + backup (sync nocturno pesado)\n"
            "todo     = skus + stock (default recomendado para 15min)"
        ),
    )
    args = parser.parse_args()

    try:
        if args.modo in ("skus", "todo"):
            sync_skus()

        if args.modo == "znube":
            sync_znube_stock()
        elif args.modo == "stock":
            sync_stock()
        elif args.modo == "clientes":
            sync_clientes()
        elif args.modo == "compras":
            sync_compras(year_lookback=1)
        elif args.modo == "conversiones":
            sync_conversiones(ventana_dias=90)
        elif args.modo == "backup":
            sync_backup()
        elif args.modo == "crm":
            sync_clientes()
            sync_compras(year_lookback=1)
            sync_conversiones(ventana_dias=90)
            sync_backup()
        elif args.modo == "todo":
            sync_stock()

    except Exception as e:
        log.critical(f"Error fatal: {e}", exc_info=True)
        log_sync(args.modo, [], 0, 0, str(e))
        sys.exit(1)

