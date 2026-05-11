const CACHE='parkgolf-v60';
const ASSETS=['./','./index.html','./manifest.json','./assets/icons/icon-192.png','./assets/icons/icon-512.png'];
const CDN_URLS=['https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js'];
self.addEventListener('install',e=>{e.waitUntil(
  caches.open(CACHE).then(c=>c.addAll(ASSETS).then(()=>Promise.allSettled(CDN_URLS.map(u=>fetch(u).then(r=>{if(r.ok)return c.put(u,r)})))))
  .then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(res=>{if(res.ok){const cl=res.clone();caches.open(CACHE).then(c=>c.put(e.request,cl))}return res}).catch(()=>caches.match('./index.html'))))});
