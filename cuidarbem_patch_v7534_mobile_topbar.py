from pathlib import Path
import re
p=Path('index.html');s=p.read_text(encoding='utf-8');marker='cuidarbem-v75-73-consultas-compact'
if marker not in s:
 patch=r'''
<!-- v75.73 — Consultas/Exames mobile: explicação compacta + próximos em cards -->
<style id="cuidarbem-v75-73-consultas-compact">
@media(max-width:767px){
 .cb7573-ai-compact{padding:14px 16px!important;margin:12px 0!important;background:rgba(255,255,255,.62)!important;border:1px solid var(--green-200)!important;border-radius:18px!important;color:var(--green-700)!important;font-size:13px!important;font-weight:750!important;line-height:1.45!important}
 .cb7573-ai-source{display:none!important}
 .cb7573-next-card{display:block!important;padding:17px 18px!important;margin:12px 0!important;cursor:pointer}
 .cb7573-next-card .row{display:flex;align-items:center;gap:12px}.cb7573-next-card .ico{font-size:25px;flex:0 0 auto}.cb7573-next-card .copy{flex:1;min-width:0}.cb7573-next-card .title{font-family:'Nunito',sans-serif;font-size:17px;font-weight:900;color:var(--green-800);line-height:1.2}.cb7573-next-card .sub{font-size:12px;color:var(--text-muted);font-weight:700;margin-top:4px;line-height:1.35}.cb7573-next-card .go{font-size:25px;color:var(--green-600)}
 .cb7573-old-next{display:none!important}
}
@media(min-width:768px){.cb7573-ai-compact,.cb7573-next-card{display:none!important}}
</style>
<script id="cuidarbem-v75-73-consultas-compact-js">
(function(){
 function tx(e){return(e&&e.textContent||'').replace(/\s+/g,' ').trim()}
 function leaf(root,needle){var a=root.querySelectorAll('*');for(var i=0;i<a.length;i++){if(a[i].children.length===0&&tx(a[i]).toLowerCase().indexOf(needle.toLowerCase())>=0)return a[i]}return null}
 function setup(){
  var title=leaf(document,'Consultas'); if(!title)return;
  var root=title.closest('.screen')||title.closest('[id^="screen-"]')||document;
  if(document.getElementById('cb7573-ai-compact'))return;
  var ai=leaf(root,'O QUE A IA EXTRAI DO PEDIDO');
  if(ai){var ac=ai.closest('.card')||ai.parentElement;if(ac){ac.classList.add('cb7573-ai-source');var note=document.createElement('div');note.id='cb7573-ai-compact';note.className='cb7573-ai-compact';note.innerHTML='✨ Pela foto, o CuidarBem identifica tipo, local, data, horário e preparo. Confira os dados antes de adicionar à Agenda.';ac.parentNode.insertBefore(note,ac)}}
  function compact(needle,id,icon,label,empty){var h=leaf(root,needle);if(!h)return;var old=h.closest('.card')||h.parentElement;if(!old)return;old.classList.add('cb7573-old-next');var c=document.createElement('section');c.id=id;c.className='card cb7573-next-card';c.innerHTML='<div class="row"><div class="ico">'+icon+'</div><div class="copy"><div class="title">'+label+'</div><div class="sub">'+empty+'</div></div><div class="go">›</div></div>';old.parentNode.insertBefore(c,old);c.onclick=function(){old.classList.toggle('cb7573-old-next');if(old.style.display==='block'){old.style.display=''}else{old.style.display='block';setTimeout(function(){old.scrollIntoView({behavior:'smooth',block:'center'})},30)}}}
  compact('Próximas consultas','cb7573-consultas','🩺','Próximas consultas','Nenhuma consulta agendada');
  compact('Próximos exames','cb7573-exames','🔬','Próximos exames','Nenhum exame agendado');
 }
 document.addEventListener('DOMContentLoaded',setup);var n=0,t=setInterval(function(){setup();if(document.getElementById('cb7573-consultas')||++n>80)clearInterval(t)},200);
})();
</script>
'''
 pos=s.rfind('</body>')
 if pos<0:raise SystemExit('body not found')
 s=s[:pos]+patch+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-73-consultas-compact';",t,count=1);sw.write_text(t,encoding='utf-8')
