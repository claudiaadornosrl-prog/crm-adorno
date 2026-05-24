// ════════════════════════════════════════════════════════════════
//  CRM Adorno — Service Worker
//  Estrategia: network-first para HTML/datos, cache-first para assets
// ════════════════════════════════════════════════════════════════

const CACHE_VERSION = 'crm-adorno-v1';
const CACHE_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './favicon.png',
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

  // Navegación HTML: network-first
  if (req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html')) {
    event.respondWith(
      fetch(req)
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
