from pathlib import Path
import re

index=Path('index.html')
s=index.read_text(encoding='utf-8')

# v75.46 — remove somente o JS antigo da v75.44 que interceptava os cliques
# com stopImmediatePropagation antes da v75.45. Mantém o CSS do botão Limpar.
s, n = re.subn(
    r'\n?<script id="cuidarbem-v75-44-state-picker-direct-js">.*?</script>\n?',
    '\n', s, count=1, flags=re.S
)

marker='cuidarbem-v75-46-remove-picker-conflict'
if marker not in s:
    patch='''\n<!-- v75.46 — Estado Geral: remove listener antigo conflitante da v75.44 -->\n<meta id="cuidarbem-v75-46-remove-picker-conflict" data-fix="picker-listener-conflict">\n'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]

index.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-46-remove-picker-conflict';",t,count=1)
sw.write_text(t,encoding='utf-8')
