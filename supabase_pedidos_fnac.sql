-- ═══════════════════════════════════════════════════════════════════════
--  CRM Adorno — Fecha de nacimiento opcional en pedidos
--  Ejecutar UNA VEZ en Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════════════

ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS fecha_nacimiento date;
