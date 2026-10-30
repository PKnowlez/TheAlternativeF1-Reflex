// The Alternative F1 Service Worker
const CACHE_NAME = 'alt-f1-cache-v1';
const PRECACHE_ASSETS = [
  '/',
  '/manifest.json',
  '/Icons/icon-192.png',
  '/Icons/icon-512.png',
  '/Icons/IconLogoApp.png',
  '/style.css'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_ASSETS).catch((err) => {
        console.warn('[PWA] Pre-caching asset error (non-fatal):', err);
      });
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  // Only handle standard http(s) GET requests
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);

  // Avoid intercepting Reflex WebSocket / event streams or external auth
  if (url.pathname.startsWith('/_event') || url.pathname.startsWith('/_ping')) {
    return;
  }

  // Network-first strategy with cache fallback
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        // Cache successful local asset responses
        if (networkResponse && networkResponse.status === 200 && url.origin === self.location.origin) {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return networkResponse;
      })
      .catch(async () => {
        const cachedResponse = await caches.match(event.request);
        if (cachedResponse) {
          return cachedResponse;
        }
        // If navigating to a page while offline, return cached root
        if (event.request.mode === 'navigate') {
          return caches.match('/');
        }
        return new Response('Network offline', { status: 503, statusText: 'Offline' });
      })
  );
});
