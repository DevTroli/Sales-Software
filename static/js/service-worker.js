self.addEventListener('install', event => {
    event.waitUntil(
      caches.open('v1').then(cache => {
        return cache.addAll([
          '/',
          '/static/css/styles.css',
          '/static/js/main.js',
          '/static/js/service-worker.js',
          '/static/images/icons-192.png',
          '/static/images/icons-512.png',
          '/manifest.json'
        ]);
      })
    );
  });
  
  self.addEventListener('fetch', event => {
    event.respondWith(
      caches.match(event.request).then(response => {
        return response || fetch(event.request);
      })
    );
  });
  