from pathlib import Path
import re
p=Path('index.html'); s=p.read_text(encoding='utf-8')
marker='cuidarbem-v75-82-accessibility-cleanup'
if marker not in s:
 patch=r'''
<!-- v75.82 — Mobile: acessibilidade útil, sem baixo estresse e DIAG fora do cuidador -->
<style id="cuidarbem-v75-82-accessibility-cleanup">
@media(max-width:767px){
 /* DIAG é ferramenta técnica: não ocupa a interface normal do cuidador */
 #diag-fab,#diag-badge,#diag-panel,.diag-fab,.diag-badge,.diag-panel,[id*="diag-fab"],[id*="diag-badge"]{display:none!important}
 /* remove a opção Baixo estresse visual dos atalhos/configurações */
 .cb7582-hide-stress{display:none!important}
 /* escala tipográfica real do app */
 html.cb7582-font-plus{font-size:17px!important}
 html.cb7582-font-plus2{font-size:19px!important}
 html.cb7582-font-plus body{font-size:1rem!important}
 html.cb7582-font-plus2 body{font-size:1rem!important}
 html.cb7582-font-plus button,html.cb7582-font-plus input,html.cb7582-font-plus select,html.cb7582-font-plus textarea,
 html.cb7582-font-plus2 button,html.cb7582-font-plus2 input,html.cb7582-font-plus2 select,html.cb7582-font-plus2 textarea{font-size:1em}
}
</style>
<script id="cuidarbem-v75-82-accessibility-cleanup-js">
(function(){
 function norm(x){return (x||'').replace(/\s+/g,' ').trim().toLowerCase()}
 function hideStress(){
  [].slice.call(document.querySelectorAll('body *')).forEach(function(el){
   if(el.children.length<8 && norm(el.textContent).indexOf('baixo estresse')>=0){
    var box=el.closest('.setting-row,.settings-row,.card,.accessibility-item,.toggle-row')||el;
    if(box && norm(box.textContent).length<180) box.classList.add('cb7582-hide-stress');
   }
  });
 }
 function hideDiag(){
  [].slice.call(document.querySelectorAll('button,div,span')).forEach(function(el){
   var t=norm(el.textContent);
   if((t==='diag'||t.indexOf('efeitos removidos')>=0) && t.length<400){
    var box=el.closest('[role="dialog"],.modal,.diag-panel,.diag-fab,.floating-btn')||el;
    box.style.display='none';
   }
  });
 }
 function applyFont(level){
  var h=document.documentElement;h.classList.remove('cb7582-font-plus','cb7582-font-plus2');
  if(level==='plus')h.classList.add('cb7582-font-plus');
  if(level==='plus2')h.classList.add('cb7582-font-plus2');
  try{localStorage.setItem('cb7582_font_size',level)}catch(e){}
 }
 function wireFont(){
  var candidates=[].slice.call(document.querySelectorAll('button,[role="button"]'));
  candidates.forEach(function(b){
   var t=norm(b.textContent);
   if(t==='a'||t==='a+'||t==='a++'){
    if(b.dataset.cb7582)return;b.dataset.cb7582='1';
    b.addEventListener('click',function(){applyFont(t==='a'?'normal':t==='a+'?'plus':'plus2')},true);
   }
  });
 }
 function setup(){hideStress();hideDiag();wireFont();}
 try{applyFont(localStorage.getItem('cb7582_font_size')||'normal')}catch(e){}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup);else setup();
 setTimeout(setup,400);setTimeout(setup,1200);
 new MutationObserver(function(){clearTimeout(window.__cb7582t);window.__cb7582t=setTimeout(setup,80)}).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>
'''
 pos=s.rfind('</body>')
 if pos<0: raise SystemExit('body not found')
 s=s[:pos]+patch+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-82-accessibility-cleanup';",t,count=1);sw.write_text(t,encoding='utf-8')
