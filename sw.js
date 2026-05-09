// CuidarBem PWA Service Worker
const CACHE_NAME = 'cuidarbem-pwa-v33-home-mais-baixo';
const APP_SHELL = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-48.png',
  './icon-72.png',
  './icon-96.png',
  './icon-128.png',
  './icon-144.png',
  './icon-152.png',
  './icon-180.png',
  './icon-192.png',
  './icon-512.png',
  './favicon.ico'
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL).catch(() => null))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
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
  const now = Date.now();
  (alarms || []).forEach(alarm => {
    const delay = alarm.fireAt - now;
    if (delay < 0 || delay > 24 * 60 * 60 * 1000) return;
    const id = setTimeout(() => {
      self.registration.showNotification(alarm.title || 'CuidarBem', {
        body: alarm.body || 'Você tem um cuidado programado.',
        icon: alarm.icon || './icon-192.png',
        badge: './icon-192.png',
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