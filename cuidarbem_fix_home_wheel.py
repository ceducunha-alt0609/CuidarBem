from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""    // Tela Início: grid com overflow:hidden — getScrollParent falha.
    // Roteia pelo painel sob o cursor (esquerda=content, direita=right-panel).
    var home = document.getElementById('screen-home');
    if (home && home.classList.contains('active')) {
      var rightPanel = home.querySelector('.desktop-right-panel');
      var panel = (rightPanel && e.clientX >= rightPanel.getBoundingClientRect().left)
        ? rightPanel : home.querySelector('.content');
      if (panel && panel.scrollHeight > panel.clientHeight) {
        e.preventDefault();
        panel.scrollBy({ top: e.deltaY * (e.deltaMode === 1 ? 20 : 1), behavior: 'auto' });
      }
      return; // sempre consome o evento na home
    }
"""
new="""    // Tela Início no desktop: o body é o scroll container atual.
    // Não interceptar a rodinha aqui; deixa o scroll nativo do navegador agir.
    var home = document.getElementById('screen-home');
    if (home && home.classList.contains('active')) {
      return;
    }
"""
if old not in s:
    raise SystemExit('home wheel routing block not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

p=Path('sw.js')
s=p.read_text(encoding='utf-8')
import re
s,n=re.subn(r"const CACHE_NAME = 'cuidarbem-v\d+-[^']+';", "const CACHE_NAME = 'cuidarbem-v59-desktop-wheel-fix';", s, count=1)
if n != 1:
    raise SystemExit('sw cache name not found')
p.write_text(s,encoding='utf-8')
