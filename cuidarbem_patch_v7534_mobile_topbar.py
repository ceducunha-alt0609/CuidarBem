from pathlib import Path
import re

index = Path('index.html')
s = index.read_text(encoding='utf-8')
marker = 'cuidarbem-v75-34-mobile-topbar-fix'
if marker not in s:
    patch = '''

<!-- v75.34 — Mobile: remove clone desktop que bagunçava a Home -->
<style id="cuidarbem-v75-34-mobile-topbar-fix">
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
    top:auto !important;
    right:auto !important;
    left:auto !important;
    transform:none !important;
    margin:12px 0 0 !important;
    padding:6px 10px !important;
  }
  #screen-home > .header > div[style*="justify-content:space-between"]{
    display:flex !important;
    position:relative !important;
    inset:auto !important;
    transform:none !important;
    margin-top:10px !important;
    margin-bottom:0 !important;
  }
  #screen-home .mobile-header-actions{
    display:grid !important;
    margin-top:12px !important;
  }
  #screen-home .content{padding-top:258px !important;}
}
</style>
<script id="cuidarbem-v75-34-mobile-topbar-fix-js">
(function(){
  'use strict';
  function repairMobileHomeTopbar(){
    if(window.innerWidth > 767) return;
    const header = document.querySelector('#screen-home > .header');
    if(!header) return;
    header.querySelectorAll(':scope > .cb-home-topbar-right').forEach(el => el.remove());
    const date = header.querySelector(':scope > .header-date, :scope > #today-date');
    if(date) date.style.removeProperty('display');
    const actions = Array.from(header.children).find(el => {
      if(!el || !el.getAttribute) return false;
      const st = el.getAttribute('style') || '';
      return st.includes('justify-content:space-between');
    });
    if(actions) actions.style.removeProperty('display');
  }
  document.addEventListener('DOMContentLoaded', function(){
    repairMobileHomeTopbar();
    setTimeout(repairMobileHomeTopbar, 80);
    setTimeout(repairMobileHomeTopbar, 350);
  });
  window.addEventListener('resize', repairMobileHomeTopbar, {passive:true});
  window.addEventListener('orientationchange', function(){ setTimeout(repairMobileHomeTopbar, 120); });
})();
</script>
'''
    s = s.replace('</body>', patch + '\n</body>', 1)
    index.write_text(s, encoding='utf-8')

sw = Path('sw.js')
t = sw.read_text(encoding='utf-8')
t = re.sub(r"const CACHE_NAME = '[^']+';", "const CACHE_NAME = 'cuidarbem-v75-34-mobile-topbar-fix';", t, count=1)
sw.write_text(t, encoding='utf-8')
