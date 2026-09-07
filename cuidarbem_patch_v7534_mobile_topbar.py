from pathlib import Path
import re

index=Path('index.html')
s=index.read_text(encoding='utf-8')

marker='cuidarbem-v75-47-center-state-actions'
if marker not in s:
    patch='''

<!-- v75.47 — Mobile: centraliza Atualizar leitura + Abrir Saúde -->
<style id="cuidarbem-v75-47-center-state-actions">
@media (max-width:767px){
  #cb75-state-card .cb75-actions{
    justify-content:center !important;
    width:100% !important;
    margin-left:auto !important;
    margin-right:auto !important;
  }
}
</style>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]

index.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-47-center-state-actions';",t,count=1)
sw.write_text(t,encoding='utf-8')
