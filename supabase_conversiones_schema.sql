-- ═══════════════════════════════════════════════════════════════════════
--  CRM Adorno — Conexión pedido → factura
--  Agrega columnas a `pedidos` para registrar cuándo un pedido terminó en venta
--  Ejecutar UNA VEZ en Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════════════

ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS compra_id            text;
ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS factura_fecha        timestamptz;
ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS factura_monto        numeric;
ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS conversion_checked_at timestamptz;

CREATE INDEX IF NOT EXISTS idx_pedidos_compra      ON pedidos(compra_id);
CREATE INDEX IF NOT EXISTS idx_pedidos_factura_fec ON pedidos(factura_fecha DESC);
