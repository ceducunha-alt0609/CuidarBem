from pathlib import Path
import re
s=Path('index.html').read_text(encoding='utf-8')
out=['CUIDARBEM UTC DATE AUDIT']
patterns=[r'toISOString\(\)\.split\(["\']T["\']\)\[0\]',r'toISOString\(\)\.slice\(0,\s*10\)',r'toISOString\(\)\.slice\(0,\s*7\)']
for pat in patterns:
    hits=list(re.finditer(pat,s))
    out.append(f'\nPATTERN {pat} count={len(hits)}')
    for i,m in enumerate(hits,1):
        p=m.start(); out.append(f'\n--- hit {i} ---\n'+s[max(0,p-900):min(len(s),p+1200)])
Path('cuidarbem_utc_dates_audit.txt').write_text('\n'.join(out),encoding='utf-8')
