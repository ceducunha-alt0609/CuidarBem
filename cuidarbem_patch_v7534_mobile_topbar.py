from pathlib import Path
import re

index=Path('index.html'); s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-54-caregiver-health'
if marker not in s:
    patch=r'''

<!-- v75.54 — Mobile: Saúde orientada ao cuidador -->
<style id="cuidarbem-v75-54-caregiver-health">
@media(max-width:767px){
  /* rótulo HOJE órfão */
  .cb7554-hide-today{display:none!important;}

  /* Histórico de sinais vitais é resultado, não tarefa */
  .cb7554-vitals-detail{display:none!important;}
  body.cb7554-vitals-open .cb7554-vitals-detail{display:block!important;}
  #cb7554-vitals-toggle{width:100%;margin:10px 0 0;display:flex;align-items:center;justify-content:center;gap:8px;}

  /* Biblioteca é consulta: uma porta compacta */
  .cb7554-library-source{display:none!important;}
  body.cb7554-library-open .cb7554-library-source{display:block!important;}
  body.cb7554-library-open #cb7554-library-entry{display:none!important;}
  #cb7554-library-entry{cursor:pointer;}
  #cb7554-library-entry .cb7554-head{display:flex;align-items:center;gap:12px;}
  #cb7554-library-entry .cb7554-ico{width:48px;height:48px;border-radius:15px;background:var(--teal-50);display:flex;align-items:center;justify-content:center;font-size:24px;flex:0 0 48px;}
  #cb7554-library-entry .cb7554-copy{flex:1;min-width:0;}
  #cb7554-library-entry .cb7554-title{font-family:'Nunito',sans-serif;font-size:17px;font-weight:900;color:var(--green-800);}
  #cb7554-library-entry .cb7554-sub{font-size:12px;color:var(--text-muted);font-weight:700;margin-top:3px;line-height:1.35;}
  #cb7554-library-entry .cb7554-go{font-size:25px;color:var(--green-600);}
  #cb7554-library-close{display:none!important;}
  body.cb7554-library-open #cb7554-library-close{display:flex!important;width:100%;justify-content:center;margin:0 0 12px;}
}
@media(min-width:768px){#cb7554-library-entry,#cb7554-library-close,#cb7554-vitals-toggle{display:none!important;}}
</style>
<script id="cuidarbem-v75-54-caregiver-health-js">
(function(){
 function txt(el){return (el&&el.textContent||'').replace(/\s+/g,' ').trim();}
 function visible(el){return !!(el&&el.getClientRects().length);}
 function health(){return document.getElementById('screen-dashboard');}
 function hideToday(){
   var root=health(); if(!root)return;
   var all=root.querySelectorAll('h1,h2,h3,h4,h5,div,span,p');
   for(var i=0;i<all.length;i++){
     if(txt(all[i])==='HOJE' && all[i].children.length===0){all[i].classList.add('cb7554-hide-today');}
   }
 }
 function vitals(){
   if(document.getElementById('cb7554-vitals-toggle'))return;
   var root=health(); if(!root)return;
   var all=root.querySelectorAll('*'), hist=null;
   for(var i=0;i<all.length;i++){
     if(txt(all[i])==='HISTÓRICO' && visible(all[i])){hist=all[i];break;}
   }
   if(!hist)return;
   var parent=hist.parentElement; if(!parent)return;
   var chart=hist.previousElementSibling;
   if(chart)chart.classList.add('cb7554-vitals-detail');
   hist.classList.add('cb7554-vitals-detail');
   var n=hist.nextElementSibling, guard=0;
   while(n && guard++<12){
     n.classList.add('cb7554-vitals-detail');
     n=n.nextElementSibling;
   }
   var btn=document.createElement('button');
   btn.id='cb7554-vitals-toggle'; btn.className='cb75-btn secondary'; btn.innerHTML='📈 Ver histórico e tendência';
   parent.insertBefore(btn,hist);
   btn.onclick=function(){
     var open=document.body.classList.toggle('cb7554-vitals-open');
     btn.innerHTML=open?'▲ Ocultar histórico':'📈 Ver histórico e tendência';
   };
 }
 function library(){
   if(document.getElementById('cb7554-library-entry'))return;
   var root=health(); if(!root)return;
   var all=root.querySelectorAll('*'), title=null;
   for(var i=0;i<all.length;i++){
     var t=txt(all[i]);
     if(t.indexOf('Biblioteca educativa pós-AVC')===0 && all[i].children.length<4){title=all[i];break;}
   }
   if(!title)return;
   var card=title.closest('.card'); if(!card)return;
   card.classList.add('cb7554-library-source');
   var entry=document.createElement('section');
   entry.id='cb7554-library-entry'; entry.className='card'; entry.tabIndex=0; entry.setAttribute('role','button');
   entry.innerHTML='<div class="cb7554-head"><div class="cb7554-ico">📚</div><div class="cb7554-copy"><div class="cb7554-title">Orientações e exercícios</div><div class="cb7554-sub">FAST, deglutição, prevenção e orientações pós-AVC.</div></div><div class="cb7554-go">›</div></div>';
   card.parentNode.insertBefore(entry,card);
   var close=document.createElement('button'); close.id='cb7554-library-close'; close.className='cb75-btn secondary'; close.innerHTML='‹ Voltar para Saúde';
   card.parentNode.insertBefore(close,card);
   function open(){document.body.classList.add('cb7554-library-open'); setTimeout(function(){close.scrollIntoView({behavior:'smooth',block:'start'});},30);}
   function shut(){document.body.classList.remove('cb7554-library-open'); setTimeout(function(){entry.scrollIntoView({behavior:'smooth',block:'center'});},30);}
   entry.onclick=open; entry.onkeydown=function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();open();}}; close.onclick=shut;
 }
 function run(){hideToday();vitals();library();}
 document.addEventListener('DOMContentLoaded',run);
 var tries=0,timer=setInterval(function(){run();if(++tries>60)clearInterval(timer);},250);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8')

sw=Path('sw.js'); t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-54-caregiver-health';",t,count=1)
sw.write_text(t,encoding='utf-8')
