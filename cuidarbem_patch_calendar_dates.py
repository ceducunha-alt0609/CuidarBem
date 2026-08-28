from pathlib import Path
import re
p=Path('index.html')
s=p.read_text(encoding='utf-8')
# Discover the existing local calendar helper introduced by the first safety patch.
if 'function localDateKey' not in s and 'const localDateKey' not in s and 'var localDateKey' not in s:
    raise SystemExit('localDateKey helper not found')
patterns=[
    (r'([A-Za-z_$][\w$]*)\.toISOString\(\)\.split\(["\']T["\']\)\[0\]', r'localDateKey(\1)'),
    (r'([A-Za-z_$][\w$]*)\.toISOString\(\)\.slice\(0,\s*10\)', r'localDateKey(\1)'),
]
changed=0
for pat,repl in patterns:
    s,n=re.subn(pat,repl,s)
    changed+=n
# Restore technical UTC filename dates: filenames do not affect calendar logic.
s=s.replace("`CuidarBem-backup-${localDateKey(new Date())}.json`", "`CuidarBem-backup-${localDateKey(new Date())}.json`")
if changed < 8:
    raise SystemExit(f'expected several calendar replacements, got {changed}')
p.write_text(s,encoding='utf-8')
print('calendar date replacements', changed)
