// ═══════════════════════════════════════════════════════════════════════
//  CRM Adorno · manual.js — Manual de uso (overlay 📖, autoinyectable)
//  🚨 REGLA: cada vez que se agrega o cambia una función del módulo,
//  actualizar la sección correspondiente acá (y bump del ?v= en index.html).
// ═══════════════════════════════════════════════════════════════════════

function _mEsc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function _manualSecciones() {
  const admin = (typeof session !== 'undefined') && session?.isAdmin;

  const base = [
    {
      icon: '🔐', titulo: 'Entrar una sola vez',
      desc: 'La sesión se comparte entre todos los módulos del sistema.',
      pasos: [
        'En el Hub, con el ícono 👤 de arriba, ingresás con tu usuario y podés tildar "Confiar en esta computadora".',
        'Con eso tildado, entrás a todos los módulos de ese equipo sin volver a escribir la clave.',
        'En las computadoras de los locales, que usan varias personas, NO se tilda: cada módulo sigue pidiendo usuario y contraseña por separado.',
        'Al salir de cualquier módulo se cierra la sesión en todos. La computadora sigue marcada como de confianza hasta que lo apagues desde el Hub.',
      ],
    },
    {
      icon: '📅', titulo: 'Hoy',
      desc: 'El tablero del día: qué pedidos necesitan acción ahora.',
      pasos: [
        'Arriba ves los pedidos "Listos para avisar" (llegó la mercadería → hay que avisar a la clienta).',
        'Los avisados sin respuesta hace más de 60 minutos aparecen en alerta — hay que reintentar el contacto.',
        'También lista recontactos programados, pedidos viejos sin resolver y los cumpleaños del día.',
        'El ranking del local muestra los pedidos completados de la semana por vendedora.',
      ],
    },
    {
      icon: '➕', titulo: 'Nuevo pedido',
      desc: 'Cargar el encargo de una clienta cuando no hay stock o hay que traerlo.',
      pasos: [
        'Cargá el DNI o CUIT: si la clienta ya compró alguna vez, el sistema la detecta solo y completa sus datos.',
        'Agregá los artículos buscando por descripción o SKU (salen de Dragonfish, con stock real).',
        'Anotá seña si dejó, y cualquier aclaración en las notas.',
        'El pedido arranca en estado "Pendiente".',
      ],
    },
    {
      icon: '📦', titulo: 'Pedidos',
      desc: 'El listado completo con el circuito de estados de cada pedido.',
      pasos: [
        'El circuito es: Pendiente → Listo para avisar → Avisado → Respondió / No contestó → Completado o Cancelado.',
        'Cuando llega la mercadería, pasá el pedido a "Listo para avisar".',
        'El botón de WhatsApp arma el mensaje solo, con la plantilla que corresponde al estado.',
        'Al avisar, marcá "Avisado" — si en 60 minutos no hay respuesta, el sistema te lo recuerda solo.',
        'Filtrá por vendedora, estado o etiquetas para encontrar rápido lo que buscás.',
      ],
    },
    {
      icon: '👥', titulo: 'Clientes',
      desc: 'La base de clientas: datos, historial de compras y etiquetas.',
      pasos: [
        'Buscá por nombre, DNI o CUIT — están todas las clientas de Dragonfish.',
        'La ficha muestra el historial completo de compras y los pedidos que hizo.',
        'Podés ponerle etiquetas (tags) para agruparlas y filtrarlas después.',
      ],
    },
    {
      icon: '⏰', titulo: 'Alertas',
      desc: 'Todos los pedidos que están esperando una acción tuya.',
      pasos: [
        'Concentra los avisados sin respuesta (+60 min) y otros vencimientos.',
        'El numerito rojo del encabezado te dice cuántas alertas hay sin resolver.',
      ],
    },
    {
      icon: '⭐', titulo: 'Satisfacción',
      desc: 'Las encuestas que las clientas responden después de completar su pedido.',
      pasos: [
        'Cada pedido completado dispara una encuesta (Google Forms); las respuestas se ven acá.',
        'Sirve para ver cómo venimos en atención por local y por vendedora.',
      ],
    },
    {
      icon: '🔍', titulo: 'Buscador y ajustes',
      desc: 'Herramientas del encabezado, siempre a mano.',
      pasos: [
        'La lupa 🔍 (o Ctrl+B) busca en todo: clientes, pedidos, productos y facturas.',
        '🌙 cambia entre tema claro y oscuro.',
        '↻ actualiza los datos sin recargar la página.',
      ],
    },
  ];

  if (admin) {
    base.push({
      icon: '🛠', titulo: 'Admin',
      desc: 'Panel de administración — solo JP.',
      pasos: [
        'Auditoría: registro de todos los cambios (quién tocó qué y cuándo).',
        'Demanda no satisfecha: qué pidieron las clientas que no teníamos — insumo para compras.',
        'Gestión de vendedoras, plantillas de WhatsApp y configuración general.',
      ],
    });
  }
  return base;
}

