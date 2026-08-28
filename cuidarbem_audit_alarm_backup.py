from pathlib import Path
import re
s=Path('index.html').read_text(encoding='utf-8')
terms=['SCHEDULE_ALARMS','CANCEL_ALARMS','Notification.requestPermission','serviceWorker','exportBackup','importBackup','restore','backup','setTimeout','showNotification','fireAt','alarm']
out=[]
out.append('CUIDARBEM ALARM/BACKUP AUDIT\n')
for t in terms:
    out.append(f'{t}={s.count(t)}')
for t in terms:
    out.append(f'\n=== {t} ===')
    hits=[m.start() for m in re.finditer(re.escape(t),s,re.I)]
    for pos in hits[:12]:
        out.append(s[max(0,pos-900):min(len(s),pos+1800)].replace('\n',' '))
Path('cuidarbem_alarm_backup_audit.txt').write_text('\n'.join(out),encoding='utf-8')
