from pathlib import Path
import re

index=Path('index.html')
s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-52-health-organization'
if marker not in s:
    patch=r'''

<!-- v75.52 — Mobile: Saúde focada no registro; tendências e reabilitação compactadas -->
<style id="cuidarbem-v75-52-health-organization">
@media(max-width:767px){
  /* linguagem de desenvolvimento fora da interface */
  #cb75-care-label{font-size:0!important;}
  #cb75-care-label::after{content:'CUIDADO DIÁRIO';font-size:14px;letter-spacing:.06em;}

  /* histórico/tendência sai do fluxo principal de Saúde */
  #screen-dashboard #dash-rings,
  #screen-dashboard #dash-trends,
  #screen-dashboard #dash-weekly{display:none!important;}
  #screen-dashboard #dash-rings + .health-section-label,
  #screen-dashboard #dash-trends + .health-section-label{display:none!important;}

  /* entrada compacta para o módulo especializado de reabilitação */
  #cb7552-rehab-entry{display:block!important;}
  #cb75-rehab-ai-card,
  #screen-dashboard #rehab-card,
  #screen-dashboard .health-section-label[style*="margin-top:16px"] + #cb75-rehab-ai-card{display:none!important;}
  #cb7552-rehab-entry .cb7552-rehab-head{display:flex;align-items:center;gap:12px;}
  #cb7552-rehab-entry .cb7552-rehab-icon{width:48px;height:48px;border-radius:15px;background:var(--teal-50);display:flex;align-items:center;justify-content:center;font-size:24px;flex:0 0 auto;}
  #cb7552-rehab-entry .cb7552-rehab-copy{flex:1;min-width:0;}
  #cb7552-rehab-entry .cb7552-rehab-title{font-family:'Nunito',sans-serif;font-size:17px;font-weight:900;color:var(--green-800);line-height:1.15;}
  #cb7552-rehab-entry .cb7552-rehab-sub{font-size:12px;color:var(--text-muted);font-weight:700;line-height:1.35;margin-top:3px;}
  #cb7552-rehab-entry .cb7552-rehab-go{font-size:25px;color:var(--green-600);}
  #cb7552-rehab-entry .cb7552-rehab-meta{display:flex;gap:7px;flex-wrap:wrap;margin-top:12px;}
  #cb7552-rehab-entry .cb7552-chip{padding:5px 9px;border-radius:999px;background:var(--green-50);border:1px solid var(--green-200);font-size:11px;font-weight:800;color:var(--green-600);}

  /* módulo completo só aparece quando solicitado */
  body.cb7552-rehab-open #cb75-rehab-ai-card,
  body.cb7552-rehab-open #screen-dashboard #rehab-card{display:block!important;}
  body.cb7552-rehab-open #cb7552-rehab-entry{display:none!important;}
  #cb7552-rehab-close{display:none;}
  body.cb7552-rehab-open #cb7552-rehab-close{display:flex!important;position:sticky;top:8px;z-index:55;margin:0 0 12px;}
}
@media(min-width:768px){#cb7552-rehab-entry,#cb7552-rehab-close{display:none!important;}}
</style>
<script id="cuidarbem-v75-52-health-organization-js">
(function(){
  function setup(){
    var rehab=document.getElementById('rehab-card');
    var ai=document.getElementById('cb75-rehab-ai-card');
    if(!rehab || !ai || document.getElementById('cb7552-rehab-entry')) return;
    var entry=document.createElement('section');
    entry.className='card cb75-card'; entry.id='cb7552-rehab-entry';
    entry.setAttribute('role','button'); entry.setAttribute('tabindex','0');
    entry.innerHTML='<div class="cb7552-rehab-head"><div class="cb7552-rehab-icon">🦾</div><div class="cb7552-rehab-copy"><div class="cb7552-rehab-title">Reabilitação Pós-AVC</div><div class="cb7552-rehab-sub">Exercícios guiados, fase atual e evolução funcional.</div></div><div class="cb7552-rehab-go">›</div></div><div class="cb7552-rehab-meta"><span class="cb7552-chip">Programa personalizado</span><span class="cb7552-chip">Barthel / mRS</span></div>';
    ai.parentNode.insertBefore(entry,ai);
    var close=document.createElement('button'); close.id='cb7552-rehab-close'; close.className='cb75-btn secondary'; close.innerHTML='‹ Voltar para Saúde';
    ai.parentNode.insertBefore(close,ai);
    function openRehab(){document.body.classList.add('cb7552-rehab-open'); setTimeout(function(){close.scrollIntoView({behavior:'smooth',block:'start'});},30);}
    function closeRehab(){document.body.classList.remove('cb7552-rehab-open'); setTimeout(function(){entry.scrollIntoView({behavior:'smooth',block:'center'});},30);}
    entry.addEventListener('click',openRehab); entry.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();openRehab();}}); close.addEventListener('click',closeRehab);
  }
  var tries=0, timer=setInterval(function(){setup(); if(document.getElementById('cb7552-rehab-entry') || ++tries>40) clearInterval(timer);},250);
  document.addEventListener('DOMContentLoaded',setup);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8')

sw=Path('sw.js'); t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-52-health-organization';",t,count=1)
sw.write_text(t,encoding='utf-8')
