-- ═══════════════════════════════════════════════════════════════════════
--  CRM Adorno — Preservar audit log al eliminar un pedido
--  Cambiar FK de pedidos_log para que sobreviva al DELETE del pedido
--  Ejecutar UNA VEZ en Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════════════

-- Drop el constraint antiguo (ON DELETE CASCADE) y crear uno con SET NULL
ALTER TABLE pedidos_log DROP CONSTRAINT IF EXISTS pedidos_log_pedido_id_fkey;
ALTER TABLE pedidos_log
  ADD CONSTRAINT pedidos_log_pedido_id_fkey
  FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE SET NULL;
