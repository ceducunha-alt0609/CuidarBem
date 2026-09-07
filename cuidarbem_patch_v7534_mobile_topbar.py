from pathlib import Path
import re

index=Path('index.html')
s=index.read_text(encoding='utf-8')

# v75.43 — corrige a desmarcação na origem, dentro do mesmo escopo de getTodayLog/saveTodayLog.
old="window.setCB75Quick = function(key,val,btn){ saveTodayLog({[key]:val}, 'cb75-state'); pushHaptic([12]); };"
new="window.setCB75Quick = function(key,val,btn){ const log=getTodayLog(); const next=(log && log[key]===val) ? '' : val; saveTodayLog({[key]:next}, 'cb75-state'); pushHaptic([12]); };"
if old in s:
    s=s.replace(old,new,1)

marker='cuidarbem-v75-43-toggle-at-source'
if marker not in s:
    patch='''\n<!-- v75.43 — Estado Geral: seleção reversível corrigida na origem -->\n<meta id="cuidarbem-v75-43-toggle-at-source" data-fix="state-toggle-source">\n'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]

index.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-43-toggle-at-source';",t,count=1)
sw.write_text(t,encoding='utf-8')
