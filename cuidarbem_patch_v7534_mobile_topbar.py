from pathlib import Path
import re
p=Path('index.html');s=p.read_text(encoding='utf-8');marker='cuidarbem-v75-74-consultas-card-fix'
if marker not in s:
 patch=r'''
<!-- v75.74 — Corrige somente Próximas consultas no mobile -->
<style id="cuidarbem-v75-74-consultas-card-fix">
@media(max-width:767px){
 #cb7574-consultas{display:block!important;padding:17px 18px!important;margin:12px 0!important;cursor:pointer}
 #cb7574-consultas .row{display:flex;align-items:center;gap:12px}#cb7574-consultas .ico{font-size:25px;flex:0 0 auto}#cb7574-consultas .copy{flex:1;min-width:0}#cb7574-consultas .title{font-family:'Nunito',sans-serif;font-size:17px;font-weight:900;color:var(--green-800);line-height:1.2}#cb7574-consultas .sub{font-size:12px;color:var(--text-muted);font-weight:700;margin-top:4px;line-height:1.35}#cb7574-consultas .go{font-size:25px;color:var(--green-600)}
 .cb7574-consult-old{display:none!important}
}
@media(min-width:768px){#cb7574-consultas{display:none!important}}
</style>
<script id="cuidarbem-v75-74-consultas-card-fix-js">
(function(){
 function tx(e){return(e&&e.textContent||'').replace(/\s+/g,' ').trim()}
 function setup(){
  if(document.getElementById('cb7574-consultas'))return;
  var all=document.querySelectorAll('*'),h=null;
  for(var i=0;i<all.length;i++){if(all[i].children.length===0&&/^Próximas consultas$/i.test(tx(all[i]))){h=all[i];break}}
  if(!h)return;
  var empty=null,p=h.parentElement;
  for(var j=0;j<6&&p;j++,p=p.parentElement){var nodes=p.querySelectorAll('*');for(var k=0;k<nodes.length;k++){if(nodes[k].children.length===0&&/Nenhuma consulta agendada/i.test(tx(nodes[k]))){empty=nodes[k];break}}if(empty)break}
  var holder=h.parentElement;if(empty&&empty.parentElement===holder){}else if(empty){var q=h.parentElement;while(q&&q.parentElement&&q.parentElement.contains(empty)&&q.parentElement!==document.body)q=q.parentElement;holder=q||h.parentElement}
  h.classList.add('cb7574-consult-old'); if(empty)empty.classList.add('cb7574-consult-old');
  var c=document.createElement('section');c.id='cb7574-consultas';c.className='card';c.innerHTML='<div class="row"><div class="ico">🩺</div><div class="copy"><div class="title">Próximas consultas</div><div class="sub">Nenhuma consulta agendada</div></div><div class="go">›</div></div>';
  h.parentNode.insertBefore(c,h);
 }
 document.addEventListener('DOMContentLoaded',setup);var n=0,t=setInterval(function(){setup();if(document.getElementById('cb7574-consultas')||++n>80)clearInterval(t)},200);
})();
</script>
'''
 pos=s.rfind('</body>')
 if pos<0:raise SystemExit('body not found')
 s=s[:pos]+patch+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-74-consultas-card-fix';",t,count=1);sw.write_text(t,encoding='utf-8')
