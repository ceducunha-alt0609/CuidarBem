from pathlib import Path

idxp=Path('index.html'); s=idxp.read_text(encoding='utf-8')

def rep(old,new,label,count=1):
    global s
    got=s.count(old)
    assert got>=count, f'{label}: expected {count}, got {got}'
    s=s.replace(old,new,count)

# Restore explicit PWA metadata using the files that actually exist.
rep('''<!-- manifest, favicon e icon-192 omitidos — app single-file, arquivos externos causariam 404 -->''', '''<link rel="manifest" href="./manifest.webmanifest">
<link rel="icon" href="./icons/favicon.ico">
<link rel="apple-touch-icon" href="./icons/icon-180.png">''', 'PWA head metadata')

# Demo seed: only on a truly fresh install, never after the user intentionally empties tasks.
rep("if (tasks.length === 0) addSampleTasks();", "if (localStorage.getItem('cuidarbem_tasks') === null) addSampleTasks();", 'demo resurrection guard')

# Local calendar dates instead of UTC slices.
rep("const tomorrowStr_ = tomorrow.toISOString().split('T')[0];", "const tomorrowStr_ = localDateKey(tomorrow);", 'tomorrow local date')
rep("function todayStr() { return new Date().toISOString().split('T')[0]; }", "function localDateKey(d = new Date()) {\n  const y = d.getFullYear();\n  const m = String(d.getMonth() + 1).padStart(2, '0');\n  const day = String(d.getDate()).padStart(2, '0');\n  return `${y}-${m}-${day}`;\n}\nfunction todayStr() { return localDateKey(new Date()); }", 'today local date')
idxp.write_text(s,encoding='utf-8')

# Service worker isolation + reliable shell paths.
swp=Path('sw.js'); w=swp.read_text(encoding='utf-8')
assert "const CACHE_NAME = 'cuidarbem-pwa-v53-init-fix-icons';" in w
w=w.replace("const CACHE_NAME = 'cuidarbem-pwa-v53-init-fix-icons';", "const CACHE_PREFIX = 'cuidarbem-';\nconst CACHE_NAME = 'cuidarbem-v54-audit-safety';",1)
start=w.index('const APP_SHELL = ['); end=w.index('];',start)+2
w=w[:start]+'''const APP_SHELL = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/favicon.ico'
];'''+w[end:]
w=w.replace("keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))", "keys.filter(k => k.startsWith(CACHE_PREFIX) && k !== CACHE_NAME).map(k => caches.delete(k))",1)
swp.write_text(w,encoding='utf-8')

# Primary manifest paths.
mp=Path('manifest.webmanifest'); m=mp.read_text(encoding='utf-8')
for size in ['48','72','96','128','144','152','180','192','512']:
    m=m.replace(f'"src": "icon-{size}.png"', f'"src": "icons/icon-{size}.png"')
mp.write_text(m,encoding='utf-8')

# Legacy manifest kept compatible for older installs/caches.
lp=Path('manifest.json'); lm=lp.read_text(encoding='utf-8')
lm=lm.replace('"src": "icon-192.png"','"src": "icons/icon-192.png"')
lm=lm.replace('"src": "icon-512.png"','"src": "icons/icon-512.png"')
lp.write_text(lm,encoding='utf-8')

# Invariants.
s2=idxp.read_text(encoding='utf-8'); w2=swp.read_text(encoding='utf-8')
for needle in [
    'rel="manifest" href="./manifest.webmanifest"',
    "localStorage.getItem('cuidarbem_tasks') === null",
    'function localDateKey',
    'const tomorrowStr_ = localDateKey(tomorrow);'
]: assert needle in s2, needle
assert "if (tasks.length === 0) addSampleTasks();" not in s2
assert "new Date().toISOString().split('T')[0]" not in s2
assert "k.startsWith(CACHE_PREFIX)" in w2
assert "./icons/icon-192.png" in w2
assert "cuidarbem-v54-audit-safety" in w2
assert '"src": "icons/icon-192.png"' in mp.read_text(encoding='utf-8')
print('CuidarBem first safety patch OK')
