from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
repls={
    "icon: 'icon-192.png'":"icon: 'icons/icon-192.png'",
    "badge: 'icon-192.png'":"badge: 'icons/icon-192.png'",
    'icon: "icon-192.png"':'icon: "icons/icon-192.png"',
    'badge: "icon-192.png"':'badge: "icons/icon-192.png"',
}
changed=0
for old,new in repls.items():
    c=s.count(old)
    if c:
        s=s.replace(old,new)
        changed += c
if changed == 0:
    raise SystemExit('no notification icon path anchors found')
if "icon: 'icon-192.png'" in s or "badge: 'icon-192.png'" in s:
    raise SystemExit('old notification icon paths remain')
p.write_text(s,encoding='utf-8')
print('replacements', changed)
