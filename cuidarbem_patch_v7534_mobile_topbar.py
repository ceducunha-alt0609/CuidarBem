from pathlib import Path
import re

index=Path('index.html')
s=index.read_text(encoding='utf-8')

marker='cuidarbem-v75-42-state-card-real-target'
if marker not in s:
    patch=r'''

<!-- v75.42 — Mobile: Estado Geral em 4 mini-cards usando DOM real -->
<style id="cuidarbem-v75-42-state-card-real-target">
@media(max-width:767px){
  #cb75-state-card > .cb75-grid-2{display:none!important;}
  #cb7542-state-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:12px 0 14px;}
  .cb7542-state-mini{border:1px solid rgba(26,107,92,.16);border-radius:16px;background:rgba(255,255,255,.8);padding:13px;min-height:88px;cursor:pointer;}
  .cb7542-state-mini.attention{border-color:rgba(220,70,60,.35);background:rgba(255,248,247,.92);}
  .cb7542-state-label{font:700 12px/1.2 'Nunito Sans',sans-serif;letter-spacing:.04em;text-transform:uppercase;color:#52645f;}
  .cb7542-state-value{font:800 16px/1.3 'Nunito',sans-serif;color:#154f45;margin-top:8px;}
  .cb7542-state-value.empty{font-weight:600;color:#7a8985;}
  .cb7542-modal{position:fixed;inset:0;z-index:10060;background:rgba(12,38,33,.48);display:flex;align-items:flex-end;justify-content:center;padding:16px;}
  .cb7542-sheet{width:min(100%,480px);background:#fff;border-radius:22px 22px 16px 16px;padding:18px;box-shadow:0 -10px 35px rgba(0,0,0,.18);}
  .cb7542-sheet-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;}
  .cb7542-sheet-title{font:800 20px/1.2 'Nunito',sans-serif;color:#154f45;}
  .cb7542-close{border:0;background:transparent;font-size:28px;line-height:1;padding:4px 8px;color:#52645f;}
  .cb7542-options{display:flex;flex-wrap:wrap;gap:9px;}
  .cb7542-options button{border:1.5px solid rgba(26,107,92,.25);border-radius:999px;background:#fff;padding:11px 14px;font:800 15px 'Nunito',sans-serif;color:#243b36;}
  .cb7542-options button.selected{background:#e8f5f1;border-color:#1a6b5c;color:#154f45;}
  .cb7542-help{font:600 12px/1.35 'Nunito Sans',sans-serif;color:#71807c;margin-top:12px;}
}
</style>
<script id="cuidarbem-v75-42-state-card-real-target-js">
(function(){
 'use strict';
 var defs=[
  {key:'mood',label:'Humor',icon:'🙂'},
  {key:'appetite',label:'Apetite',icon:'🍽️'},
  {key:'sleep',label:'Sono',icon:'🌙'},
  {key:'mobility',label:'Mobilidade',icon:'🚶'}
 ];
 function norm(v){return(v||'').replace(/\s+/g,' ').trim().toLowerCase();}
 function card(){return document.getElementById('cb75-state-card');}
 function originals(key){var c=card();return c?Array.from(c.querySelectorAll('.cb75-choice[data-cb75-key="'+key+'"]')):[];}
 function active(key){return originals(key).find(function(b){return b.classList.contains('active');});}
 function refresh(){
  var grid=document.getElementById('cb7542-state-grid');if(!grid)return;
  defs.forEach(function(d){var mini=grid.querySelector('[data-key="'+d.key+'"]');if(!mini)return;var a=active(d.key);var v=mini.querySelector('.cb7542-state-value');var txt=a?norm(a.dataset.cb75Val||a.textContent):'';v.textContent=txt||'Não informado';v.classList.toggle('empty',!txt);mini.classList.toggle('attention',/triste|ansioso|irritado|baixo|recusou|interrompido|pouco|sonolento|com apoio|baixa|acamado/.test(txt));});
 }
 function openPicker(d){
  var bs=originals(d.key);if(!bs.length)return;
  var modal=document.createElement('div');modal.className='cb7542-modal';
  modal.innerHTML='<div class="cb7542-sheet"><div class="cb7542-sheet-head"><div class="cb7542-sheet-title">'+d.icon+' '+d.label+'</div><button type="button" class="cb7542-close">×</button></div><div class="cb7542-options"></div><div class="cb7542-help">Toque novamente na opção marcada para desmarcar.</div></div>';
  var box=modal.querySelector('.cb7542-options');
  bs.forEach(function(orig){var b=document.createElement('button');b.type='button';b.innerHTML=orig.innerHTML;if(orig.classList.contains('active'))b.classList.add('selected');b.onclick=function(){orig.click();setTimeout(function(){refresh();modal.remove();},40);};box.appendChild(b);});
  modal.querySelector('.cb7542-close').onclick=function(){modal.remove();};modal.onclick=function(e){if(e.target===modal)modal.remove();};document.body.appendChild(modal);
 }
 function setup(){
  if(innerWidth>=768)return;var c=card();if(!c)return;
  if(!document.getElementById('cb7542-state-grid')){var original=c.querySelector(':scope > .cb75-grid-2');if(!original)return;var grid=document.createElement('div');grid.id='cb7542-state-grid';defs.forEach(function(d){var mini=document.createElement('div');mini.className='cb7542-state-mini';mini.dataset.key=d.key;mini.innerHTML='<div class="cb7542-state-label">'+d.icon+' '+d.label+'</div><div class="cb7542-state-value empty">Não informado</div>';mini.onclick=function(){openPicker(d);};grid.appendChild(mini);});c.insertBefore(grid,original);}
  refresh();
 }
 var previous=window.setCB75Quick;
 window.setCB75Quick=function(key,val,btn){
   try{var log=(typeof getTodayLog==='function')?getTodayLog():{};var next=(log&&log[key]===val)?'':val;if(typeof saveTodayLog==='function')saveTodayLog({[key]:next},'cb75-state');if(typeof pushHaptic==='function')pushHaptic([12]);setTimeout(refresh,20);return;}catch(e){}
   if(typeof previous==='function')return previous(key,val,btn);
 };
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup,{once:true});else setup();setTimeout(setup,150);setTimeout(setup,500);setTimeout(setup,1200);
 var c=card();if(c)new MutationObserver(refresh).observe(c,{subtree:true,attributes:true,attributeFilter:['class']});
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-42-state-card-real-target';",t,count=1);sw.write_text(t,encoding='utf-8')
