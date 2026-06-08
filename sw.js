// 서비스 워커 비활성화 — 모든 이전 캐시 삭제
self.addEventListener('install', e => {
  e.waitUntil(
    caches.keys().then(ks => Promise.all(ks.map(k => caches.delete(k))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(ks => Promise.all(ks.map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// 캐시 없이 항상 네트워크에서 가져옴
self.addEventListener('fetch', e => {
  e.respondWith(fetch(e.request));
});
