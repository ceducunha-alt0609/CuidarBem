from pathlib import Path
import re

index=Path('index.html')
s=index.read_text(encoding='utf-8')

# v75.44 — seletor dos 4 mini-cards grava direto via setCB75Quick e inclui Limpar.
marker='cuidarbem-v75-44-state-picker-direct'
if marker not in s:
    patch=r'''

<!-- v75.44 — Estado Geral: picker direto + botão Limpar -->
<style id="cuidarbem-v75-44-state-picker-direct">
@media(max-width:767px){
  .cb7542-clear{margin-top:14px;width:100%;border:1.5px solid rgba(220,70,60,.35);border-radius:12px;background:#fff7f6;color:#9a3a33;padding:11px 14px;font:800 14px 'Nunito',sans-serif;}
}
</style>
<script id="cuidarbem-v75-44-state-picker-direct-js">
(function(){
 'use strict';
 function rebuildPickerBehavior(){
   if(innerWidth>=768)return;
   var cards=document.querySelectorAll('#cb7542-state-grid .cb7542-state-mini');
   cards.forEach(function(mini){
     if(mini.dataset.cb7544==='1')return;
     mini.dataset.cb7544='1';
     mini.addEventListener('click',function(ev){
       ev.stopImmediatePropagation();
       var key=mini.dataset.key;
       var defs={mood:['🙂 Humor'],appetite:['🍽️ Apetite'],sleep:['🌙 Sono'],mobility:['🚶 Mobilidade']};
       var originals=Array.from(document.querySelectorAll('#cb75-state-card .cb75-choice[data-cb75-key="'+key+'"]'));
       if(!originals.length)return;
       var modal=document.createElement('div');modal.className='cb7542-modal';
       modal.innerHTML='<div class="cb7542-sheet"><div class="cb7542-sheet-head"><div class="cb7542-sheet-title">'+(defs[key]?defs[key][0]:key)+'</div><button type="button" class="cb7542-close">×</button></div><div class="cb7542-options"></div><button type="button" class="cb7542-clear">Limpar seleção</button></div>';
       var box=modal.querySelector('.cb7542-options');
       originals.forEach(function(orig){
         var b=document.createElement('button');
         b.type='button'; b.innerHTML=orig.innerHTML;
         if(orig.classList.contains('active'))b.classList.add('selected');
         b.addEventListener('click',function(){
           var val=orig.dataset.cb75Val||'';
           if(typeof window.setCB75Quick==='function')window.setCB75Quick(key,val,orig);
           modal.remove();
         });
         box.appendChild(b);
       });
       modal.querySelector('.cb7542-clear').addEventListener('click',function(){
         var active=originals.find(function(b){return b.classList.contains('active');});
         if(active&&typeof window.setCB75Quick==='function')window.setCB75Quick(key,active.dataset.cb75Val||'',active);
         modal.remove();
       });
       modal.querySelector('.cb7542-close').onclick=function(){modal.remove();};
       modal.onclick=function(e){if(e.target===modal)modal.remove();};
       document.body.appendChild(modal);
     },true);
   });
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',rebuildPickerBehavior,{once:true});else rebuildPickerBehavior();
 setTimeout(rebuildPickerBehavior,200);setTimeout(rebuildPickerBehavior,700);setTimeout(rebuildPickerBehavior,1400);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]

index.write_text(s,encoding='utf-8')
sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-44-state-picker-direct';",t,count=1)
sw.write_text(t,encoding='utf-8')
