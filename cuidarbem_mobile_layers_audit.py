from pathlib import Path
import re
s=Path('index.html').read_text(encoding='utf-8')
out=['CUIDARBEM MOBILE LAYERS AUDIT']
for term in ['premium-topbar','premium-icon-btn','premium-bell','backdrop-filter','will-change','translateZ(0)','position:fixed','position: fixed','diagnostico','diagnóstico','diagnostic','premium']:
    out.append(f'{term}={s.lower().count(term.lower())}')
# capture CSS rule heads containing risky compositor props
for prop in ['backdrop-filter','will-change','translateZ(0)']:
    out.append('\n=== RULES '+prop+' ===')
    for m in re.finditer(re.escape(prop),s,re.I):
        start=max(s.rfind('}',0,m.start())+1, s.rfind('{',0,m.start())-180)
        end=min(s.find('}',m.end())+1 if s.find('}',m.end())!=-1 else m.end()+300, len(s))
        snippet=s[start:end].strip().replace('\n',' ')
        out.append(snippet[:1000])
# premium/diagnostic HTML attributes and ids/classes
out.append('\n=== PREMIUM IDENTIFIERS ===')
idents=sorted(set(re.findall(r'(?:id|class)=["\'][^"\']*(?:premium|diagnos)[^"\']*["\']',s,re.I)))
out.extend(idents[:200])
# media mobile chunks mentioning premium topbar or backdrop
out.append('\n=== MOBILE HOT CHUNKS ===')
for m in re.finditer(r'@media\s*\(max-width\s*:\s*767px\)',s,re.I):
    chunk=s[m.start():m.start()+5000]
    if 'backdrop-filter' in chunk or 'premium' in chunk or 'will-change' in chunk or 'position:fixed' in chunk.replace(' ',''):
        out.append(chunk[:5000])
Path('cuidarbem_mobile_layers_report.txt').write_text('\n'.join(out),encoding='utf-8')
print('layers audit ok')
