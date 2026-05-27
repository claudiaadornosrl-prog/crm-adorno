# Plan — Módulo RRHH Claudia Adorno SRL

**Fecha:** 2026-05-25
**Owner:** JP
**Arquitectura:** Opción C (app separada + Supabase compartida + landing hub)

---

## 1. Arquitectura general

```
                    ┌────────────────────────┐
                    │  hub.adornosrl (web)   │
                    │  Landing con tarjetas: │
                    │  → CRM   → RRHH        │
                    └────────────┬───────────┘
                                 │
              ┌──────────────────┴───────────────────┐
              │                                      │
     ┌────────▼────────┐                  ┌─────────▼────────┐
     │  crm-adorno     │                  │   rrhh-adorno    │
     │  (GitHub Pages) │                  │  (GitHub Pages)  │
     │  index.html     │                  │  index.html      │
     └────────┬────────┘                  └─────────┬────────┘
              │                                     │
              └─────────────┬───────────────────────┘
                            │
                  ┌─────────▼─────────┐
                  │     SUPABASE      │
                  │  ─ tablas crm_*   │
                  │  ─ tablas rrhh_*  │
                  │  ─ auth + storage │
                  └───────────────────┘
```

**Repos nuevos:**
- `rrhh-adorno` → app HTML/JS single-file con el módulo
- `hub-adorno` (opcional, podemos empezar sin él) → landing simple

**Mismo Supabase**, prefijo `rrhh_` en todas las tablas nuevas para no chocar con CRM. RLS por rol.

---

## 2. Roles y permisos

| Rol | Quién | Acceso |
|-----|-------|--------|
| **Admin** | JP | Todo: ABM empleados, sueldos, asistencias, vacaciones, documentos, reportes, audit log |
| **Gerente de local** | (futuro, por sucursal) | Solo su local: ver empleados, aprobar vacaciones, cargar apercibimientos, ver asistencias |
| **Empleado** | Cada vendedora/admin con login propio | Solo su propio legajo: mis datos, mis recibos, mis vacaciones, mis fichadas, mis certificados |

Auth: Supabase Auth (email + password). Cada empleado tiene un registro en `rrhh_usuarios` linkeado a su `rrhh_empleados.id`.

---

## 3. Modelo de datos (15 tablas)

### Base
1. **`rrhh_empleados`** — maestro
   - Identidad: `dni`, `cuil`, `nombre`, `apellido`, `nombre_completo`, `fecha_nacimiento`, `sexo`
   - Contacto: `direccion`, `telefono`, `email`, `contacto_emergencia_*`
   - Laboral: `local` (unicenter/alcorta/oficina), `categoria_cct`, `tipo_contrato` (dep/monotr), `fecha_ingreso`, `fecha_baja`, `motivo_baja`, `estado` (activo/licencia/baja)
   - Pago: `cbu`, `banco`
   - Extra: `foto_url`, `hijos` (jsonb), `notas_internas`

2. **`rrhh_categorias_cct`** — escalas CCT 130/75
   - `codigo` (admin_A, vendedor_B…), `nombre`, `sueldo_basico`, `fecha_vigencia`

3. **`rrhh_usuarios`** — login
   - `empleado_id` (FK), `email`, `rol` (admin/gerente/empleado), `local_gerencia` (si gerente), `activo`

### Operativo
4. **`rrhh_sueldos`** — liquidaciones mes a mes
   - `empleado_id`, `periodo` (YYYY-MM), conceptos (básico, antigüedad, presentismo, comisiones, hs extras, premios, SAC, vacaciones), `bruto`, `descuentos`, `neto`, `recibo_url`, `validado` (control automático), `observaciones`

5. **`rrhh_asistencias`** — resumen mensual
   - `empleado_id`, `periodo`, `dias_trabajados`, `ausencias`, `vacaciones`, `licencias`, `llegadas_tarde`, `horas_extras`, `reporte_crosschex_url`, `analisis_url`

6. **`rrhh_asistencias_detalle`** — día por día (opcional)
   - `empleado_id`, `fecha`, `entrada`, `salida`, `estado` (puntual/tarde/ausente/vac/lic/feriado), `minutos_tarde`

7. **`rrhh_vacaciones`** — saldo anual
   - `empleado_id`, `año`, `dias_correspondientes`, `dias_tomados`, `dias_pendientes`

8. **`rrhh_vacaciones_movimientos`** — pedidos/aprobaciones
   - `vacaciones_id`, `fecha_desde`, `fecha_hasta`, `dias`, `estado` (solicitada/aprobada/tomada/cancelada), `aprobado_por`

9. **`rrhh_licencias`** — licencias especiales
   - `empleado_id`, `tipo` (matrimonio, nacimiento, fallecimiento, examen, enfermedad, ART, otra), `desde`, `hasta`, `dias`, `certificado_url`

10. **`rrhh_certificados_medicos`**
    - `empleado_id`, `desde`, `hasta`, `diagnostico`, `medico`, `archivo_url`, `validado`

11. **`rrhh_apercibimientos`**
    - `empleado_id`, `fecha`, `motivo`, `severidad` (leve/grave), `archivo_url`, `firmado`

12. **`rrhh_documentos`** — repositorio general
    - `empleado_id`, `tipo` (contrato, alta AFIP, CBU, DNI frente/dorso, CV, otros), `archivo_url`, `fecha_vencimiento`

13. **`rrhh_premios`** — premios extra
    - `empleado_id`, `fecha`, `tipo`, `monto`, `motivo`

14. **`rrhh_log`** — audit log (mismo patrón que `pedidos_log` del CRM)
    - `timestamp`, `usuario`, `accion`, `tabla`, `registro_id`, `campo`, `valor_anterior`, `valor_nuevo`

