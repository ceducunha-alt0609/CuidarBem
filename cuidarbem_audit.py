from pathlib import Path
import re

files = {p.name: p.read_text(encoding='utf-8', errors='ignore') for p in Path('.').glob('*') if p.is_file() and p.suffix in {'.html','.js','.json','.webmanifest','.txt','.sql','.md'}}
idx = files.get('index.html','')
alljs = files.get('all.js','')
sw = files.get('sw.js','')
combo = idx + '\n' + alljs

terms = {
  'service_worker_register': r'serviceWorker\.register',
  'manifest_links': r'rel=["\']manifest["\']',
  'localStorage': r'localStorage',
  'indexedDB': r'indexedDB',
  'supabase': r'supabase',
  'fetch_calls': r'\bfetch\s*\(',
  'toISOString_slice': r'toISOString\(\).*?slice\(',
  'new_Date_iso': r'new Date\([^\)]*\)\.toISOString',
  'setTimeout': r'setTimeout\s*\(',
  'notifications': r'Notification|showNotification',
  'backup_export': r'backup|exportar|exportBackup|download',
  'backup_import': r'importar|restore|restaur|FileReader',
  'seed_demo': r'demo|seed|exemplo|mock|sample',
  'innerHTML': r'innerHTML\s*=',
  'eval': r'\beval\s*\(',
  'confirm': r'\bconfirm\s*\(',
}

out=[]
out.append('CUIDARBEM STRUCTURAL AUDIT')
out.append(f'index_bytes={len(idx.encode("utf-8"))}')
out.append(f'alljs_bytes={len(alljs.encode("utf-8"))}')
for k,pat in terms.items():
    out.append(f'{k}={len(re.findall(pat, combo, flags=re.I|re.S))}')

for needle in ['serviceWorker.register','localStorage','supabase','toISOString','FileReader','Notification','showNotification','setTimeout','seed','demo','backup','restaur']:
    out.append(f'\n=== {needle} ===')
    pos = combo.lower().find(needle.lower())
    if pos < 0: out.append('NOT FOUND')
    else: out.append(combo[max(0,pos-700):pos+1800])

out.append('\n=== SW ACTIVATE ===')
pos=sw.find("self.addEventListener('activate'")
out.append(sw[pos:pos+900] if pos>=0 else 'NOT FOUND')
out.append('\n=== SW APP_SHELL ===')
pos=sw.find('const APP_SHELL')
out.append(sw[pos:pos+1000] if pos>=0 else 'NOT FOUND')

Path('cuidarbem_audit_report.txt').write_text('\n'.join(out), encoding='utf-8')
print('audit ok')
