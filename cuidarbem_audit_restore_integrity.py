from pathlib import Path
import re
s=Path('index.html').read_text(encoding='utf-8')
out=['CUIDARBEM RESTORE INTEGRITY AUDIT']
patterns=['function buildSnapshot','function applySnapshot','function importBackupJSON','function restoreLocalBackup','function restoreCloudBackup','cb_auto_backup','JSON.parse','localStorage.setItem']
for pat in patterns:
    out.append(f'\n=== {pat} ===')
    for m in list(re.finditer(re.escape(pat),s))[:8]:
        p=m.start(); out.append(s[max(0,p-700):min(len(s),p+4200)])
Path('cuidarbem_restore_integrity_audit.txt').write_text('\n'.join(out),encoding='utf-8')
