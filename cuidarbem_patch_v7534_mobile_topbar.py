from pathlib import Path
import re

index=Path('index.html'); s=index.read_text(encoding='utf-8')
marker='cuidarbem-v75-62-no-static-home-flash'
if marker not in s:
    # Remove o estado ACTIVE gravado estaticamente na Home e no botão Início.
    # A tela correta passa a ser escolhida somente no boot, a partir da última guia salva.
    s,n1=re.subn(r'(<[^>]+class=["\']screen)\s+active(["\'][^>]+id=["\']screen-home["\'])',r'\1\2',s,count=1,flags=re.I)
    s,n2=re.subn(r'(<button[^>]+class=["\']nav-btn)\s+active(["\'][^>]+id=["\']nav-home["\'])',r'\1\2',s,count=1,flags=re.I)
    # Fallback para a ordem de atributos existente no app.
    if not n1:
        s=s.replace('class="screen active" id="screen-home"','class="screen" id="screen-home"',1)
    if not n2:
        s=s.replace('class="nav-btn active" onclick="goScreen(\'home\',this)" id="nav-home"','class="nav-btn" onclick="goScreen(\'home\',this)" id="nav-home"',1)

    pre=r'''<style id="cuidarbem-v75-62-no-static-home-flash">
@media(max-width:767px){
  /* Enquanto o boot decide a guia, nenhuma screen antiga pode pintar. */
  html.cb761-booting .screen{display:none!important;visibility:hidden!important;}
}
</style>
'''
    hp=s.find('</head>')
    if hp==-1: raise SystemExit('ERRO: </head> não encontrado')
    s=s[:hp]+pre+'\n'+s[hp:]

index.write_text(s,encoding='utf-8')
sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-62-no-static-home-flash';",t,count=1);sw.write_text(t,encoding='utf-8')
