from pathlib import Path
import re
s=Path('index.html').read_text(encoding='utf-8')
terms=['premium','diagnost','position: fixed','position:fixed','backdrop-filter','filter:','will-change','transform:','translateZ','animation:','transition:','touchstart','touchmove','pointerdown','pointerup','onclick=','addEventListener']
out=['CUIDARBEM MOBILE RENDER AUDIT']
for t in terms:
    out.append(f'{t}={s.lower().count(t.lower())}')
patterns=['premium','diagnost','backdrop-filter','will-change','translateZ','position: fixed','position:fixed','touchstart','touchmove']
for p in patterns:
    out.append('\n=== '+p+' ===')
    for m in list(re.finditer(re.escape(p),s,re.I))[:12]:
        a=max(0,m.start()-700); b=min(len(s),m.end()+1400)
        out.append(s[a:b])
Path('cuidarbem_mobile_render_report.txt').write_text('\n'.join(out),encoding='utf-8')
print('audit ok')
