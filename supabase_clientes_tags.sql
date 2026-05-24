-- ═══════════════════════════════════════════════════════════════════════
--  CRM Adorno — Tags/etiquetas a clientes
--  Ejecutar UNA VEZ en Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════════════

ALTER TABLE clientes ADD COLUMN IF NOT EXISTS tags text[] DEFAULT '{}'::text[];

-- Índice GIN para filtros tipo `tags @> {VIP}` (contains)
CREATE INDEX IF NOT EXISTS idx_clientes_tags ON clientes USING gin (tags);
