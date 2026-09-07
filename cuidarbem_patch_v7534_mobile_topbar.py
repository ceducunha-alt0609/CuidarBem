from pathlib import Path
import re
index=Path('index.html');s=index.read_text(encoding='utf-8');marker='cuidarbem-v75-70-reports-caregiver'
if marker not in s:
 patch=r'''
<!-- v75.70 — Relatórios mobile: leitura primeiro, detalhes sob demanda -->
<style id="cuidarbem-v75-70-reports-caregiver">
@media(max-width:767px){
 #cb7570-period{display:flex;gap:8px;margin:0 0 14px;padding:4px;background:rgba(255,255,255,.62);border:1px solid var(--green-200);border-radius:16px}
 #cb7570-period button{flex:1;border:0;background:transparent;border-radius:12px;padding:10px 8px;font-weight:900;color:var(--green-700);font-size:13px}
 #cb7570-period button.active{background:var(--green-600);color:white;box-shadow:0 3px 10px rgba(0,0,0,.08)}
 .cb7570-compact{cursor:pointer}.cb7570-compact .cb7570-head{display:flex;align-items:center;gap:10px}.cb7570-compact .cb7570-copy{flex:1;min-width:0}.cb7570-compact .cb7570-title{font-family:'Nunito',sans-serif;font-weight:900;font-size:17px;color:var(--green-800)}.cb7570-compact .cb7570-sub{font-size:12px;font-weight:700;color:var(--text-muted);margin-top:3px;line-height:1.35}.cb7570-compact .cb7570-go{font-size:25px;color:var(--green-600)}
 body:not(.cb7570-summary-open) #cb7570-summary-source{display:none!important}body.cb7570-summary-open #cb7570-summary-entry{display:none!important}
 body:not(.cb7570-adherence-open) #cb7570-adherence-source{display:none!important}body.cb7570-adherence-open #cb7570-adherence-entry{display:none!important}
 body:not(.cb7570-functional-open) #cb7570-functional-source{display:none!important}body.cb7570-functional-open #cb7570-functional-entry{display:none!important}
 .cb7570-close{display:none!important;width:100%;margin:0 0 10px}.cb7570-summary-open #cb7570-summary-close,.cb7570-adherence-open #cb7570-adherence-close,.cb7570-functional-open #cb7570-functional-close{display:flex!important}
 .cb7570-empty-note{font-size:12px;color:var(--text-muted);font-weight:700}
}
@media(min-width:768px){#cb7570-period,.cb7570-compact,.cb7570-close{display:none!important}}
</style>
<script id="cuidarbem-v75-70-reports-caregiver-js">
(function(){
 function tx(e){return(e&&e.textContent||'').replace(/\s+/g,' ').trim()}function leafFind(re){var a=document.querySelectorAll('body *');for(var i=0;i<a.length;i++)if(a[i].children.length===0&&re.test(tx(a[i])))return a[i];return null}
 function cardOf(e){return e&&(e.closest('.card')||e.parentElement)}
 function compact(id,source,title,sub,icon,cls){if(!source||document.getElementById(id))return;source.id=id+'-source';var e=document.createElement('section');e.id=id+'-entry';e.className='card cb7570-compact';e.innerHTML='<div class="cb7570-head"><div style="font-size:25px">'+icon+'</div><div class="cb7570-copy"><div class="cb7570-title">'+title+'</div><div class="cb7570-sub">'+sub+'</div></div><div class="cb7570-go">›</div></div>';source.parentNode.insertBefore(e,source);var b=document.createElement('button');b.id=id+'-close';b.className='cb75-btn secondary cb7570-close';b.textContent='‹ Voltar aos relatórios';source.parentNode.insertBefore(b,source);function open(){document.body.classList.add(cls);setTimeout(function(){b.scrollIntoView({behavior:'smooth',block:'start'})},30)}function close(){document.body.classList.remove(cls);setTimeout(function(){e.scrollIntoView({behavior:'smooth',block:'center'})},30)}e.onclick=open;b.onclick=close}
 function setup(){var screen=leafFind(/^Relatórios$/i);if(!screen)return;var root=screen.closest('.screen')||document;
  if(!document.getElementById('cb7570-period')){var content=root.querySelector('.content')||root;var p=document.createElement('div');p.id='cb7570-period';p.innerHTML='<button class="active" data-days="7">Últimos 7 dias</button><button data-days="30">Últimos 30 dias</button>';content.insertBefore(p,content.firstElementChild);p.onclick=function(ev){var b=ev.target.closest('button');if(!b)return;p.querySelectorAll('button').forEach(function(x){x.classList.toggle('active',x===b)});p.dataset.days=b.dataset.days}}
  var sum=leafFind(/Resumo semanal para|Resumo semanal CuidarBem/i);var sc=cardOf(sum);if(sc){var html=sc.innerHTML;sc.innerHTML=html.replace(/CuidarBem\s+V\d+(?:\.\d+)?/ig,'CuidarBem');compact('cb7570-summary',sc,'Resumo do período','Leitura para família ou consulta médica · texto, voz e PDF','📝','cb7570-summary-open')}
  var adh=leafFind(/^ADESÃO POR CATEGORIA$/i);compact('cb7570-adherence',cardOf(adh),'Adesão aos cuidados','Remédios, consultas, exames, fisioterapia e exercícios','📊','cb7570-adherence-open');
  var fun=leafFind(/^EVOLUÇÃO FUNCIONAL$/i);compact('cb7570-functional',cardOf(fun),'Evolução funcional','Barthel / mRS e tendência funcional','🧭','cb7570-functional-open');
  var monthly=leafFind(/^ADESÃO MENSAL$/i),mc=cardOf(monthly);if(mc&&/0%/.test(tx(mc))){var graphs=mc.querySelectorAll('canvas,svg');graphs.forEach(function(g){g.style.display='none'});}
 }
 document.addEventListener('DOMContentLoaded',setup);var n=0,t=setInterval(function(){setup();if(++n>50)clearInterval(t)},250);
})();
</script>
'''
 pos=s.rfind('</body>');
 if pos<0: raise SystemExit('body not found')
 s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8');sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-70-reports-caregiver';",t,count=1);sw.write_text(t,encoding='utf-8')
