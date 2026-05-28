-- ═══════════════════════════════════════════════════════════════════════
--  CRM ADORNO — Alerta de 60 min en estado 'Avisado'
--
--  Flujo:
--    Pendiente → Listo para avisar → Avisado → Respondió / No contestó → Completado
--
--  Cuando un pedido pasa a 'Avisado', se guarda timestamp en `avisado_at`.
--  El frontend muestra alertas para los pedidos donde:
--      estado = 'Avisado' AND avisado_at < now() - 60 min
--  Cuando la vendedora confirma "Respondió" o "No contestó", el estado cambia
--  y la alerta desaparece sola.
-- ═══════════════════════════════════════════════════════════════════════

-- ─── Migración: renombrar el estado viejo ───
UPDATE pedidos SET estado = 'No contestó' WHERE estado = 'Sin Respuesta';

-- ─── Nueva columna: cuándo pasó a Avisado ───
ALTER TABLE pedidos
    ADD COLUMN IF NOT EXISTS avisado_at timestamptz;
COMMENT ON COLUMN pedidos.avisado_at IS
'Timestamp de cuando el pedido pasó a estado Avisado. Se usa para disparar la alerta de los 60min.';

-- ─── Trigger: setear avisado_at automáticamente cuando el estado pase a Avisado ───
CREATE OR REPLACE FUNCTION pedidos_set_avisado_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    -- Caso 1: paso de cualquier estado a 'Avisado' → setear el timestamp
    IF NEW.estado = 'Avisado' AND (OLD.estado IS NULL OR OLD.estado <> 'Avisado') THEN
        NEW.avisado_at = now();
    END IF;
    -- Caso 2: ya no está más en 'Avisado' (pasó a Respondió / No contestó / Completado / etc.)
    -- → limpiar el timestamp para que no aparezca como vencido por error
    IF NEW.estado <> 'Avisado' AND OLD.estado = 'Avisado' THEN
        -- Nota: no borramos avisado_at para mantener auditoría — el frontend filtra por estado
        -- de todos modos. Si querés auditar, dejá esta línea comentada.
        NULL;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_pedidos_avisado_at ON pedidos;
CREATE TRIGGER trg_pedidos_avisado_at
    BEFORE INSERT OR UPDATE OF estado ON pedidos
    FOR EACH ROW
    EXECUTE FUNCTION pedidos_set_avisado_at();

-- ─── Backfill: los pedidos que YA están en 'Avisado' pero no tienen avisado_at ───
-- Como no tenemos updated_at, usamos created_at como aproximación.
-- (Esto puede sobrestimar la antigüedad si el pedido se demoró en pasar a Avisado,
-- pero garantiza que todos los avisados actuales aparezcan en la alerta de 60min.)
UPDATE pedidos
SET avisado_at = created_at
WHERE estado = 'Avisado' AND avisado_at IS NULL;

-- ─── Índice para que la query del frontend sea rápida ───
CREATE INDEX IF NOT EXISTS idx_pedidos_avisado_vencido
    ON pedidos(avisado_at)
    WHERE estado = 'Avisado';
