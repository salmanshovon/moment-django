const CACHE_NAME = 'my-app-cache-v2';  // ← Change version to force update
const OFFLINE_URL = '/offline/';       // Add a fallback page

const urlsToCache = [
  '/',
  '/offline/',
  // Remove dynamic routes (cache them in fetch handler instead)
  // '/users/home/',  // ← Problematic! Cache this dynamically
  // '/api/'         // ← Handle API caching separately
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
      .then(() => self.skipWaiting())  // ← Force active state
  );
});

self.addEventListener('fetch', event => {
  // Handle API/JSON requests
  if (event.request.url.includes('/api/') || 
      event.request.headers.get('accept').includes('application/json')) {
    event.respondWith(
      fetch(event.request)
        .then(res => cacheApiResponse(event.request, res))
        .catch(() => caches.match(OFFLINE_URL))
    );
    return;
  }

  // Cache-first strategy for static assets
  event.respondWith(
    caches.match(event.request)
      .then(cached => cached || fetchAndCache(event.request))
  );
});

async function fetchAndCache(request) {
  try {
    const res = await fetch(request);
    const cache = await caches.open(CACHE_NAME);
    await cache.put(request, res.clone());
    return res;
  } catch (err) {
    const cached = await caches.match(request);
    return cached || caches.match(OFFLINE_URL);
  }
}