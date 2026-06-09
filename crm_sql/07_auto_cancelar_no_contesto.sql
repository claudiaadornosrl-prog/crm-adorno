-- ═══════════════════════════════════════════════════════════════════════
-- 07. AUTO-CANCELACIÓN de pedidos sin respuesta después del re-contacto
-- ═══════════════════════════════════════════════════════════════════════
-- Flow del CRM (revisado con JP, 2026-06-08):
--   Pendiente → Listo para avisar → Avisado
--     ├─ Respondió → (espera) → Completado
--     └─ No contestó
--         └─ 72h después del primer aviso (fecha_aviso) → se le manda refuerzo
--             ├─ Respondió → Completado
--             └─ NO responde 24h después del re-contacto → AUTO-CANCELAR
-- ═══════════════════════════════════════════════════════════════════════

-- Columna para registrar cuándo fue el re-contacto
ALTER TABLE pedidos
    ADD COLUMN IF NOT EXISTS fecha_recontacto timestamptz;

CREATE INDEX IF NOT EXISTS idx_pedidos_recontacto
    ON pedidos(fecha_recontacto)
    WHERE fecha_recontacto IS NOT NULL;

COMMENT ON COLUMN pedidos.fecha_recontacto IS
'Cuándo se envió el WA de refuerzo al cliente (template recontactar). NULL si todavía no se hizo. Usado para auto-cancelar si pasan 24h sin respuesta.';

-- ═══════════════════════════════════════════════════════════════════════
-- RPC: auto-cancelar pedidos 'No contestó' con re-contacto hace +24h
-- ═══════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION crm_auto_cancelar_no_contesto()
RETURNS int
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_cancelados int;
BEGIN
    WITH actualizados AS (
        UPDATE pedidos
        SET estado = 'Cancelado',
            fecha_completado = NOW()   -- usamos fecha_completado como timestamp final
        WHERE estado = 'No contestó'
          AND motivo = 'Avisar cuando ingrese'   -- solo este motivo usa el flow auto
          AND fecha_recontacto IS NOT NULL
          AND fecha_recontacto < NOW() - INTERVAL '24 hours'
        RETURNING id
    )
    SELECT COUNT(*) INTO v_cancelados FROM actualizados;

    -- Registrar en pedidos_log (best-effort)
    BEGIN
        INSERT INTO pedidos_log (pedido_id, usuario, accion, campo, valor_anterior, valor_nuevo)
        SELECT p.id, 'sistema', 'estado', 'estado', 'No contestó', 'Cancelado'
        FROM pedidos p
        WHERE p.estado = 'Cancelado'
          AND p.fecha_completado > NOW() - INTERVAL '1 minute';
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    RETURN v_cancelados;
END;
$$;

GRANT EXECUTE ON FUNCTION crm_auto_cancelar_no_contesto() TO authenticated, anon;

COMMENT ON FUNCTION crm_auto_cancelar_no_contesto() IS
'Cancela automáticamente pedidos en estado No contestó cuyo re-contacto fue hace +24h. Retorna cantidad cancelada. Llamada por el cliente JS al cargar la app (renderHoy) y por el sync nocturno de Dragonfish.';

SELECT '✅ 07_auto_cancelar_no_contesto.sql aplicado' AS status;
