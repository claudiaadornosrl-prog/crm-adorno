# Claude Adorno · Memoria del proyecto

Este archivo es la memoria operativa del proyecto para sesiones futuras de Claude.
Leerlo al inicio ahorra a JP tener que explicar el contexto desde cero cada vez.

## 🏢 El negocio

**Claudia Adorno SRL** · CUIT 30-70967311-0 · Buenos Aires
Retail de objetos para baño/cocina. Dueña: Claudia Adorno. Operación a cargo de
JP (Juan Pablo Simonelli, hijo, juanpsimonelli@gmail.com).

### Locales activos
- **Alcorta** (Palermo) · 7 empleadas activas · vendedoras + encargada Soraya
- **Unicenter** (Martínez) · 7 empleadas activas · vendedoras + encargada Soraya
- **Oficina** (Don Torcuato) · 5 empleadas activas · venta online + administración
  - 🚨 **REGLA IMPORTANTE**: JP (admin) cumple también el rol de "encargada"
    para Oficina. En cualquier flujo nuevo con rol gerente/encargada, considerar
    que JP debe poder hacer ambas funciones para Oficina.

### Empleadas total
19 activas. Padrón completo está en `rrhh_empleados` con CUIL, categoría CCT,
fecha de ingreso, foto, etc.

### CCT
130/75 Empleados de Comercio. Categorías: Vendedor B (mayoría),
Administrativo B, Encargada (no estándar para Soraya), Maestranza B,
Franquera (Escasany), Directora SRL (Claudia).

### Modos de liquidación especiales
- **Contreras** y **Escasany** liquidan en modo `doble_blanco`: básico ajustado
  vía solver inverso para que el neto coincida con lo pactado. El campo
  `ajuste_blanco` en `rrhh_liquidacion` guarda el delta vs escalafón puro.

---

## 🧱 Arquitectura técnica

### Stack
- **Frontend**: Single-page HTML estático con vanilla JS, vendoreado con
  CDN libs (jsPDF, SheetJS, Tabler Icons, Google Fonts). NO build step.
- **Backend**: Supabase (PostgreSQL + PostgREST + Auth + Storage).
  Proyecto único `kwwiykssrpabncpqtmwi` compartido por todos los módulos.
- **Hosting**: GitHub Pages, organización `claudiaadornosrl-prog/`.
- **PWA**: Service worker simple network-first en cada módulo. Botón
  "⬇ Instalar" usa `beforeinstallprompt` (con fallback iOS Safari).
- **Scripts back-office**: Python en `migrations/` o `sync_anviz/`. Ejecución
  vía Windows Task Scheduler.

### Módulos productivos
| Módulo | Repo | URL |
|---|---|---|
| Hub | `hub` | https://claudiaadornosrl-prog.github.io/hub/ |
| CRM | `crm-adorno` | https://claudiaadornosrl-prog.github.io/crm-adorno/ |
| RRHH | `rrhh-adorno` | https://claudiaadornosrl-prog.github.io/rrhh-adorno/ |
| Banco | `banco-adorno` | (pendiente fase B en adelante) |

### Datos sensibles
- 🚨 **REGLA REPO PÚBLICO MÍNIMO** (desde 2026-06-10): los repos GitHub son
  públicos (Pages free lo exige), así que SOLO se commitea lo que Pages sirve:
  `index.html`, `manifest`, `service-worker.js`, `assets/`, `deploy.ps1`, README.
  `sql/`, `migrations/`, `sync_anviz/`, `supabase/` quedan SOLO en disco local
  (gitignoreados). El historial de rrhh-adorno fue purgado con git filter-repo
  (backup pre-purga en `backups/rrhh-adorno_pre-filtro_2026-06-10`). Pendiente
  aplicar lo mismo a crm-adorno / ventas-adorno / tesoreria-adorno.
- Service role key Supabase: en `sync_anviz/.env` local (NUNCA en chat ni en git).
- Anon key Supabase: pública, en cada index.html.
- Google App Password para Gmail IMAP: en `sync_anviz/.env`.
- Cuenta Google que firma OAuth: **claudiaadornosrl@gmail.com** (NO juanpsimonelli@gmail.com).

---

## 🔐 Auth y permisos

### Roles RRHH
- `admin` (JP) → control total
- `gerente` (encargadas Soraya/Marisa/etc.) → solo su `local_gerencia`
- `empleado` → solo lo propio (self-service)

