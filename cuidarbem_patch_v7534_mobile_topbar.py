from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Remove a camada dinâmica v75.78: ela disputava com o renderizador original.
s=re.sub(r'\s*<style id="cuidarbem-v75-78-consultas-exames-final">.*?</style>\s*','\n',s,flags=re.S)
s=re.sub(r'\s*<script id="cuidarbem-v75-78-consultas-exames-final-js">.*?</script>\s*','\n',s,flags=re.S)

old='''      <!-- UPCOMING APPTS -->
      <div class="section-header" style="margin-top:16px">
        <div class="section-title">🩺 Próximas consultas</div>
      </div>
      <div id="appt-upcoming-cons"></div>
      <div class="section-header" style="margin-top:16px">
        <div class="section-title">🔬 Próximos exames</div>
      </div>
      <div id="appt-upcoming-exam"></div>'''
new='''      <!-- UPCOMING APPTS v75.79 — estrutura original compactada -->
      <section class="card cb7579-upcoming-card" id="cb7579-cons-card">
        <div class="cb7579-upcoming-head"><span class="cb7579-upcoming-ico">🩺</span><div class="cb7579-upcoming-copy"><div class="cb7579-upcoming-title">Próximas consultas</div><div id="appt-upcoming-cons" class="cb7579-upcoming-body"></div></div><span class="cb7579-upcoming-go">›</span></div>
      </section>
      <section class="card cb7579-upcoming-card" id="cb7579-exam-card">
        <div class="cb7579-upcoming-head"><span class="cb7579-upcoming-ico">🔬</span><div class="cb7579-upcoming-copy"><div class="cb7579-upcoming-title">Próximos exames</div><div id="appt-upcoming-exam" class="cb7579-upcoming-body"></div></div><span class="cb7579-upcoming-go">›</span></div>
      </section>'''
count=s.count(old)
if count==0 and 'cb7579-cons-card' not in s:
    raise SystemExit('ERRO: bloco original de próximas consultas/exames não encontrado')
if count:
    s=s.replace(old,new)

marker='cuidarbem-v75-79-consultas-source-fix'
if marker not in s:
    css=r'''
<style id="cuidarbem-v75-79-consultas-source-fix">
@media(max-width:767px){
  .cb7579-upcoming-card{padding:17px 18px!important;margin:12px 0!important}
  .cb7579-upcoming-head{display:flex;align-items:center;gap:12px}
  .cb7579-upcoming-ico{font-size:25px;flex:0 0 34px;text-align:center}
  .cb7579-upcoming-copy{flex:1;min-width:0}
  .cb7579-upcoming-title{font-family:'Nunito',sans-serif;font-size:17px;font-weight:900;color:var(--green-800);line-height:1.2}
  .cb7579-upcoming-body{font-size:12px;color:var(--text-muted);font-weight:700;line-height:1.35;margin-top:4px}
  .cb7579-upcoming-body>div{padding:0!important;font-size:12px!important;color:var(--text-muted)!important}
  .cb7579-upcoming-go{font-size:25px;color:var(--green-600);flex:0 0 auto}
}
</style>
'''
    pos=s.rfind('</body>')
    if pos<0: raise SystemExit('body not found')
    s=s[:pos]+css+'\n'+s[pos:]

p.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-79-consultas-source-fix';",t,count=1)
sw.write_text(t,encoding='utf-8')