15. **`rrhh_feriados`** — calendario AR (compartido con la skill control-asistencias)
    - `fecha`, `nombre`, `tipo` (nacional/puente/no laborable)

**Storage buckets Supabase:**
- `rrhh-recibos`
- `rrhh-certificados`
- `rrhh-apercibimientos`
- `rrhh-documentos`
- `rrhh-fotos`
- `rrhh-asistencias-raw` (Excel originales CrossChex)

---

## 4. Pantallas

### ADMIN (vos)
- **Dashboard "Hoy"** — cumpleaños del mes, certificados activos, licencias en curso, vacaciones próximas, alertas (vencimientos, control sueldos OK/error)
- **Empleados** — listado con filtros (local/estado/categoría) + vista 360 por empleado con tabs:
  - Datos personales
  - Legajo (documentos)
  - Sueldos (timeline + control automático)
  - Asistencias (mes a mes)
  - Vacaciones (saldo + historial)
  - Certificados + licencias + apercibimientos
  - Premios
- **Sueldos** — listado mensual, bulk upload, alertas del control automático
- **Asistencias** — dashboard mensual por local, importar CrossChex
- **Vacaciones** — tablero saldos, aprobar pendientes
- **Documentos** — bibliotecas por tipo, buscar
- **Reportes** — exports Excel/PDF (lista de empleados, vacaciones tomadas, horas extras del mes, etc.)
- **Configuración** — categorías CCT, escalas vigentes, locales
- **Audit log**

### GERENTE
- Su local solamente: dashboard + empleados (read salvo asistencias/vacaciones) + aprobar vacaciones

### EMPLEADO
- Mi legajo (datos personales — algunos editables, otros no)
- Mis recibos (descargar PDF)
- Mis vacaciones (saldo + solicitar)
- Mis fichadas del mes
- Cambiar contraseña

---

## 5. Integraciones con lo que ya tenés

| Existente | Cómo se conecta |
|-----------|----------------|
| Skill `control-sueldos-adorno` | Cuando subís recibo PDF → ejecuta skill → guarda en `rrhh_sueldos` con `validado=true/false` + observaciones |
| Skill `control-asistencias-crosschex` / `fichadas-procesamiento` | Subís Excel CrossChex → procesa → guarda en `rrhh_asistencias` + `rrhh_asistencias_detalle` |
| Carpeta OneDrive `EMPLEADOS/` | Script de migración inicial: levanta todos los PDFs y los importa a Supabase Storage + crea registros |
| Vendedoras del CRM | Import inicial: las constantes `VENDEDORAS` del CRM → crear 14 registros en `rrhh_empleados` |
| Backups CRM (OneDrive) | Mismo sistema, agregar tablas RRHH |
| WhatsApp Business API (futuro) | Avisos de cumpleaños, vencimientos de certificados, recordatorios |

---

## 6. Fases de build

| Fase | Qué | Estimado |
|------|-----|----------|
| **0 — Infra** | Repo `rrhh-adorno`, schema SQL (15 tablas), storage buckets, RLS policies, auth Supabase, landing hub | 1 día |
| **1 — Empleados + Admin** | ABM completo, vista 360, migración desde carpeta EMPLEADOS | 3-4 días |
| **2 — Sueldos** | Upload recibos, parseo con skill, historial, alertas | 2-3 días |
| **3 — Asistencias** | Import CrossChex, dashboard mensual, cruce vacaciones/feriados | 2-3 días |
| **4 — Vacaciones + Licencias** | Saldo automático, flow solicitud/aprobación, calendario | 2 días |
| **5 — Documentos + Apercibimientos** | Storage organizado, vencimientos con alertas | 1-2 días |
| **6 — Self-service empleados** | Login, vistas restringidas, cambio password | 2-3 días |
| **7 — Gerentes** | Vistas por local, permisos diferenciados | 1-2 días |
| **8 — Landing hub** | Página inicial linkeando CRM + RRHH | 0.5 día |

**Total:** ~15-20 días reales (en bloques cortos).

---

## 7. Decisiones pendientes (necesito tu input)

1. **Nombre del repo y URL final:** `rrhh-adorno` → `https://claudiaadornosrl-prog.github.io/rrhh-adorno/` ¿OK?
2. **Schema vs prefijo:** ¿tablas con prefijo `rrhh_` en `public`, o creamos un schema `rrhh` aparte? (recomiendo prefijo, es más simple)
3. **Auth:** ¿usamos Supabase Auth nativo (email/password con recovery) o seguimos con el patrón actual del CRM (password único compartido por rol)? Para self-service de empleados **necesitamos auth real**, recomiendo Supabase Auth.
4. **Foto de empleado:** ¿sacan vos las fotos o cada empleado se sube una desde su panel?
5. **Recibos viejos:** ¿migramos todo el histórico que tenés en OneDrive o arrancamos desde un mes específico (ej. enero 2026)?
6. **Ex-empleados:** ¿los importamos también con `estado=baja` o arrancamos solo con activos?
7. **Categorías CCT:** ¿tenés la tabla actualizada de categorías y escalas, o la armamos en base a lo que la skill `control-sueldos` ya conoce?

---

## 8. Próximo paso propuesto

Si te cierra el plan, arrancamos por **Fase 0 (infra)**:
1. Crear carpeta `C:\RRHH_Adorno\` con la estructura base
2. Inicializar repo Git + GitHub Pages
3. Escribir los 15 SQL de schema para Supabase
4. Crear los buckets de Storage
5. Setup de Supabase Auth con un primer usuario admin (vos)

Y de ahí pasamos a Fase 1 (empleados + migración de carpeta EMPLEADOS).
