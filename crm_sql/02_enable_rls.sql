-- ═══════════════════════════════════════════════════════════════════════
--  CRM ADORNO — Activar RLS en pedidos / pedidos_log (Fase final)
--
--  ⚠️ CORRER ESTO SOLO DESPUÉS de:
--     1. Haber corrido 01_login_setup.sql
--     2. Haber deployado el frontend con login (que ya usa el token de usuario)
--     3. Haber probado que el login funciona y se ven los pedidos
--
--  Al activar RLS, las llamadas con anon key (sin login) dejan de poder
--  leer/escribir pedidos. Por eso el frontend tiene que estar migrado antes.
-- ═══════════════════════════════════════════════════════════════════════

ALTER TABLE pedidos     ENABLE ROW LEVEL SECURITY;
ALTER TABLE pedidos_log ENABLE ROW LEVEL SECURITY;

-- Verificación: listar policies activas
-- SELECT tablename, policyname, cmd FROM pg_policies
-- WHERE tablename IN ('pedidos','pedidos_log') ORDER BY tablename, policyname;
