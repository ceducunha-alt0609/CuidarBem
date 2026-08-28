from pathlib import Path
s=Path('index.html').read_text(encoding='utf-8',errors='ignore')
funcs=['cbCollectSnapshot','cbApplySnapshot','buildCloudPayload','pullState','pushStateNow','queuePush','startRealtimeListener','createSupabaseFamily','joinSupabaseFamily']
out=[]
for f in funcs:
    out.append('\n=== '+f+' ===')
    # find first few occurrences and emit generous context
    start=0; n=0
    while True:
        p=s.find(f,start)
        if p<0: break
        n+=1
        out.append(s[max(0,p-1200):p+5200])
        start=p+len(f)
        if n>=3: break
    if n==0: out.append('NOT FOUND')
Path('cuidarbem_sync_conflict_report.txt').write_text('\n'.join(out),encoding='utf-8')
print('conflict audit ok')
