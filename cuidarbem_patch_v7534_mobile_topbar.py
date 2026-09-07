from pathlib import Path
import re
p=Path('index.html');s=p.read_text(encoding='utf-8');marker='cuidarbem-v75-76-consultas-exames-stable'
if marker not in s:
 patch=r'''
<!-- v75.76 — Consultas/Exames: dois cards estáveis, sem textos órfãos -->
<style id="cuidarbem-v75-76-consultas-exames-stable">
@media(max-width:767px){
 #cb7573-consultas,#cb7574-consultas,#cb7575-consultas{display:none!important}
 #cb7576-upcoming{display:block!important;margin-top:12px}
 #cb7576-upcoming .cb7576-card{display:flex!important;align-items:center;gap:12px;padding:17px 18px!important;margin:12px 0!important;cursor:pointer}
 #cb7576-upcoming .ico{font-size:25px;flex:0 0 auto;width:34px;text-align:center}
 #cb7576-upcoming .copy{flex:1;min-width:0}
 #cb7576-upcoming .title{font-family:'Nunito',sans-serif;font-size:17px;font-weight:900;color:var(--green-800);line-height:1.2}
 #cb7576-upcoming .sub{font-size:12px;color:var(--text-muted);font-weight:700;margin-top:4px;line-height:1.35}
 #cb7576-upcoming .go{font-size:25px;color:var(--green-600)}
 .cb7576-hide-old{display:none!important}
}
@media(min-width:768px){#cb7576-upcoming{display:none!important}}
</style>
<script id="cuidarbem-v75-76-consultas-exames-stable-js">
(function(){
 function tx(e){return(e&&e.textContent||'').replace(/\s+/g,' ').trim()}
 function setup(){
  if(innerWidth>767)return;
  var all=document.querySelectorAll('*'),ch=null,eh=null;
  for(var i=0;i<all.length;i++){
   if(all[i].children.length)continue;
   var t=tx(all[i]);
   if(!ch&&/^Próximas consultas$/i.test(t))ch=all[i];
   if(!eh&&/^Próximos exames$/i.test(t))eh=all[i];
  }
  if(!ch||!eh)return;
  var root=ch.closest('.screen')||ch.closest('[id^="screen-"]')||document;
  /* neutraliza os patches anteriores que competiam entre si */
  ['cb7573-consultas','cb7574-consultas','cb7575-consultas','cb7573-exames'].forEach(function(id){var e=document.getElementById(id);if(e)e.style.setProperty('display','none','important')});
  var leaves=root.querySelectorAll('*');
  for(var j=0;j<leaves.length;j++){
   if(leaves[j].children.length)continue;
   var z=tx(leaves[j]);
   if(/^Próximas consultas$/i.test(z)||/^Próximos exames$/i.test(z)||/^Nenhuma consulta agendada\.?$/i.test(z)||/^Nenhum exame agendado\.?$/i.test(z))leaves[j].classList.add('cb7576-hide-old');
  }
  if(document.getElementById('cb7576-upcoming'))return;
  var wrap=document.createElement('div');wrap.id='cb7576-upcoming';
  wrap.innerHTML='<section id="cb7576-consultas" class="card cb7576-card"><div class="ico">🩺</div><div class="copy"><div class="title">Próximas consultas</div><div class="sub">Nenhuma consulta agendada</div></div><div class="go">›</div></section><section id="cb7576-exames" class="card cb7576-card"><div class="ico">🔬</div><div class="copy"><div class="title">Próximos exames</div><div class="sub">Nenhum exame agendado</div></div><div class="go">›</div></section>';
  var anchor=ch.parentElement;anchor.parentNode.insertBefore(wrap,anchor);
 }
 function run(){setup()}
 document.addEventListener('DOMContentLoaded',run);
 var n=0,t=setInterval(function(){run();if(document.getElementById('cb7576-upcoming')||++n>100)clearInterval(t)},200);
 /* reaplica ocultação depois de renderizações tardias, evitando o pisca-pisca */
 var mo=new MutationObserver(function(){if(innerWidth<=767)setup()});
 document.addEventListener('DOMContentLoaded',function(){mo.observe(document.body,{childList:true,subtree:true})});
})();
</script>
'''
 pos=s.rfind('</body>')
 if pos<0:raise SystemExit('body not found')
 s=s[:pos]+patch+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-76-consultas-exames-stable';",t,count=1);sw.write_text(t,encoding='utf-8')
