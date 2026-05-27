-- ═══════════════════════════════════════════════════════════════════════
--  CRM Adorno — Schema para clientes 360° y compras
--  Espejo de Dragonfish (CLI + COMPROBANTEV + COMPROBANTEVDET)
--  Ejecutar UNA VEZ en Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════════════

-- ─── 1. CLIENTES (maestro deduplicado por GLOBALID) ───────────────────
CREATE TABLE IF NOT EXISTS clientes (
    globalid                 varchar(38) PRIMARY KEY,
    clcod_unicenter          varchar(10),                -- código en UNI1/UNI2 (pueden diferir)
    clcod_alcorta            varchar(10),                -- código en ALCO1/ALCO2
    apellido                 varchar(60),
    nombre                   varchar(120),               -- primer + segundo nombre concatenados
    nombre_completo          varchar(185),               -- CLNOM directo de Dragonfish
    cuit                     varchar(15),
    dni                      varchar(10),
    tipo_doc                 varchar(2),
    email                    varchar(250),
    telefono                 varchar(30),
    celular                  varchar(30),
    direccion                varchar(250),
    piso                     varchar(3),
    depto                    varchar(3),
    localidad                varchar(70),
    provincia                varchar(2),
    codigo_postal            varchar(8),
    pais                     varchar(3),
    fecha_alta               timestamptz,                -- CLFING
    vendedora_habitual       varchar(10),                -- CLVEND
    sexo                     varchar(10),
    hijos                    integer,
    observaciones            text,
    estado                   varchar(13),
    activo                   boolean DEFAULT true,
    locales_presentes        text[],                     -- ['unicenter','alcorta']
    -- Métricas agregadas (calculadas por el sync, NO en runtime)
    total_compras            numeric DEFAULT 0,
    cantidad_compras         integer DEFAULT 0,
    ticket_promedio          numeric DEFAULT 0,
    ultima_compra_fecha      timestamptz,
    primera_compra_fecha     timestamptz,
    sucursal_favorita        varchar(20),                -- 'unicenter' o 'alcorta'
    actualizado_en           timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_clientes_dni        ON clientes(dni);
CREATE INDEX IF NOT EXISTS idx_clientes_cuit       ON clientes(cuit);
CREATE INDEX IF NOT EXISTS idx_clientes_celular    ON clientes(celular);
CREATE INDEX IF NOT EXISTS idx_clientes_apellido   ON clientes(apellido);
CREATE INDEX IF NOT EXISTS idx_clientes_ultcompra  ON clientes(ultima_compra_fecha DESC);
CREATE INDEX IF NOT EXISTS idx_clientes_total      ON clientes(total_compras DESC);
-- Full-text search por nombre (útil para el buscador del panel)
CREATE INDEX IF NOT EXISTS idx_clientes_fts_nombre ON clientes USING gin (to_tsvector('spanish', coalesce(nombre_completo, '')));


-- ─── 2. COMPRAS (cabecera de comprobantes de venta) ───────────────────
CREATE TABLE IF NOT EXISTS compras (
    id                       text PRIMARY KEY,           -- {base_origen}:{CODIGO}
    cliente_globalid         varchar(38) REFERENCES clientes(globalid) ON DELETE SET NULL,
    cliente_clcod            varchar(10),
    local_id                 varchar(20),                -- 'unicenter' / 'alcorta'
    base_origen              varchar(20),                -- 'UNI1' / 'UNI2' / 'ALCO1' / 'ALCO2'
    fecha                    timestamptz,
    letra                    char(1),
    punto_venta              integer,
    numero                   bigint,
    tipo_comprobante         integer,
    vendedora                varchar(10),
    cuit_factura             varchar(15),
    cliente_factura          varchar(185),
    total                    numeric,
    subtotal                 numeric,
    total_descuento          numeric,
    total_iva                numeric,
    cantidad_items           numeric,
    anulado                  boolean DEFAULT false,
    observaciones            varchar(250)
);

CREATE INDEX IF NOT EXISTS idx_compras_cliente     ON compras(cliente_globalid);
CREATE INDEX IF NOT EXISTS idx_compras_fecha       ON compras(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_compras_local_fecha ON compras(local_id, fecha DESC);
CREATE INDEX IF NOT EXISTS idx_compras_anulado     ON compras(anulado) WHERE anulado = false;


-- ─── 3. COMPRAS_DETALLE (líneas de cada comprobante) ──────────────────
CREATE TABLE IF NOT EXISTS compras_detalle (
    compra_id                text REFERENCES compras(id) ON DELETE CASCADE,
    nro_item                 integer,
    sku                      varchar(15),
    descripcion              varchar(100),
    cantidad                 numeric,
    precio_unitario          numeric,
    monto_total              numeric,
    talle                    varchar(5),
    color                    varchar(6),
    PRIMARY KEY (compra_id, nro_item)
);

CREATE INDEX IF NOT EXISTS idx_cd_sku       ON compras_detalle(sku);
CREATE INDEX IF NOT EXISTS idx_cd_compra    ON compras_detalle(compra_id);


-- ─── 4. RLS — políticas abiertas (mismo patrón que articulos/pedidos) ─
ALTER TABLE clientes        ENABLE ROW LEVEL SECURITY;
ALTER TABLE compras         ENABLE ROW LEVEL SECURITY;
ALTER TABLE compras_detalle ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS clientes_all ON clientes;
CREATE POLICY clientes_all ON clientes FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS compras_all ON compras;
CREATE POLICY compras_all ON compras FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS compras_detalle_all ON compras_detalle;
CREATE POLICY compras_detalle_all ON compras_detalle FOR ALL USING (true) WITH CHECK (true);