### Helper functions SQL (en `02_rls.sql`)
- `rrhh_is_admin()`, `rrhh_is_gerente()`, `rrhh_gerente_local()`,
  `rrhh_mi_empleado_id()`, `rrhh_current_user()`
- Todos `SECURITY DEFINER STABLE` con check de `auth.uid()` y `activo=true`
- **Reusables desde otros módulos** (ej: banco-adorno los reusa).

### Convención de session JS
- `session.rol` (es, con una `l`) — NO `session.role` (en).
- `session.empleado_id`, `session.empleadoData.local` (objeto), `session.user?.email`.
- ⚠️ Bug recurrente: usar `session.role` en código nuevo. **Siempre `session.rol`.**

---

## 🧮 Módulos clave (estado funcional)

### RRHH
- Empleados (CRUD)
- Sueldos (cálculo CCT 130/75 + fórmula Adorno: fijo+comisión+premio+viáticos+extras+feriado)
- Liquidación mensual con grilla por local + KPIs (Recibo CCT / Total / A acreditar banco / Efectivo)
- Préstamos (sistema francés, capital→banco, interés→efectivo)
- Aumentos pedidos (workflow admin→encargada→aprobación→aplicación)
- Retiros mercadería (encargada carga, se descuenta en liquidación)
- Asistencias (sync Anviz CrossChex + calendario mensual + banco minutos)
- Vacaciones (flujo dual vendedora→encargada, francos asociados, PDF firmable)
- PDF recibo + workflow firma vía Gmail (estilo vacaciones)
- Botón Exportar Galicia (XLSX para Galicia Office)
- Self-service empleadas (mi calendario, mi legajo, mis recibos, mis fichadas, etc.)
- Inbox anónimo vendedoras → admin
- PWA installable

### CRM
- Login real por sucursal (password) + admin "JP"
- Pedidos: estados Pendiente → Listo para avisar → Avisado → Respondió/No contestó → Completado / Cancelado
- Alerta automática a los 60min en estado Avisado (dashboard Hoy + badge header + tab Alertas)
- Sync nocturno Dragonfish: skus + stock + clientes + compras + conversiones + backup
- Sync stock cada 15min (skus + stock)
- Detección de cliente Dragonfish por DNI o CUIT (~52k clientes)
- WhatsApp templates por estado
- Satisfacción ⭐ (encuestas Google Forms sincronizadas)
- Tags y filtros por vendedora, local
- PWA installable

### Hub
- Landing con asterisco coral + "Claude" en Spectral + "Adorno" en Forum
- Cards CRM y RRHH (mosaico colorido)
- Sin login propio, solo redirección a cada módulo
- PWA installable

### Tesorería
**Cuentas integradas con scrapers** (`tesoreria-adorno/scrapers/`):
- **Galicia** (Office Banking, Playwright): CC ARS, CA USD, FIMA ARS/USD, Títulos
  ARS/USD, Plazo Fijo ARS/USD. Captura saldos del dashboard, movs de CC/CA con
  detalle CUIT/CBU/razón social expandido, tenencias FIMA (cuotapartes + valor
  unidad), movs FIMA (Agregar/Retirar). Filtra echeqs pendientes hasta que se
  acrediten.
- **MP Locales** (API REST + access token): pagos cada hora, retiros vía
  release_report. Saldo disponible vs pendiente calculado por
  `money_release_date` (porque el endpoint `/balance` da 403 con scopes estándar).
- **MP Web**: aún sin API (JP es colaborador, no admin). Parser de mails pendiente.
- **PPI** (SDK oficial `ppi-client`): saldo + tenencias FCI, una vez por día.

**Conceptos clave**:
- `saldo_banco_actual` + `saldo_banco_at` en `tesoreria_cuentas`: saldo "real"
  reportado por el banco/MP. La función `tesoreria_saldo_cuenta(id)` lo prioriza
  si está fresco (< 7 días), sino cae al cálculo `sum + offset_ancla`.
- `saldo_banco_pendiente`: lo que aún no se liberó (usado en MP, no en Galicia).
- `tesoreria_movimientos.nota`: campo TEXT para anotaciones. La PWA tinta amarillo
  las filas con nota y muestra el texto en cursiva debajo de la descripción.
