// Define cache name and assets to cache
const CACHE_NAME = 'my-app-cache-v1';
const BASE_URL = self.location.origin;

// URLs to cache (both static and dynamic)
const urlsToCache = [
  '/',  '/home/', '/api/', '/tasks/'
];

// Install event - cache base assets
self.addEventListener('install', event => {
  console.log('[Service Worker] Install Event triggered'); // Add console.log
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[Service Worker] Caching app shell'); // Add console.log
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('[Service Worker] Install completed'); // Add console.log
      })
      .catch(error => {
        console.error('[Service Worker] Install failed:', error); // Add console.error
      })
  );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', event => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    console.log('[Service Worker] Fetch event ignored for non-GET request:', event.request.url); // Add console.log
    return;
  }

  // Handle AJAX requests
  if (event.request.headers.get('accept').includes('application/json') || 
      event.request.url.includes('/api/')) {
    console.log('[Service Worker] Fetching AJAX request:', event.request.url); // Add console.log
    event.respondWith(
      fetchAndCache(event.request)
    );
    return;
  }

  // For other requests, try cache first
  console.log('[Service Worker] Fetching request:', event.request.url); // Add console.log
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          console.log('[Service Worker] Found in cache:', event.request.url); // Add console.log
          return response;
        }
        console.log('[Service Worker] Not found in cache, fetching from network:', event.request.url); // Add console.log
        return fetchAndCache(event.request);
      })
  );
});

// Helper function to fetch and cache
function fetchAndCache(request) {
  return fetch(request)
    .then(response => {
      // Check if we received a valid response
      if (!response || response.status !== 200 || response.type !== 'basic') {
        console.log('[Service Worker] Invalid response:', response); // Add console.log
        return response;
      }

      // Clone the response (stream can only be consumed once)
      const responseToCache = response.clone();

      // Cache the response
      caches.open(CACHE_NAME)
        .then(cache => {
          console.log('[Service Worker] Caching response:', request.url); // Add console.log
          cache.put(request, responseToCache);
        });

      return response;
    })
    .catch(error => {
      console.error('[Service Worker] Fetch failed:', error); // Add console.error
      // If fetch fails, try to return cached version
      return caches.match(request)
        .then(response => {
          if (response) {
            console.log('[Service Worker] Serving cached fallback for:', request.url); // Add console.log
            return response;
          }
          console.error('[Service Worker] No cached version available for:', request.url); // Add console.error
          return Promise.reject('No cached version available');
        });
    });
}

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activate Event triggered'); // Add console.log
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            console.log('[Service Worker] Deleting old cache:', cacheName); // Add console.log
            return caches.delete(cacheName);
          }
          return null;
        }).filter(promise => promise) //filter out null promises
      );
    }).then(()=>{
      console.log('[Service Worker] Activate completed'); // Add console log
    })
  );
});