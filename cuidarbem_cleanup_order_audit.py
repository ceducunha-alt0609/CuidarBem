from pathlib import Path
s=Path('index.html').read_text(encoding='utf-8')
marker='<style id="cb-effects-cleanup">'
pos=s.find(marker)
assert pos>=0
before=s[:pos]; after=s[pos:]
terms=['backdrop-filter','will-change','animation:','isolation:isolate','translateZ(0)','transform:']
out=['CUIDARBEM CLEANUP ORDER AUDIT',f'cleanup_offset={pos}',f'index_len={len(s)}',f'after_len={len(after)}']
for t in terms:
    out.append(f'{t}: before={before.count(t)} after={after.count(t)}')
out.append('\n=== AFTER CLEANUP HEAD ===\n'+after[:12000])
# identify style ids after cleanup
import re
out.append('\n=== STYLE IDS AFTER CLEANUP ===')
out.extend(re.findall(r'<style[^>]*id=["\']([^"\']+)',after,re.I))
Path('cuidarbem_cleanup_order_report.txt').write_text('\n'.join(out),encoding='utf-8')
print('cleanup order audit ok')
