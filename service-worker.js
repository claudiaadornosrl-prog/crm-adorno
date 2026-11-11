// ════════════════════════════════════════════════════════════════
//  CRM Adorno — Service Worker
//  Estrategia: network-first para HTML/datos, cache-first para assets
// ════════════════════════════════════════════════════════════════

// (4-nov-2026) Al publicar, cambiar también CRM_VERSION en index.html (mismo texto): el número se ve arriba en el CRM y
// las pestañas abiertas con una versión más vieja avisan "Actualizar a vN"
const CACHE_VERSION = 'crm-adorno-v107-banner-comun';
const CACHE_ASSETS = [
  './',
  './index.html',
  './manual.js',
  './manifest.json',
  './icon-192-v2.png',
  './icon-512-v2.png',
  './favicon.png',
  './fonts/URWGothic-Book.ttf',
];

// Install: cachear el shell mínimo
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then(cache => cache.addAll(CACHE_ASSETS))
      .catch(err => console.warn('[SW] Cache addAll error:', err))
  );
  self.skipWaiting();
});

// Activate: limpiar caches viejos
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch:
//  - Navegaciones (HTML): network-first, fallback al index cacheado (offline)
//  - Assets propios: cache-first
//  - APIs (Supabase, externos): solo network (no cachear datos)
self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Saltar APIs externas y assets de CDN (los cachean ellos)
  if (
    url.hostname.includes('supabase.co') ||
    url.hostname.includes('jsdelivr.net') ||
    url.hostname.includes('cdnjs.cloudflare.com')
  ) {
    return;  // dejar que el browser maneje
  }

  // (4-nov-2026) el control de versión del CRM pide este archivo: siempre a la red, nunca al cache
  if (url.pathname.endsWith('/service-worker.js')) return;

  // Navegación HTML: network-first
  // (4-nov-2026) cache 'no-cache': GitHub Pages manda max-age=600 y el navegador podía dar una página de hasta 10
  // minutos atrás aunque ya hubiera una versión nueva publicada (JP: "estoy corriendo versiones viejas"); así revalida
  // siempre con el servidor (si no cambió, vuelve un 304 sin bajar todo)
  if (req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html')) {
    event.respondWith(
      fetch(req, { cache: 'no-cache' })
        .then(resp => {
          // Actualizar cache del index si la response es OK
          if (resp && resp.ok) {
            const clone = resp.clone();
            caches.open(CACHE_VERSION).then(c => c.put('./index.html', clone));
          }
          return resp;
        })
        .catch(() => caches.match('./index.html'))
    );
    return;
  }

  // Otros assets propios: cache-first con fallback a red
  event.respondWith(
    caches.match(req).then(cached => {
      if (cached) return cached;
      return fetch(req).then(resp => {
        if (resp && resp.ok) {
          const clone = resp.clone();
          caches.open(CACHE_VERSION).then(c => c.put(req, clone));
        }
        return resp;
      }).catch(() => cached);
    })
  );
});
