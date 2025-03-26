// Service Worker with enhanced offline support for Django
const CACHE_NAME = 'django-app-v3';
const OFFLINE_URL = '/offline/';
const CORE_ASSETS = [
  '/',
  '/offline/',
];

// Install - Cache core assets and offline page
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(CORE_ASSETS);
      })
      .then(() => self.skipWaiting()))
});

// Activate - Clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            return caches.delete(cache);
          }
        })
      );
    })
    .then(() => {
      return self.clients.claim();
    })
  );
});

// Fetch - Network first with cache fallback
self.addEventListener('fetch', event => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  const requestUrl = new URL(event.request.url);

  // Handle API requests separately
  if (isApiRequest(event.request)) {
    event.respondWith(handleApiRequest(event.request));
    return;
  }

  // Handle HTML pages (including offline fallback)
  if (isHtmlRequest(event.request)) {
    event.respondWith(
      fetch(event.request)
        .then(response => cacheThenReturn(event.request, response))
        .catch(() => {
          return caches.match(OFFLINE_URL);
        })
    );
    return;
  }

  // Default cache-first strategy for static assets
  event.respondWith(
    caches.match(event.request)
      .then(cached => cached || fetchAndCache(event.request))
  );
});

// Helper Functions
function isApiRequest(request) {
  return request.url.includes('/api/') || 
         request.headers.get('accept')?.includes('application/json');
}

function isHtmlRequest(request) {
  return request.headers.get('accept')?.includes('text/html');
}

async function handleApiRequest(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      await cacheApiResponse(request, response);
    }
    return response.clone();
  } catch (err) {
    const cached = await caches.match(request);
    return cached || jsonOfflineResponse();
  }
}

async function fetchAndCache(request) {
  const response = await fetch(request);
  if (response.ok) {
    const cache = await caches.open(CACHE_NAME);
    await cache.put(request, response.clone());
  }
  return response;
}

async function cacheThenReturn(request, response) {
  const cache = await caches.open(CACHE_NAME);
  await cache.put(request, response.clone());
  return response;
}

async function cacheApiResponse(request, response) {
  const cache = await caches.open(CACHE_NAME);
  await cache.put(request, response.clone());
}

function jsonOfflineResponse() {
  return new Response(
    JSON.stringify({ error: "You're offline", retry: true }),
    { headers: { 'Content-Type': 'application/json' } }
  );
}
