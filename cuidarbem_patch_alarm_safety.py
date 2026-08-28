from pathlib import Path
p=Path('sw.js')
s=p.read_text(encoding='utf-8')
s=s.replace("const CACHE_NAME = 'cuidarbem-v55-sync-conflict-guard';","const CACHE_NAME = 'cuidarbem-v56-alarm-lifecycle-guard';")
s=s.replace("function scheduleAlarms(alarms) {\n  clearScheduledAlarms();", "function scheduleAlarms(alarms) {\n  clearScheduledAlarms();\n  // Best-effort only: service workers may be suspended/terminated by the OS.\n  // Timers are intentionally limited to the next 24h and must be refreshed by the app.")
s=s.replace("self.addEventListener('message', event => {", "self.addEventListener('activate', event => {\n  // In-memory timers do not survive a worker restart. Ask any open client to refresh them.\n  event.waitUntil(\n    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(list => {\n      list.forEach(client => client.postMessage({ type: 'REQUEST_ALARM_REFRESH' }));\n    })\n  );\n});\n\nself.addEventListener('message', event => {")
p.write_text(s,encoding='utf-8')

p=Path('index.html')
s=p.read_text(encoding='utf-8')
anchor="function requestNotifPermission() {"
insert="""// Alarm lifecycle guard: the browser/Android can terminate a service worker and discard its in-memory timers.\n// Whenever the app returns to the foreground, refresh the next 24h schedule.\n(function installAlarmLifecycleRefresh(){\n  function refreshSoon(){\n    if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {\n      setTimeout(function(){ if (typeof scheduleAlarmsOnSW === 'function') scheduleAlarmsOnSW(); }, 250);\n    }\n  }\n  document.addEventListener('visibilitychange', function(){ if (!document.hidden) refreshSoon(); });\n  window.addEventListener('pageshow', refreshSoon);\n  if ('serviceWorker' in navigator) {\n    navigator.serviceWorker.addEventListener('message', function(event){\n      if (event.data && event.data.type === 'REQUEST_ALARM_REFRESH') refreshSoon();\n    });\n  }\n})();\n\n"""
if insert.strip() not in s:
    if anchor not in s: raise SystemExit('request permission anchor missing')
    s=s.replace(anchor,insert+anchor,1)
p.write_text(s,encoding='utf-8')
# trigger workflow
