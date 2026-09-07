from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Mantém a estrutura fonte da v75.79 e apenas garante que o renderizador original
# rode também no carregamento inicial da PWA (antes ele era chamado ao trocar de guia).
marker='cuidarbem-v75-80-upcoming-initial-render'
if marker not in s:
    patch=r'''
<!-- v75.80 — Consultas/Exames: render inicial também no refresh -->
<script id="cuidarbem-v75-80-upcoming-initial-render">
(function(){
  function renderNow(){
    try{
      if(typeof window.renderApptUpcoming==='function'){
        window.renderApptUpcoming();
        return true;
      }
      if(typeof renderApptUpcoming==='function'){
        renderApptUpcoming();
        return true;
      }
    }catch(e){}
    return false;
  }
  function boot(){
    renderNow();
    setTimeout(renderNow,120);
    setTimeout(renderNow,400);
    setTimeout(renderNow,900);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot,{once:true});
  else boot();
  window.addEventListener('load',function(){setTimeout(renderNow,60)},{once:true});
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos<0: raise SystemExit('body not found')
    s=s[:pos]+patch+'\n'+s[pos:]

p.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-80-upcoming-initial-render';",t,count=1)
sw.write_text(t,encoding='utf-8')
