from pathlib import Path
import re

index=Path('index.html'); s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-59-refresh-stability'
if marker not in s:
    # Remove a rotina antiga e redundante de navegação que tenta ler data-screen,
    # embora a navegação real use onclick=goScreen(...). Ela podia disputar o estado visual.
    blocks=re.findall(r'<script(?:\s[^>]*)?>[\s\S]*?</script>',s,flags=re.I)
    for b in blocks:
        if "document.querySelectorAll('.nav-btn').forEach(btn=>" in b and "getAttribute('data-screen')" in b:
            s=s.replace(b,'',1)
            break

    head_patch=r'''
<!-- v75.59 — boot estável: sem flash da Home durante atualização -->
<style id="cuidarbem-v75-59-refresh-stability">
@media(max-width:767px){
  html.cb759-booting .screen{visibility:hidden!important;}
  html.cb759-booting .bottom-nav{visibility:hidden!important;}
  html.cb759-booting *,html.cb759-booting *::before,html.cb759-booting *::after{
    animation:none!important;transition:none!important;
  }
}
</style>
<script id="cuidarbem-v75-59-boot-head">
(function(){
  try{document.documentElement.classList.add('cb759-booting');}catch(e){}
})();
</script>
'''
    hpos=s.rfind('</head>')
    if hpos==-1: raise SystemExit('ERRO: </head> real não encontrado')
    s=s[:hpos]+head_patch+'\n'+s[hpos:]

    tail_patch=r'''
<script id="cuidarbem-v75-59-refresh-stability-js">
(function(){
  var KEY='cuidarbem_last_screen_v759';
  var valid=['home','calendar','dashboard','ocr','reports','appt','profile'];
  function save(name){try{if(valid.indexOf(name)>=0)localStorage.setItem(KEY,name);}catch(e){}}
  function restore(){
    var name='home';
    try{var saved=localStorage.getItem(KEY);if(valid.indexOf(saved)>=0)name=saved;}catch(e){}
    var screen=document.getElementById('screen-'+name);
    var nav=document.getElementById('nav-'+name);
    if(screen){
      document.querySelectorAll('.screen.active').forEach(function(el){el.classList.remove('active');});
      screen.classList.add('active');
    }
    if(nav){
      document.querySelectorAll('.nav-btn.active').forEach(function(el){el.classList.remove('active');});
      nav.classList.add('active');
    }
    requestAnimationFrame(function(){
      requestAnimationFrame(function(){document.documentElement.classList.remove('cb759-booting');});
    });
  }

  /* A navegação oficial continua sendo goScreen; apenas registramos a última guia. */
  var oldGo=window.goScreen;
  if(typeof oldGo==='function'){
    window.goScreen=function(name,btn){save(name);return oldGo.apply(this,arguments);};
  }

  document.addEventListener('click',function(e){
    var btn=e.target&&e.target.closest?e.target.closest('.nav-btn'):null;
    if(!btn)return;
    var id=btn.id||'';
    if(id.indexOf('nav-')===0)save(id.slice(4));
  },true);

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',restore,{once:true});else restore();
  /* Failsafe: nunca deixar a interface escondida se algum módulo antigo falhar. */
  setTimeout(function(){document.documentElement.classList.remove('cb759-booting');},1800);
})();
</script>
'''
    bpos=s.rfind('</body>')
    if bpos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:bpos]+tail_patch+'\n'+s[bpos:]

index.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-59-refresh-stability';",t,count=1);sw.write_text(t,encoding='utf-8')
