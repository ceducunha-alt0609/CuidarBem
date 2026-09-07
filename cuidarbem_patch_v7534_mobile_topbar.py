from pathlib import Path
import re

index=Path('index.html'); s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-65-medication-simple-choice'
if marker not in s:
    patch=r'''
<!-- v75.65 — Mobile: receita como ação principal; manual como alternativa -->
<style id="cuidarbem-v75-65-medication-simple-choice">
@media(max-width:767px){
 #screen-ocr #cb7563-methods{display:block!important;margin-top:12px!important;}
 #screen-ocr #cb7563-gallery{display:none!important;}
 #screen-ocr #cb7563-manual{width:100%!important;min-height:62px!important;flex-direction:row!important;gap:9px!important;font-size:16px!important;border-radius:16px!important;}
 #screen-ocr #cb7563-manual .ico{font-size:22px!important;}
 #screen-ocr #ocr-upload-zone>.card:first-child{cursor:pointer!important;}
 #screen-ocr #ocr-upload-zone>.card:first-child::after{content:'Toque para ler a receita ›';display:block;margin-top:12px;font-size:12px;font-weight:800;color:var(--green-600);}
}
</style>
<script id="cuidarbem-v75-65-medication-simple-choice-js">
(function(){
 function setup(){
   var zone=document.getElementById('ocr-upload-zone');if(!zone)return;
   var upload=zone.querySelector('.card');if(!upload||upload.dataset.cb7565)return;
   upload.dataset.cb7565='1';upload.setAttribute('role','button');upload.setAttribute('tabindex','0');
   function choose(){var f=document.getElementById('ocr-file-input');if(f){f.removeAttribute('capture');f.click();}}
   upload.addEventListener('click',choose);
   upload.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();choose();}});
 }
 document.addEventListener('DOMContentLoaded',setup);var n=0,x=setInterval(function(){setup();if(document.querySelector('#ocr-upload-zone .card[data-cb7565]')||++n>50)clearInterval(x);},250);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-65-medication-simple-choice';",t,count=1);sw.write_text(t,encoding='utf-8')
