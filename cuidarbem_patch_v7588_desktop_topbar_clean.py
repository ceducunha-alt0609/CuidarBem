from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='cuidarbem-v75-88-desktop-topbar-clean'
if marker not in s:
    patch=r'''
<!-- v75.88 — Desktop topbar clean: busca central única + ações únicas à direita -->
<style id="cuidarbem-v75-88-desktop-topbar-clean">
@media (min-width:768px){
  #screen-home>.header{position:relative!important;padding-left:30px!important;padding-right:20px!important;overflow:visible!important}
  #screen-home .mobile-topbar-title-row{position:relative!important;z-index:4!important;flex:0 0 230px!important;width:230px!important;margin:0!important}

  /* usa somente a busca funcional criada na v75.86 */
  #screen-home .cb-desktop-search{display:none!important}
  #screen-home>.header>#cb7586-search{
    display:block!important;
    position:absolute!important;
    left:50%!important;
    right:auto!important;
    top:50%!important;
    transform:translate(-50%,-50%)!important;
    width:min(390px,34vw)!important;
    margin:0!important;
    z-index:35!important;
  }

  /* um único conjunto Maria + SAMU */
  #screen-home>.header>.cb7588-actions{
    position:absolute!important;
    right:18px!important;
    top:50%!important;
    transform:translateY(-50%)!important;
    display:flex!important;
    align-items:center!important;
    gap:9px!important;
    width:auto!important;
    margin:0!important;
    z-index:22!important;
  }
  #screen-home>.header>.cb7588-date{
    position:absolute!important;
    right:20px!important;
    top:14px!important;
    margin:0!important;
    padding:0!important;
    font-size:11.5px!important;
    line-height:1!important;
    white-space:nowrap!important;
    color:rgba(255,255,255,.9)!important;
    z-index:23!important;
  }
}
@media (min-width:768px) and (max-width:1180px){
  #screen-home>.header>#cb7586-search{width:min(330px,31vw)!important}
}
@media (max-width:767px){#screen-home>.header>#cb7586-search{display:none!important}}
</style>
<script id="cuidarbem-v75-88-desktop-topbar-clean-js">
(function(){
  function clean(){
    if(innerWidth<768)return;
    var h=document.querySelector('#screen-home>.header');
    if(!h)return;

    /* restaura somente a busca v75.86 */
    h.querySelectorAll('.cb-desktop-search').forEach(function(x){x.style.setProperty('display','none','important');});
    var search=h.querySelector('#cb7586-search');
    if(search) search.style.setProperty('display','block','important');

    /* mantém apenas um Maria e um SAMU; remove duplicados criados por camadas anteriores */
    var patients=Array.from(h.querySelectorAll('.header-patient'));
    var samus=Array.from(h.querySelectorAll('button[onclick="openSamuMode()"]'));
    patients.slice(1).forEach(function(x){x.remove();});
    samus.slice(1).forEach(function(x){x.remove();});

    var patient=patients[0];
    var samu=samus[0];
    var group=null;
    if(patient && samu && patient.parentElement===samu.parentElement) group=patient.parentElement;
    else if(patient) group=patient.parentElement;
    if(group){
      group.classList.remove('cb7587-actions');
      group.classList.add('cb7588-actions');
      group.style.removeProperty('display');
    }

    /* data única */
    var dates=Array.from(h.querySelectorAll('.header-date'));
    dates.forEach(function(d,i){
      d.classList.remove('cb7587-date');
      if(i===0){d.classList.add('cb7588-date');d.style.removeProperty('display');}
      else d.remove();
    });

    try{localStorage.setItem('cuidarbem_patch_version','v75.88-desktop-topbar-clean')}catch(e){}
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',clean,{once:true});else clean();
  setTimeout(clean,250);setTimeout(clean,900);setTimeout(clean,1800);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos<0: raise SystemExit('missing </body>')
    s=s[:pos]+patch+'\n'+s[pos:]
    p.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-88-desktop-topbar-clean';",t,count=1)
sw.write_text(t,encoding='utf-8')
