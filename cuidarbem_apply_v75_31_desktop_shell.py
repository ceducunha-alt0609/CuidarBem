from pathlib import Path
import base64
import re

INDEX = Path('index.html')
SW = Path('sw.js')
MARKER = '<!-- v75.23 — Desktop shell: topbar contínua + sidebar integrada + pesquisa global -->'
CHUNKS = [Path(f'cuidarbem_v75_31_chunk_{i:02d}.txt') for i in range(9)]

s = INDEX.read_text(encoding='utf-8')
if MARKER not in s:
    payload = ''.join(p.read_text(encoding='utf-8').strip() for p in CHUNKS)
    patch = base64.b64decode(payload).decode('utf-8')
    pos = s.rfind('</body>')
    if pos < 0:
        raise RuntimeError('final </body> not found')
    s = s[:pos] + patch + '\n' + s[pos:]
    INDEX.write_text(s, encoding='utf-8')
else:
    print('Desktop shell already present; index unchanged')

t = SW.read_text(encoding='utf-8')
new = "const CACHE_NAME = 'cuidarbem-v61-desktop-shell-v75-31';"
if new not in t:
    t = re.sub(r"const CACHE_NAME = 'cuidarbem-[^']+';", new, t, count=1)
SW.write_text(t, encoding='utf-8')
