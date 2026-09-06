from pathlib import Path
import re

index = Path('index.html')
s = index.read_text(encoding='utf-8')

# Remove o patch v75.34 que foi parar dentro de um template de impressão.
s = re.sub(
    r'\n\n<!-- v75\.34 — Mobile: remove clone desktop que bagunçava a Home -->.*?</script>\n',
    '\n',
    s,
    count=1,
    flags=re.S,
)

# Impede a criação do bloco desktop no mobile na origem do problema.
needle = 'function buildRightHomeBlock(header){'
replacement = "function buildRightHomeBlock(header){\n    if(window.innerWidth < 768) return;"
if needle in s and replacement not in s:
    s = s.replace(needle, replacement, 1)

marker = 'cuidarbem-v75-35-mobile-topbar-root-fix'
if marker not in s:
    patch = '''

<!-- v75.35 — Mobile Home: restaura a ordem original e bloqueia clone desktop -->
<style id="cuidarbem-v75-35-mobile-topbar-root-fix">
@media (max-width:767px){
  #screen-home > .header{
    display:block !important;
    height:auto !important;
    min-height:238px !important;
    padding:calc(env(safe-area-inset-top) + 16px) 18px 16px !important;
    overflow:hidden !important;
  }
  #screen-home .cb-home-topbar-right{display:none !important;}
  #screen-home > .header > .header-date,
  #screen-home > .header > #today-date{
    display:inline-flex !important;
    position:relative !important;
    inset:auto !important;
    transform:none !important;
    margin:12px 0 0 !important;
    padding:6px 10px !important;
  }
  #screen-home > .header > div[style*="justify-content:space-between"]{
    display:flex !important;
    align-items:center !important;
    justify-content:space-between !important;
    position:relative !important;
    inset:auto !important;
    transform:none !important;
    margin-top:10px !important;
    margin-bottom:0 !important;
  }
  #screen-home .mobile-header-actions{
    display:grid !important;
    grid-template-columns:1fr 1fr 1fr !important;
    margin-top:12px !important;
  }
  #screen-home .content{padding-top:258px !important;}
}
</style>
<script id="cuidarbem-v75-35-mobile-topbar-root-fix-js">
(function(){
  'use strict';
  function cleanMobileHome(){
    if(window.innerWidth >= 768) return;
    const header = document.querySelector('#screen-home > .header');
    if(!header) return;
    header.querySelectorAll('.cb-home-topbar-right').forEach(el => el.remove());
  }
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', cleanMobileHome, {once:true});
  }else{
    cleanMobileHome();
  }
  setTimeout(cleanMobileHome, 100);
  setTimeout(cleanMobileHome, 500);
  window.addEventListener('resize', cleanMobileHome, {passive:true});
  window.addEventListener('orientationchange', function(){setTimeout(cleanMobileHome,120);});
})();
</script>
'''
    pos = s.rfind('</body>')
    if pos == -1:
        raise SystemExit('ERRO: </body> real não encontrado')
    s = s[:pos] + patch + '\n' + s[pos:]

index.write_text(s, encoding='utf-8')

sw = Path('sw.js')
t = sw.read_text(encoding='utf-8')
t = re.sub(r"const CACHE_NAME = '[^']+';", "const CACHE_NAME = 'cuidarbem-v75-35-mobile-topbar-root-fix';", t, count=1)
sw.write_text(t, encoding='utf-8')
