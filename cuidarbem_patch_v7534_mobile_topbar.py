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

# v75.36 — pull-to-refresh próprio do app para o mobile.
refresh_marker = 'cuidarbem-v75-36-pull-refresh'
if refresh_marker not in s:
    refresh_patch = '''

<!-- v75.36 — Mobile: puxar para atualizar dentro do scroll interno do app -->
<style id="cuidarbem-v75-36-pull-refresh">
@media (max-width:767px){
  #cb-pull-refresh{
    position:fixed;
    left:50%;
    top:calc(env(safe-area-inset-top) + 10px);
    transform:translate(-50%,-70px) scale(.92);
    z-index:10050;
    display:flex;
    align-items:center;
    gap:8px;
    padding:8px 13px;
    border-radius:999px;
    background:rgba(255,255,255,.96);
    color:#0d6655;
    border:1px solid rgba(13,102,85,.18);
    box-shadow:0 8px 24px rgba(0,55,45,.20);
    font-family:'Nunito',sans-serif;
    font-size:12px;
    font-weight:900;
    opacity:0;
    pointer-events:none;
    transition:transform .16s ease,opacity .16s ease;
  }
  #cb-pull-refresh.show{opacity:1;}
  #cb-pull-refresh.ready{color:#08725e;}
  #cb-pull-refresh.refreshing .cb-pr-icon{animation:cb-pr-spin .7s linear infinite;}
  @keyframes cb-pr-spin{to{transform:rotate(360deg)}}
}
</style>
<div id="cb-pull-refresh" aria-hidden="true"><span class="cb-pr-icon">↻</span><span class="cb-pr-text">Puxe para atualizar</span></div>
<script id="cuidarbem-v75-36-pull-refresh-js">
(function(){
  'use strict';
  if(!('ontouchstart' in window)) return;

  const THRESHOLD = 82;
  let startY = 0;
  let startX = 0;
  let pulling = false;
  let distance = 0;
  let activeScroller = null;
  const indicator = document.getElementById('cb-pull-refresh');
  const text = indicator && indicator.querySelector('.cb-pr-text');

  function currentScroller(){
    return document.querySelector('.screen.active');
  }
  function atTop(scroller){
    return !!scroller && (scroller.scrollTop || 0) <= 1;
  }
  function blockedTarget(target){
    return !!target.closest('input,textarea,select,[contenteditable="true"],.modal-overlay.open,.cb75-modal-overlay.open,.alerts-center-overlay.open,.edit-med-overlay.open');
  }
  function reset(){
    pulling = false;
    distance = 0;
    activeScroller = null;
    if(!indicator) return;
    indicator.classList.remove('show','ready','refreshing');
    indicator.style.transform = 'translate(-50%,-70px) scale(.92)';
    if(text) text.textContent = 'Puxe para atualizar';
  }
  async function refreshApp(){
    if(!indicator) return location.reload();
    indicator.classList.add('show','refreshing');
    indicator.classList.remove('ready');
    indicator.style.transform = 'translate(-50%,0) scale(1)';
    if(text) text.textContent = 'Atualizando…';
    try{
      if('serviceWorker' in navigator){
        const reg = await navigator.serviceWorker.getRegistration('./');
        if(reg) await reg.update();
      }
    }catch(e){}
    setTimeout(function(){ location.reload(); }, 180);
  }

  document.addEventListener('touchstart', function(e){
    if(window.innerWidth >= 768 || e.touches.length !== 1 || blockedTarget(e.target)) return;
    const scroller = currentScroller();
    if(!atTop(scroller)) return;
    startY = e.touches[0].clientY;
    startX = e.touches[0].clientX;
    activeScroller = scroller;
    pulling = true;
    distance = 0;
  }, {passive:true});

  document.addEventListener('touchmove', function(e){
    if(!pulling || !activeScroller || e.touches.length !== 1) return;
    if(!atTop(activeScroller)){ reset(); return; }
    const dy = e.touches[0].clientY - startY;
    const dx = Math.abs(e.touches[0].clientX - startX);
    if(dy <= 0 || dx > Math.abs(dy)){ reset(); return; }
    distance = Math.min(120, dy * .62);
    if(distance < 10) return;
    if(indicator){
      indicator.classList.add('show');
      const y = Math.min(16, -44 + distance * .72);
      indicator.style.transform = 'translate(-50%,' + y + 'px) scale(' + Math.min(1, .92 + distance/600) + ')';
      const ready = distance >= THRESHOLD;
      indicator.classList.toggle('ready', ready);
      if(text) text.textContent = ready ? 'Solte para atualizar' : 'Puxe para atualizar';
    }
  }, {passive:true});

  document.addEventListener('touchend', function(){
    if(!pulling) return;
    const shouldRefresh = distance >= THRESHOLD;
    if(shouldRefresh) refreshApp();
    else reset();
  }, {passive:true});
  document.addEventListener('touchcancel', reset, {passive:true});
})();
</script>
'''
    pos = s.rfind('</body>')
    if pos == -1:
        raise SystemExit('ERRO: </body> real não encontrado para pull refresh')
    s = s[:pos] + refresh_patch + '\n' + s[pos:]

index.write_text(s, encoding='utf-8')

sw = Path('sw.js')
t = sw.read_text(encoding='utf-8')
t = re.sub(r"const CACHE_NAME = '[^']+';", "const CACHE_NAME = 'cuidarbem-v75-36-pull-refresh';", t, count=1)
sw.write_text(t, encoding='utf-8')
