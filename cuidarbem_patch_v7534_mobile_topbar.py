from pathlib import Path
import re

index=Path('index.html'); s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-60-refresh-prepaint'
if marker not in s:
    # Faz o próprio pull-to-refresh salvar a guia ANTES do reload.
    old="""  async function refreshApp(){
    if(!indicator) return location.reload();
    indicator.classList.add('show','refreshing');
    indicator.classList.remove('ready');
    indicator.style.transform = 'translate(-50%,0) scale(1)';
    if(text) text.textContent = 'Atualizando…';
"""
    new="""  async function refreshApp(){
    try{
      var active=document.querySelector('.screen.active');
      var name=active&&active.id&&active.id.indexOf('screen-')===0?active.id.slice(7):'';
      if(name) localStorage.setItem('cuidarbem_last_screen_v759',name);
    }catch(e){}
    if(!indicator) return location.reload();
    indicator.classList.add('show','refreshing');
    indicator.classList.remove('ready');
    indicator.style.transform = 'translate(-50%,0) scale(1)';
    if(text) text.textContent = 'Atualizando…';
"""
    if old in s: s=s.replace(old,new,1)

    # Prepaint real: aplicado no início do <head>, antes de qualquer body poder aparecer.
    pre=r'''<style id="cuidarbem-v75-60-refresh-prepaint">
@media(max-width:767px){
 html.cb760-booting body{visibility:hidden!important;}
 html.cb760-booting *,html.cb760-booting *::before,html.cb760-booting *::after{animation:none!important;transition:none!important;}
}
</style>
<script id="cuidarbem-v75-60-refresh-prepaint-js">
(function(){
 try{
   var h=document.documentElement;h.classList.add('cb760-booting');
   var k='cuidarbem_last_screen_v759',v=localStorage.getItem(k)||'home';
   h.setAttribute('data-cb760-screen',v);
 }catch(e){}
})();
</script>
'''
    h=s.find('<head>')
    if h==-1: raise SystemExit('ERRO: <head> não encontrado')
    h=s.find('>',h)+1
    s=s[:h]+'\n'+pre+s[h:]

    tail=r'''<script id="cuidarbem-v75-60-refresh-finalize-js">
(function(){
 var KEY='cuidarbem_last_screen_v759';
 var valid=['home','calendar','dashboard','ocr','reports','appt','profile'];
 function activeName(){var x=document.querySelector('.screen.active');return x&&x.id&&x.id.indexOf('screen-')===0?x.id.slice(7):'';}
 function saveActive(){try{var n=activeName();if(valid.indexOf(n)>=0)localStorage.setItem(KEY,n);}catch(e){}}
 function restore(){
   var name='home';try{var v=localStorage.getItem(KEY);if(valid.indexOf(v)>=0)name=v;}catch(e){}
   var sc=document.getElementById('screen-'+name),nav=document.getElementById('nav-'+name);
   if(sc){document.querySelectorAll('.screen.active').forEach(function(x){x.classList.remove('active');});sc.classList.add('active');}
   if(nav){document.querySelectorAll('.nav-btn.active').forEach(function(x){x.classList.remove('active');});nav.classList.add('active');}
   saveActive();
   requestAnimationFrame(function(){requestAnimationFrame(function(){document.documentElement.classList.remove('cb760-booting');});});
 }
 document.addEventListener('click',function(e){var b=e.target&&e.target.closest?e.target.closest('.nav-btn'):null;if(b)setTimeout(saveActive,0);},true);
 if(window.MutationObserver){
   new MutationObserver(function(){saveActive();}).observe(document.documentElement,{subtree:true,attributes:true,attributeFilter:['class']});
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',restore,{once:true});else restore();
 setTimeout(function(){document.documentElement.classList.remove('cb760-booting');},2200);
})();
</script>
'''
    b=s.rfind('</body>')
    if b==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:b]+tail+'\n'+s[b:]

index.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-60-refresh-prepaint';",t,count=1);sw.write_text(t,encoding='utf-8')
