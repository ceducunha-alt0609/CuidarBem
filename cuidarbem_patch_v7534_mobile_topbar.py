from pathlib import Path
import re

index=Path('index.html'); s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-63-medication-intake'
if marker not in s:
    patch=r'''
<!-- v75.63 — Mobile: receita vira entrada segura de medicamentos -->
<style id="cuidarbem-v75-63-medication-intake">
@media(max-width:767px){
 #screen-ocr .header-sub-title{font-size:0!important;}
 #screen-ocr .header-sub-title::after{content:'💊 Adicionar medicamento';font-size:22px;font-weight:800;}
 #screen-ocr .header-date{font-size:0!important;}
 #screen-ocr .header-date::after{content:'Cadastre pela receita ou manualmente';font-size:13px;}
 #screen-ocr #ocr-upload-zone>.card:first-child{padding:22px 18px!important;border-style:solid!important;background:var(--card-bg)!important;}
 #screen-ocr #ocr-upload-zone>.card:first-child>div:first-child{font-size:38px!important;margin-bottom:8px!important;}
 #screen-ocr #ocr-upload-zone>.card:first-child>div:nth-child(2){font-size:17px!important;}
 #screen-ocr .cb7563-methods{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;}
 #screen-ocr .cb7563-method{border:1.5px solid var(--green-200);border-radius:16px;background:var(--card-bg);padding:15px 10px;min-height:86px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;font-family:'Nunito',sans-serif;color:var(--green-800);font-weight:800;font-size:14px;cursor:pointer;}
 #screen-ocr .cb7563-method .ico{font-size:25px;}
 #screen-ocr .cb7563-safe{margin-top:14px;padding:11px 13px;border-radius:13px;background:var(--green-50);color:var(--green-600);font-size:12px;line-height:1.4;font-weight:700;}
 #screen-ocr .cb7563-old-actions{display:none!important;}
 #screen-ocr .cb7563-how{display:none!important;}
}
@media(min-width:768px){.cb7563-methods,.cb7563-safe{display:none!important;}}
</style>
<script id="cuidarbem-v75-63-medication-intake-js">
(function(){
 function norm(e){return (e&&e.textContent||'').replace(/\s+/g,' ').trim();}
 function setup(){
   var zone=document.getElementById('ocr-upload-zone'); if(!zone||document.getElementById('cb7563-methods'))return;
   var upload=zone.querySelector('.card'); if(!upload)return;
   var title=upload.children[1],sub=upload.children[2];
   if(title)title.textContent='Ler receita';
   if(sub)sub.textContent='Fotografe ou escolha uma imagem para preencher os dados';
   var old=upload.nextElementSibling;
   if(old)old.classList.add('cb7563-old-actions');
   var methods=document.createElement('div'); methods.id='cb7563-methods'; methods.className='cb7563-methods';
   methods.innerHTML='<button class="cb7563-method" type="button" id="cb7563-gallery"><span class="ico">🖼️</span><span>Escolher receita</span></button><button class="cb7563-method" type="button" id="cb7563-manual"><span class="ico">✍️</span><span>Adicionar manualmente</span></button>';
   (old||upload).insertAdjacentElement('afterend',methods);
   var safe=document.createElement('div');safe.className='cb7563-safe';safe.innerHTML='🛡️ A leitura organiza o que está na receita. Confira nome, dose, via, frequência e horários antes de adicionar à Agenda.';methods.insertAdjacentElement('afterend',safe);
   document.getElementById('cb7563-gallery').onclick=function(){var f=document.getElementById('ocr-file-input');if(f){f.removeAttribute('capture');f.click();}};
   document.getElementById('cb7563-manual').onclick=function(){
     var add=document.querySelector('[onclick*="openAddTaskModal"], [onclick*="openTaskModal"], #add-task-btn, #btn-add-task');
     if(add){add.click();return;}
     if(typeof openAddTaskModal==='function'){openAddTaskModal();return;}
     if(typeof goScreen==='function'){goScreen('calendar',document.getElementById('nav-calendar'));setTimeout(function(){var b=document.querySelector('#screen-calendar .btn-add');if(b)b.click();},100);}
   };
   /* Remove o card explicativo antigo: fluxo deve se explicar sozinho. */
   var root=document.getElementById('screen-ocr'),cards=root?root.querySelectorAll('.card'):[];
   cards.forEach(function(c){var x=norm(c);if(x.indexOf('COMO FUNCIONA')>=0||x.indexOf('Fotografe a receita médica')>=0){c.classList.add('cb7563-how');}});
 }
 document.addEventListener('DOMContentLoaded',setup);var n=0,x=setInterval(function(){setup();if(document.getElementById('cb7563-methods')||++n>50)clearInterval(x);},250);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-63-medication-intake';",t,count=1);sw.write_text(t,encoding='utf-8')
