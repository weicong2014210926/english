/* 英语趣学 H5 · Service Worker
   应用壳缓存策略：导航请求网络优先(离线回退 index.html)，静态资源缓存优先(动态兜底)。
   版本号变更即触发更新。 */
const CACHE = 'eq-h5-v1';
const SHELL = [
  '.',
  'index.html',
  'manifest.webmanifest',
  'icon.svg',
  'css/styles.css',
  'js/words.js',
  'js/sm2.js',
  'js/app.js',
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;

  // 导航（页面打开）：网络优先，失败回退缓存首页，保证离线可进
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).catch(() => caches.match('index.html')));
    return;
  }
  // 静态资源：缓存优先，未命中再网络并写入缓存
  e.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      const copy = res.clone();
      caches.open(CACHE).then((c) => c.put(req, copy));
      return res;
    }).catch(() => hit))
  );
});
