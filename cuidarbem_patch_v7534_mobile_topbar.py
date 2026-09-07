from pathlib import Path
import re

index=Path('index.html'); s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-57-complications-compact'
if marker not in s:
    patch=r'''

<!-- v75.57 — Mobile: FAST visível, checklist sob demanda -->
<style id="cuidarbem-v75-57-complications-compact">
@media(max-width:767px){
  #complication-card:not(.cb7557-open) .complication-intro,
  #complication-card:not(.cb7557-open) #complication-list,
  #complication-card:not(.cb7557-open) .complication-actions,
  #complication-card:not(.cb7557-open) #complication-log{display:none!important;}
  #cb7557-complication-toggle{width:100%;margin-top:10px;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 14px;border-radius:13px;border:1.5px solid var(--green-200);background:var(--green-50);color:var(--green-800);font-family:'Nunito',sans-serif;font-size:13px;font-weight:900;cursor:pointer;}
  #cb7557-complication-toggle .cb7557-left{display:flex;align-items:center;gap:8px;min-width:0;}
  #cb7557-complication-toggle .cb7557-status{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  #cb7557-complication-toggle .cb7557-go{font-size:21px;line-height:1;color:var(--green-600);}
  #complication-card.cb7557-has-alert #cb7557-complication-toggle{border-color:#fecdd3;background:#fff1f2;color:#9f1239;}
  #complication-card.cb7557-has-alert #cb7557-complication-toggle .cb7557-go{color:#be123c;}
  #complication-card:not(.cb7557-open) #complication-alert.ok{display:none!important;}
  #complication-card:not(.cb7557-open) #complication-alert.danger{display:block!important;}
}
@media(min-width:768px){#cb7557-complication-toggle{display:none!important;}}
</style>
<script id="cuidarbem-v75-57-complications-compact-js">
(function(){
 function setup(){
   var card=document.getElementById('complication-card');
   var list=document.getElementById('complication-list');
   if(!card||!list)return;
   var btn=document.getElementById('cb7557-complication-toggle');
   if(!btn){
     btn=document.createElement('button');
     btn.id='cb7557-complication-toggle';
     var fast=card.querySelector('.fast-sticky');
     if(fast) fast.insertAdjacentElement('afterend',btn); else card.insertBefore(btn,card.firstChild);
     btn.addEventListener('click',function(){
       var open=card.classList.toggle('cb7557-open');
       refresh();
       if(open){var intro=card.querySelector('.complication-intro');if(intro)setTimeout(function(){intro.scrollIntoView({behavior:'smooth',block:'nearest'});},30);}
     });
   }
   function refresh(){
     var checked=list.querySelectorAll('input:checked').length;
     var open=card.classList.contains('cb7557-open');
     card.classList.toggle('cb7557-has-alert',checked>0);
     var label=checked?('⚠️ '+checked+' sinal'+(checked>1?'is':'')+' marcado'+(checked>1?'s':'')):'✅ Nenhum sinal marcado hoje';
     btn.innerHTML='<span class="cb7557-left"><span>🧠</span><span class="cb7557-status">'+label+'</span></span><span class="cb7557-go">'+(open?'⌃':'›')+'</span>';
   }
   list.querySelectorAll('input').forEach(function(i){if(!i.dataset.cb7557){i.dataset.cb7557='1';i.addEventListener('change',refresh);}});
   var alert=document.getElementById('complication-alert');
   if(alert&&!alert.dataset.cb7557){alert.dataset.cb7557='1';new MutationObserver(refresh).observe(alert,{attributes:true,childList:true,subtree:true});}
   refresh();
 }
 document.addEventListener('DOMContentLoaded',setup);var n=0,x=setInterval(function(){setup();if(document.getElementById('cb7557-complication-toggle')||++n>50)clearInterval(x);},250);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-57-complications-compact';",t,count=1);sw.write_text(t,encoding='utf-8')
