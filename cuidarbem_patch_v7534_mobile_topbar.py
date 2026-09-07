from pathlib import Path
import re
index=Path('index.html');s=index.read_text(encoding='utf-8');marker='cuidarbem-v75-66-medication-form'
if marker not in s:
 patch=r'''
<!-- v75.66 — cadastro manual de medicamento no próprio módulo -->
<style id="cuidarbem-v75-66-medication-form">
@media(max-width:767px){
 #cb7566-med-modal{position:fixed;inset:0;z-index:99999;background:rgba(12,45,38,.42);display:none;align-items:flex-end;}
 #cb7566-med-modal.open{display:flex;}
 #cb7566-med-sheet{background:#f8fffc;width:100%;max-height:92vh;overflow:auto;border-radius:26px 26px 0 0;padding:20px 20px calc(24px + env(safe-area-inset-bottom));box-shadow:0 -8px 30px rgba(0,0,0,.16);}
 .cb7566-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:16px}.cb7566-title{font:900 21px 'Nunito',sans-serif;color:var(--green-800)}
 .cb7566-close{border:0;background:transparent;font-size:27px;color:var(--text-muted)}
 .cb7566-grid{display:grid;grid-template-columns:1fr 1fr;gap:11px}.cb7566-field{display:flex;flex-direction:column;gap:5px}.cb7566-field.full{grid-column:1/-1}.cb7566-field label{font-size:12px;font-weight:800;color:var(--green-800);text-transform:uppercase;letter-spacing:.03em}
 .cb7566-field input,.cb7566-field select,.cb7566-field textarea{width:100%;box-sizing:border-box;border:1.5px solid var(--green-200);border-radius:14px;background:white;padding:13px 12px;font:inherit;color:var(--text);min-height:48px}.cb7566-field textarea{min-height:72px;resize:vertical}
 .cb7566-note{margin:13px 0;padding:10px 12px;border-radius:12px;background:var(--green-50);font-size:12px;line-height:1.4;color:var(--green-600);font-weight:700}.cb7566-actions{display:flex;gap:10px}.cb7566-actions button{flex:1;min-height:52px;border-radius:15px;font-weight:900;font-size:15px}.cb7566-cancel{background:white;border:1.5px solid var(--green-200);color:var(--green-800)}.cb7566-save{border:0;background:var(--green-600);color:white}
}
</style>
<script id="cuidarbem-v75-66-medication-form-js">
(function(){
 function setup(){var b=document.getElementById('cb7563-manual');if(!b||document.getElementById('cb7566-med-modal'))return;
  var m=document.createElement('div');m.id='cb7566-med-modal';m.innerHTML='<div id="cb7566-med-sheet"><div class="cb7566-head"><div class="cb7566-title">💊 Novo medicamento</div><button class="cb7566-close" type="button">×</button></div><form id="cb7566-med-form"><div class="cb7566-grid"><div class="cb7566-field full"><label>Medicamento *</label><input id="cb7566-name" required placeholder="Ex.: Losartana"></div><div class="cb7566-field"><label>Dose / concentração *</label><input id="cb7566-dose" required placeholder="Ex.: 50 mg"></div><div class="cb7566-field"><label>Via *</label><select id="cb7566-route" required><option value="Oral">Oral</option><option>Sublingual</option><option>Inalatória</option><option>Tópica</option><option>Ocular</option><option>Outra</option></select></div><div class="cb7566-field full"><label>Frequência / horários *</label><input id="cb7566-times" required placeholder="Ex.: 08:00 e 20:00"></div><div class="cb7566-field"><label>Início</label><input id="cb7566-start" type="date"></div><div class="cb7566-field"><label>Término</label><input id="cb7566-end" type="date"></div><div class="cb7566-field full"><label>Observação</label><textarea id="cb7566-obs" placeholder="Ex.: após alimentação"></textarea></div></div><div class="cb7566-note">🛡️ Registre conforme a prescrição/orientação profissional. Confira os dados antes de salvar.</div><div class="cb7566-actions"><button type="button" class="cb7566-cancel">Cancelar</button><button type="submit" class="cb7566-save">Salvar medicamento</button></div></form></div>';
  document.body.appendChild(m);function open(e){if(e){e.preventDefault();e.stopImmediatePropagation();}m.classList.add('open');setTimeout(function(){document.getElementById('cb7566-name').focus()},80)}function close(){m.classList.remove('open')}
  b.addEventListener('click',open,true);m.querySelector('.cb7566-close').onclick=close;m.querySelector('.cb7566-cancel').onclick=close;m.addEventListener('click',function(e){if(e.target===m)close()});
  m.querySelector('form').onsubmit=function(e){e.preventDefault();var rec={id:'med-'+Date.now(),name:document.getElementById('cb7566-name').value.trim(),dose:document.getElementById('cb7566-dose').value.trim(),route:document.getElementById('cb7566-route').value,times:document.getElementById('cb7566-times').value.trim(),start:document.getElementById('cb7566-start').value,end:document.getElementById('cb7566-end').value,obs:document.getElementById('cb7566-obs').value.trim(),createdAt:new Date().toISOString()};var a=[];try{a=JSON.parse(localStorage.getItem('cb75_medications')||'[]')}catch(x){}a.push(rec);localStorage.setItem('cb75_medications',JSON.stringify(a));close();this.reset();if(typeof showToast==='function')showToast('💊 Medicamento salvo.');else alert('Medicamento salvo.');};
 }
 document.addEventListener('DOMContentLoaded',setup);var n=0,x=setInterval(function(){setup();if(document.getElementById('cb7566-med-modal')||++n>50)clearInterval(x)},250);
})();
</script>
'''
 pos=s.rfind('</body>');s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8');sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-66-medication-form';",t,count=1);sw.write_text(t,encoding='utf-8')
