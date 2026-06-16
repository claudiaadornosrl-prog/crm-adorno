# CRM · Claudia Adorno SRL

PWA del equipo de vendedoras para gestionar pedidos pendientes por local. Integrada
con Dragonfish (stock + clientes + compras), Google Forms (encuestas de satisfacción)
y WhatsApp (templates por estado).

## Qué hace

- **Pedidos**: CRUD con workflow de estados:
  `Pendiente → Listo para avisar → Avisado → Respondió / No contestó → Completado / Cancelado`
- **Alerta automática** a los 60min en estado Avisado (dashboard Hoy + badge header
  + tab Alertas).
- **Auto-cancelar**: pedidos en "No contestó" con `fecha_recontacto < now - 24h`
  se cancelan automáticamente (RPC `crm_auto_cancelar_no_contesto()`).
- **Sync nocturno Dragonfish**: skus + stock + clientes + compras + conversiones
  + backup gzip a OneDrive (rotación 30 días).
- **Sync stock cada 15min**: detecta llegadas de stock para pedidos pendientes
  y los marca como "Listo para avisar" automáticamente.
- **Detección de cliente Dragonfish** por DNI o CUIT (~52k clientes).
- **WhatsApp templates** por estado (URLs `wa.me/...` — API Business pendiente).
- **Satisfacción ⭐**: encuestas Google Forms sincronizadas diariamente.
- **Tags y filtros** por vendedora, local.

## Stack

- **Frontend**: `index.html` PWA single-file (~5k líneas, 245 KB), vanilla JS
- **Backend**: Supabase (`kwwiykssrpabncpqtmwi`)
- **Sync**: Python `sync_dragonfish.py` corriendo via Windows Task Scheduler
- **Hosting**: GitHub Pages (`claudiaadornosrl-prog/crm-adorno`)

## Estructura del repo

```
CRM_Adorno/  (= repo crm-adorno + carpeta contenedora del proyecto Claudia Adorno)
├── index.html              # PWA CRM
├── service-worker.js       # network-first HTML, cache-first assets
├── manifest.json
├── deploy.ps1
├── sync_dragonfish.py      # 1142 líneas, sync_skus/stock/clientes/compras/conversiones/backup
├── crm_sql/                # gitignored
│   ├── 01_login_setup.sql
│   ├── 02_pedidos.sql
│   ├── 03_clientes_compras.sql
│   ├── 04_satisfaccion.sql
│   ├── 05_alerta_60min.sql
│   ├── 06_sku_map.sql
│   ├── 07_auto_cancelar_no_contesto.sql
│   └── 08_fix_seguridad_clientes.sql  # REVOKE de anon, importante
├── CLAUDE.md               # memoria operativa del proyecto Claudia Adorno (todos los modulos)
├── SESSIONS.md             # log de sesiones por fecha
├── tesoreria-adorno/       # submódulo Tesorería
├── ventas-adorno/          # submódulo Ventas
└── rrhh-adorno/            # submódulo RRHH (sync_encuestas.py vive acá pero alimenta CRM)
```

## Cómo correr

### Sync Dragonfish

```powershell
cd C:\CRM_Adorno
py sync_dragonfish.py --modo todo        # skus + stock
py sync_dragonfish.py --modo crm         # clientes + compras + conversiones + backup
py sync_dragonfish.py --modo backup      # solo backup
```

### Tasks Windows

| Tarea | Comando | Frecuencia |
|---|---|---|
| CRM_Adorno_SyncStock | `sync_dragonfish.py --modo todo` | cada 15min |
| CRM_Adorno_SyncCRM_Nocturno | `sync_dragonfish.py --modo crm` | diaria 03:30 |
| CRM_Adorno_SyncEncuestas | `sync_encuestas.py --aplicar` | diaria 08:00 |

### Deploy

```powershell
cd C:\CRM_Adorno
git add index.html service-worker.js
git commit -m "vXX: ..."
git push  # GitHub Pages deploya solo
```

Hard refresh: `Ctrl+Shift+R`.

## Tablas Supabase

| Tabla | Rol |
|---|---|
| `pedidos` | Tabla principal de pedidos |
| `pedidos_log` | Log de transiciones de estado |
| `articulos` | Catálogo Dragonfish (sync diario) |
| `clientes` | ~52k clientes Dragonfish |
| `compras` + `compras_detalle` | Historial compras del cliente |
| `locales` | Catálogo de locales |
| `sku_map` | Mapeo SKU Dragonfish → CRM |
| `sync_log` | Log de runs del sync (revisar para detectar fallas) |
| `crm_encuestas` | Encuestas Google Forms |
| `crm_usuarios` | Login |

