from pathlib import Path
import re

index=Path('index.html'); s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-53-health-compact-details'
if marker not in s:
    patch=r'''

<!-- v75.53 — Mobile: sinais vitais enxutos + biblioteca compacta -->
<style id="cuidarbem-v75-53-health-compact-details">
@media(max-width:767px){
  /* remove rótulo órfão HOJE deixado pela área de adesão */
  #screen-dashboard .health-section-label{margin-top:14px;}

  /* Sinais vitais: registrar aqui; tendência/histórico sob demanda */
  body:not(.cb7553-vitals-open) #screen-dashboard #vitals-chart,
  body:not(.cb7553-vitals-open) #screen-dashboard #vitals-history,
  body:not(.cb7553-vitals-open) #screen-dashboard .vitals-chart,
  body:not(.cb7553-vitals-open) #screen-dashboard .vitals-history{display:none!important;}
  #cb7553-vitals-toggle{width:100%;margin-top:10px;display:flex;align-items:center;justify-content:center;gap:7px;}

  /* Biblioteca: vira porta de entrada compacta */
  #cb7553-library-entry{display:block!important;}
  body:not(.cb7553-library-open) #cb7553-library-entry ~ .cb7553-library-source{display:none!important;}
  body.cb7553-library-open #cb7553-library-entry{display:none!important;}
  #cb7553-library-entry .head{display:flex;align-items:center;gap:12px;}
  #cb7553-library-entry .ico{width:48px;height:48px;border-radius:15px;background:var(--teal-50);display:flex;align-items:center;justify-content:center;font-size:24px;}
  #cb7553-library-entry .copy{flex:1;min-width:0;}
  #cb7553-library-entry .title{font-family:'Nunito',sans-serif;font-size:17px;font-weight:900;color:var(--green-800);}
  #cb7553-library-entry .sub{font-size:12px;color:var(--text-muted);font-weight:700;margin-top:3px;line-height:1.35;}
  #cb7553-library-entry .go{font-size:25px;color:var(--green-600);}
  #cb7553-library-close{display:none;}
  body.cb7553-library-open #cb7553-library-close{display:flex!important;position:sticky;top:8px;z-index:55;margin:0 0 12px;}
}
@media(min-width:768px){#cb7553-library-entry,#cb7553-library-close,#cb7553-vitals-toggle{display:none!important;}}
</style>
<script id="cuidarbem-v75-53-health-compact-details-js">
(function(){
 function text(el){return (el&&el.textContent||'').replace(/\s+/g,' ').trim();}
 function setupVitals(){
   if(document.getElementById('cb7553-vitals-toggle')) return;
   var screen=document.getElementById('screen-dashboard'); if(!screen) return;
   var hist=null, nodes=screen.querySelectorAll('*');
   for(var i=0;i<nodes.length;i++){if(/^HISTÓRICO$/i.test(text(nodes[i]))){hist=nodes[i];break;}}
   if(!hist) return;
   var card=hist.closest('.card') || hist.parentElement; if(!card) return;
   var btn=document.createElement('button'); btn.id='cb7553-vitals-toggle'; btn.className='cb75-btn secondary'; btn.innerHTML='📈 Ver histórico e tendência';
   hist.parentNode.insertBefore(btn,hist);
   var chart=hist.previousElementSibling;
   if(chart) chart.id=chart.id||'vitals-chart';
   var wrap=hist.parentElement; hist.id=hist.id||'vitals-history';
   btn.addEventListener('click',function(){var open=document.body.classList.toggle('cb7553-vitals-open'); btn.innerHTML=open?'▲ Ocultar histórico':'📈 Ver histórico e tendência';});
 }
 function setupLibrary(){
   if(document.getElementById('cb7553-library-entry')) return;
   var screen=document.getElementById('screen-dashboard'); if(!screen) return;
   var nodes=screen.querySelectorAll('*'), title=null;
   for(var i=0;i<nodes.length;i++){if(text(nodes[i]).indexOf('Biblioteca educativa pós-AVC')===0){title=nodes[i];break;}}
   if(!title) return;
   var card=title.closest('.card'); if(!card) return;
   card.classList.add('cb7553-library-source');
   var entry=document.createElement('section'); entry.id='cb7553-library-entry'; entry.className='card cb75-card'; entry.setAttribute('role','button'); entry.setAttribute('tabindex','0');
   entry.innerHTML='<div class="head"><div class="ico">📚</div><div class="copy"><div class="title">Biblioteca educativa pós-AVC</div><div class="sub">FAST, deglutição, prevenção e orientações por fase.</div></div><div class="go">›</div></div>';
   card.parentNode.insertBefore(entry,card);
   var close=document.createElement('button'); close.id='cb7553-library-close'; close.className='cb75-btn secondary'; close.innerHTML='‹ Voltar para Saúde'; card.parentNode.insertBefore(close,card);
   function open(){document.body.classList.add('cb7553-library-open'); setTimeout(function(){close.scrollIntoView({behavior:'smooth',block:'start'});},30);}
   function shut(){document.body.classList.remove('cb7553-library-open'); setTimeout(function(){entry.scrollIntoView({behavior:'smooth',block:'center'});},30);}
   entry.addEventListener('click',open); entry.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();open();}}); close.addEventListener('click',shut);
 }
 function setupOrphanToday(){
   var screen=document.getElementById('screen-dashboard'); if(!screen) return;
   var labels=screen.querySelectorAll('.health-section-label');
   for(var i=0;i<labels.length;i++){if(text(labels[i])==='HOJE'){labels[i].style.display='none';}}
 }
 function setup(){setupVitals();setupLibrary();setupOrphanToday();}
 var tries=0,timer=setInterval(function(){setup();if(++tries>40)clearInterval(timer);},250); document.addEventListener('DOMContentLoaded',setup);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8')
sw=Path('sw.js'); t=sw.read_text(encoding='utf-8'); t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-53-health-compact-details';",t,count=1); sw.write_text(t,encoding='utf-8')
