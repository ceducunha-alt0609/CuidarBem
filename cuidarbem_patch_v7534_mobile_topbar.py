from pathlib import Path
import re

index=Path('index.html'); s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-61-refresh-race-fix'
if marker not in s:
    # Remove as tentativas v75.59/v75.60 que podiam gravar HOME antes da restauração.
    ids=[
      'cuidarbem-v75-59-refresh-stability','cuidarbem-v75-59-boot-head','cuidarbem-v75-59-refresh-stability-js',
      'cuidarbem-v75-60-refresh-prepaint','cuidarbem-v75-60-refresh-prepaint-js','cuidarbem-v75-60-refresh-finalize-js'
    ]
    for i in ids:
      s=re.sub(r'<style[^>]*id=["\']'+re.escape(i)+r'["\'][^>]*>[\s\S]*?</style>\s*','',s,count=1,flags=re.I)
      s=re.sub(r'<script[^>]*id=["\']'+re.escape(i)+r'["\'][^>]*>[\s\S]*?</script>\s*','',s,count=1,flags=re.I)

    pre=r'''<style id="cuidarbem-v75-61-refresh-race-fix">
@media(max-width:767px){
 html.cb761-booting body{visibility:hidden!important;}
 html.cb761-booting *,html.cb761-booting *::before,html.cb761-booting *::after{animation:none!important;transition:none!important;}
}
</style>
<script id="cuidarbem-v75-61-refresh-race-fix-head">
(function(){try{document.documentElement.classList.add('cb761-booting');}catch(e){}})();
</script>
'''
    hp=s.find('<head>')
    if hp==-1: raise SystemExit('ERRO: <head> não encontrado')
    hp=s.find('>',hp)+1
    s=s[:hp]+'\n'+pre+s[hp:]

    tail=r'''<script id="cuidarbem-v75-61-refresh-race-fix-js">
(function(){
  var KEY='cuidarbem_last_screen';
  var valid=['home','calendar','dashboard','ocr','reports','appt','profile'];
  var restoring=true;
  function getActive(){var x=document.querySelector('.screen.active');return x&&x.id&&x.id.indexOf('screen-')===0?x.id.slice(7):'';}
  function save(name){try{if(!restoring&&valid.indexOf(name)>=0)localStorage.setItem(KEY,name);}catch(e){}}
  function apply(name){
    if(valid.indexOf(name)<0)name='home';
    var sc=document.getElementById('screen-'+name),nav=document.getElementById('nav-'+name);
    if(!sc)return false;
    document.querySelectorAll('.screen.active').forEach(function(x){x.classList.remove('active');});
    sc.classList.add('active');
    document.querySelectorAll('.nav-btn.active').forEach(function(x){x.classList.remove('active');});
    if(nav)nav.classList.add('active');
    return true;
  }
  function boot(){
    var name='home';
    try{var v=localStorage.getItem(KEY);if(valid.indexOf(v)>=0)name=v;}catch(e){}
    apply(name);
    /* Só depois da tela correta estar aplicada liberamos qualquer gravação. */
    requestAnimationFrame(function(){requestAnimationFrame(function(){
      restoring=false;
      document.documentElement.classList.remove('cb761-booting');
    });});

    /* Navegação oficial: grava somente após clique real do usuário. */
    document.addEventListener('click',function(e){
      var b=e.target&&e.target.closest?e.target.closest('.nav-btn'):null;
      if(!b)return;
      var id=b.id||''; if(id.indexOf('nav-')===0)save(id.slice(4));
    },true);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
  setTimeout(function(){restoring=false;document.documentElement.classList.remove('cb761-booting');},2200);
})();
</script>
'''
    bp=s.rfind('</body>')
    if bp==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:bp]+tail+'\n'+s[bp:]

    # Pull-to-refresh: salva explicitamente a guia ativa na chave definitiva antes do reload.
    s=s.replace("localStorage.setItem('cuidarbem_last_screen_v759',name);","localStorage.setItem('cuidarbem_last_screen',name);",1)

index.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-61-refresh-race-fix';",t,count=1);sw.write_text(t,encoding='utf-8')
