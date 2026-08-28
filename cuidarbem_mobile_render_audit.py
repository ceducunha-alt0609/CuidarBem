from pathlib import Path
import re
s=Path('index.html').read_text(encoding='utf-8')
terms=['premium','diagnost','position: fixed','position:fixed','backdrop-filter','filter:','will-change','transform:','translateZ','animation:','transition:','touchstart','touchmove','pointerdown','pointerup','onclick=','addEventListener','wheel','preventDefault','overflow-y','overflow:hidden']
out=['CUIDARBEM MOBILE/DESKTOP RENDER AUDIT']
for t in terms:
    out.append(f'{t}={s.lower().count(t.lower())}')
patterns=['premium','diagnost','backdrop-filter','will-change','translateZ','position: fixed','position:fixed','touchstart','touchmove','wheel','preventDefault','screen-home','desktop-right-panel']
for p in patterns:
    out.append('\n=== '+p+' ===')
    hits=list(re.finditer(re.escape(p),s,re.I))
    for m in hits[:20]:
        a=max(0,m.start()-1200); b=min(len(s),m.end()+2600)
        out.append(s[a:b])
Path('cuidarbem_mobile_render_report.txt').write_text('\n'.join(out),encoding='utf-8')
print('audit ok')
