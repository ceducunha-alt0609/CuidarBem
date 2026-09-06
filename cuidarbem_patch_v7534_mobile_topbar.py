from pathlib import Path
import re

index=Path('index.html')
s=index.read_text(encoding='utf-8')

# v75.38 — apenas centraliza o conjunto dos dois comandos restantes do Resumo do Dia no mobile.
marker='cuidarbem-v75-38-center-summary-actions'
if marker not in s:
    patch='''

<!-- v75.38 — Mobile: centraliza Comando por voz + Queda/sintoma -->
<style id="cuidarbem-v75-38-center-summary-actions">
@media (max-width:767px){
  #screen-home .home-ai-actions,
  #screen-home .summary-actions,
  #screen-home .ai-actions,
  #screen-home .quick-actions{
    justify-content:center !important;
  }
}
</style>
<script id="cuidarbem-v75-38-center-summary-actions-js">
(function(){
  'use strict';
  function norm(v){return (v||'').replace(/\s+/g,' ').trim().toLowerCase();}
  function center(){
    if(window.innerWidth>=768)return;
    var root=document.querySelector('#screen-home');
    if(!root)return;
    var buttons=Array.from(root.querySelectorAll('button,a,[role="button"]'));
    var voice=buttons.find(function(el){var t=norm(el.textContent);return t.indexOf('comando por voz')!==-1;});
    var fall=buttons.find(function(el){var t=norm(el.textContent);return t.indexOf('queda/sintoma')!==-1;});
    if(!voice||!fall)return;
    var p=voice.parentElement;
    if(p&&p===fall.parentElement){
      p.style.justifyContent='center';
      p.style.width='100%';
      p.style.marginLeft='auto';
      p.style.marginRight='auto';
    }
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',center,{once:true});else center();
  setTimeout(center,100);setTimeout(center,500);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]

index.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';", "const CACHE_NAME = 'cuidarbem-v75-38-center-summary-actions';", t, count=1)
sw.write_text(t,encoding='utf-8')
