from pathlib import Path
import re
p=Path('index.html'); s=p.read_text(encoding='utf-8')
marker='cuidarbem-v75-81-more-patient-nav'
if marker not in s:
 patch=r'''
<!-- v75.81 — Mobile: barra enxuta + Mais + Paciente -->
<style id="cuidarbem-v75-81-more-patient-nav">
@media(max-width:767px){
 #cb7581-more-sheet{position:fixed;inset:0;z-index:10050;background:rgba(14,43,37,.34);display:none;align-items:flex-end;padding:14px}
 #cb7581-more-sheet.open{display:flex}
 #cb7581-more-panel{width:100%;background:#fff;border-radius:26px;padding:10px 14px 18px;box-shadow:0 -12px 38px rgba(0,0,0,.18)}
 .cb7581-handle{width:44px;height:5px;border-radius:9px;background:#d5dfdc;margin:3px auto 15px}
 .cb7581-title{font:900 20px 'Nunito',sans-serif;color:#174f43;margin:0 4px 12px}
 .cb7581-more-item{width:100%;border:1px solid #d7e4e0;background:#f9fcfb;border-radius:18px;padding:15px 16px;margin:8px 0;display:flex;align-items:center;gap:13px;text-align:left;color:#173f37;font:800 16px 'Nunito',sans-serif}
 .cb7581-more-item span:first-child{font-size:24px;width:32px;text-align:center}.cb7581-more-item b{margin-left:auto;font-size:24px;color:#187d69}
 #cb7581-patient-screen{position:fixed;inset:0;z-index:10020;background:var(--bg,#edf8f4);display:none;overflow:auto;padding-bottom:100px}
 #cb7581-patient-screen.open{display:block}
 .cb7581-patient-head{background:linear-gradient(135deg,#08745f,#00836d);color:#fff;border-radius:0 0 36px 36px;padding:34px 28px 25px;font:800 28px 'Nunito',sans-serif}
 .cb7581-patient-back{border:0;background:transparent;color:#fff;font-size:17px;font-weight:800;padding:0 0 14px}
 .cb7581-patient-body{padding:22px 26px}.cb7581-patient-card{background:#fff;border:1px solid #cfe0dc;border-radius:22px;padding:18px;margin-bottom:13px;box-shadow:0 5px 16px rgba(20,80,65,.06)}
 .cb7581-patient-card h3{margin:0 0 5px;color:#174f43;font:900 18px 'Nunito',sans-serif}.cb7581-patient-card p{margin:0;color:#61716d;font-size:13px;line-height:1.45}
 .cb7581-patient-open{width:100%;border:0;background:transparent;padding:0;text-align:left}
}
@media(min-width:768px){#cb7581-more-sheet,#cb7581-patient-screen{display:none!important}}
</style>
<script id="cuidarbem-v75-81-more-patient-nav">
(function(){
 function norm(x){return (x||'').replace(/\s+/g,' ').trim();}
 function clickByText(txt){var a=[].slice.call(document.querySelectorAll('button,a,[role="button"]'));var el=a.find(function(n){return norm(n.textContent).toLowerCase().indexOf(txt.toLowerCase())>=0});if(el){el.click();return true}return false}
 function setup(){
  if(document.getElementById('cb7581-more-sheet'))return;
  var sheet=document.createElement('div');sheet.id='cb7581-more-sheet';sheet.innerHTML='<div id="cb7581-more-panel"><div class="cb7581-handle"></div><div class="cb7581-title">Mais</div><button class="cb7581-more-item" data-go="consulta"><span>🩺</span><span>Consultas e exames</span><b>›</b></button><button class="cb7581-more-item" data-go="patient"><span>👩</span><span>Paciente</span><b>›</b></button><button class="cb7581-more-item" data-go="perfil"><span>⚙️</span><span>Configurações</span><b>›</b></button></div>';document.body.appendChild(sheet);
  var ps=document.createElement('section');ps.id='cb7581-patient-screen';ps.innerHTML='<div class="cb7581-patient-head"><button class="cb7581-patient-back">‹ Voltar</button><div>👩 Paciente</div></div><div class="cb7581-patient-body"><button class="cb7581-patient-open cb7581-patient-card" data-section="perfil"><h3>👤 Dados pessoais e clínicos</h3><p>Identificação, cuidador, diagnóstico, perfil neurológico e observações essenciais.</p></button><button class="cb7581-patient-open cb7581-patient-card" data-section="perfil"><h3>🆘 Emergência e saúde</h3><p>Contato de emergência, alergias, cirurgias, internações e histórico de eventos.</p></button><button class="cb7581-patient-open cb7581-patient-card" data-section="perfil"><h3>🏥 SUS, convênio e benefícios</h3><p>Cartão SUS, convênio, Farmácia Popular, benefícios e documentos.</p></button><button class="cb7581-patient-open cb7581-patient-card" data-section="perfil"><h3>📋 Histórico de atendimentos</h3><p>Consultas, exames e fisioterapia registrados.</p></button></div>';document.body.appendChild(ps);
  sheet.addEventListener('click',function(e){if(e.target===sheet){sheet.classList.remove('open');return}var b=e.target.closest('[data-go]');if(!b)return;sheet.classList.remove('open');var g=b.dataset.go;if(g==='patient'){ps.classList.add('open')}else if(g==='consulta'){clickByText('Consulta')}else{clickByText('Perfil')}});
  ps.querySelector('.cb7581-patient-back').onclick=function(){ps.classList.remove('open');sheet.classList.add('open')};
  ps.querySelectorAll('[data-section]').forEach(function(b){b.onclick=function(){ps.classList.remove('open');clickByText('Perfil')}});
  /* reaproveita a última posição da barra como Mais, sem espremer novos itens */
  var navs=[].slice.call(document.querySelectorAll('nav, .bottom-nav, .nav-bottom, .mobile-nav, footer'));
  var root=navs.find(function(n){return /Início/.test(n.textContent||'')&&/Agenda/.test(n.textContent||'')&&/Perfil/.test(n.textContent||'')});
  if(root){var items=[].slice.call(root.querySelectorAll('button,a,[role="button"]'));var prof=items.find(function(n){return /Perfil/.test(n.textContent||'')});if(prof){prof.dataset.cb7581Original='perfil';prof.innerHTML=prof.innerHTML.replace(/Perfil/g,'Mais');prof.addEventListener('click',function(e){e.preventDefault();e.stopImmediatePropagation();sheet.classList.add('open')},true)}}
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup);else setup();setTimeout(setup,500);
})();
</script>
'''
 pos=s.rfind('</body>');
 if pos<0: raise SystemExit('body not found')
 s=s[:pos]+patch+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-81-more-patient-nav';",t,count=1);sw.write_text(t,encoding='utf-8')
