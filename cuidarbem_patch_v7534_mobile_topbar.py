from pathlib import Path
import re
index=Path('index.html');s=index.read_text(encoding='utf-8');marker='cuidarbem-v75-68-medication-time-labels'
if marker not in s:
 patch=r'''
<!-- v75.68 — identifica horários e separa período do tratamento -->
<style id="cuidarbem-v75-68-medication-time-labels">
@media(max-width:767px){
 #cb7567-times-wrap{margin-top:10px;grid-template-columns:repeat(2,minmax(0,1fr))!important}
 .cb7568-time-field{display:flex;flex-direction:column;gap:5px;min-width:0}.cb7568-time-field label{font-size:11px!important;font-weight:800!important;color:var(--green-700)!important;text-transform:uppercase;letter-spacing:.03em}.cb7568-time-field input{width:100%!important}
 .cb7568-period-label{grid-column:1/-1;margin:4px 0 -2px;font-size:12px;font-weight:900;color:var(--green-800);text-transform:uppercase;letter-spacing:.04em}
}
</style>
<script id="cuidarbem-v75-68-medication-time-labels-js">
(function(){
 function setup(){var freq=document.getElementById('cb7567-frequency'),wrap=document.getElementById('cb7567-times-wrap'),start=document.getElementById('cb7566-start');if(!freq||!wrap||!start||freq.dataset.cb7568)return;freq.dataset.cb7568='1';
  function labelTimes(){var inputs=[].slice.call(wrap.querySelectorAll('.cb7567-time'));inputs.forEach(function(inp,i){if(inp.parentElement.classList.contains('cb7568-time-field'))return;var box=document.createElement('div');box.className='cb7568-time-field';var lab=document.createElement('label');lab.textContent=(i+1)+'º horário';inp.parentNode.insertBefore(box,inp);box.appendChild(lab);box.appendChild(inp);});}
  freq.addEventListener('change',function(){setTimeout(labelTimes,0)});
  var sf=start.closest('.cb7566-field');if(sf&&!document.getElementById('cb7568-period-label')){var p=document.createElement('div');p.id='cb7568-period-label';p.className='cb7568-period-label';p.textContent='Período do tratamento';sf.parentNode.insertBefore(p,sf);}
 }
 document.addEventListener('DOMContentLoaded',setup);var n=0,x=setInterval(function(){setup();if(document.querySelector('#cb7567-frequency[data-cb7568]')||++n>50)clearInterval(x)},250);
})();
</script>
'''
 pos=s.rfind('</body>');s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8');sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-68-medication-time-labels';",t,count=1);sw.write_text(t,encoding='utf-8')
