from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'cuidarbem-v75-86-desktop-topbar'
if marker not in s:
    patch = r'''
<!-- v75.86 — Desktop topbar: saudação à esquerda + busca global central + ações à direita -->
<style id="cuidarbem-v75-86-desktop-topbar">
@media (min-width:768px){
  #screen-home>.header{
    padding-left:22px!important;
    padding-right:18px!important;
    gap:0!important;
  }
  #screen-home .mobile-topbar-title-row{
    flex:0 0 230px!important;
    width:230px!important;
    margin:0!important;
    padding:0!important;
  }
  #screen-home .header-greeting{font-size:15px!important;line-height:1.15!important;margin:0!important}
  #screen-home .mobile-header-subtitle{font-size:11.5px!important;line-height:1.25!important;margin-top:7px!important;max-width:205px!important}

  /* esconde a busca antiga do shell; esta versão monta uma busca única e estável */
  #screen-home .cb-desktop-search{display:none!important}

  #cb7586-search{
    position:absolute!important;
    z-index:35!important;
    left:50%!important;
    top:50%!important;
    transform:translate(-50%,-50%)!important;
    width:min(470px,38vw)!important;
  }
  #cb7586-search .cb7586-box{
    height:44px;
    display:flex;
    align-items:center;
    border-radius:14px;
    background:rgba(255,255,255,.96);
    border:1px solid rgba(255,255,255,.72);
    box-shadow:0 6px 18px rgba(0,61,49,.14), inset 0 1px rgba(255,255,255,.8);
  }
  #cb7586-search .cb7586-box:focus-within{background:#fff;box-shadow:0 8px 24px rgba(0,61,49,.18),0 0 0 3px rgba(255,255,255,.10)}
  #cb7586-search .cb7586-icon{width:42px;flex:0 0 42px;display:flex;align-items:center;justify-content:center;color:#58716a;font-size:16px}
  #cb7586-search input{flex:1;min-width:0;height:100%;border:0;outline:0;background:transparent;color:#17352d;font:700 13px 'Nunito Sans',sans-serif;padding:0 6px 0 0}
  #cb7586-search input::placeholder{color:#7e918a;opacity:1;font-weight:600}
  #cb7586-search .cb7586-clear{width:36px;height:36px;margin-right:4px;border:0;background:transparent;color:#6b7d77;border-radius:10px;cursor:pointer;font-size:18px;display:none}
  #cb7586-search .cb7586-clear.show{display:block}
  #cb7586-search .cb7586-results{position:absolute;display:none;top:51px;left:0;right:0;max-height:360px;overflow:auto;padding:7px;border-radius:15px;background:rgba(255,255,255,.99);border:1px solid rgba(12,108,88,.12);box-shadow:0 20px 48px rgba(0,55,45,.20)}
  #cb7586-search .cb7586-results.open{display:block}
  #cb7586-search .cb7586-item{width:100%;border:0;background:transparent;padding:10px 11px;border-radius:11px;display:flex;gap:10px;align-items:flex-start;text-align:left;cursor:pointer;color:#17352d;font-family:inherit}
  #cb7586-search .cb7586-item:hover{background:#edf8f3}
  #cb7586-search .cb7586-item-ico{width:30px;height:30px;flex:0 0 30px;border-radius:9px;display:flex;align-items:center;justify-content:center;background:#e7f4ef;font-size:15px}
  #cb7586-search .cb7586-item b{display:block;font-size:13px;line-height:1.25}.cb7586-item small{display:block;font-size:11px;color:#6c7e77;margin-top:2px;line-height:1.3}
  #cb7586-search .cb7586-empty{padding:14px 12px;color:#6d7e78;font-size:12.5px;text-align:center}

  /* direita: data + paciente + SAMU realmente ancorados no canto */
  #screen-home>.header>.header-date{
    position:absolute!important;
    right:222px!important;
    top:21px!important;
    margin:0!important;
    padding:0!important;
    font-size:11.5px!important;
    white-space:nowrap!important;
    z-index:4!important;
  }
  #screen-home>.header>div[style*="justify-content:space-between"]{
    position:absolute!important;
    right:18px!important;
    top:50%!important;
    transform:translateY(-50%)!important;
    margin:0!important;
    display:flex!important;
    align-items:center!important;
    gap:8px!important;
    width:auto!important;
    z-index:5!important;
  }
  #screen-home .header-patient{margin:0!important}
  #screen-home .header button[onclick="openSamuMode()"]{margin:0!important}
}
@media (min-width:768px) and (max-width:1120px){
  #cb7586-search{width:min(340px,34vw)!important}
  #screen-home>.header>.header-date{display:none!important}
}
@media (max-width:767px){#cb7586-search{display:none!important}}
</style>
<script id="cuidarbem-v75-86-desktop-topbar-js">
(function(){'use strict';
  const META=[
    {id:'home',label:'Início',icon:'⌂',sub:'Resumo e tarefas de hoje'},
    {id:'calendar',label:'Agenda',icon:'📅',sub:'Rotinas, remédios e compromissos'},
    {id:'dashboard',label:'Saúde',icon:'♡',sub:'Acompanhamento e evolução'},
    {id:'ocr',label:'Receita',icon:'📷',sub:'Receitas e leitura por câmera'},
    {id:'reports',label:'Relatório',icon:'▥',sub:'Histórico e indicadores'},
    {id:'appt',label:'Consulta',icon:'🗓',sub:'Consultas e exames'},
    {id:'profile',label:'Paciente',icon:'♙',sub:'Dados, perfil clínico e informações do paciente'}
  ];
  const norm=v=>String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const esc=v=>String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  function go(id){try{if(typeof window.goScreen==='function')window.goScreen(id);else{document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));document.getElementById('screen-'+id)?.classList.add('active')}}catch(e){}}
  function taskResults(q){const out=[];try{const list=Array.isArray(window.tasks)?window.tasks:(typeof tasks!=='undefined'&&Array.isArray(tasks)?tasks:[]);list.forEach(t=>{const hay=norm([t.name,t.medName,t.doctor,t.examDoctor,t.local,t.type,t.obs,t.dose,t.date,t.time].filter(Boolean).join(' '));if(hay.includes(q))out.push({icon:t.type==='med'?'💊':t.type==='cons'?'🩺':t.type==='exam'?'🔬':t.type==='fisio'?'🦾':'✓',title:t.name||t.medName||'Registro',sub:[t.date,t.time,t.dose,t.doctor||t.examDoctor,t.local].filter(Boolean).join(' · '),screen:'calendar'})})}catch(e){}return out.slice(0,6)}
  function mount(){
    if(innerWidth<768)return;
    const header=document.querySelector('#screen-home>.header');
    if(!header||document.getElementById('cb7586-search'))return;
    const dates=header.querySelectorAll('.header-date');
    dates.forEach((d,i)=>{if(i>0)d.style.display='none'});
    const root=document.createElement('div');root.id='cb7586-search';
    root.innerHTML='<div class="cb7586-box"><span class="cb7586-icon">⌕</span><input type="search" autocomplete="off" aria-label="Busca global" placeholder="Buscar no CuidarBem..."><button class="cb7586-clear" type="button" aria-label="Limpar">×</button></div><div class="cb7586-results"></div>';
    header.appendChild(root);
    const input=root.querySelector('input'), clear=root.querySelector('.cb7586-clear'), panel=root.querySelector('.cb7586-results');
    function render(){const raw=input.value.trim();clear.classList.toggle('show',!!raw);if(!raw){panel.classList.remove('open');panel.innerHTML='';return}const q=norm(raw);const screens=META.filter(x=>norm(x.label+' '+x.sub).includes(q)).map(x=>({icon:x.icon,title:x.label,sub:x.sub,screen:x.id}));const results=[...screens,...taskResults(q)].slice(0,9);panel.classList.add('open');if(!results.length){panel.innerHTML='<div class="cb7586-empty">Nenhum resultado encontrado.</div>';return}panel.innerHTML=results.map((r,i)=>'<button class="cb7586-item" type="button" data-i="'+i+'"><span class="cb7586-item-ico">'+esc(r.icon)+'</span><span><b>'+esc(r.title)+'</b><small>'+esc(r.sub||'')+'</small></span></button>').join('');panel.querySelectorAll('.cb7586-item').forEach((b,i)=>b.addEventListener('click',()=>{go(results[i].screen);panel.classList.remove('open');input.blur()}));}
    input.addEventListener('input',render);input.addEventListener('focus',()=>{if(input.value.trim())render()});clear.addEventListener('click',()=>{input.value='';render();input.focus()});document.addEventListener('pointerdown',e=>{if(!root.contains(e.target))panel.classList.remove('open')});
    try{localStorage.setItem('cuidarbem_patch_version','v75.86-desktop-topbar')}catch(e){}
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});else mount();
  setTimeout(mount,350);setTimeout(mount,1000);
})();
</script>
'''
    pos = s.rfind('</body>')
    if pos < 0:
        raise SystemExit('body not found')
    s = s[:pos] + patch + '\n' + s[pos:]
    p.write_text(s, encoding='utf-8')

sw = Path('sw.js')
t = sw.read_text(encoding='utf-8')
t = re.sub(r"const CACHE_NAME = '[^']+';", "const CACHE_NAME = 'cuidarbem-v75-86-desktop-topbar';", t, count=1)
sw.write_text(t, encoding='utf-8')
