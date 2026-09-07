from pathlib import Path
import re

index=Path('index.html'); s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-58-health-final-today'
if marker not in s:
    patch=r'''

<!-- v75.58 — Saúde: remove definitivamente o HOJE original -->
<style id="cuidarbem-v75-58-health-final-today">
@media(max-width:767px){
  #screen-dashboard .health-dashboard > .health-section-label.cb7558-original-today{display:none!important;}
}
</style>
<script id="cuidarbem-v75-58-health-final-today-js">
(function(){
 function clean(){
   var rings=document.getElementById('dash-rings');
   if(!rings)return;
   var label=rings.previousElementSibling;
   if(label && label.classList.contains('health-section-label')) label.classList.add('cb7558-original-today');
 }
 document.addEventListener('DOMContentLoaded',clean);
 var n=0,x=setInterval(function(){clean();if(document.querySelector('.cb7558-original-today')||++n>50)clearInterval(x);},200);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-58-health-final-today';",t,count=1);sw.write_text(t,encoding='utf-8')
