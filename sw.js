// CuidarBem PWA Service Worker
const CACHE_PREFIX = 'cuidarbem-';
const CACHE_NAME = 'cuidarbem-v59-desktop-wheel-fix';
const APP_SHELL = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/favicon.ico'
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL).catch(() => null))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith(CACHE_PREFIX) && k !== CACHE_NAME).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
      .then(() => clients.matchAll({ type: 'window', includeUncontrolled: true }))
      .then(list => {
        // In-memory timers do not survive a worker restart. Ask open clients to refresh them.
        list.forEach(client => client.postMessage({ type: 'REQUEST_ALARM_REFRESH' }));
      })
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    fetch(event.request)
      .then(response => {
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone)).catch(() => null);
        return response;
      })
      .catch(() => caches.match(event.request).then(cached => cached || caches.match('./index.html')))
  );
});

let alarmTimers = [];

function clearScheduledAlarms() {
  alarmTimers.forEach(id => clearTimeout(id));
  alarmTimers = [];
}

function scheduleAlarms(alarms) {
  clearScheduledAlarms();
  // Best-effort only: service workers may be suspended/terminated by the OS.
  // Timers are intentionally limited to the next 24h and must be refreshed by the app.
  const now = Date.now();
  (alarms || []).forEach(alarm => {
    const delay = alarm.fireAt - now;
    if (delay < 0 || delay > 24 * 60 * 60 * 1000) return;
    const id = setTimeout(() => {
      self.registration.showNotification(alarm.title || 'CuidarBem', {
        body: alarm.body || 'Você tem um cuidado programado.',
        icon: alarm.icon || './icons/icon-192.png',
        badge: './icons/icon-192.png',
        tag: alarm.tag || 'cb-alarm',
        renotify: alarm.renotify !== false,
        requireInteraction: alarm.requireInteraction || false,
        vibrate: alarm.phase === 'before' ? [160, 80, 160] : [220, 100, 220, 100, 220],
        actions: [{ action: 'open', title: 'Abrir CuidarBem' }],
        data: { taskId: alarm.taskId, phase: alarm.phase, url: self.registration.scope }
      });
    }, delay);
    alarmTimers.push(id);
  });
}

self.addEventListener('message', event => {
  if (!event.data) return;
  if (event.data.type === 'SCHEDULE_ALARMS') scheduleAlarms(event.data.alarms);
  if (event.data.type === 'CANCEL_ALARMS') clearScheduledAlarms();
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  const url = event.notification.data && event.notification.data.url ? event.notification.data.url : self.registration.scope;
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(list => {
      for (const client of list) {
        if ('focus' in client) return client.focus();
      }
      if (clients.openWindow) return clients.openWindow(url);
    })
  );
});