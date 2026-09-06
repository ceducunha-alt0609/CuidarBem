from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='cuidarbem-v75-32-subtelas-fullwidth-fix'
if marker not in s:
    patch='''\n<!-- v75.32 — Desktop: subtelas com a mesma largura útil da Home -->\n<style id="cuidarbem-v75-32-subtelas-fullwidth-fix">\n@media (min-width:768px){\n  #screen-calendar.active,\n  #screen-dashboard.active,\n  #screen-ocr.active,\n  #screen-reports.active,\n  #screen-appt.active,\n  #screen-profile.active{\n    width:calc(100vw - var(--cb-desktop-sidebar,260px)) !important;\n    max-width:none !important;\n    min-width:0 !important;\n    margin-left:var(--cb-desktop-sidebar,260px) !important;\n  }\n\n  #screen-calendar > .header-sub,\n  #screen-dashboard > .header-sub,\n  #screen-ocr > .header-sub,\n  #screen-reports > .header-sub,\n  #screen-appt > .header-sub,\n  #screen-profile > .header-sub{\n    width:100% !important;\n    max-width:none !important;\n    min-width:0 !important;\n    margin-left:0 !important;\n    margin-right:0 !important;\n    box-sizing:border-box !important;\n  }\n\n  #screen-calendar .content,\n  #screen-dashboard .health-dashboard,\n  #screen-ocr .content,\n  #screen-reports .content,\n  #screen-appt .content,\n  #screen-profile .content{\n    width:100% !important;\n    max-width:none !important;\n    box-sizing:border-box !important;\n  }\n}\n</style>\n<script id="cuidarbem-v75-32-version">\n(function(){\n  try{ localStorage.setItem('cuidarbem_patch_version','v75.32-subtelas-fullwidth-fix'); }catch(e){}\n})();\n</script>\n'''
    i=s.rfind('</body>')
    assert i!=-1
    s=s[:i]+patch+s[i:]
    p.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
import re
t=re.sub(r"const CACHE_NAME = 'cuidarbem-[^']+';","const CACHE_NAME = 'cuidarbem-v62-subtelas-fullwidth';",t,count=1)
sw.write_text(t,encoding='utf-8')
