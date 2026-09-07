from pathlib import Path
import re
p=Path('index.html'); s=p.read_text(encoding='utf-8')
marker='cuidarbem-v75-85-patient-sections'
if marker not in s:
 patch=r'''
<!-- v75.85 — Mobile: Paciente vira índice com painéis específicos -->
<style id="cuidarbem-v75-85-patient-sections">
@media(max-width:767px){
 #cb7585-patient-index{display:none;padding:16px 16px calc(var(--nav-h) + 22px);}
 body.cb7585-patient-index-open #cb7585-patient-index{display:block!important;}
 body.cb7585-patient-index-open #screen-profile{display:none!important;}
 #cb7585-patient-index .cb7585-title{font:900 22px 'Nunito',sans-serif;color:var(--green-800);margin:4px 0 4px;}
 #cb7585-patient-index .cb7585-sub{font-size:13px;color:var(--text-muted);font-weight:700;margin-bottom:16px;line-height:1.4;}
 #cb7585-patient-index .cb7585-grid{display:grid;grid-template-columns:1fr;gap:10px;}
 #cb7585-patient-index .cb7585-item{background:var(--card-bg);border:0;border-radius:16px;box-shadow:var(--shadow);padding:15px 14px;display:flex;align-items:center;gap:12px;text-align:left;width:100%;font-family:inherit;color:var(--text);}
 #cb7585-patient-index .cb7585-ico{width:44px;height:44px;border-radius:14px;background:var(--green-50);display:flex;align-items:center;justify-content:center;font-size:22px;flex:0 0 auto;}
 #cb7585-patient-index .cb7585-copy{flex:1;min-width:0;}.cb7585-item b{display:block;font:900 15px 'Nunito',sans-serif;color:var(--green-800);}.cb7585-item small{display:block;font-size:12px;color:var(--text-muted);font-weight:700;margin-top:2px;line-height:1.3;}.cb7585-go{font-size:24px;color:var(--green-600);}
 #cb7585-back{display:none!important;position:sticky;top:8px;z-index:80;margin:8px 16px 12px;width:calc(100% - 32px);}
 body.cb7585-patient-detail #cb7585-back{display:flex!important;justify-content:center;}
 body.cb7585-patient-detail #screen-profile .header-sub{display:none!important;}
 body.cb7585-patient-detail #screen-profile .content>*{display:none!important;}
 body.cb7585-patient-detail #screen-profile .content>*.cb7585-show{display:block!important;}
}
@media(min-width:768px){#cb7585-patient-index,#cb7585-back{display:none!important;}}
</style>
<script id="cuidarbem-v75-85-patient-sections-js">
(function(){
 var groups=[
  {k:'dados',i:'👤',t:'Dados pessoais',s:'Identificação, nascimento, sangue e cuidador.',terms:['dados do paciente','nome do paciente','data de nascimento','tipo sanguíneo','cuidador principal']},
  {k:'emergencia',i:'🆘',t:'Emergência',s:'Contato, informações essenciais e ficha rápida.',terms:['contato de emergência','ficha de emergência','modo samu']},
  {k:'clinico',i:'🩺',t:'Perfil clínico',s:'Diagnósticos, condições, alergias e observações.',terms:['diagnóstico','diagnostico','outras condições','outras condicoes','alergias','observações essenciais','observacoes essenciais']},
  {k:'neuro',i:'🧠',t:'Perfil neurológico funcional',s:'Lado afetado, mobilidade e prioridades funcionais.',terms:['perfil neurológico','perfil neurologico','lado afetado','prioridade funcional']},
  {k:'atend',i:'🏥',t:'Atendimentos e internações',s:'Histórico de atendimentos, internações e cirurgias.',terms:['histórico de atendimentos','historico de atendimentos','internações e cirurgias','internacoes e cirurgias','cirurgias realizadas','histórico rápido de eventos','historico rapido de eventos']},
  {k:'sus',i:'💳',t:'Convênio, SUS e benefícios',s:'Cartão SUS, convênio, benefícios e Farmácia Popular.',terms:['convênio / sus','convenio / sus','cartão sus','cartao sus','benefícios, sus','beneficios, sus','farmácia popular','farmacia popular']},
  {k:'habitos',i:'🌿',t:'Hábitos de saúde',s:'Informações complementares da rotina de saúde.',terms:['hábitos de saúde','habitos de saude']},
  {k:'familia',i:'👨‍👩‍👧',t:'Compartilhamento familiar',s:'Pessoas autorizadas e acesso da família.',terms:['compartilhamento familiar']}
 ];
 function norm(x){return (x||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/\s+/g,' ').trim();}
 function profile(){return document.getElementById('screen-profile');}
 function topCards(){var sc=profile();if(!sc)return[];var c=sc.querySelector('.content');return c?Array.from(c.children):[];}
 function matches(el,terms){var tx=norm(el.textContent);return terms.some(function(t){return tx.indexOf(norm(t))>=0;});}
 function index(){
  var old=document.getElementById('cb7585-patient-index');if(old)return old;
  var d=document.createElement('div');d.id='cb7585-patient-index';d.innerHTML='<div class="cb7585-title">👤 Paciente</div><div class="cb7585-sub">Informações organizadas por assunto. Toque no que deseja consultar ou atualizar.</div><div class="cb7585-grid"></div>';
  var grid=d.querySelector('.cb7585-grid');groups.forEach(function(g){var b=document.createElement('button');b.className='cb7585-item';b.dataset.group=g.k;b.innerHTML='<span class="cb7585-ico">'+g.i+'</span><span class="cb7585-copy"><b>'+g.t+'</b><small>'+g.s+'</small></span><span class="cb7585-go">›</span>';grid.appendChild(b);});
  var sc=profile();if(sc)sc.parentNode.insertBefore(d,sc);return d;
 }
 function backButton(){var b=document.getElementById('cb7585-back');if(b)return b;var sc=profile();if(!sc)return null;b=document.createElement('button');b.id='cb7585-back';b.className='cb75-btn secondary';b.textContent='‹ Voltar para Paciente';var c=sc.querySelector('.content');if(c)c.parentNode.insertBefore(b,c);return b;}
 function clear(){topCards().forEach(function(x){x.classList.remove('cb7585-show');});}
 function openIndex(){clear();document.body.classList.remove('cb7585-patient-detail');document.body.classList.add('cb7585-patient-index-open');var d=index();if(d)d.scrollTop=0;}
 function openGroup(key){var g=groups.find(function(x){return x.k===key;});if(!g)return;clear();var cards=topCards(),hit=0;cards.forEach(function(x){if(matches(x,g.terms)){x.classList.add('cb7585-show');hit++;}});document.body.classList.remove('cb7585-patient-index-open');document.body.classList.add('cb7585-patient-detail');var sc=profile();if(sc){sc.classList.add('active');sc.scrollTop=0;}if(!hit){openIndex();}}
 function setup(){var sc=profile();if(!sc)return;var d=index(),back=backButton();if(d&&!d.dataset.wired){d.dataset.wired='1';d.addEventListener('click',function(e){var b=e.target.closest('[data-group]');if(b)openGroup(b.dataset.group);});}if(back&&!back.dataset.wired){back.dataset.wired='1';back.addEventListener('click',openIndex);}document.addEventListener('click',function(e){var b=e.target.closest('[data-go="perfil"],[data-section="perfil"]');if(b){setTimeout(openIndex,0);}},true);}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup);else setup();setTimeout(setup,300);setTimeout(setup,900);
})();
</script>
'''
 pos=s.rfind('</body>')
 if pos<0: raise SystemExit('body not found')
 s=s[:pos]+patch+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-85-patient-sections';",t,count=1);sw.write_text(t,encoding='utf-8')
