const CACHE='parkgolf-v30';
const ASSETS=['./','./index.html','./manifest.json','./assets/icons/icon-192.png','./assets/icons/icon-512.png'];
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)))});
self.addEventListener('activate',e=>e.waitUntil(
  caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())
));
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  e.respondWith(
    caches.match(e.request).then(r=>{
      if(r)return r;
      return fetch(e.request).then(res=>{
        if(res&&res.status===200&&res.type==='basic'){
          const cl=res.clone();caches.open(CACHE).then(c=>c.put(e.request,cl));
        }
        return res;
      }).catch(()=>e.request.mode==='navigate'?caches.match('./index.html'):new Response('',{status:404}));
    })
  );
});
