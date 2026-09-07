from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Remove os quatro patches experimentais de Consultas/Exames que passaram a
# competir entre si no runtime (inclusive MutationObserver da v75.76).
for ver, slug in [
    ('75-73','consultas-compact'),
    ('75-74','consultas-card-fix'),
    ('75-75','consultas-mirror-exames'),
    ('75-76','consultas-exames-stable'),
]:
    s=re.sub(r'\n?<!-- v'+re.escape(ver.replace('-','.'))+r'.*?<style id="cuidarbem-v'+ver+'-'+re.escape(slug)+r'">.*?</style>\s*<script id="cuidarbem-v'+ver+'-'+re.escape(slug)+r'-js">.*?</script>\s*', '\n', s, flags=re.S)
    # fallback pelo id, caso o comentário varie
    s=re.sub(r'\s*<style id="cuidarbem-v'+ver+'-'+re.escape(slug)+r'">.*?</style>\s*', '\n', s, flags=re.S)
    s=re.sub(r'\s*<script id="cuidarbem-v'+ver+'-'+re.escape(slug)+r'-js">.*?</script>\s*', '\n', s, flags=re.S)

marker='cuidarbem-v75-77-consultas-exames-clean'
if marker not in s:
    patch=r'''
<!-- v75.77 — Consultas/Exames: uma única implementação estável -->
<style id="cuidarbem-v75-77-consultas-exames-clean">
@media(max-width:767px){
  #cb7577-ai-note{padding:14px 16px!important;margin:12px 0!important;background:rgba(255,255,255,.62)!important;border:1px solid var(--green-200)!important;border-radius:18px!important;color:var(--green-700)!important;font-size:13px!important;font-weight:750!important;line-height:1.45!important}
  #cb7577-upcoming{display:block!important;margin-top:10px!important}
  #cb7577-upcoming .cb7577-card{display:flex!important;align-items:center!important;gap:12px!important;padding:17px 18px!important;margin:12px 0!important;cursor:pointer!important}
  #cb7577-upcoming .ico{font-size:25px!important;flex:0 0 34px!important;text-align:center!important}
  #cb7577-upcoming .copy{flex:1!important;min-width:0!important}
  #cb7577-upcoming .title{font-family:'Nunito',sans-serif!important;font-size:17px!important;font-weight:900!important;color:var(--green-800)!important;line-height:1.2!important}
  #cb7577-upcoming .sub{font-size:12px!important;color:var(--text-muted)!important;font-weight:700!important;margin-top:4px!important;line-height:1.35!important}
  #cb7577-upcoming .go{font-size:25px!important;color:var(--green-600)!important}
  .cb7577-hide-legacy{display:none!important}
}
@media(min-width:768px){#cb7577-ai-note,#cb7577-upcoming{display:none!important}}
</style>
<script id="cuidarbem-v75-77-consultas-exames-clean-js">
(function(){
  function tx(e){return(e&&e.textContent||'').replace(/\s+/g,' ').trim()}
  function leaf(root,re){
    var a=root.querySelectorAll('*');
    for(var i=0;i<a.length;i++) if(a[i].children.length===0&&re.test(tx(a[i]))) return a[i];
    return null;
  }
  function hideLeaf(el,root){
    if(!el)return;
    var n=el;
    while(n.parentElement&&n.parentElement!==root&&n.parentElement.classList&&!n.parentElement.classList.contains('content')&&tx(n.parentElement)===tx(n)) n=n.parentElement;
    n.classList.add('cb7577-hide-legacy');
  }
  function setup(){
    if(innerWidth>767)return false;
    var aiTitle=leaf(document,/^O QUE A IA EXTRAI DO PEDIDO$/i);
    var consult=leaf(document,/^Próximas consultas$/i);
    var exam=leaf(document,/^Próximos exames$/i);
    var seed=aiTitle||consult||exam;
    if(!seed)return false;
    var root=seed.closest('.screen')||seed.closest('[id^="screen-"]');
    if(!root)return false;

    var aiCard=aiTitle&&(aiTitle.closest('.card')||aiTitle.parentElement);
    if(aiCard)aiCard.classList.add('cb7577-hide-legacy');

    var note=document.getElementById('cb7577-ai-note');
    if(!note){
      note=document.createElement('div');note.id='cb7577-ai-note';
      note.innerHTML='✨ Pela foto, o CuidarBem identifica tipo, local, data, horário e preparo. Confira os dados antes de adicionar à Agenda.';
      if(aiCard&&aiCard.parentNode)aiCard.parentNode.insertBefore(note,aiCard.nextSibling);
      else {var content=root.querySelector('.content')||root;content.appendChild(note)}
    }

    /* Oculta somente os quatro textos/embrulhos originais. Não exige que todos existam. */
    hideLeaf(leaf(root,/^Próximas consultas$/i),root);
    hideLeaf(leaf(root,/^Nenhuma consulta agendada\.?$/i),root);
    hideLeaf(leaf(root,/^Próximos exames$/i),root);
    hideLeaf(leaf(root,/^Nenhum exame agendado\.?$/i),root);

    var wrap=document.getElementById('cb7577-upcoming');
    if(!wrap){
      wrap=document.createElement('div');wrap.id='cb7577-upcoming';
      wrap.innerHTML='<section id="cb7577-consultas" class="card cb7577-card"><div class="ico">🩺</div><div class="copy"><div class="title">Próximas consultas</div><div class="sub">Nenhuma consulta agendada</div></div><div class="go">›</div></section><section id="cb7577-exames" class="card cb7577-card"><div class="ico">🔬</div><div class="copy"><div class="title">Próximos exames</div><div class="sub">Nenhum exame agendado</div></div><div class="go">›</div></section>';
      note.parentNode.insertBefore(wrap,note.nextSibling);
    }
    return true;
  }
  document.addEventListener('DOMContentLoaded',setup);
  var tries=0,timer=setInterval(function(){setup();if(++tries>=24)clearInterval(timer)},250);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos<0: raise SystemExit('body not found')
    s=s[:pos]+patch+'\n'+s[pos:]

p.write_text(s,encoding='utf-8')
sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-77-consultas-exames-clean';",t,count=1)
sw.write_text(t,encoding='utf-8')
