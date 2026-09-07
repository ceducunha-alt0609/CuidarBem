from pathlib import Path
import re
p=Path('index.html'); s=p.read_text(encoding='utf-8')
marker='cuidarbem-v75-84-more-cleanup-a11y-fix'
if marker not in s:
 patch=r'''
<!-- v75.84 — Mobile: Mais sem duplicidade + engrenagem funcional -->
<style id="cuidarbem-v75-84-more-cleanup-a11y-fix">
@media(max-width:767px){
 #a11y-panel.cb7584-force-open{opacity:1!important;pointer-events:auto!important;transform:scale(1) translateY(0)!important;display:block!important}
}
</style>
<script id="cuidarbem-v75-84-more-cleanup-a11y-fix-js">
(function(){
 function setup(){
  var sheet=document.getElementById('cb7581-more-sheet');
  if(sheet){
   var dup=sheet.querySelector('[data-go="consulta"]');
   if(dup)dup.remove();
  }
  var fab=document.getElementById('a11y-fab'), panel=document.getElementById('a11y-panel');
  if(fab && panel && !fab.dataset.cb7584){
   fab.dataset.cb7584='1';
   fab.onclick=null;
   fab.addEventListener('click',function(e){
    e.preventDefault();e.stopPropagation();
    var open=!panel.classList.contains('cb7584-force-open');
    panel.classList.toggle('cb7584-force-open',open);
    panel.classList.toggle('open',open);
   },true);
   document.addEventListener('click',function(e){
    if(!panel.contains(e.target)&&!fab.contains(e.target)){
      panel.classList.remove('cb7584-force-open','open');
    }
   },true);
  }
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup);else setup();
 setTimeout(setup,250);setTimeout(setup,800);
})();
</script>
'''
 pos=s.rfind('</body>')
 if pos<0: raise SystemExit('body not found')
 s=s[:pos]+patch+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-84-more-cleanup-a11y-fix';",t,count=1);sw.write_text(t,encoding='utf-8')
