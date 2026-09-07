from pathlib import Path
import re

index=Path('index.html')
s=index.read_text(encoding='utf-8')

marker='cuidarbem-v75-49-risk-tight'
if marker not in s:
    patch='''

<!-- v75.49 — Mobile: compactação leve dos riscos previstos -->
<style id="cuidarbem-v75-49-risk-tight">
@media(max-width:767px){
  #cb75-risk-panel #cb75-risk-list{gap:7px!important;}
  #cb75-risk-panel .cb75-item{padding:9px 12px!important;min-height:0!important;}
  #cb75-risk-panel .cb75-item-icon{width:48px!important;height:48px!important;min-width:48px!important;}
  #cb75-risk-panel .cb75-item-title{line-height:1.22!important;}
  #cb75-risk-panel .cb75-item.cb7548-open{padding-top:11px!important;padding-bottom:11px!important;}
}
</style>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-49-risk-tight';",t,count=1)
sw.write_text(t,encoding='utf-8')
