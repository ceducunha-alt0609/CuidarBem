from pathlib import Path
import re
index=Path('index.html');s=index.read_text(encoding='utf-8');marker='cuidarbem-v75-69-medication-auto-times'
if marker not in s:
 patch=r'''
<!-- v75.69 — calcula horários seguintes a partir do primeiro -->
<style id="cuidarbem-v75-69-medication-auto-times">
@media(max-width:767px){
 .cb7567-time.cb7569-suggested{background:#fff7df!important;border-color:#e4bd68!important;color:#76520b!important;box-shadow:inset 0 0 0 1px rgba(202,145,35,.08)}
 .cb7568-time-field.cb7569-auto label{color:#9a6811!important}.cb7568-time-field.cb7569-auto label::after{content:' · sugerido';font-size:9px;font-weight:800;text-transform:none;letter-spacing:0;color:#a97920}
}
</style>
<script id="cuidarbem-v75-69-medication-auto-times-js">
(function(){
 function setup(){var freq=document.getElementById('cb7567-frequency'),wrap=document.getElementById('cb7567-times-wrap');if(!freq||!wrap||freq.dataset.cb7569)return;freq.dataset.cb7569='1';
  function mins(v){var p=v.split(':');return (+p[0])*60+(+p[1])}function clock(m){m=(m+1440)%1440;return String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0')}
  function step(){var v=freq.value;if(v==='2x/dia'||v==='12/12h')return 720;if(v==='3x/dia'||v==='8/8h')return 480;if(v==='4x/dia'||v==='6/6h')return 360;return 0}
  function bind(){var ins=[].slice.call(wrap.querySelectorAll('.cb7567-time'));if(!ins.length)return;ins.forEach(function(x,i){x.dataset.cb7569Index=i;if(i>0)x.addEventListener('input',function(){this.classList.remove('cb7569-suggested');var b=this.closest('.cb7568-time-field');if(b)b.classList.remove('cb7569-auto')})});ins[0].addEventListener('change',function(){var gap=step(),base=this.value;if(!gap||!base)return;ins.slice(1).forEach(function(x,i){x.value=clock(mins(base)+gap*(i+1));x.classList.add('cb7569-suggested');var b=x.closest('.cb7568-time-field');if(b)b.classList.add('cb7569-auto')})});
  }
  freq.addEventListener('change',function(){setTimeout(bind,20)});
  var mo=new MutationObserver(function(){setTimeout(bind,0)});mo.observe(wrap,{childList:true,subtree:true});
 }
 document.addEventListener('DOMContentLoaded',setup);var n=0,x=setInterval(function(){setup();if(document.querySelector('#cb7567-frequency[data-cb7569]')||++n>50)clearInterval(x)},250);
})();
</script>
'''
 pos=s.rfind('</body>');s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8');sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-69-medication-auto-times';",t,count=1);sw.write_text(t,encoding='utf-8')
