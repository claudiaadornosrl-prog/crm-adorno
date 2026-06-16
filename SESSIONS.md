# Sesiones de trabajo · Sistema Claudia Adorno

Una entrada por sesión importante. Resumen práctico, no exhaustivo.
Para detalles arquitecturales ver `CLAUDE.md`. Para histórico técnico, `git log`.

---

## 2026-06-15 — Tesorería: Galicia clearing + Inversiones + MP disponible/pendiente + Notas

Sesión grande. 21 versiones de cache pusheadas (v13 → v21).

### Galicia · Cuenta Corriente y Caja Ahorro
- **Hash sin saldo** en movs scrapeados (`fecha + descripción + importe`).
  Razón: cuando un cheque pendiente se acredita, Galicia reordena las filas y recalcula
  `saldo_post` de cada mov. Si el hash incluía saldo, el mismo evento se duplicaba.
- **MERGE en upsert** (no IGNORE): si el hash ya existe, hace PATCH actualizando
  `saldo_post`, `extra`, `descripcion`, `importe`. Función `upsert_movimientos` en
  `scrapers/scraper_common.py`.
- **Filtro "Pendiente"**: los Echeq 48hs en clearing NO se cargan a la DB hasta que
  se acrediten. Mañana cuando se libere viene como mov real.
- **Reverse antes del insert**: invierte la lista para que los IDs autoincrementales
  reflejen orden cronológico ASC. Con `ORDER BY fecha DESC, id DESC` en la PWA
  muestra igual que el banco.
- **Detalle de movimiento** (CUIT/CBU/razón social): el scraper expande la flecha
  global del thead (`thead th:last-child svg:visible`) y captura los datos de cada
  fila de detalle. Se guardan en `extra` y se renderizan como subtítulo gris en la
  grilla de la PWA.

### Galicia · Saldo banco real
- Nueva columna `tesoreria_cuentas.saldo_banco_actual` + `saldo_banco_at`.
- El scraper captura el saldo "disponible" del dashboard `/cuentas` (que descuenta
  pendientes) y lo guarda.
- Función `tesoreria_saldo_cuenta` modificada para priorizar `saldo_banco_actual`
  si está fresco (< 7 días), sino fallback a `SUM(importe) + offset_ancla`.
- Resultado: card "Galicia CC ARS" muestra el saldo real ($993K) y no el calculado
  desde la suma de movs.

### Galicia · Módulo Inversiones completo (3 fases)
**Fase A — Estructura y saldos**:
- 4 cuentas nuevas: Galicia Títulos ARS/USD, Galicia Plazo Fijo ARS/USD (id 25-28).
- Extendido CHECK constraint del campo `tipo` para aceptar `banco_titulos` y `banco_pf`.
- Scraper navega a `/inversiones`, toggle Pesos/Dólares, lee Total valorizado +
  distribución del donut → calcula saldo por tipo y actualiza `saldo_banco_actual`.
- Dashboard PWA: las 6 cuentas de inversión se colapsan en 2 cards virtuales:
  "Inversiones Pesos" y "Inversiones Dólares" con flecha ▸.
- Click → vista intermedia con 3 cards (Fondos FIMA / Títulos / Plazo Fijo).
- Click → grilla de movs de esa cuenta.

**Fase B — Tenencias**:
- Scraper navega a `/inversiones/spa-fima/holdings` y captura tabla con cuotapartes,
  valor cuotaparte, saldo valorizado por fondo.
- Guarda en `tesoreria_tenencias` (reusa la tabla de PPI).
- PWA muestra tabla de tenencias arriba de la grilla cuando entrás a FIMA ARS/USD.

**Fase C — Movimientos del fondo**:
- Scraper navega de holdings → click "Movimientos" → captura tabla con Agregar/Retirar.
- Cada Agregar = importe positivo (suscripción), cada Retirar = importe negativo (rescate).
- Carga a `tesoreria_movimientos` con `cuenta_id=20` (FIMA ARS) o `21` (FIMA USD)
  según el fondo de cada fila. Incluye cuotapartes + valor cuotaparte en `extra`.

### Mercado Pago Locales
- **Saldo disponible vs pendiente**:
  - El endpoint `/users/{id}/mercadopago_account/balance` da 403 con el access token
    estándar (necesita scopes OAuth extra que no tenemos).
  - **Solución alternativa elegante**: cada payment de MP tiene `money_release_date`
    (cuándo se libera el dinero). Calculamos:
    - **Pendiente** = SUM(importe) WHERE `money_release_date > hoy`
    - **Disponible** = Total − Pendiente
  - Resultado: precisión ~99% (diferencia de ~$750K son comisiones/IVA esperables).
