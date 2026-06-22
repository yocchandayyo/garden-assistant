/* みどりのAI庭師 Service Worker */
const CACHE = "garden-v1";
const ASSETS = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icon-180.png",
  "./icon-192.png",
  "./icon-512.png"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
  );
  self.clients.claim();
});

/* network-first：更新を優先しつつ、オフライン時はキャッシュにフォールバック */
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;                 // Gemini への POST 等は素通し
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;  // 外部リクエストはキャッシュしない
  e.respondWith(
    fetch(req).then(res => {
      const clone = res.clone();
      caches.open(CACHE).then(c => c.put(req, clone)).catch(() => {});
      return res;
    }).catch(() => caches.match(req).then(m => m || caches.match("./index.html")))
  );
});

/* 通知タップでアプリを前面に */
self.addEventListener("notificationclick", e => {
  e.notification.close();
  e.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then(list => {
      for (const c of list) { if ("focus" in c) return c.focus(); }
      if (clients.openWindow) return clients.openWindow("./");
    })
  );
});
