from pathlib import Path
import re

index=Path('index.html')
s=index.read_text(encoding='utf-8')

marker='cuidarbem-v75-45-state-picker-storage'
if marker not in s:
    patch=r'''

<!-- v75.45 — Estado Geral: picker grava diretamente no registro diário -->
<script id="cuidarbem-v75-45-state-picker-storage-js">
(function(){
 'use strict';
 const KEY='cb75_daily_log_v75';
 function dayKey(){const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
 function readAll(){try{return JSON.parse(localStorage.getItem(KEY)||'{}')||{};}catch(e){return {};}}
 function writeState(key,val){
   const all=readAll(), day=dayKey();
   const base=all[day]||{date:day,mood:'',appetite:'',sleep:'',mobility:'',patientFeeling:'',water:0,meals:0,ndd:'',sleepHours:'',sleepQuality:'',reposition:false,skinCheck:false,redness:false,notes:''};
   all[day]={...base,[key]:val,date:day,updatedAt:Date.now()};
   localStorage.setItem(KEY,JSON.stringify(all));
   document.querySelectorAll('#cb75-state-card .cb75-choice[data-cb75-key="'+key+'"]').forEach(function(b){b.classList.toggle('active',(b.dataset.cb75Val||'')===val);});
   const mini=document.querySelector('#cb7542-state-grid .cb7542-state-mini[data-key="'+key+'"]');
   if(mini){const v=mini.querySelector('.cb7542-state-value');if(v){v.textContent=val||'Não informado';v.classList.toggle('empty',!val);}mini.classList.toggle('attention',/triste|ansioso|irritado|baixo|recusou|interrompido|pouco|sonolento|com apoio|baixa|acamado/.test(val||''));}
   try{window.dispatchEvent(new CustomEvent('cb75-state-updated',{detail:{key:key,value:val,date:day}}));}catch(e){}
 }
 function install(){
   if(innerWidth>=768)return;
   document.querySelectorAll('#cb7542-state-grid .cb7542-state-mini').forEach(function(mini){
     if(mini.dataset.cb7545==='1')return;
     mini.dataset.cb7545='1';
     mini.addEventListener('click',function(ev){
       ev.preventDefault();ev.stopImmediatePropagation();
       const key=mini.dataset.key;
       const labels={mood:'🙂 Humor',appetite:'🍽️ Apetite',sleep:'🌙 Sono',mobility:'🚶 Mobilidade'};
       const originals=Array.from(document.querySelectorAll('#cb75-state-card .cb75-choice[data-cb75-key="'+key+'"]'));
       if(!originals.length)return;
       document.querySelectorAll('.cb7542-modal').forEach(function(m){m.remove();});
       const modal=document.createElement('div');modal.className='cb7542-modal cb7545-modal';
       modal.innerHTML='<div class="cb7542-sheet"><div class="cb7542-sheet-head"><div class="cb7542-sheet-title">'+(labels[key]||key)+'</div><button type="button" class="cb7542-close">×</button></div><div class="cb7542-options"></div><button type="button" class="cb7542-clear">Limpar seleção</button></div>';
       const box=modal.querySelector('.cb7542-options');
       const all=readAll(), current=((all[dayKey()]||{})[key]||'');
       originals.forEach(function(orig){
         const val=orig.dataset.cb75Val||'';
         const b=document.createElement('button');b.type='button';b.innerHTML=orig.innerHTML;b.dataset.value=val;
         if(current===val)b.classList.add('selected');
         b.onclick=function(e){e.preventDefault();e.stopPropagation();writeState(key,current===val?'':val);modal.remove();};
         box.appendChild(b);
       });
       modal.querySelector('.cb7542-clear').onclick=function(e){e.preventDefault();e.stopPropagation();writeState(key,'');modal.remove();};
       modal.querySelector('.cb7542-close').onclick=function(){modal.remove();};
       modal.onclick=function(e){if(e.target===modal)modal.remove();};
       document.body.appendChild(modal);
     },true);
   });
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
 setTimeout(install,250);setTimeout(install,800);setTimeout(install,1600);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]

index.write_text(s,encoding='utf-8')
sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-45-state-picker-storage';",t,count=1)
sw.write_text(t,encoding='utf-8')
