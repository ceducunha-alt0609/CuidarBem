from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='cuidarbem-v75-87-desktop-topbar-balance'
if marker not in s:
    patch=r'''
<!-- v75.87 — Desktop topbar: busca realmente central + ações à direita + data única -->
<style id="cuidarbem-v75-87-desktop-topbar-balance">
@media (min-width:768px){
  #screen-home>.header{position:relative!important;padding-left:30px!important;padding-right:22px!important;overflow:visible!important}
  #screen-home .mobile-topbar-title-row{position:relative!important;z-index:4!important;flex:0 0 230px!important;width:230px!important;margin:0!important}

  /* usa a busca original do shell, que já é funcional, e a traz para o centro real */
  #screen-home>.header>.cb-desktop-search{
    display:block!important;
    position:absolute!important;
    left:50%!important;
    right:auto!important;
    top:50%!important;
    transform:translate(-50%,-50%)!important;
    width:min(390px,36vw)!important;
    margin:0!important;
    z-index:30!important;
  }
  #screen-home>.header>#cb7586-search{display:none!important}

  /* grupo Maria + SAMU no lado direito */
  #screen-home>.header>.cb7587-actions{
    position:absolute!important;
    right:20px!important;
    top:50%!important;
    transform:translateY(-50%)!important;
    display:flex!important;
    align-items:center!important;
    gap:9px!important;
    width:auto!important;
    margin:0!important;
    z-index:20!important;
  }

  /* data única e discreta */
  #screen-home>.header>.cb7587-date{
    position:absolute!important;
    right:20px!important;
    top:15px!important;
    margin:0!important;
    padding:0!important;
    font-size:11.5px!important;
    line-height:1!important;
    white-space:nowrap!important;
    color:rgba(255,255,255,.88)!important;
    z-index:21!important;
  }

  #screen-home .header-patient{margin:0!important}
  #screen-home .header button[onclick="openSamuMode()"]{margin:0!important}
}
@media (min-width:768px) and (max-width:1180px){
  #screen-home>.header>.cb-desktop-search{width:min(330px,31vw)!important}
}
@media (max-width:767px){
  #screen-home>.header>.cb7587-actions,#screen-home>.header>.cb7587-date{display:none!important}
}
</style>
<script id="cuidarbem-v75-87-desktop-topbar-balance-js">
(function(){
  function apply(){
    if(innerWidth<768)return;
    var h=document.querySelector('#screen-home>.header');
    if(!h)return;

    /* limpa duplicidades de data */
    var dates=Array.from(h.querySelectorAll('.header-date'));
    dates.forEach(function(d){d.style.setProperty('display','none','important');});
    var mainDate=dates[0];
    if(mainDate){mainDate.classList.add('cb7587-date');mainDate.style.removeProperty('display');}

    /* encontra o bloco que contém Maria e SAMU sem depender do style inline */
    var patient=h.querySelector('.header-patient');
    var samu=h.querySelector('button[onclick="openSamuMode()"]');
    var group=null;
    if(patient&&patient.parentElement&&patient.parentElement===samu?.parentElement) group=patient.parentElement;
    else if(patient) group=patient.parentElement;
    if(group){group.classList.add('cb7587-actions');}

    /* garante uma única busca visível no desktop */
    var oldSearch=Array.from(h.children).find(function(x){return x.classList&&x.classList.contains('cb-desktop-search');});
    if(oldSearch) oldSearch.style.removeProperty('display');
    var newer=h.querySelector('#cb7586-search');
    if(newer) newer.style.setProperty('display','none','important');

    try{localStorage.setItem('cuidarbem_patch_version','v75.87-desktop-topbar-balance')}catch(e){}
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',apply,{once:true});else apply();
  setTimeout(apply,250);setTimeout(apply,900);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos<0: raise SystemExit('missing </body>')
    s=s[:pos]+patch+'\n'+s[pos:]
    p.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-87-desktop-topbar-balance';",t,count=1)
sw.write_text(t,encoding='utf-8')
