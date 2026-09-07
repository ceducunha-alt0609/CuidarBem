from pathlib import Path
import re

index=Path('index.html')
s=index.read_text(encoding='utf-8')

marker='cuidarbem-v75-48-risk-accordion'
if marker not in s:
    patch=r'''

<!-- v75.48 — Mobile: riscos previstos compactos e expansíveis -->
<style id="cuidarbem-v75-48-risk-accordion">
@media(max-width:767px){
  #cb75-risk-panel #cb75-risk-list{gap:9px!important;}
  #cb75-risk-panel .cb75-item{cursor:pointer;padding:12px 14px!important;align-items:center!important;}
  #cb75-risk-panel .cb75-item-main{min-width:0;}
  #cb75-risk-panel .cb75-item-title{padding-right:26px;position:relative;font-weight:800!important;}
  #cb75-risk-panel .cb75-item-title::after{content:'›';position:absolute;right:2px;top:-3px;font-size:24px;color:#1a6b5c;transition:transform .18s ease;}
  #cb75-risk-panel .cb75-item.cb7548-open .cb75-item-title::after{transform:rotate(90deg);}
  #cb75-risk-panel .cb75-item-text,
  #cb75-risk-panel .cb75-score{display:none!important;}
  #cb75-risk-panel .cb75-item.cb7548-open{align-items:flex-start!important;}
  #cb75-risk-panel .cb75-item.cb7548-open .cb75-item-text{display:block!important;margin-top:5px;}
  #cb75-risk-panel .cb75-item.cb7548-open .cb75-score{display:block!important;margin-top:9px;}
}
</style>
<script id="cuidarbem-v75-48-risk-accordion-js">
(function(){
 'use strict';
 function bind(){
   if(window.innerWidth>=768)return;
   var list=document.getElementById('cb75-risk-list');
   if(!list)return;
   Array.from(list.querySelectorAll('.cb75-item')).forEach(function(item){
     if(item.dataset.cb7548)return;
     item.dataset.cb7548='1';
     item.setAttribute('role','button');
     item.setAttribute('tabindex','0');
     item.setAttribute('aria-expanded','false');
     function toggle(){
       var open=item.classList.toggle('cb7548-open');
       item.setAttribute('aria-expanded',open?'true':'false');
     }
     item.addEventListener('click',toggle);
     item.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();toggle();}});
   });
 }
 function watch(){
   var list=document.getElementById('cb75-risk-list');
   if(!list)return false;
   bind();
   new MutationObserver(bind).observe(list,{childList:true,subtree:false});
   return true;
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){if(!watch()){setTimeout(watch,300);setTimeout(watch,900);}}, {once:true});
 else if(!watch()){setTimeout(watch,300);setTimeout(watch,900);}
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]

index.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-48-risk-accordion';",t,count=1)
sw.write_text(t,encoding='utf-8')
