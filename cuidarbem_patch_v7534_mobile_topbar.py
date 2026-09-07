from pathlib import Path
import re
p=Path('index.html'); s=p.read_text(encoding='utf-8')
marker='cuidarbem-v75-83-more-navigation-fix'
if marker not in s:
 patch=r'''
<!-- v75.83 — Mobile: Mais usa a navegação real do app -->
<script id="cuidarbem-v75-83-more-navigation-fix">
(function(){
 function closeMore(){var sh=document.getElementById('cb7581-more-sheet');if(sh)sh.classList.remove('open')}
 function closePatient(){var ps=document.getElementById('cb7581-patient-screen');if(ps)ps.classList.remove('open')}
 function go(name){
  closeMore();closePatient();
  var btn=document.getElementById('nav-'+name);
  if(typeof window.goScreen==='function' && btn){window.goScreen(name,btn);return true}
  if(btn){btn.click();return true}return false;
 }
 function setup(){
  var sheet=document.getElementById('cb7581-more-sheet');
  if(sheet && !sheet.dataset.cb7583){sheet.dataset.cb7583='1';sheet.addEventListener('click',function(e){
    var b=e.target.closest('[data-go]');if(!b)return;
    var g=b.dataset.go;
    if(g==='consulta'){e.preventDefault();e.stopImmediatePropagation();go('appt')}
    else if(g==='perfil'){e.preventDefault();e.stopImmediatePropagation();go('profile')}
  },true)}
  var ps=document.getElementById('cb7581-patient-screen');
  if(ps && !ps.dataset.cb7583){ps.dataset.cb7583='1';ps.addEventListener('click',function(e){
    var b=e.target.closest('[data-section]');if(!b)return;
    e.preventDefault();e.stopImmediatePropagation();go('profile');
  },true)}
  /* engrenagem flutuante = acessibilidade, não Perfil/Configurações */
  var fab=document.querySelector('.a11y-fab');
  if(fab)fab.style.display='flex';
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup);else setup();
 setTimeout(setup,300);setTimeout(setup,900);
})();
</script>
'''
 pos=s.rfind('</body>')
 if pos<0: raise SystemExit('body not found')
 s=s[:pos]+patch+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-83-more-navigation-fix';",t,count=1);sw.write_text(t,encoding='utf-8')
