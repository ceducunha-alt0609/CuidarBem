from pathlib import Path
import re
p=Path('index.html');s=p.read_text(encoding='utf-8');marker='cuidarbem-v75-75-consultas-mirror-exames'
if marker not in s:
 patch=r'''
<!-- v75.75 — Consultas: espelha diretamente o card de exames -->
<style id="cuidarbem-v75-75-consultas-mirror-exames">
@media(max-width:767px){
 #cb7575-consultas{display:block!important;margin:12px 0!important;cursor:pointer}
 #cb7575-consultas .title{font-family:'Nunito',sans-serif;font-size:17px;font-weight:900;color:var(--green-800)!important}
 #cb7575-consultas .sub{font-size:12px;color:var(--text-muted);font-weight:700;margin-top:4px}
 #cb7575-consultas .go{font-size:25px;color:var(--green-600)}
}
@media(min-width:768px){#cb7575-consultas{display:none!important}}
</style>
<script id="cuidarbem-v75-75-consultas-mirror-exames-js">
(function(){
 function tx(e){return(e&&e.textContent||'').replace(/\s+/g,' ').trim()}
 function setup(){
  if(innerWidth>767||document.getElementById('cb7575-consultas'))return;
  var exam=document.getElementById('cb7573-exames');if(!exam)return;
  var consultHeading=null,all=document.querySelectorAll('*');
  for(var i=0;i<all.length;i++){if(all[i].children.length===0&&/^Próximas consultas$/i.test(tx(all[i]))){consultHeading=all[i];break}}
  if(!consultHeading)return;
  var c=exam.cloneNode(true);c.id='cb7575-consultas';
  var ico=c.querySelector('.ico'),title=c.querySelector('.title'),sub=c.querySelector('.sub');
  if(ico)ico.textContent='🩺';if(title)title.textContent='Próximas consultas';if(sub)sub.textContent='Nenhuma consulta agendada';
  consultHeading.parentNode.insertBefore(c,consultHeading);
  consultHeading.style.setProperty('display','none','important');
  var next=consultHeading.nextElementSibling;
  if(next&&/Nenhuma consulta agendada/i.test(tx(next)))next.style.setProperty('display','none','important');
  c.onclick=function(){
   var olds=document.querySelectorAll('.cb7573-old-next');
   for(var j=0;j<olds.length;j++){if(/Próximas consultas|Nenhuma consulta agendada/i.test(tx(olds[j])))olds[j].style.display='block'}
  };
 }
 document.addEventListener('DOMContentLoaded',setup);var n=0,t=setInterval(function(){setup();if(document.getElementById('cb7575-consultas')||++n>100)clearInterval(t)},200);
})();
</script>
'''
 pos=s.rfind('</body>')
 if pos<0:raise SystemExit('body not found')
 s=s[:pos]+patch+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-75-consultas-mirror-exames';",t,count=1);sw.write_text(t,encoding='utf-8')
