from pathlib import Path
import re

index=Path('index.html'); s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-55-health-direct'
if marker not in s:
    patch=r'''

<!-- v75.55 — Saúde mobile: seletores diretos da estrutura real -->
<style id="cuidarbem-v75-55-health-direct">
@media(max-width:767px){
  /* Histórico de sinais vitais: IDs reais */
  body:not(.cb7555-vitals-open) #vital-chart,
  body:not(.cb7555-vitals-open) #vital-history,
  body:not(.cb7555-vitals-open) #vital-history-table,
  body:not(.cb7555-vitals-open) #vital-hist-pagination,
  body:not(.cb7555-vitals-open) #vital-hist-view-btn,
  body:not(.cb7555-vitals-open) #vital-freq-alert{display:none!important;}
  .cb7555-hist-head{display:none!important;}
  body.cb7555-vitals-open .cb7555-hist-head{display:flex!important;}
  #cb7555-vitals-toggle{width:100%;margin-top:10px;display:flex;justify-content:center;align-items:center;gap:8px;}

  /* Biblioteca: ID real criado pela v75 */
  #cb75-edu-card{display:none!important;}
  body.cb7555-library-open #cb75-edu-card{display:block!important;}
  body.cb7555-library-open #cb7555-library-entry{display:none!important;}
  #cb7555-library-entry .row{display:flex;align-items:center;gap:12px;}
  #cb7555-library-entry .ico{width:48px;height:48px;border-radius:15px;background:var(--teal-50);display:flex;align-items:center;justify-content:center;font-size:24px;flex:0 0 48px;}
  #cb7555-library-entry .copy{flex:1;min-width:0;}
  #cb7555-library-entry .title{font-family:'Nunito',sans-serif;font-size:17px;font-weight:900;color:var(--green-800);}
  #cb7555-library-entry .sub{font-size:12px;color:var(--text-muted);font-weight:700;line-height:1.35;margin-top:3px;}
  #cb7555-library-entry .go{font-size:25px;color:var(--green-600);}
  #cb7555-library-close{display:none!important;}
  body.cb7555-library-open #cb7555-library-close{display:flex!important;width:100%;justify-content:center;margin-bottom:12px;}
  .cb7555-hide-today{display:none!important;}
}
@media(min-width:768px){#cb7555-vitals-toggle,#cb7555-library-entry,#cb7555-library-close{display:none!important;}}
</style>
<script id="cuidarbem-v75-55-health-direct-js">
(function(){
 function t(e){return (e&&e.textContent||'').replace(/\s+/g,' ').trim();}
 function setup(){
   var root=document.getElementById('screen-dashboard'); if(!root)return;
   /* HOJE: pega somente o nó curto visível, sem depender de classe */
   root.querySelectorAll('div,span,p,h2,h3,h4').forEach(function(e){if(t(e)==='HOJE' && e.children.length===0)e.classList.add('cb7555-hide-today');});

   /* Vital: ancora no ID real do canvas/histórico */
   var hist=document.getElementById('vital-history');
   if(hist && !document.getElementById('cb7555-vitals-toggle')){
     var head=hist.previousElementSibling;
     if(head)head.classList.add('cb7555-hist-head');
     var btn=document.createElement('button'); btn.id='cb7555-vitals-toggle'; btn.className='cb75-btn secondary'; btn.innerHTML='📈 Ver histórico e tendência';
     (head&&head.parentNode?head.parentNode:hist.parentNode).insertBefore(btn,head||hist);
     btn.onclick=function(){var open=document.body.classList.toggle('cb7555-vitals-open');btn.innerHTML=open?'▲ Ocultar histórico':'📈 Ver histórico e tendência';if(open&&typeof renderVitalChart==='function')setTimeout(renderVitalChart,50);};
   }

   /* Biblioteca: ancora diretamente em #cb75-edu-card */
   var edu=document.getElementById('cb75-edu-card');
   if(edu && !document.getElementById('cb7555-library-entry')){
     var entry=document.createElement('section'); entry.id='cb7555-library-entry'; entry.className='card cb75-card'; entry.tabIndex=0; entry.setAttribute('role','button');
     entry.innerHTML='<div class="row"><div class="ico">📚</div><div class="copy"><div class="title">Orientações e exercícios</div><div class="sub">FAST, deglutição, prevenção e orientações pós-AVC.</div></div><div class="go">›</div></div>';
     edu.parentNode.insertBefore(entry,edu);
     var close=document.createElement('button');close.id='cb7555-library-close';close.className='cb75-btn secondary';close.innerHTML='‹ Voltar para Saúde';edu.parentNode.insertBefore(close,edu);
     function open(){document.body.classList.add('cb7555-library-open');setTimeout(function(){close.scrollIntoView({behavior:'smooth',block:'start'});},30);}
     function shut(){document.body.classList.remove('cb7555-library-open');setTimeout(function(){entry.scrollIntoView({behavior:'smooth',block:'center'});},30);}
     entry.onclick=open;entry.onkeydown=function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();open();}};close.onclick=shut;
   }
 }
 document.addEventListener('DOMContentLoaded',setup);var n=0,x=setInterval(function(){setup();if(++n>60)clearInterval(x);},250);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-55-health-direct';",t,count=1);sw.write_text(t,encoding='utf-8')
