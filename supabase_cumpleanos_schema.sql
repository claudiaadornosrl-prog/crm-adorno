-- ═══════════════════════════════════════════════════════════════════════
--  CRM Adorno — Cumpleaños
--  Agrega columna fecha_nacimiento a clientes
--  Ejecutar UNA VEZ en Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════════════

ALTER TABLE clientes ADD COLUMN IF NOT EXISTS fecha_nacimiento date;

-- Índice para búsquedas por mes/día (próximos cumpleaños)
CREATE INDEX IF NOT EXISTS idx_clientes_fecha_nac ON clientes(fecha_nacimiento);
