from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
anchor='''<!-- Data/hora desktop — canto superior direito -->'''
assert anchor in s
patch='''<!-- v75.16 — desktop Home: scroll nativo real nos dois painéis -->
<style id="cuidarbem-v75-16-native-home-scroll">
@media (min-width: 768px) {
  #screen-home.active {
    height: 100svh !important;
    max-height: 100svh !important;
    overflow: hidden !important;
  }
  #screen-home.active > .content,
  #screen-home.active > .desktop-right-panel {
    min-height: 0 !important;
    height: auto !important;
    max-height: 100% !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    overscroll-behavior-y: contain !important;
    scrollbar-width: thin !important;
    scrollbar-color: rgba(0,107,88,.35) transparent !important;
  }
}
</style>
'''
# place late so it wins conflicting historical desktop rules
s=s.replace(anchor, patch+'\n'+anchor,1)
# wheel router must leave Home entirely to the browser; already expected from v59
assert "if (home && home.classList.contains('active')) {\n      return;\n    }" in s
p.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
assert "cuidarbem-v59-desktop-wheel-fix" in t
t=t.replace("cuidarbem-v59-desktop-wheel-fix","cuidarbem-v60-native-home-scroll",1)
sw.write_text(t,encoding='utf-8')
