from pathlib import Path
import re

index=Path('index.html'); s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-56-hide-orphan-today'
if marker not in s:
    patch=r'''

<!-- v75.56 — Mobile: remove HOJE órfão em Saúde -->
<style id="cuidarbem-v75-56-hide-orphan-today">
@media(max-width:767px){#cb7556-orphan-today{display:none!important;}}
</style>
<script id="cuidarbem-v75-56-hide-orphan-today-js">
(function(){
 function clean(){
   var vital=document.getElementById('vital-chart'); if(!vital)return;
   var card=vital.closest('.card'); if(!card)return;
   var node=card.previousElementSibling, guard=0;
   while(node && guard++<5){
     var text=(node.textContent||'').replace(/\s+/g,' ').trim();
     if(text==='HOJE'){node.id='cb7556-orphan-today';return;}
     node=node.previousElementSibling;
   }
 }
 document.addEventListener('DOMContentLoaded',clean);var n=0,x=setInterval(function(){clean();if(document.getElementById('cb7556-orphan-today')||++n>50)clearInterval(x);},250);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-56-hide-orphan-today';",t,count=1);sw.write_text(t,encoding='utf-8')