function abrirManual() {
  if (document.getElementById('manual-overlay')) return;
  const items = _manualSecciones();
  const ov = document.createElement('div');
  ov.id = 'manual-overlay';
  ov.innerHTML = `
    <div class="m-box">
      <div class="m-head">
        <span style="font-size:22px;">📖</span>
        <div style="flex:1;">
          <div style="font-weight:700;font-size:16px;">Manual · CRM</div>
          <div style="font-size:12px;opacity:.85;">Guía rápida de cada herramienta del módulo</div>
        </div>
        <button class="m-close" onclick="cerrarManual()">✕</button>
      </div>
      ${items.map((s, i) => `
        <div class="m-sec">
          <div class="m-tit">${s.icon} ${i + 1}. ${_mEsc(s.titulo)}</div>
          <div class="m-desc">${_mEsc(s.desc)}</div>
          <ul class="m-pasos">${s.pasos.map(p => `<li>${_mEsc(p)}</li>`).join('')}</ul>
        </div>`).join('')}
      <div class="m-foot">💡 Este manual se actualiza junto con el sistema. ¿Falta algo o no funciona? Avisale a JP.</div>
    </div>`;
  ov.addEventListener('click', e => { if (e.target === ov) cerrarManual(); });
  document.body.appendChild(ov);
  _manualLupa(ov);
  document.body.style.overflow = 'hidden';
}

