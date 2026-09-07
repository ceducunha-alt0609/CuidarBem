from pathlib import Path
import re
p=Path('index.html');s=p.read_text(encoding='utf-8');marker='cuidarbem-v75-71-reports-real-dom'
if marker not in s:
 patch=r'''
<!-- v75.71 — Relatórios mobile: localizar estrutura real por conteúdo -->
<style id="cuidarbem-v75-71-reports-real-dom">
@media(max-width:767px){
 .cb7571-entry{display:block!important;padding:18px 20px!important;cursor:pointer}
 .cb7571-entry .r{display:flex;align-items:center;gap:12px}.cb7571-entry .i{font-size:25px}.cb7571-entry .c{flex:1;min-width:0}.cb7571-entry .t{font-family:'Nunito',sans-serif;font-size:17px;font-weight:900;color:var(--green-800)}.cb7571-entry .s{font-size:12px;font-weight:700;color:var(--text-muted);margin-top:3px;line-height:1.35}.cb7571-entry .g{font-size:25px;color:var(--green-600)}
 .cb7571-source.cb7571-collapsed{display:none!important}.cb7571-entry.cb7571-open{display:none!important}.cb7571-back{display:none!important;width:100%;margin:0 0 10px}.cb7571-back.cb7571-show{display:flex!important}
 #cb7571-period{display:flex;gap:8px;margin:0 22px 14px;padding:4px;border:1px solid var(--green-200);border-radius:16px;background:rgba(255,255,255,.65)}#cb7571-period button{flex:1;border:0;background:transparent;border-radius:12px;padding:10px 5px;font-weight:900;color:var(--green-700)}#cb7571-period button.active{background:var(--green-600);color:#fff}
}
@media(min-width:768px){.cb7571-entry,.cb7571-back,#cb7571-period{display:none!important}}
</style>
<script id="cuidarbem-v75-71-reports-real-dom-js">
(function(){
 function txt(e){return(e&&e.textContent||'').replace(/\s+/g,' ').trim()}
 function findExact(re){var a=document.querySelectorAll('body *'),best=null;for(var i=0;i<a.length;i++){var t=txt(a[i]);if(re.test(t)&&(!best||a[i].children.length<best.children.length))best=a[i]}return best}
 function sourceFor(el){if(!el)return null;var n=el;while(n&&n!==document.body){var t=txt(n);if((n.classList&&n.classList.contains('card'))||(/Resumo semanal para médico\/família/i.test(t)&&/Gerar resumo/i.test(t))||(/ADESÃO POR CATEGORIA/i.test(t)&&/Remédios/i.test(t)&&/Exames/i.test(t))||(/EVOLUÇÃO FUNCIONAL/i.test(t)&&/BARTHEL ATUAL/i.test(t)))return n;n=n.parentElement}return el.parentElement}
 function make(key,el,title,sub,icon){if(!el||document.getElementById('cb7571-'+key+'-entry'))return;var src=sourceFor(el);if(!src)return;src.id='cb7571-'+key+'-source';src.classList.add('cb7571-source','cb7571-collapsed');var e=document.createElement('section');e.id='cb7571-'+key+'-entry';e.className='card cb7571-entry';e.innerHTML='<div class="r"><div class="i">'+icon+'</div><div class="c"><div class="t">'+title+'</div><div class="s">'+sub+'</div></div><div class="g">›</div></div>';src.parentNode.insertBefore(e,src);var b=document.createElement('button');b.className='cb75-btn secondary cb7571-back';b.textContent='‹ Voltar aos relatórios';src.parentNode.insertBefore(b,src);e.onclick=function(){src.classList.remove('cb7571-collapsed');e.classList.add('cb7571-open');b.classList.add('cb7571-show');setTimeout(function(){b.scrollIntoView({behavior:'smooth',block:'start'})},30)};b.onclick=function(){src.classList.add('cb7571-collapsed');e.classList.remove('cb7571-open');b.classList.remove('cb7571-show');setTimeout(function(){e.scrollIntoView({behavior:'smooth',block:'center'})},30)}}
 function setup(){
  var h=findExact(/^Relatórios$/i);if(!h)return;var root=h;while(root.parentElement&&root.parentElement!==document.body&&txt(root.parentElement).indexOf('ADESÃO POR CATEGORIA')<0)root=root.parentElement;
  var sum=findExact(/Resumo semanal para médico\/família/i);make('summary',sum,'Resumo do período','Para família ou consulta médica · texto, voz e PDF','📝');
  var fun=findExact(/^EVOLUÇÃO FUNCIONAL$/i);make('functional',fun,'Evolução funcional','Barthel / mRS e acompanhamento da recuperação','🧭');
  var cat=findExact(/^ADESÃO POR CATEGORIA$/i);make('category',cat,'Adesão aos cuidados','Remédios, consultas, exames, fisioterapia e exercícios','📊');
  var v=findExact(/Resumo semanal CuidarBem V\d+/i);if(v&&v.children.length===0)v.textContent=v.textContent.replace(/\s+V\d+(?:\.\d+)?/i,'');
  if(!document.getElementById('cb7571-period')&&sum){var src=document.getElementById('cb7571-summary-entry')||sourceFor(sum);if(src&&src.parentNode){var q=document.createElement('div');q.id='cb7571-period';q.innerHTML='<button class="active">7 dias</button><button>30 dias</button>';src.parentNode.insertBefore(q,src);q.onclick=function(e){if(e.target.tagName!=='BUTTON')return;q.querySelectorAll('button').forEach(function(x){x.classList.toggle('active',x===e.target)})}}}
  var monthly=findExact(/^ADESÃO MENSAL$/i);if(monthly){var mc=sourceFor(monthly);if(mc&&/^0%/.test(txt(mc).replace('ADESÃO MENSAL','').trim())){mc.querySelectorAll('canvas,svg').forEach(function(x){x.style.display='none'})}}
 }
 document.addEventListener('DOMContentLoaded',setup);var n=0,t=setInterval(function(){setup();if(++n>80)clearInterval(t)},200);
})();
</script>
'''
 pos=s.rfind('</body>');
 if pos<0:raise SystemExit('body not found')
 s=s[:pos]+patch+'\n'+s[pos:]
p.write_text(s,encoding='utf-8');sw=Path('sw.js');t=sw.read_text(encoding='utf-8');t=re.sub(r"const CACHE_NAME = '[^']+';","const CACHE_NAME = 'cuidarbem-v75-71-reports-real-dom';",t,count=1);sw.write_text(t,encoding='utf-8')
