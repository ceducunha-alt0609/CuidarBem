from pathlib import Path
import re

index = Path('index.html')
s = index.read_text(encoding='utf-8')

# Remove o patch v75.34 que foi parar dentro de um template de impressão.
s = re.sub(
    r'\n\n<!-- v75\.34 — Mobile: remove clone desktop que bagunçava a Home -->.*?</script>\n',
    '\n', s, count=1, flags=re.S)

# Impede a criação do bloco desktop no mobile na origem do problema.
needle = 'function buildRightHomeBlock(header){'
replacement = "function buildRightHomeBlock(header){\n    if(window.innerWidth < 768) return;"
if needle in s and replacement not in s:
    s = s.replace(needle, replacement, 1)

# v75.37 — aposenta Mão única no mobile sem tocar nos demais comandos.
# O recurso antigo pode ter IDs/classes variáveis; removemos o botão pelo texto e limpamos
# barras flutuantes que ele cria quando o estado estava previamente ativado.
marker37 = 'cuidarbem-v75-37-remove-one-hand'
if marker37 not in s:
    patch37 = '''

<!-- v75.37 — Mobile: aposenta Mão única e sua barra duplicada -->
<style id="cuidarbem-v75-37-remove-one-hand">
@media (max-width:767px){
  .one-hand-bar,.onehand-bar,.one-hand-toolbar,.onehand-toolbar,
  .one-hand-controls,.onehand-controls,.one-hand-dock,.onehand-dock,
  #one-hand-bar,#onehand-bar,#one-hand-toolbar,#onehand-toolbar,
  #one-hand-controls,#onehand-controls,#one-hand-dock,#onehand-dock{
    display:none !important;
  }
}
</style>
<script id="cuidarbem-v75-37-remove-one-hand-js">
(function(){
  'use strict';
  function norm(v){return (v||'').replace(/\s+/g,' ').trim().toLowerCase();}
  function cleanOneHand(){
    if(window.innerWidth >= 768) return;
    document.querySelectorAll('button,a,[role="button"]').forEach(function(el){
      var txt = norm(el.textContent);
      if(txt === 'mão única' || txt === 'mao unica' || txt.indexOf('mão única') !== -1 || txt.indexOf('mao unica') !== -1){
        el.remove();
      }
    });
    document.querySelectorAll('.one-hand-bar,.onehand-bar,.one-hand-toolbar,.onehand-toolbar,.one-hand-controls,.onehand-controls,.one-hand-dock,.onehand-dock,#one-hand-bar,#onehand-bar,#one-hand-toolbar,#onehand-toolbar,#one-hand-controls,#onehand-controls,#one-hand-dock,#onehand-dock').forEach(function(el){el.remove();});
    document.body.classList.remove('one-hand','onehand','one-hand-mode','onehand-mode','cb-one-hand','cb-onehand');
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded',cleanOneHand,{once:true});
  else cleanOneHand();
  setTimeout(cleanOneHand,100);
  setTimeout(cleanOneHand,500);
  new MutationObserver(cleanOneHand).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch37+'\n'+s[pos:]

index.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';", "const CACHE_NAME = 'cuidarbem-v75-37-remove-one-hand';", t, count=1)
sw.write_text(t,encoding='utf-8')