- `extra` JSONB en movs: guarda info extra (CUIT/CBU/razón social en Galicia,
  fees + money_release_date en MP, cuotapartes + valor_cuotaparte en FIMA, etc).

**Dashboard PWA — drill-down de inversiones**:
- Cuentas tipo `banco_fondo|banco_titulos|banco_pf` se agrupan visualmente en cards
  virtuales "Inversiones Pesos" / "Inversiones Dólares" con flecha ▸.
- Click → vista intermedia con 3 cards (FIMA / Títulos / PF).
- Click → grilla de movs + tabla de tenencias arriba (cuando hay).

**MERGE en `upsert_movimientos`** (`scraper_common.py`):
- Si el hash externo ya existe, hace PATCH actualizando saldo_post, extra,
  descripcion, importe, fecha, local, canal. NO duplica.
- Hash de Galicia NO incluye saldo (porque el banco recalcula cuando se acreditan
  cheques) — formato: `fecha + descripcion + importe + comprobante`.

### Banco (en desarrollo)
- Fase A: SQL base ✅ (4 tablas + helper `banco_saldo_cuenta()` + 5 cuentas + 16 categorías)
- Fase B: repo + setup + auth — pendiente
- Fase C-F: UI cuentas, movimientos, integración con sueldos, import extracto — pendiente

---

## 🔧 Scheduled tasks Windows

| Tarea | Comando | Frecuencia |
|---|---|---|
| CRM_Adorno_SyncStock | `sync_dragonfish.py --modo todo` | cada 15min |
| CRM_Adorno_SyncCRM_Nocturno | `sync_dragonfish.py --modo crm` | diaria 03:30 |
| CRM_Adorno_SyncEncuestas | `sync_encuestas.py --aplicar` | diaria 08:00 |
| CRM_Adorno_ProcesarRecibos | `11_procesar_recibos_firmados.py --aplicar --marcar-leido` | cada hora |
| RRHH_SyncVentas | `sync_ventas.py --aplicar` | cada 4hs |

---

## 📋 Convenciones y reglas operativas

### Trabajar con archivos grandes (lecciones aprendidas)
- **No usar `Edit` tool en index.html**: trunca el archivo cuando es muy grande.
  Usar `Read` para leer secciones específicas, y para modificar usar Python en
  bash con anchors `assert`. Después siempre validar con `node --check`.
- **Validar sintaxis** después de cambios: extraer el bloque `<script>` con
  Python y correr `node --check /tmp/file.js`.
- Si el JS bytes da 0 en la validación, el archivo está truncado — restaurar
  cola desde HEAD con Python.

### Tipografía oficial del proyecto
- **Logo "Claude"**: Spectral 500 (gratis, parecida a Tiempos Headline de Klim)
- **Logo "Adorno"**: Forum (gratis)
- **Header recibo PDF**: Forum (cargada en runtime desde jsdelivr)
- **Fonts vacaciones PDF**: Architects Daughter (estilo manuscrito)
- **Color coral del asterisco Claude**: `#D97757`

### Colores módulos
- CRM: turquesa `#0f6e56` (teal)
- RRHH: violeta `#534ab7` (purple)
- Banco: naranja `#ff6b00` o ámbar (a definir)

### Etiquetar comandos a JP
En cualquier instrucción a JP, identificar siempre dónde correr:
- 🟦 **SQL Editor de Supabase**
- 🟨 **PowerShell** / 🟨 **PowerShell como Administrador**
- 🟪 **CMD** (rara vez)
- ⬜ **SQL Server Management Studio** (para Dragonfish)
- 🌐 **Navegador**
- 🟦 etc.

### PowerShell vs CMD
- `%USERDOMAIN%\%USERNAME%` solo funciona en CMD. En PowerShell usar
  `$env:USERDOMAIN\$env:USERNAME` o evitar la opción del schtasks.

### Sintaxis Supabase JS
- Cliente: `sb` (UMD `@supabase/supabase-js@2`)
- Queries: `sb.from('tabla').select(...).eq(...).single()`
- Updates: `sb.from('tabla').update({...}).eq('id', x)`
- RLS: cuando un cambio de schema deja PostgREST con cache vieja, ejecutar
  `NOTIFY pgrst, 'reload schema';` en el SQL Editor.

