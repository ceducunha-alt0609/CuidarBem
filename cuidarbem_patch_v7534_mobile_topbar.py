from pathlib import Path
import re
index=Path('index.html');s=index.read_text(encoding='utf-8');marker='cuidarbem-v75-67-medication-schedule'
if marker not in s:
 patch=r'''
<!-- v75.67 — frequência estruturada, horários e uso contínuo -->
<style id="cuidarbem-v75-67-medication-schedule">
@media(max-width:767px){
 .cb7567-times{display:grid;grid-template-columns:repeat(2,1fr);gap:9px}.cb7567-times input{min-width:0}.cb7567-hidden{display:none!important}
 .cb7567-continuous{grid-column:1/-1;display:flex;align-items:center;gap:9px;padding:3px 2px;font-size:14px;font-weight:800;color:var(--green-800)}.cb7567-continuous input{width:20px!important;height:20px!important;min-height:0!important}
}
</style>
<script id="cuidarbem-v75-67-medication-schedule-js">
(function(){
 function setup(){var form=document.getElementById('cb7566-med-form'),old=document.getElementById('cb7566-times');if(!form||!old||document.getElementById('cb7567-frequency'))return;
  var field=old.closest('.cb7566-field');field.innerHTML='<label>Frequência *</label><select id="cb7567-frequency" required><option value="">Selecionar</option><option value="1x/dia">1x ao dia</option><option value="2x/dia">2x ao dia</option><option value="3x/dia">3x ao dia</option><option value="4x/dia">4x ao dia</option><option value="6/6h">A cada 6 horas</option><option value="8/8h">A cada 8 horas</option><option value="12/12h">A cada 12 horas</option><option value="se necessário">Se necessário</option><option value="outro">Outro / conforme prescrição</option></select><div id="cb7567-times-wrap" class="cb7567-times cb7567-hidden"></div>';
  var freq=document.getElementById('cb7567-frequency'),wrap=document.getElementById('cb7567-times-wrap');
  function count(){var v=freq.value;if(v==='1x/dia')return 1;if(v==='2x/dia'||v==='12/12h')return 2;if(v==='3x/dia'||v==='8/8h')return 3;if(v==='4x/dia'||v==='6/6h')return 4;return 0}
  function draw(){var n=count();wrap.innerHTML='';wrap.classList.toggle('cb7567-hidden',!n);for(var i=0;i<n;i++){var x=document.createElement('input');x.type='time';x.required=true;x.className='cb7567-time';x.setAttribute('aria-label','Horário '+(i+1));wrap.appendChild(x)}}freq.addEventListener('change',draw);
  var end=document.getElementById('cb7566-end'),endField=end.closest('.cb7566-field');var cont=document.createElement('label');cont.className='cb7567-continuous';cont.innerHTML='<input type="checkbox" id="cb7567-continuous"> Uso contínuo';endField.insertAdjacentElement('afterend',cont);var chk=document.getElementById('cb7567-continuous');chk.addEventListener('change',function(){end.disabled=this.checked;if(this.checked)end.value='';endField.style.opacity=this.checked?'.45':'1'});
  form.onsubmit=function(e){e.preventDefault();var times=[].map.call(document.querySelectorAll('.cb7567-time'),function(x){return x.value}).filter(Boolean);var rec={id:'med-'+Date.now(),name:document.getElementById('cb7566-name').value.trim(),dose:document.getElementById('cb7566-dose').value.trim(),route:document.getElementById('cb7566-route').value,frequency:freq.value,times:times,start:document.getElementById('cb7566-start').value,end:chk.checked?'':end.value,continuous:chk.checked,obs:document.getElementById('cb7566-obs').value.trim(),createdAt:new Date().toISOString()};var a=[];try{a=JSON.parse(localStorage.getItem('cb75_medications')||'[]')}catch(x){}a.push(rec);localStorage.setItem('cb75_medications',JSON.stringify(a));document.getElementById('cb7566-med-modal').classList.remove('open');this.reset();end.disabled=false;endField.style.opacity='1';wrap.innerHTML='';wrap.classList.add('cb7567-hidden');if(typeof showToast==='function')showToast('💊 Medicamento salvo.');else alert('Medicamento salvo.');};
 }
 document.addEventListener('DOMContentLoaded',setup);var n=0,x=setInterval(function(){setup();if(document.getElementById('cb7567-frequency')||++n>50)clearInterval(x)},250);
})();
</script>
'''
 pos=s.rfind('</body>');s=s[:pos]+patch+'\n'+s[pos:]
index.write_text(s,encoding='utf-8');sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-67-medication-schedule';",t,count=1);sw.write_text(t,encoding='utf-8')
