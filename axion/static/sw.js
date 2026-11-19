// AXION Progressive Web App — Service Worker
const CACHE_NAME = 'axion-pwa-v2';

// Resolve base scope from service worker registration
function getBaseScope() {
  try {
    return new URL(self.registration.scope).pathname;
  } catch {
    return '/';
  }
}

function getPrecacheUrls() {
  const base = getBaseScope().replace(/\/$/, '');
  return [
    `${base}/`,
    `${base}/index.html`,
    `${base}/manifest.webmanifest`,
    `${base}/favicon.svg`,
    `${base}/icons/icon-192.png`,
    `${base}/icons/icon-512.png`,
    `${base}/icons/icon-maskable.png`,
    `${base}/icons/apple-touch-icon.png`
  ];
}

// Install: Pre-cache core application shell safely
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      const urls = getPrecacheUrls();
      await Promise.allSettled(
        urls.map(async (url) => {
          try {
            const res = await fetch(url);
            if (res.ok) {
              await cache.put(url, res);
            }
          } catch {
            // Non-blocking: allow offline precache to succeed even if single asset isn't ready
          }
        })
      );
    }).then(() => self.skipWaiting())
  );
});

// Activate: Purge obsolete caches and claim clients immediately
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

// Fetch: Network-first for API, Stale-While-Revalidate for UI assets
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  if (request.method !== 'GET') {
    return;
  }

  // API endpoints: Network-first, fallback to offline response
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).catch(() => {
        return new Response(
          JSON.stringify({
            error: 'Offline',
            detail: 'You are working offline. Responses will sync when reconnected.'
          }),
          {
            headers: { 'Content-Type': 'application/json' },
            status: 503
          }
        );
      })
    );
    return;
  }

  // Web App Navigations (HTML): Network first with fallback to cached index.html
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.status === 200) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return response;
        })
        .catch(async () => {
          const cache = await caches.open(CACHE_NAME);
          const base = getBaseScope();
          return (
            (await cache.match(request)) ||
            (await cache.match(`${base}index.html`)) ||
            (await cache.match(base)) ||
            (await cache.match('/index.html')) ||
            (await cache.match('/'))
          );
        })
    );
    return;
  }

  // Static Assets, Fonts & Images: Cache-first, then network update
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      const fetchPromise = fetch(request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const copy = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return networkResponse;
        })
        .catch(() => cachedResponse);

      return cachedResponse || fetchPromise;
    })
  );
});
