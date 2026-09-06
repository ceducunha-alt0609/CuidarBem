from pathlib import Path
import re

index=Path('index.html')
s=index.read_text(encoding='utf-8')

marker='cuidarbem-v75-40-summary-card-real-target'
if marker not in s:
    patch=r'''

<!-- v75.40 — Mobile: Resumo do Dia compacto usando IDs reais -->
<style id="cuidarbem-v75-40-summary-card-real-target">
@media (max-width:767px){
  #cb75-resumo-dia{padding-bottom:14px!important;}
  #cb75-resumo-dia #cb75-brief-list{display:none!important;}
  #cb75-resumo-dia .cb7540-glance{display:flex;align-items:center;gap:12px;margin-top:12px;padding:14px 15px;border:1px solid rgba(26,107,92,.16);border-radius:16px;background:rgba(255,255,255,.78);cursor:pointer;}
  #cb75-resumo-dia .cb7540-icon{font-size:25px;flex:0 0 auto;}
  #cb75-resumo-dia .cb7540-copy{flex:1;min-width:0;}
  #cb75-resumo-dia .cb7540-main{font:800 17px/1.25 'Nunito',sans-serif;color:#154f45;}
  #cb75-resumo-dia .cb7540-sub{font:600 14px/1.35 'Nunito Sans',sans-serif;color:#52645f;margin-top:4px;}
  #cb75-resumo-dia .cb7540-arrow{font-size:24px;color:#1a6b5c;font-weight:900;}
  #cb75-resumo-dia .cb75-actions{display:flex!important;justify-content:center!important;gap:10px!important;margin-top:12px!important;}
}
</style>
<script id="cuidarbem-v75-40-summary-card-real-target-js">
(function(){
  'use strict';
  function norm(v){return (v||'').replace(/\s+/g,' ').trim();}
  function setup(){
    if(window.innerWidth>=768)return;
    var card=document.getElementById('cb75-resumo-dia');
    if(!card)return;
    var list=document.getElementById('cb75-brief-list');
    var actions=card.querySelector('.cb75-actions');
    if(!document.getElementById('cb7540-glance')){
      var glance=document.createElement('div');
      glance.id='cb7540-glance';
      glance.className='cb7540-glance';
      glance.innerHTML='<span class="cb7540-icon">🧠</span><div class="cb7540-copy"><div class="cb7540-main">Resumo rápido do dia</div><div class="cb7540-sub">Toque para abrir a leitura ampliada</div></div><span class="cb7540-arrow">›</span>';
      if(actions)card.insertBefore(glance,actions);else card.appendChild(glance);
      glance.addEventListener('click',function(){
        var btn=document.getElementById('mobile-kiosk-btn')||document.getElementById('kiosk-btn');
        if(btn)btn.click();
      });
    }
    function refreshGlance(){
      var glance=document.getElementById('cb7540-glance'); if(!glance)return;
      var main=glance.querySelector('.cb7540-main');
      var sub=glance.querySelector('.cb7540-sub');
      var chip=document.getElementById('cb75-brief-chip');
      var txt=norm(list?list.innerText:'');
      var chipTxt=norm(chip?chip.innerText:'');
      var low=/hidrata[cç][aã]o baixa|baixa no registro/i.test(txt);
      var missing=/n[aã]o preenchido/i.test(txt);
      var count=(low?1:0)+(missing?1:0);
      if(count){
        main.textContent=count+' ponto'+(count>1?'s':'')+' para conferir';
        var parts=[];
        if(missing)parts.push('Estado geral não preenchido');
        if(low)parts.push('Hidratação baixa');
        sub.textContent=parts.join(' • ');
      }else if(chipTxt && !/cuidador ativo/i.test(chipTxt)){
        main.textContent=chipTxt;
        sub.textContent='Toque para abrir o resumo completo';
      }else{
        main.textContent='Rotina em dia';
        sub.textContent='Toque para abrir o resumo completo';
      }
    }
    refreshGlance();
    if(list&&!list.dataset.cb7540Observed){
      list.dataset.cb7540Observed='1';
      new MutationObserver(refreshGlance).observe(list,{childList:true,subtree:true,characterData:true});
    }
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup,{once:true});else setup();
  setTimeout(setup,120);setTimeout(setup,500);setTimeout(setup,1200);
})();
</script>
'''
    pos=s.rfind('</body>')
    if pos==-1: raise SystemExit('ERRO: </body> real não encontrado')
    s=s[:pos]+patch+'\n'+s[pos:]

index.write_text(s,encoding='utf-8')
sw=Path('sw.js'); t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';", "const CACHE_NAME = 'cuidarbem-v75-40-summary-card-real-target';", t, count=1)
sw.write_text(t,encoding='utf-8')
