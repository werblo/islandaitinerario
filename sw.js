const CACHE_NAME = 'islanda-2026-v4';

const APP_SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-180.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) => Promise.all(
      names.filter((n) => n !== CACHE_NAME).map((n) => caches.delete(n))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Cache-first per tutto cio che, una volta scaricato, non cambia piu:
  //  - le foto in images/
  //  - i tile della mappa (richiesti come <img> da Leaflet): cosi le zone
  //    gia visualizzate online restano visibili anche offline
  //  - la libreria Leaflet, che ha un URL versionato quindi immutabile
  const isStatic = url.pathname.includes('/images/')
    || req.destination === 'image'
    || url.hostname === 'unpkg.com';

  if (isStatic) {
    // Cache-first: una volta visti restano disponibili offline.
    event.respondWith(
      caches.match(req).then((cached) => cached || fetch(req).then((res) => {
        if (res && res.ok) {
          const clone = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
        }
        return res;
      }).catch(() => cached))
    );
    return;
  }

  // Tutto il resto (pagina, meteo/aurora live, ecc.): rete prima (dati
  // sempre aggiornati quando c'e connessione), cache come riserva offline
  // (l'ultima risposta valida ricevuta, incluse le previsioni meteo).
  event.respondWith(
    fetch(req, { cache: 'no-store' }).then((res) => {
      if (res && res.ok) {
        const clone = res.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
      }
      return res;
    }).catch(() => caches.match(req))
  );
});
