from pathlib import Path
import re
p=Path('index.html')
s=p.read_text(encoding='utf-8')
pattern=r'\n\s*<div class="vitals-bar vitals-cards-grid header-vitals-row" id="vitals-bar-main">.*?</div>\s*\n(?=\s*</div>\s*\n\s*</header>|\s*<div class="header-wave|\s*<main|\s*<div class="content)'
m=re.search(pattern,s,re.S)
if not m:
    # safer structural fallback: locate opening and balance nested divs
    marker='<div class="vitals-bar vitals-cards-grid header-vitals-row" id="vitals-bar-main">'
    start=s.find(marker)
    if start<0: raise SystemExit('topbar vitals container not found')
    pos=start; depth=0; end=None
    tag=re.compile(r'</?div\b[^>]*>',re.I)
    for tm in tag.finditer(s,start):
        if tm.group(0).lower().startswith('</div'): depth-=1
        else: depth+=1
        if depth==0:
            end=tm.end(); break
    if end is None: raise SystemExit('could not balance topbar vitals container')
    s=s[:start]+s[end:]
else:
    s=s[:m.start()]+'\n'+s[m.end():]
if 'id="vitals-bar-main"' in s: raise SystemExit('topbar vitals still present')
# Keep dashboard vital tracking intact.
for anchor in ['id="tab-bp"','id="tab-gluc"','id="tab-spo2"','id="tab-temp"']:
    if anchor not in s: raise SystemExit(f'dashboard vital control unexpectedly missing: {anchor}')
p.write_text(s,encoding='utf-8')