function cerrarManual() {
  const ov = document.getElementById('manual-overlay');
  if (ov) ov.remove();
  document.body.style.overflow = '';
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') cerrarManual(); });

(function _manualInit() {
  const css = document.createElement('style');
  css.textContent = `
    #manual-overlay{position:fixed;inset:0;background:rgba(15,23,42,.55);z-index:9999;display:flex;align-items:flex-start;justify-content:center;padding:20px 12px;overflow-y:auto;-webkit-overflow-scrolling:touch;}
    #manual-overlay .m-box{background:#f8fafc;border-radius:14px;max-width:760px;width:100%;padding-bottom:6px;box-shadow:0 20px 60px rgba(0,0,0,.3);}
    #manual-overlay .m-head{position:sticky;top:0;background:#0f6e56;color:#fff;padding:14px 18px;border-radius:14px 14px 0 0;display:flex;align-items:center;gap:10px;z-index:1;}
    #manual-overlay .m-close{background:rgba(255,255,255,.18);border:none;color:#fff;font-size:16px;border-radius:8px;padding:6px 11px;cursor:pointer;}
    #manual-overlay .m-sec{background:#fff;border:1px solid #e2e8f0;border-left:4px solid #0f6e56;border-radius:10px;margin:14px 14px 0;padding:14px 18px;}
    #manual-overlay .m-tit{font-weight:700;font-size:15px;margin-bottom:4px;color:#064e3b;}
    #manual-overlay .m-desc{font-size:13px;color:#475569;margin-bottom:8px;}
    #manual-overlay .m-pasos{margin:0 0 2px 18px;padding:0;font-size:13px;line-height:1.65;color:#334155;}
    #manual-overlay .m-pasos li{margin-bottom:4px;}
    #manual-overlay .m-foot{margin:16px 14px 12px;background:#fef3c7;border-left:4px solid #d97706;border-radius:8px;padding:11px 14px;font-size:12.5px;color:#92400e;}`;
  document.head.appendChild(css);

  const hdr = document.querySelector('.header-right');
  if (hdr) {
    const b = document.createElement('button');
    b.className = 'header-search-btn';
    b.title = 'Manual de uso';
    b.textContent = '📖';
    b.onclick = () => abrirManual();
    hdr.insertBefore(b, hdr.firstChild);
  }
})();

// ── 🔍 Lupa del manual (29-sep, pedido Contreras): busca por palabra, sin tildes ni mayúsculas.
//    Deja solo las secciones que la contienen, dentro de ellas los pasos que la contienen,
//    y resalta la palabra. Mismo bloque en todos los módulos (el de RRHH usa _mLupaFiltrar).
function _mLupaNorm(s){ return String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
function _mLupaMarcar(el, q){
  const nodos = [], w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) nodos.push(w.currentNode);
  nodos.forEach(n => {
    const t = n.nodeValue; let norm = '', mapa = [];
    for (let i = 0; i < t.length; i++){ const c = _mLupaNorm(t[i]); for (let k = 0; k < c.length; k++){ norm += c[k]; mapa.push(i); } }
    let desde = 0, pos, frag = null, ult = 0;
    while (q && (pos = norm.indexOf(q, desde)) >= 0){
      frag = frag || document.createDocumentFragment();
      const a = mapa[pos], b = mapa[pos + q.length - 1] + 1;
      if (a > ult) frag.appendChild(document.createTextNode(t.slice(ult, a)));
      const m = document.createElement('mark'); m.textContent = t.slice(a, b);
      m.style.cssText = 'background:#fde047;color:inherit;padding:0 1px;border-radius:3px'; frag.appendChild(m);
      ult = b; desde = pos + q.length;
    }
    if (frag){ if (ult < t.length) frag.appendChild(document.createTextNode(t.slice(ult))); n.parentNode.replaceChild(frag, n); }
  });
}
function _mLupaFiltrar(cont, selSec, texto, info){
  if (!cont) return;
  const q = _mLupaNorm(String(texto || '').trim());
  let vistas = 0;
  cont.querySelectorAll(selSec).forEach(sec => {
    if (sec.dataset.mOrig == null) sec.dataset.mOrig = sec.innerHTML; else sec.innerHTML = sec.dataset.mOrig;
    if (!q){ sec.style.display = ''; return; }
    const lis = [...sec.querySelectorAll('li')];
    const enLis = lis.filter(li => _mLupaNorm(li.textContent).includes(q));
    const hay = _mLupaNorm(sec.textContent).includes(q);
    sec.style.display = hay ? '' : 'none';
    if (!hay) return;
    vistas++;
    if (enLis.length) lis.forEach(li => { if (!enLis.includes(li)) li.style.display = 'none'; });
    _mLupaMarcar(sec, q);
  });
  if (info) info.textContent = !q ? '' : vistas ? `${vistas} ${vistas === 1 ? 'sección' : 'secciones'} con «${String(texto).trim()}»` : `No encontré «${String(texto).trim()}» en el manual.`;
  const primera = q && cont.querySelector('mark');
  if (primera) primera.scrollIntoView({block: 'center', behavior: 'smooth'});
}
function _manualLupa(ov){
  const head = ov && ov.querySelector('.m-head'); if (!head) return;
  head.style.flexWrap = 'wrap';
  const box = document.createElement('div');
  box.style.cssText = 'flex-basis:100%;display:flex;gap:8px;align-items:center;margin-top:8px';
  box.innerHTML = '<input type="search" placeholder="🔍 Buscar en el manual (por ej.: equivalencias, remito, echeq)…" '
    + 'style="flex:1;min-width:0;padding:8px 11px;border-radius:9px;border:none;font-size:14px;color:#0f172a;font-family:inherit">'
    + '<span class="m-lupa-info" style="font-size:12px;opacity:.9;white-space:nowrap"></span>';
  head.appendChild(box);
  const inp = box.querySelector('input'), info = box.querySelector('.m-lupa-info');
  let t = null;
  inp.addEventListener('input', () => { clearTimeout(t); t = setTimeout(() => _mLupaFiltrar(ov, '.m-sec', inp.value, info), 250); });
  inp.addEventListener('keydown', e => { if (e.key === 'Escape' && inp.value){ e.stopPropagation(); inp.value = ''; _mLupaFiltrar(ov, '.m-sec', '', info); } });
  setTimeout(() => inp.focus(), 50);
}
