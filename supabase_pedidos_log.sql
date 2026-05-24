-- ═══════════════════════════════════════════════════════════════════════
--  CRM Adorno — Audit log de cambios en pedidos
--  Tabla pedidos_log que registra cada modificación
--  Ejecutar UNA VEZ en Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS pedidos_log (
    id              bigserial PRIMARY KEY,
    pedido_id       bigint REFERENCES pedidos(id) ON DELETE CASCADE,
    timestamp       timestamptz DEFAULT now(),
    usuario         text,           -- nombre de la vendedora o 'Admin'
    accion          text NOT NULL,  -- 'crear', 'editar', 'estado', 'eliminar'
    campo           text,           -- nombre del campo cambiado (NULL si crear)
    valor_anterior  text,
    valor_nuevo     text
);

CREATE INDEX IF NOT EXISTS idx_pedidos_log_pedido    ON pedidos_log(pedido_id);
CREATE INDEX IF NOT EXISTS idx_pedidos_log_timestamp ON pedidos_log(timestamp DESC);

-- RLS abierto (mismo patrón que el resto)
ALTER TABLE pedidos_log ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS pedidos_log_all ON pedidos_log;
CREATE POLICY pedidos_log_all ON pedidos_log FOR ALL USING (true) WITH CHECK (true);