## Integraciones

- **Dragonfish**: 5 bases SQL Server (`DRAGONFISH_UNI1/2`, `_ALCO1/2`, `_ADMIN`)
  via ODBC Driver 17 + Trusted_Connection. Sync con `pyodbc` + retry exponencial.
- **Google Forms**: 2 forms (Unicenter/Alcorta) sincronizados via
  `rrhh-adorno/sync_anviz/sync_encuestas.py`.
- **WhatsApp**: solo URLs `wa.me/...` por ahora. API Business pendiente.

## Conceptos clave

### Workflow de pedidos

```
Pendiente
   ↓ stock_ingreso (manual o auto desde sync_stock)
Listo para avisar
   ↓ Avisar via WhatsApp (vendedora elige plantilla)
Avisado (trigger setea avisado_at)
   ↓ Cliente responde
Respondió ────→ Completado / Cancelado
   o
No contestó (fecha_recontacto = +24h)
   ↓ Auto-cancelar via RPC
Cancelado
```

### Detección de duplicados

- **Clientes**: PK `GLOBALID` de Dragonfish.
- **Compras**: PK compuesta `f"{db_name}:{codigo}"` (robusto entre bases).
- **Conversiones**: match por DNI (CUIT contiene DNI) o nombre normalizado
  (>=2 tokens). Falso positivo posible con nombres comunes ("Maria Lopez").
- **Pedidos**: NO hay constraint. Misma vendedora cargando dos veces = 2 pedidos.

### RLS (importante)

`08_fix_seguridad_clientes.sql` cerró un bug donde `clientes`/`compras`/
`compras_detalle` estaban abiertos a `anon`. **Verificar siempre que ese SQL
se haya aplicado** en producción:

```sql
SELECT tablename, policyname, roles FROM pg_policies
WHERE schemaname = 'public' AND tablename IN ('clientes','compras','compras_detalle');
```

Todas las policies deben ser `TO authenticated`, NO `TO anon`.

## Troubleshooting

### "Sync Dragonfish silenciosamente no actualiza"
1. `sync_log` tiene `error_global IS NOT NULL`? Hoy nadie monitorea esto.
2. Verificar que `Trusted_Connection` funciona desde el usuario que corre la
   tarea.
3. Si `DRAGONFISH_X` está offline, el sync hace `continue` sin alertar.
   **Pendiente: alerta email/WA cuando hay error_global.**

### "Pedidos viejos desaparecen"
- `loadPedidos` no pagina. PostgREST corta a 1000 filas en silencio. Si pasamos
  los 1000 pedidos históricos, los viejos no se ven.
- Fix pendiente: agregar `.range(0, 999)` y paginación si hay más.

### "Cumpleaños no aparece"
- `renderHoy` trae solo 500 clientes (`limit:500`) — con 52k clientes con
  fecha_nac, no garantiza traer los próximos a cumplir.
- Fix pendiente: query directa filtrando por DAY(fecha_nac) y MONTH(fecha_nac)
  del próximo mes.

### "Búsqueda de cliente lenta"
- `ilike '*q*'` con leading wildcard ignora el índice GIN FTS.
- Fix pendiente: usar `ilike 'q*'` (sin leading wildcard) o índice trigram.

### "Marqué pedido como avisado pero otra vendedora lo había marcado como completado"
- Las 3 cuentas por local son compartidas. Dos vendedoras simultáneas se pisan
  (`pedidos_log` registra transiciones falsas).
- Fix pendiente: PATCH condicional `?estado=eq.<esperado>`.

## Pendientes activos

De `CLAUDE.md`:
- #4, #5 — WhatsApp Business API (gestión Meta)
- #7 — Backend WhatsApp en Supabase Edge Functions
- Push diferido de clientes nuevos al Dragonfish
- Probar live: alerta 60min, 24h auto-cancelar, conversion match

QA findings (16/06/2026):
- ✅ FIX aplicado: `fetchPedidos()` → `loadPedidos()` (index.html:2223)
- Verificar que `08_fix_seguridad_clientes.sql` se aplicó en producción
- Paginar `loadPedidos` con `.range()`
- PATCH condicional en `markEstado`
- Parametrizar SKUs en `sync_dragonfish.py` (riesgo SQL injection con `IN (...)`)
- Borrar `vendedoras.html` (legacy 73 KB)
- Alerta sobre `sync_log.error_global IS NOT NULL`

Ver `C:\CRM_Adorno\SESSIONS.md` para historial.