### Deploy y cache busting
- Después de cada `deploy.ps1`, **si JP trabaja desde browser normal** (no PWA
  instalada), siempre **`Ctrl + Shift + R`** para hard-refresh, sino sigue
  corriendo el JS viejo cacheado y los nuevos triggers no se ejecutan.
- Síntoma típico: nada anda, pero la Edge Function NO recibe invocaciones cuando
  el evento se dispara desde el cliente.
- Cuando bump del CACHE_VERSION del service worker, recordar: la PWA instalada
  toma la versión nueva al cerrar y reabrir; el browser normal con la pestaña
  abierta necesita hard-refresh.

### Edge Functions sin Supabase CLI
- JP **no tiene Supabase CLI instalada**. Para deploys de Edge Functions usar
  el dashboard inline editor:
  Dashboard → Edge Functions → Deploy a new function → pegar code → Deploy
  → tab "Code" → seleccionar all → pegar code real → "Deploy updates".
- El editor default carga un placeholder de `withSupabase`/`ReqPayload` que
  hay que reemplazar manualmente.
- Para inyectar código TypeScript grande sin copy-paste manual, desde la
  consola del browser: `monaco.editor.getEditors()[0].getModel().setValue(code)`.

### Web Push Notifications (sistema)
- VAPID keys generadas con `sync_anviz/generar_vapid_keys.py` (one-shot, JP ya
  las cargó: pública en `index.html`, privada en Supabase Secrets como
  `VAPID_PRIVATE_KEY` + `VAPID_SUBJECT`).
- Edge Function: `supabase/functions/enviar-push/index.ts`.
- Tabla: `rrhh_push_subscriptions` con RLS (empleada ve solo las propias).
- Service worker tiene `addEventListener('push')` + `notificationclick`.
- Self-service: botón "🔔 Activar notificaciones" en `renderMiLegajo`.
- **iOS limitation**: Web Push solo funciona si la PWA está instalada en
  pantalla de inicio. Avisarle a las vendedoras: "Compartir → Agregar a
  pantalla de inicio". Si abren desde Safari directo, las notifs no llegan.
- Anti-spam: usar `tag: 'turno-' + empId` o similares para que notifs del mismo
  tipo se reemplacen y no spammeen al celu.

---

## 🚨 Pendientes activos importantes

Ver `task list` en cada sesión. Los más relevantes ahora:

### Acción de JP (no código)
- #4, #5 — WhatsApp Business API (gestión Meta)
- #42 — Probar API Anviz con `probar_anviz.ps1`
- #43 — Pedir Developer Mode Anviz (Oficina · Company 110001026)
- #138 — Recordatorio JP cumple rol encargado Oficina

### Código pendiente grande
- Push diferido de clientes nuevos al Dragonfish
- #7 — Backend WhatsApp API en Supabase Edge Functions
- #25 — Integración fina control-sueldos al subir recibo
- #27 — Drag&drop bulk recibos
- #101 — Plan B: levantar fichadas Anviz sin API
- #47 — Importar saldos iniciales banco (mejor dentro del módulo Banco)
- Banco Fase B en adelante

### Mantenimiento
- Probar live: PDF recibo + firma + envío Gmail, alerta 60min, Galicia export

---

## 💡 Para Claude en sesiones futuras

1. **Leé este archivo al inicio** de una sesión nueva. Si JP no lo menciona,
   no hace falta — pero si la sesión es larga o entra en un módulo
   desconocido, revisarlo ahorra rondas.
2. **No re-introducir el bug `session.role`**: siempre `session.rol`.
3. **No usar Edit tool en `index.html` grandes** sin verificar después.
4. **Antes de cada Edit grande**: leer la línea inmediatamente anterior y
   posterior al bloque a modificar, para que el anchor sea único.
5. **Después de cambios JS**: extraer el script y `node --check` + verificar
   que el archivo termine en `</script></body></html>`.
6. **JP es práctico**: prefiere soluciones simples y pragmáticas, no la
   "arquitectura perfecta". Empezar por Fase A funcional y crecer.
7. **JP tiene background limitado de IT**: explicar comandos paso a paso,
   etiquetar siempre el entorno (PowerShell/SQL/Navegador), no asumir
   conocimiento de git/CLI avanzado.

---

*Última actualización: por Claude, en sesión de mayo 2026.
Mantener este archivo vivo: cuando se completan módulos importantes o
cambian decisiones operativas, actualizar las secciones relevantes.*
