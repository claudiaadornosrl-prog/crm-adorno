-- ═══════════════════════════════════════════════════════════════════════
-- 06. SCORING POR TOQUES — agregar columna `vendedora` a pedidos_log
-- ═══════════════════════════════════════════════════════════════════════
-- El ranking actual cuenta pedidos cargados por vendedora. Lo cambiamos
-- a "puntos por acción":
--   - Captación (cargar pedido):      1 pt → pedidos.vendedora
--   - Seguimiento 1 (Avisado):         1 pt → log con vendedora seteada
--   - Seguimiento 2 (Re-contactar):    1 pt → log con vendedora seteada
--
-- La vendedora que aparece en cada log puede ser distinta a la que está
-- logueada (varias vendedoras comparten el mismo login del local).
-- ═══════════════════════════════════════════════════════════════════════

ALTER TABLE pedidos_log
    ADD COLUMN IF NOT EXISTS vendedora text;

CREATE INDEX IF NOT EXISTS idx_pedidos_log_vendedora_accion
    ON pedidos_log(vendedora, accion)
    WHERE vendedora IS NOT NULL;

COMMENT ON COLUMN pedidos_log.vendedora IS
'Vendedora a la que se le acredita el punto del scoring (puede ser distinta del usuario logueado).';

SELECT '✅ 06_pedidos_log_vendedora.sql aplicado — columna vendedora agregada' AS status;