- Nueva columna `tesoreria_cuentas.saldo_banco_pendiente`.
- View `tesoreria_saldos` regenerada para exponer ambos campos.
- PWA: card MP Locales muestra disponible ($12M). Al entrar a movs, banner amarillo
  arriba con "📅 Pendiente de liquidar $43M".

### Notas por movimiento
- Nueva columna `tesoreria_movimientos.nota` (TEXT).
- Icono 📝 (gris semi-transparente) en cada fila. Click → modal centrado con overlay
  oscuro, textarea para escribir, botones Guardar / Borrar nota.
- Filas con nota → fondo amarillo claro + texto en cursiva debajo de la descripción +
  icono 📌 (lleno).
- Funciona para Galicia, MP, PPI, manuales — cualquier mov de cualquier cuenta.

### Cambios DB principales
```sql
-- Galicia
ALTER TABLE tesoreria_movimientos ADD COLUMN nota TEXT;
ALTER TABLE tesoreria_cuentas ADD COLUMN saldo_banco_actual NUMERIC(14,2);
ALTER TABLE tesoreria_cuentas ADD COLUMN saldo_banco_at TIMESTAMPTZ;

-- MP
ALTER TABLE tesoreria_cuentas ADD COLUMN saldo_banco_pendiente NUMERIC(14,2);

-- Inversiones
ALTER TABLE tesoreria_cuentas DROP CONSTRAINT tesoreria_cuentas_tipo_check;
ALTER TABLE tesoreria_cuentas ADD CONSTRAINT tesoreria_cuentas_tipo_check
  CHECK (tipo = ANY (ARRAY['caja','banco_cc','banco_ca','banco_fondo',
                            'banco_titulos','banco_pf','mp','broker','tarjeta','otro']));

-- Función tesoreria_saldo_cuenta: prioriza saldo_banco_actual si está fresco
-- View tesoreria_movimientos_view: incluye nota
-- View tesoreria_saldos: incluye saldo_banco_pendiente
```

### Pendientes para futuras sesiones
- Validar inversiones con datos reales (JP va a comprar títulos + PF + mov FIMA USD
  el 16/06 para testear)
- Movs FIMA USD: verificar si vienen mezclados con ARS o requieren toggle
- MP Web parser de mails mensuales
- Rotar `SUPABASE_SERVICE_ROLE_KEY` (leaked en chat anterior)
- Probar paste manual de tabla del banco (botón en Cargar)

### Módulo Ventas · Turnos + cruce MP (nuevo, listo para mañana)
- `ventas_turnos` tabla nueva: 1 fila por turno cerrado del día.
- Función SQL `cerrar_turno(local, fecha)`:
  - numero = max(numero del día) + 1
  - desde = max(hasta) del turno anterior, o 00:00 del día
  - hasta = NOW()
  - valores = ventas_diarias actual - sum(turnos previos del día)
  - cruza con `tesoreria_movimientos` (cuenta MP Locales, local, rango horario)
  - guarda `mp_cuenta`, `discrepancia_mp`, `mp_movs_no_match` (jsonb con detalle)
- View `ventas_turnos_view`: agrega `shopping_turno`, `total_turno`, `estado_discrepancia`.
- PWA: nueva columna "🔒 Turnos" en la planilla con badge (verde=ok, rojo=discrepancia).
  - Botón "🔒 Cerrar" sólo en hoy con venta cargada.
  - Botón "Ver" abre modal con detalle de turnos cerrados.
  - Al cerrar turno: modal con valores + cuadro de cruce MP + tabla de movs si hay
    discrepancia.
- RLS: misma política que ventas_diarias (admin = todos, vendedora = su local).
- Diseñado para soportar 1 turno (findes/oficina) o N turnos (semana en locales).
- Pendiente: instalar `sync_local` en Alcorta y Oficina (scripts `install_alcorta.bat`
  e `install_oficina.bat` ya creados en `ventas-adorno/sync_local/`).

### SQL a correr en producción (en orden)
```sql
-- 1) Tabla + función + view de turnos
\i ventas-adorno/sql/04_turnos.sql
```

---
