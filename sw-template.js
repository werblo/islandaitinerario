// Generato da render.py a partire da sw-template.js: non modificare sw.js a mano.
const VERSION = '__APP_VERSION__';
const APP_CACHE = 'islanda-2026-app-' + VERSION;
const TILE_CACHE = 'islanda-2026-tiles';
const LIVE_CACHE = 'islanda-2026-live';

// Pagina, Leaflet, icone e tutte le foto usate dall'app: scaricati
// all'installazione, così l'app funziona offline dalla prima apertura.
const PRECACHE = __PRECACHE__;

self.addEventListener('install', (event) => {
  // cache: 'reload' salta la cache HTTP del browser: si scarica davvero
  // la versione appena pubblicata (anche una foto sostituita con lo stesso nome).
  event.waitUntil(
    caches.open(APP_CACHE).then((cache) =>
      cache.addAll(PRECACHE.map((u) => new Request(u, { cache: 'reload' }))))
  );
  // Niente skipWaiting qui: la nuova versione si attiva alla riapertura
  // dell'app (la pagina lo chiede quando non la stai usando).
});

self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) => Promise.all(
      names
        .filter((n) => n.startsWith('islanda-2026-') && ![APP_CACHE, TILE_CACHE, LIVE_CACHE].includes(n))
        .map((n) => caches.delete(n))
    )).then(() => self.clients.claim())
  );
});

function tileKey(url) {
  // a/b/c.tile.openstreetmap.org servono le stesse tile: una sola copia in cache
  return 'https://tile.openstreetmap.org' + url.pathname;
}

function putIfOk(cacheName, key, res) {
  if (res && res.ok) {
    const clone = res.clone();
    caches.open(cacheName).then((cache) => cache.put(key, clone));
  }
  return res;
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Tile della mappa: cache-first (restano visibili offline)
  if (url.hostname.endsWith('tile.openstreetmap.org')) {
    const key = tileKey(url);
    event.respondWith(
      caches.open(TILE_CACHE).then((cache) => cache.match(key)).then((cached) =>
        cached || fetch(req).then((res) => putIfOk(TILE_CACHE, key, res)))
    );
    return;
  }

  if (url.origin === self.location.origin) {
    // Foto: subito quella in cache, intanto si riscarica in background
    // (stale-while-revalidate) così una foto sostituita si aggiorna online.
    if (url.pathname.includes('/images/')) {
      event.respondWith(
        caches.open(APP_CACHE).then((cache) => cache.match(req, { ignoreSearch: true })).then((cached) => {
          const fresh = fetch(req, { cache: 'no-cache' })
            .then((res) => putIfOk(APP_CACHE, req, res))
            .catch(() => cached);
          if (cached) { event.waitUntil(fresh); return cached; }
          return fresh;
        })
      );
      return;
    }
    // Pagina e file statici: dalla cache della versione installata
    // (coerente con il service worker), rete solo se mancano.
    const isPage = req.mode === 'navigate';
    event.respondWith(
      caches.open(APP_CACHE)
        .then((cache) => cache.match(isPage ? 'index.html' : req, { ignoreSearch: true }))
        .then((cached) => cached || fetch(req))
    );
    return;
  }

  // Dati live (meteo, aurora, cambio, percorsi OSRM di riserva):
  // rete prima, ultimo dato salvato se offline.
  event.respondWith(
    fetch(req, { cache: 'no-store' })
      .then((res) => putIfOk(LIVE_CACHE, req, res))
      .catch(() => caches.open(LIVE_CACHE).then((cache) => cache.match(req)))
  );
});

// Avvisi aurora: notifica push mandata dal workflow "Avvisi aurora" su GitHub,
// mostrata anche ad app chiusa. Toccandola si apre l'app.
self.addEventListener('push', (event) => {
  let data = {};
  try { data = event.data ? event.data.json() : {}; } catch (e) { data = { body: event.data && event.data.text() }; }
  event.waitUntil(self.registration.showNotification(data.title || 'Aurora boreale', {
    body: data.body || '',
    tag: data.tag || 'aurora',
    renotify: true,
    icon: 'icons/icon-192.png',
    lang: 'it',
  }));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((list) => {
      const open = list.find((c) => new URL(c.url).pathname.startsWith(new URL(self.registration.scope).pathname));
      return open ? open.focus() : self.clients.openWindow(self.registration.scope);
    })
  );
});
