from pathlib import Path
import re
s=Path('index.html').read_text(encoding='utf-8')
out=['CUIDARBEM STRUCTURAL AUDIT','']
# top-level-ish function declarations
funcs=re.findall(r'(?m)^function\s+([A-Za-z_$][\w$]*)\s*\(',s)
from collections import Counter
fc=Counter(funcs)
out.append('FUNCTION DECLARATIONS DUPLICATES:')
for k,v in sorted(fc.items(), key=lambda x:(-x[1],x[0])):
    if v>1: out.append(f'{k}={v}')
# const/let patch aliases
aliases=re.findall(r'const\s+(_orig[A-Za-z0-9_$]+)\s*=\s*window\.([A-Za-z0-9_$]+)',s)
out.append('\nPATCH ALIASES:')
for a,b in aliases: out.append(f'{a} <- {b}')
# repeated event listener signatures rough
listeners=re.findall(r'addEventListener\(\s*[\"\']([^\"\']+)[\"\']',s)
lc=Counter(listeners)
out.append('\nEVENT LISTENER COUNTS:')
for k,v in sorted(lc.items(), key=lambda x:(-x[1],x[0])): out.append(f'{k}={v}')
# premium/diag/version markers
for term in ['premium','cb-effects-cleanup','cb-diag-btn','_orig','PATCH','v48','v75','LOCKED','TRAVADO']:
    out.append(f'COUNT {term}={s.count(term)}')
# snippets around duplicate functions and patches
for name,v in fc.items():
    if v>1:
        out.append(f'\n=== DUP FUNCTION {name} ({v}) ===')
        for m in list(re.finditer(r'(?m)^function\s+'+re.escape(name)+r'\s*\(',s))[:8]:
            p=m.start(); out.append(s[max(0,p-500):min(len(s),p+1400)].replace('\n',' '))
out.append('\n=== PATCH CONTEXTS ===')
for m in list(re.finditer(r'_orig[A-Za-z0-9_$]+',s))[:40]:
    p=m.start(); out.append(s[max(0,p-450):min(len(s),p+1100)].replace('\n',' '))
Path('cuidarbem_structural_audit.txt').write_text('\n'.join(out),encoding='utf-8')
