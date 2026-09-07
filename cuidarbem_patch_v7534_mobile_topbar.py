from pathlib import Path
import re

index=Path('index.html'); s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-64-medication-header-fix'
if marker not in s:
    patch=r'''
<!-- v75.64 — Mobile: corrige sobreposição do cabeçalho de medicamentos -->
<style id="cuidarbem-v75-64-medication-header-fix">
@media(max-width:767px){
 #screen-ocr .header-sub-title,
 #screen-ocr .header-date{font-size:inherit!important;}
 #screen-ocr .header-sub-title::after,
 #screen-ocr .header-date::after{content:none!important;display:none!important;}
 #screen-ocr .header-sub-title{font-size:22px!important;font-weight:800!important;line-height:1.15!important;}
 #screen-ocr .header-date{font-size:13px!important;line-height:1.35!important;margin-top:5px!important;}
}
</style>
<script id="cuidarbem-v75-64-medication-header-fix-js">
(function(){
 function fix(){
   var root=document.getElementById('screen-ocr');if(!root)return;
   var t=root.querySelector('.header-sub-title'),d=root.querySelector('.header-date');
   if(t)t.textContent='💊 Adicionar medicamento';
   if(d)d.textContent='Cadastre pela receita ou manualmente';
 }
 fix();document.addEventListener('DOMContentLoaded',fix);setTimeout(fix,100);setTimeout(fix,600);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-64-medication-header-fix';",t,count=1);sw.write_text(t,encoding='utf-8')
