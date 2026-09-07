from pathlib import Path
import re
p=Path('index.html');s=p.read_text(encoding='utf-8');marker='cuidarbem-v75-72-reports-direct-ids'
if marker not in s:
 patch=r'''
<!-- v75.72 — Relatórios mobile: IDs/classes reais -->
<style id="cuidarbem-v75-72-reports-direct-ids">
@media(max-width:767px){
 #screen-reports .stats-grid{display:none!important}
 .cb7572-entry{display:block!important;padding:18px 20px!important;cursor:pointer}
 .cb7572-entry .r{display:flex;align-items:center;gap:12px}.cb7572-entry .i{font-size:25px}.cb7572-entry .c{flex:1;min-width:0}.cb7572-entry .t{font-family:'Nunito',sans-serif;font-size:17px;font-weight:900;color:var(--green-800)}.cb7572-entry .s{font-size:12px;font-weight:700;color:var(--text-muted);margin-top:3px;line-height:1.35}.cb7572-entry .g{font-size:25px;color:var(--green-600)}
 .cb7572-source{display:none!important}.cb7572-source.open{display:block!important}.cb7572-entry.open{display:none!important}
 .cb7572-back{display:none!important;width:100%;margin:0 0 10px}.cb7572-back.show{display:flex!important}
 #cb7572-period{display:flex;gap:8px;margin:0 0 14px;padding:4px;border:1px solid var(--green-200);border-radius:16px;background:rgba(255,255,255,.65)}#cb7572-period button{flex:1;border:0;background:transparent;border-radius:12px;padding:10px 5px;font-weight:900;color:var(--green-700)}#cb7572-period button.active{background:var(--green-600);color:#fff}
}
@media(min-width:768px){.cb7572-entry,.cb7572-back,#cb7572-period{display:none!important}}
</style>
<script id="cuidarbem-v75-72-reports-direct-ids-js">
(function(){
 function make(key,src,title,sub,icon){if(!src||document.getElementById('cb7572-'+key+'-entry'))return;src.classList.add('cb7572-source');var e=document.createElement('section');e.id='cb7572-'+key+'-entry';e.className='card cb7572-entry';e.innerHTML='<div class="r"><div class="i">'+icon+'</div><div class="c"><div class="t">'+title+'</div><div class="s">'+sub+'</div></div><div class="g">›</div></div>';src.parentNode.insertBefore(e,src);var b=document.createElement('button');b.className='cb75-btn secondary cb7572-back';b.textContent='‹ Voltar aos relatórios';src.parentNode.insertBefore(b,src);e.onclick=function(){src.classList.add('open');e.classList.add('open');b.classList.add('show');setTimeout(function(){b.scrollIntoView({behavior:'smooth',block:'start'})},30)};b.onclick=function(){src.classList.remove('open');e.classList.remove('open');b.classList.remove('show');setTimeout(function(){e.scrollIntoView({behavior:'smooth',block:'center'})},30)}}
 function setup(){var root=document.getElementById('screen-reports');if(!root)return;
  var weekly=document.getElementById('cb75-weekly-report-card');make('summary',weekly,'Resumo do período','Para família ou consulta médica · texto, voz e PDF','📝');
  var monthly=document.getElementById('monthly-adherence-pct');if(monthly){var mc=monthly.closest('.cb-analytics-card');make('monthly',mc,'Adesão mensal','Visão dos últimos 30 dias','📈')}
  var functional=document.getElementById('functional-evolution-summary');if(functional){var fc=functional.closest('.cb-analytics-card');make('functional',fc,'Evolução funcional','Barthel / mRS e acompanhamento da recuperação','🧭')}
  var adh=document.getElementById('adherence-list');if(adh){var ac=adh.closest('.card');make('category',ac,'Adesão aos cuidados','Remédios, consultas, exames, fisioterapia e exercícios','📊')}
  var sum=document.getElementById('cb75-weekly-summary');if(sum)sum.textContent=sum.textContent.replace(/CuidarBem\s+V\d+(?:\.\d+)?/ig,'CuidarBem');
  if(!document.getElementById('cb7572-period')){var content=root.querySelector('.content'),anchor=document.getElementById('cb7572-summary-entry')||content.firstElementChild;if(content&&anchor){var q=document.createElement('div');q.id='cb7572-period';q.innerHTML='<button class="active">7 dias</button><button>30 dias</button>';content.insertBefore(q,anchor);q.onclick=function(e){if(e.target.tagName!=='BUTTON')return;q.querySelectorAll('button').forEach(function(x){x.classList.toggle('active',x===e.target)})}}}
 }
 document.addEventListener('DOMContentLoaded',setup);var n=0,t=setInterval(function(){setup();if(++n>80)clearInterval(t)},200);
})();
</script>
'''
 pos=s.rfind('</body>');
 if pos<0:raise SystemExit('body not found')
 s=s[:pos]+patch+'\n'+s[pos:]
p.write_text(s,encoding='utf-8');sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-72-reports-direct-ids';",t,count=1);sw.write_text(t,encoding='utf-8')
