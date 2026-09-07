from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Remove a implementação v75.77 para substituí-la por uma única versão sem
# classes genéricas e com detecção tolerante aos emojis dos títulos originais.
s=re.sub(r'\s*<style id="cuidarbem-v75-77-consultas-exames-clean">.*?</style>\s*', '\n', s, flags=re.S)
s=re.sub(r'\s*<script id="cuidarbem-v75-77-consultas-exames-clean-js">.*?</script>\s*', '\n', s, flags=re.S)

marker='cuidarbem-v75-78-consultas-exames-final'
if marker not in s:
    patch=r'''
<!-- v75.78 — Consultas/Exames: cards finais e remoção robusta dos textos antigos -->
<style id="cuidarbem-v75-78-consultas-exames-final">
@media(max-width:767px){
  #cb7578-upcoming{display:block!important;margin-top:10px!important}
  #cb7578-upcoming .cb7578-card{display:flex!important;align-items:center!important;gap:12px!important;padding:17px 18px!important;margin:12px 0!important;cursor:pointer!important}
  #cb7578-upcoming .cb7578-ico{display:block!important;font-size:25px!important;flex:0 0 34px!important;text-align:center!important}
  #cb7578-upcoming .cb7578-copy{display:block!important;flex:1!important;min-width:0!important}
  #cb7578-upcoming .cb7578-title{display:block!important;font-family:'Nunito',sans-serif!important;font-size:17px!important;font-weight:900!important;color:var(--green-800)!important;line-height:1.2!important}
  #cb7578-upcoming .cb7578-sub{display:block!important;font-size:12px!important;color:var(--text-muted)!important;font-weight:700!important;margin-top:4px!important;line-height:1.35!important}
  #cb7578-upcoming .cb7578-go{display:block!important;font-size:25px!important;color:var(--green-600)!important}
  .cb7578-hide-legacy{display:none!important}
}
@media(min-width:768px){#cb7578-upcoming{display:none!important}}
</style>
<script id="cuidarbem-v75-78-consultas-exames-final-js">
(function(){
  function tx(e){return(e&&e.textContent||'').replace(/\s+/g,' ').trim()}
  function norm(v){return (v||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/^[^a-z0-9]+/i,'').trim()}
  function isLegacyText(v){
    var t=norm(v);
    return t==='proximas consultas'||t==='nenhuma consulta agendada.'||t==='nenhuma consulta agendada'||t==='proximos exames'||t==='nenhum exame agendado.'||t==='nenhum exame agendado';
  }
  function hideLegacy(root){
    var all=root.querySelectorAll('*');
    for(var i=0;i<all.length;i++){
      var e=all[i], t=tx(e);
      if(!t)continue;
      if(e.children.length===0 && isLegacyText(t)) e.classList.add('cb7578-hide-legacy');
    }
  }
  function setup(){
    if(innerWidth>767)return false;
    var root=null, all=document.querySelectorAll('*');
    for(var i=0;i<all.length;i++){
      if(all[i].children.length===0 && (norm(tx(all[i]))==='proximas consultas'||norm(tx(all[i]))==='proximos exames')){
        root=all[i].closest('.screen')||all[i].closest('[id^="screen-"]');
        if(root)break;
      }
    }
    if(!root){
      var cam=document.querySelector('.nav-item.active, .bottom-nav .active');
      root=(cam&&cam.closest('.screen'))||document.querySelector('[id^="screen-"] .content')?.closest('.screen')||document;
    }
    hideLegacy(root);

    if(document.getElementById('cb7578-upcoming'))return true;
    var note=document.getElementById('cb7577-ai-note');
    if(!note){
      var notes=root.querySelectorAll('*');
      for(var j=0;j<notes.length;j++){
        if(notes[j].children.length===0 && tx(notes[j]).indexOf('Pela foto, o CuidarBem identifica tipo')>=0){note=notes[j].closest('.card')||notes[j];break;}
      }
    }
    if(!note)return false;

    var wrap=document.createElement('div');wrap.id='cb7578-upcoming';
    wrap.innerHTML='<section id="cb7578-consultas" class="card cb7578-card"><div class="cb7578-ico">🩺</div><div class="cb7578-copy"><div class="cb7578-title">Próximas consultas</div><div class="cb7578-sub">Nenhuma consulta agendada</div></div><div class="cb7578-go">›</div></section><section id="cb7578-exames" class="card cb7578-card"><div class="cb7578-ico">🔬</div><div class="cb7578-copy"><div class="cb7578-title">Próximos exames</div><div class="cb7578-sub">Nenhum exame agendado</div></div><div class="cb7578-go">›</div></section>';
    note.parentNode.insertBefore(wrap,note.nextSibling);
    hideLegacy(root);
    return true;
  }
  document.addEventListener('DOMContentLoaded',setup);
  var tries=0,timer=setInterval(function(){setup();if(++tries>=80)clearInterval(timer)},250);
  document.addEventListener('DOMContentLoaded',function(){
    var mo=new MutationObserver(function(){
      var w=document.getElementById('cb7578-upcoming');
      var root=w&&(w.closest('.screen')||w.closest('[id^="screen-"]'));
      if(root)hideLegacy(root);
    });
    mo.observe(document.body,{childList:true,subtree:true});
  });
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos<0: raise SystemExit('body not found')
    s=s[:pos]+patch+'\n'+s[pos:]

p.write_text(s,encoding='utf-8')
sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-78-consultas-exames-final';",t,count=1)
sw.write_text(t,encoding='utf-8')
