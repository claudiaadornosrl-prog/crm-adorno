-- ═══════════════════════════════════════════════════════════════════════
--  CRM ADORNO — RLS en tablas de catálogo (SEG-2)
--
--  Cierra las 4 alertas restantes de Supabase. Pre-requisito: el sync
--  (sync_dragonfish.py) ya usa service_role, que IGNORA RLS — así sigue
--  escribiendo el catálogo sin problema.
--
--  Modelo:
--    - articulos / locales / sku_map: lectura abierta (el CRM los lee;
--      no son datos sensibles), escritura solo service_role (el sync).
--    - sync_log: cerrado a público (solo lo escribe el sync con service_role).
-- ═══════════════════════════════════════════════════════════════════════

-- ─── articulos: lectura pública, escritura solo service_role ───
ALTER TABLE articulos ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS articulos_read ON articulos;
CREATE POLICY articulos_read ON articulos FOR SELECT TO anon, authenticated USING (true);

-- ─── locales: lectura pública (el CRM lo usa para nombres/db_codes) ───
ALTER TABLE locales ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS locales_read ON locales;
CREATE POLICY locales_read ON locales FOR SELECT TO anon, authenticated USING (true);

-- ─── sku_map: lectura pública ───
ALTER TABLE sku_map ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS sku_map_read ON sku_map;
CREATE POLICY sku_map_read ON sku_map FOR SELECT TO anon, authenticated USING (true);

-- ─── sync_log: cerrado a público (solo service_role escribe, bypassa RLS) ───
ALTER TABLE sync_log ENABLE ROW LEVEL SECURITY;
-- sin policies para anon/authenticated → nadie más que service_role accede
