// Retired: the old GEWAS cache-first worker. This version clears its caches and unregisters itself.
self.addEventListener('install', () => self.skipWaiting())
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.map((k) => caches.delete(k)))).then(() => self.registration.unregister()).then(() => self.clients.matchAll()).then((cs) => cs.forEach((c) => c.navigate(c.url))))
})
