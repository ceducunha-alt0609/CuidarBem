from pathlib import Path
s=Path('index.html').read_text(encoding='utf-8',errors='ignore')
needles=['toggleSupabaseSync','supabaseSync','saveToSupabase','loadFromSupabase','subscribe','realtime','autoBackup','backup','restore','exportData','importData','scheduleAlarmsOnSW','buildSmartAlarmPayload']
out=['CUIDARBEM SYNC/BACKUP/ALARMS AUDIT']
for n in needles:
    out.append('\n=== '+n+' ===')
    start=0; hits=0
    while True:
        p=s.lower().find(n.lower(),start)
        if p<0: break
        hits+=1
        out.append(s[max(0,p-900):p+2600])
        start=p+len(n)
        if hits>=4: break
    if hits==0: out.append('NOT FOUND')
Path('cuidarbem_sync_audit_report.txt').write_text('\n'.join(out),encoding='utf-8')
print('sync audit ok')
