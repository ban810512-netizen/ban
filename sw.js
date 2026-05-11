const CACHE='parkgolf-v13';
const ASSETS=['./','./index.html','./manifest.json','./assets/icons/icon-192.png','./assets/icons/icon-512.png'];
const CDN_URLS=['https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>Promise.all([c.addAll(ASSETS),...CDN_URLS.map(u=>fetch(u).then(r=>c.put(u,r)).catch(()=>{}))])).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(nr=>{if(nr&&nr.status===200){const c=nr.clone();caches.open(CACHE).then(ca=>ca.put(e.request,c))}return nr}).catch(()=>new Response('Offline',{status:503}))))});
