-- ═══════════════════════════════════════════════════════════════════════
--  CRM ADORNO — Login por sucursal + RLS (Fase 2)
--
--  Modelo:
--    - 1 cuenta por sucursal (unicenter/alcorta/oficina @adorno.local)
--    - 1 admin (juanpsimonelli@gmail.com) que ve TODO
--    - Cada sucursal solo ve/edita SUS pedidos
--
--  IMPORTANTE: este script crea la tabla puente, helpers, mapeo y policies,
--  pero NO activa RLS en pedidos todavía (eso lo hace 02_enable_rls.sql,
--  después de migrar el frontend al login). Si activás RLS antes de que el
--  frontend use el token, el CRM en producción deja de leer pedidos.
--
--  Pre-requisito: crear las 3 cuentas de sucursal en Supabase Auth
--  (Authentication → Users → Add user, con Auto Confirm):
--    unicenter@adorno.local / cas27257
--    alcorta@adorno.local   / cas27257
--    oficina@adorno.local   / cas27257
--  La cuenta admin (juanpsimonelli@gmail.com) ya existe.
-- ═══════════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────────
--  1. Tabla puente: auth.users → local
-- ───────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS crm_usuarios (
    auth_user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    local_id     text,                  -- 'unicenter'/'alcorta'/'oficina'; NULL para admin
    es_admin     boolean DEFAULT false,
    creado_at    timestamptz DEFAULT now()
);

-- ───────────────────────────────────────────────────────────────────────
--  2. Helpers SECURITY DEFINER (leen crm_usuarios con privilegios elevados)
-- ───────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION crm_mi_local()
RETURNS text LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $func$
    SELECT local_id FROM crm_usuarios WHERE auth_user_id = auth.uid() LIMIT 1;
$func$;

CREATE OR REPLACE FUNCTION crm_es_admin()
RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $func$
    SELECT COALESCE((SELECT es_admin FROM crm_usuarios WHERE auth_user_id = auth.uid() LIMIT 1), false);
$func$;

-- ───────────────────────────────────────────────────────────────────────
--  3. Mapeo de cuentas → local (busca por email en auth.users)
-- ───────────────────────────────────────────────────────────────────────
INSERT INTO crm_usuarios (auth_user_id, local_id, es_admin)
SELECT id, 'unicenter', false FROM auth.users WHERE email = 'unicenter@claudiaadorno.com'
ON CONFLICT (auth_user_id) DO UPDATE SET local_id = EXCLUDED.local_id, es_admin = EXCLUDED.es_admin;

INSERT INTO crm_usuarios (auth_user_id, local_id, es_admin)
SELECT id, 'alcorta', false FROM auth.users WHERE email = 'alcorta@claudiaadorno.com'
ON CONFLICT (auth_user_id) DO UPDATE SET local_id = EXCLUDED.local_id, es_admin = EXCLUDED.es_admin;

INSERT INTO crm_usuarios (auth_user_id, local_id, es_admin)
SELECT id, 'oficina', false FROM auth.users WHERE email = 'administracion@claudiaadorno.com'
ON CONFLICT (auth_user_id) DO UPDATE SET local_id = EXCLUDED.local_id, es_admin = EXCLUDED.es_admin;

-- Admin (ve todo) — la cuenta que ya venía en uso
INSERT INTO crm_usuarios (auth_user_id, local_id, es_admin)
SELECT id, NULL, true FROM auth.users WHERE email = 'juanpsimonelli@gmail.com'
ON CONFLICT (auth_user_id) DO UPDATE SET local_id = EXCLUDED.local_id, es_admin = EXCLUDED.es_admin;

-- ───────────────────────────────────────────────────────────────────────
--  4. RLS en crm_usuarios (cada uno lee solo su fila)
-- ───────────────────────────────────────────────────────────────────────
ALTER TABLE crm_usuarios ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS crm_usuarios_self ON crm_usuarios;
CREATE POLICY crm_usuarios_self ON crm_usuarios FOR SELECT TO authenticated
    USING (auth_user_id = auth.uid());

-- ───────────────────────────────────────────────────────────────────────
--  5. Policies en pedidos (se crean ahora; entran en vigor al activar RLS)
--     local_id se compara case-insensitive (el frontend usa ilike)
-- ───────────────────────────────────────────────────────────────────────
DROP POLICY IF EXISTS pedidos_select ON pedidos;
DROP POLICY IF EXISTS pedidos_insert ON pedidos;
DROP POLICY IF EXISTS pedidos_update ON pedidos;
DROP POLICY IF EXISTS pedidos_delete ON pedidos;

CREATE POLICY pedidos_select ON pedidos FOR SELECT TO authenticated
    USING (crm_es_admin() OR lower(local_id) = lower(crm_mi_local()));

CREATE POLICY pedidos_insert ON pedidos FOR INSERT TO authenticated
    WITH CHECK (crm_es_admin() OR lower(local_id) = lower(crm_mi_local()));

CREATE POLICY pedidos_update ON pedidos FOR UPDATE TO authenticated
    USING (crm_es_admin() OR lower(local_id) = lower(crm_mi_local()))
    WITH CHECK (crm_es_admin() OR lower(local_id) = lower(crm_mi_local()));

CREATE POLICY pedidos_delete ON pedidos FOR DELETE TO authenticated
    USING (crm_es_admin() OR lower(local_id) = lower(crm_mi_local()));

-- ───────────────────────────────────────────────────────────────────────
--  6. Policies en pedidos_log (filtra por el local del pedido referenciado)
-- ───────────────────────────────────────────────────────────────────────
DROP POLICY IF EXISTS pedidos_log_select ON pedidos_log;
DROP POLICY IF EXISTS pedidos_log_insert ON pedidos_log;

CREATE POLICY pedidos_log_select ON pedidos_log FOR SELECT TO authenticated
    USING (
        crm_es_admin() OR EXISTS (
            SELECT 1 FROM pedidos p
            WHERE p.id = pedidos_log.pedido_id
              AND lower(p.local_id) = lower(crm_mi_local())
        )
    );

-- INSERT al log: cualquier usuario autenticado puede registrar (append-only, no sensible)
CREATE POLICY pedidos_log_insert ON pedidos_log FOR INSERT TO authenticated
    WITH CHECK (true);
