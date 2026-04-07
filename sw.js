/* Service Worker — Economic Map 오프라인 캐시 */
const CACHE_NAME = 'economic-map-v5';
const STATIC_ASSETS = [
  './',
  './index.html',
  './d3.min.js',
  './data/data.json',
  './data/values.json',
];

/* Install: 정적 자산 프리캐시 */
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

/* Activate: 이전 캐시 정리 */
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

/* Fetch: Network-first for data, Cache-first for static */
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  /* data/values.json → network first (fresh data), fallback to cache */
  if (url.pathname.endsWith('/values.json')) {
    event.respondWith(
      fetch(event.request)
        .then((resp) => {
          const clone = resp.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          return resp;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  /* 기타 → cache first, fallback to network */
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request).then((resp) => {
        if (resp.ok && url.origin === self.location.origin) {
          const clone = resp.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return resp;
      });
    })
  );
});
