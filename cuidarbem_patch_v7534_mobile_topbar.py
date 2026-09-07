from pathlib import Path
import re

index=Path('index.html')
s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-51-agenda-no-duplicate'
if marker not in s:
    patch=r'''

<!-- v75.51 — Mobile: Agenda mantém progresso + painel original do calendário -->
<style id="cuidarbem-v75-51-agenda-no-duplicate">
@media(max-width:767px){
  #cb7550-agenda-today > .section-header,
  #cb7550-agenda-today > .section-header + .card{display:none!important;}
}
</style>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8')

sw=Path('sw.js'); t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-51-agenda-no-duplicate';",t,count=1)
sw.write_text(t,encoding='utf-8')
