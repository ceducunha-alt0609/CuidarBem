from pathlib import Path
import re

index=Path('index.html')
s=index.read_text(encoding='utf-8')

marker='cuidarbem-v75-41-general-state-cards'
if marker not in s:
    patch=r'''

<!-- v75.41 — Mobile: Estado Geral em 4 mini-cards + seleção reversível -->
<style id="cuidarbem-v75-41-general-state-cards">
@media(max-width:767px){
  .cb7541-panel{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:12px 0;}
  .cb7541-card{border:1px solid rgba(26,107,92,.16);border-radius:16px;background:rgba(255,255,255,.78);padding:13px;min-height:88px;cursor:pointer;}
  .cb7541-label{font:700 12px/1.2 'Nunito Sans',sans-serif;letter-spacing:.04em;text-transform:uppercase;color:#52645f;}
  .cb7541-value{font:800 16px/1.3 'Nunito',sans-serif;color:#154f45;margin-top:8px;}
  .cb7541-value.empty{font-weight:600;color:#7a8985;}
  .cb7541-card.attention{border-color:rgba(220,70,60,.35);}
  .cb7541-original{display:none!important;}
  .cb7541-modal{position:fixed;inset:0;z-index:10050;background:rgba(12,38,33,.45);display:flex;align-items:flex-end;justify-content:center;padding:16px;}
  .cb7541-sheet{width:min(100%,480px);background:#fff;border-radius:22px 22px 16px 16px;padding:18px;box-shadow:0 -10px 35px rgba(0,0,0,.18);}
  .cb7541-sheet-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;}
  .cb7541-sheet-title{font:800 20px/1.2 'Nunito',sans-serif;color:#154f45;}
  .cb7541-close{border:0;background:transparent;font-size:26px;padding:4px 8px;}
  .cb7541-options{display:flex;flex-wrap:wrap;gap:9px;}
  .cb7541-options button{border:1.5px solid rgba(26,107,92,.25);border-radius:999px;background:#fff;padding:11px 14px;font:800 15px 'Nunito',sans-serif;color:#243b36;}
  .cb7541-options button.selected{background:#e8f5f1;border-color:#1a6b5c;color:#154f45;}
  .cb7541-help{font:600 12px/1.35 'Nunito Sans',sans-serif;color:#71807c;margin-top:12px;}
}
</style>
<script id="cuidarbem-v75-41-general-state-cards-js">
(function(){
 'use strict';
 var defs=[
  {key:'humor',label:'Humor',icon:'🙂',words:['calmo','triste','ansioso','irritado']},
  {key:'apetite',label:'Apetite',icon:'🍽️',words:['bom','regular','baixo','recusou']},
  {key:'sono',label:'Sono',icon:'🌙',words:['bom','interrompido','pouco','sonolento']},
  {key:'mobilidade',label:'Mobilidade',icon:'🚶',words:['boa','com apoio','baixa','acamado']}
 ];
 function norm(v){return(v||'').replace(/\s+/g,' ').trim().toLowerCase();}
 function findSection(){
  var root=document.querySelector('#screen-home');if(!root)return null;
  var nodes=Array.from(root.querySelectorAll('*'));
  var title=nodes.find(function(el){return norm(el.textContent)==='estado geral do paciente'&&el.children.length<3;});
  return title?(title.closest('.card')||title.parentElement):null;
 }
 function findButtons(section,d){return Array.from(section.querySelectorAll('button,[role="button"]')).filter(function(b){var t=norm(b.textContent);return d.words.some(function(w){return t===w||t.endsWith(' '+w)||t.indexOf(w)!==-1;});});}
 function selected(buttons){return buttons.find(function(b){return b.classList.contains('active')||b.classList.contains('selected')||b.getAttribute('aria-pressed')==='true'||/background[^;]*(green|#0|var\(--primary)/i.test(b.getAttribute('style')||'');});}
 function valueOf(section,d){var bs=findButtons(section,d),s=selected(bs);return s?norm(s.textContent):'';}
 function refresh(section,panel){defs.forEach(function(d){var c=panel.querySelector('[data-cb7541="'+d.key+'"]');if(!c)return;var v=valueOf(section,d);var val=c.querySelector('.cb7541-value');val.textContent=v||'Não informado';val.classList.toggle('empty',!v);c.classList.toggle('attention',/triste|ansioso|irritado|baixo|recusou|interrompido|pouco|sonolento|com apoio|baixa|acamado/.test(v));});}
 function open(section,panel,d){
  var bs=findButtons(section,d);if(!bs.length)return;
  var modal=document.createElement('div');modal.className='cb7541-modal';
  var opts=bs.map(function(b,i){return '<button type="button" data-i="'+i+'">'+b.innerHTML+'</button>';}).join('');
  modal.innerHTML='<div class="cb7541-sheet"><div class="cb7541-sheet-head"><div class="cb7541-sheet-title">'+d.icon+' '+d.label+'</div><button class="cb7541-close" type="button">×</button></div><div class="cb7541-options">'+opts+'</div><div class="cb7541-help">Toque na opção marcada novamente para desmarcar.</div></div>';
  document.body.appendChild(modal);
  var cur=selected(bs);Array.from(modal.querySelectorAll('[data-i]')).forEach(function(o){if(cur===bs[+o.dataset.i])o.classList.add('selected');o.onclick=function(){var target=bs[+o.dataset.i];var was=target===selected(bs);if(was){target.click();setTimeout(function(){target.classList.remove('active','selected');target.setAttribute('aria-pressed','false');refresh(section,panel);},30);}else{target.click();setTimeout(function(){refresh(section,panel);},30);}modal.remove();};});
  modal.querySelector('.cb7541-close').onclick=function(){modal.remove();};modal.onclick=function(e){if(e.target===modal)modal.remove();};
 }
 function setup(){
  if(innerWidth>=768)return;var section=findSection();if(!section||section.dataset.cb7541)return;section.dataset.cb7541='1';
  var panel=document.createElement('div');panel.className='cb7541-panel';
  defs.forEach(function(d){var c=document.createElement('div');c.className='cb7541-card';c.dataset.cb7541=d.key;c.innerHTML='<div class="cb7541-label">'+d.icon+' '+d.label+'</div><div class="cb7541-value empty">Não informado</div>';c.onclick=function(){open(section,panel,d);};panel.appendChild(c);});
  var firstGroup=null;defs.some(function(d){var b=findButtons(section,d)[0];if(b){firstGroup=b.closest('div');return true;}return false;});
  if(firstGroup){var host=firstGroup.parentElement;host.insertBefore(panel,firstGroup);Array.from(host.children).forEach(function(ch){if(ch!==panel&&defs.some(function(d){return findButtons(ch,d).length>0;}))ch.classList.add('cb7541-original');});}
  else section.appendChild(panel);
  refresh(section,panel);new MutationObserver(function(){refresh(section,panel);}).observe(section,{subtree:true,attributes:true,attributeFilter:['class','aria-pressed']});
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup,{once:true});else setup();setTimeout(setup,300);setTimeout(setup,900);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-41-general-state-cards';",t,count=1);sw.write_text(t,encoding='utf-8')
