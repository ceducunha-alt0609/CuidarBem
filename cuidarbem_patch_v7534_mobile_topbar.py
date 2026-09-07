from pathlib import Path
import re

index=Path('index.html')
s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-50-home-to-agenda'
if marker not in s:
    patch=r'''

<!-- v75.50 — Mobile: Progresso + Tarefas de hoje migram da Home para Agenda -->
<style id="cuidarbem-v75-50-home-to-agenda">
@media(max-width:767px){
  #screen-home .mobile-only-progress,
  #screen-home .section-header:has(+ #today-tasks-card),
  #screen-home #today-tasks-card,
  #screen-home #today-tasks-card + .btn-add{display:none!important;}
  #cb7550-agenda-today{margin-bottom:14px;}
  #cb7550-agenda-today .card-title{margin-bottom:10px;}
  #cb7550-agenda-today .cat-pills{overflow-x:auto;flex-wrap:nowrap;scrollbar-width:none;margin-bottom:12px;}
  #cb7550-agenda-today .cat-pills::-webkit-scrollbar{display:none;}
  #cb7550-agenda-today .cat-pill{flex:0 0 auto;}
}
@media(min-width:768px){#cb7550-agenda-today{display:none!important;}}
</style>
<script id="cuidarbem-v75-50-home-to-agenda-js">
(function(){
 'use strict';
 function buildAgendaToday(){
   if(window.innerWidth>=768 || document.getElementById('cb7550-agenda-today')) return;
   var cal=document.querySelector('#screen-calendar .content');
   if(!cal)return;
   var firstCard=cal.querySelector(':scope > .card');
   if(!firstCard)return;
   var box=document.createElement('div');
   box.id='cb7550-agenda-today';
   box.innerHTML=`
     <div class="card mobile-only-progress" style="margin-bottom:12px">
       <div class="card-title">Progresso de hoje</div>
       <div class="progress-ring-wrap">
         <svg width="80" height="80" class="progress-ring">
           <circle class="ring-bg" cx="40" cy="40" r="32"></circle>
           <circle class="ring-fill" id="ring-fill-agenda" cx="40" cy="40" r="32" stroke-dasharray="201" stroke-dashoffset="201"></circle>
         </svg>
         <div class="progress-info">
           <div class="progress-pct" id="pct-text-agenda">0%</div>
           <div class="progress-label">concluído hoje</div>
           <div class="progress-count" id="count-text-agenda">0 de 0 tarefas</div>
         </div>
       </div>
     </div>
     <div class="section-header">
       <div class="section-title">Tarefas de hoje</div>
       <div class="cat-pills">
         <button class="cat-pill all active" data-f="all">Todas</button>
         <button class="cat-pill med" data-f="med">💊 Remédio</button>
         <button class="cat-pill cons" data-f="cons">🩺 Consulta</button>
         <button class="cat-pill exam" data-f="exam">🔬 Exame</button>
         <button class="cat-pill fisio" data-f="fisio">🦾 Fisio</button>
         <button class="cat-pill exer" data-f="exer">🏃 Exercício</button>
       </div>
     </div>
     <div class="card"><div id="cb7550-today-list"></div></div>`;
   firstCard.insertAdjacentElement('afterend',box);
   box.querySelectorAll('.cat-pill').forEach(function(btn){btn.addEventListener('click',function(){box.querySelectorAll('.cat-pill').forEach(b=>b.classList.remove('active'));btn.classList.add('active');sync(btn.dataset.f);});});
   sync('all');
 }
 function sync(filter){
   var src=document.getElementById('today-tasks-list'), dst=document.getElementById('cb7550-today-list');
   if(src&&dst){
     dst.innerHTML=src.innerHTML;
     if(filter&&filter!=='all') Array.from(dst.querySelectorAll('.task-item')).forEach(function(it){if(!it.classList.contains('task-item-'+filter)&&!it.querySelector('.badge-'+filter))it.style.display='none';});
   }
   var p=document.getElementById('pct-text-mobile'), c=document.getElementById('count-text-mobile'), r=document.getElementById('ring-fill-mobile');
   var pa=document.getElementById('pct-text-agenda'), ca=document.getElementById('count-text-agenda'), ra=document.getElementById('ring-fill-agenda');
   if(p&&pa)pa.textContent=p.textContent;if(c&&ca)ca.textContent=c.textContent;if(r&&ra)ra.setAttribute('stroke-dashoffset',r.getAttribute('stroke-dashoffset')||'201');
 }
 function watch(){buildAgendaToday();var src=document.getElementById('today-tasks-list');if(src)new MutationObserver(function(){var a=document.querySelector('#cb7550-agenda-today .cat-pill.active');sync(a?a.dataset.f:'all');}).observe(src,{childList:true,subtree:true,attributes:true});setInterval(function(){if(document.getElementById('screen-calendar')?.classList.contains('active'))sync(document.querySelector('#cb7550-agenda-today .cat-pill.active')?.dataset.f||'all');},1000);}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',watch,{once:true});else watch();
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8')

sw=Path('sw.js'); t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-50-home-to-agenda';",t,count=1)
sw.write_text(t,encoding='utf-8')
