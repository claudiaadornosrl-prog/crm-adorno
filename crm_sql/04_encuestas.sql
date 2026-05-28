-- ═══════════════════════════════════════════════════════════════════════
--  CRM ADORNO — Encuestas de satisfacción (Google Forms → Supabase)
--
--  Las encuestas de Google Forms (una por local: Unicenter y Alcorta) se
--  envían al cliente junto con la factura electrónica. Son ANÓNIMAS: solo
--  capturan un puntaje de satisfacción + un comentario libre.
--
--  Un script local (sync_encuestas.py) lee las respuestas vía la API de
--  Google Forms y las vuelca acá con la service_role key. El CRM muestra un
--  panel de satisfacción leyendo de esta tabla.
--
--  RLS: cada local ve sus encuestas; el admin ve todas; solo service_role
--  escribe (consistente con 'pedidos').
-- ═══════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS crm_encuestas (
    id            bigserial PRIMARY KEY,
    local_id      text NOT NULL,            -- 'unicenter' / 'alcorta'
    form_id       text,                     -- id del Google Form de origen
    response_id   text UNIQUE,              -- id de respuesta de Forms (dedup)
    creado_at     timestamptz NOT NULL,     -- fecha de envío de la respuesta
    puntaje       numeric,                  -- calificación normalizada (ej. 4)
    puntaje_max   int,                       -- tope de la escala (ej. 5 o 3)
    comentario    text,                     -- texto libre (puede ser NULL)
    raw           jsonb,                    -- respuesta completa, por las dudas
    importado_at  timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_encuestas_local_fecha
    ON crm_encuestas(local_id, creado_at DESC);

ALTER TABLE crm_encuestas ENABLE ROW LEVEL SECURITY;

-- Lectura: el admin todas; cada local solo las suyas (case-insensitive)
DROP POLICY IF EXISTS encuestas_select ON crm_encuestas;
CREATE POLICY encuestas_select ON crm_encuestas FOR SELECT TO authenticated
    USING (crm_es_admin() OR lower(local_id) = lower(crm_mi_local()));

-- Escritura: solo service_role (el script de sync). authenticated NO inserta.
-- (service_role bypasea RLS, así que no hace falta policy de INSERT/UPDATE.)
