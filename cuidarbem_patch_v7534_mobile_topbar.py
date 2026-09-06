from pathlib import Path
import re

index=Path('index.html')
s=index.read_text(encoding='utf-8')

marker='cuidarbem-v75-39-summary-card'
if marker not in s:
    patch=r'''

<!-- v75.39 — Mobile: Resumo do Dia vira card compacto clicável -->
<style id="cuidarbem-v75-39-summary-card">
@media (max-width:767px){
  .cb7539-summary-card{cursor:pointer;position:relative;padding-bottom:14px!important;}
  .cb7539-summary-card .cb7539-hide-detail{display:none!important;}
  .cb7539-summary-card .cb7539-glance{display:flex;align-items:center;gap:10px;margin-top:10px;padding:12px 14px;border:1px solid rgba(26,107,92,.14);border-radius:16px;background:rgba(255,255,255,.72);}
  .cb7539-glance-icon{font-size:24px;flex:0 0 auto;}
  .cb7539-glance-copy{flex:1;min-width:0;}
  .cb7539-glance-main{font:800 16px/1.25 'Nunito',sans-serif;color:#154f45;}
  .cb7539-glance-sub{font:600 13px/1.35 'Nunito Sans',sans-serif;color:#52645f;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .cb7539-glance-arrow{font-size:22px;color:#1a6b5c;font-weight:900;}
  .cb7539-summary-card .cb7539-actions{display:flex!important;justify-content:center!important;gap:10px!important;margin-top:12px!important;}
}
</style>
<script id="cuidarbem-v75-39-summary-card-js">
(function(){
 'use strict';
 function norm(v){return (v||'').replace(/\s+/g,' ').trim().toLowerCase();}
 function visible(el){return !!(el&&el.getClientRects().length);}
 function setup(){
   if(window.innerWidth>=768)return;
   var root=document.querySelector('#screen-home'); if(!root)return;
   var all=Array.from(root.querySelectorAll('*'));
   var title=all.find(function(el){return visible(el)&&norm(el.textContent).indexOf('resumo do dia v75')===0&&el.children.length<=3;});
   if(!title)return;
   var card=title.closest('.card')||title.parentElement; if(!card||card.classList.contains('cb7539-summary-card'))return;
   card.classList.add('cb7539-summary-card');
   var buttons=Array.from(card.querySelectorAll('button,a,[role="button"]'));
   var voice=buttons.find(function(el){return norm(el.textContent).indexOf('comando por voz')!==-1;});
   var fall=buttons.find(function(el){return norm(el.textContent).indexOf('queda/sintoma')!==-1;});
   var actions=(voice&&fall&&voice.parentElement===fall.parentElement)?voice.parentElement:null;
   if(actions)actions.classList.add('cb7539-actions');
   Array.from(card.children).forEach(function(ch){if(ch!==title&&ch!==actions)ch.classList.add('cb7539-hide-detail');});
   var texts=Array.from(card.querySelectorAll('*')).filter(function(el){return el!==title&&!el.closest('.cb7539-actions')&&el.textContent&&el.children.length===0;}).map(function(el){return el.textContent.trim();}).filter(Boolean);
   var attention=texts.filter(function(t){var n=norm(t);return n.indexOf('não preenchido')!==-1||n.indexOf('nao preenchido')!==-1||n.indexOf('baixa')!==-1||n.indexOf('pendência')!==-1||n.indexOf('pendencia')!==-1;});
   var count=attention.length;
   var glance=document.createElement('div'); glance.className='cb7539-glance';
   glance.innerHTML='<span class="cb7539-glance-icon">'+(count?'⚠️':'🌿')+'</span><div class="cb7539-glance-copy"><div class="cb7539-glance-main">'+(count?(count+' ponto'+(count>1?'s':'')+' para conferir'):'Rotina em dia')+'</div><div class="cb7539-glance-sub">'+(count?attention.slice(0,2).join(' • '):'Toque para ver o resumo completo')+'</div></div><span class="cb7539-glance-arrow">›</span>';
   if(actions)card.insertBefore(glance,actions);else card.appendChild(glance);
   function openSummary(e){
     if(e.target.closest('button,a,[role="button"]'))return;
     var simple=Array.from(root.querySelectorAll('button,a,[role="button"]')).find(function(el){return norm(el.textContent).indexOf('modo simples')!==-1;});
     if(simple)simple.click();
   }
   title.style.cursor='pointer'; glance.addEventListener('click',openSummary); title.addEventListener('click',openSummary);
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup,{once:true});else setup();
 setTimeout(setup,150);setTimeout(setup,600);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]

index.write_text(s,encoding='utf-8')
sw=Path('sw.js'); t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';", "const CACHE_NAME = 'cuidarbem-v75-39-summary-card';", t, count=1)
sw.write_text(t,encoding='utf-8')
