-- ═══════════════════════════════════════════════════════════════════════
--  CRM Adorno — Stock en vivo por SKU (alimentado desde ZNube)
--  Ejecutar UNA VEZ en Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════════════

ALTER TABLE articulos ADD COLUMN IF NOT EXISTS stock_unicenter   numeric DEFAULT 0;
ALTER TABLE articulos ADD COLUMN IF NOT EXISTS stock_alcorta     numeric DEFAULT 0;
ALTER TABLE articulos ADD COLUMN IF NOT EXISTS stock_actualizado timestamptz;

CREATE INDEX IF NOT EXISTS idx_articulos_stock_uni  ON articulos(stock_unicenter) WHERE stock_unicenter > 0;
CREATE INDEX IF NOT EXISTS idx_articulos_stock_alco ON articulos(stock_alcorta)   WHERE stock_alcorta > 0;
