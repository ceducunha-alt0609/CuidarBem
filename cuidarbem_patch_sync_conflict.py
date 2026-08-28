from pathlib import Path
p=Path('index.html'); s=p.read_text(encoding='utf-8')

def rep(old,new,label,count=1):
    global s
    got=s.count(old)
    assert got>=count, f'{label}: expected {count}, got {got}'
    s=s.replace(old,new,count)

rep("const SB_ENABLED_KEY = 'cb_supabase_sync_enabled';", "const SB_ENABLED_KEY = 'cb_supabase_sync_enabled';\nconst SB_DIRTY_KEY = 'cb_supabase_local_dirty';", 'dirty key')

# Clear pending-local marker only after a remote snapshot is deliberately applied.
rep("""      window.cbApplySnapshot(data.state, { silent });
      setLastSync('Dados recebidos: ' + new Date().toLocaleString('pt-BR') + (data.updated_by ? ' · por ' + data.updated_by : ''));""", """      window.cbApplySnapshot(data.state, { silent });
      localStorage.setItem(SB_DIRTY_KEY, '0');
      setLastSync('Dados recebidos: ' + new Date().toLocaleString('pt-BR') + (data.updated_by ? ' · por ' + data.updated_by : ''));""", 'pull clears dirty')

# Successful push means local changes are now represented in cloud.
rep("""  setStatus('✅ Sincronizado em tempo real', 'var(--teal-600)', true);
  setLastSync('Última sincronização enviada: ' + new Date().toLocaleString('pt-BR'));""", """  localStorage.setItem(SB_DIRTY_KEY, '0');
  setStatus('✅ Sincronizado em tempo real', 'var(--teal-600)', true);
  setLastSync('Última sincronização enviada: ' + new Date().toLocaleString('pt-BR'));""", 'push clears dirty')

# Do not let a broadcast overwrite unsent local work.
rep("""      if (!payload || payload.familyCode !== familyCode) return;
      const remoteTs = Date.parse(payload.updated_at_client || '') || 0;""", """      if (!payload || payload.familyCode !== familyCode) return;
      if (localStorage.getItem(SB_DIRTY_KEY) === '1') {
        setStatus('⚠️ Conflito: há alterações locais não enviadas', 'var(--amber-600)', true);
        setLastSync('Escolha Forçar envio (local) ou Entrar / sincronizar (nuvem).');
        return;
      }
      const remoteTs = Date.parse(payload.updated_at_client || '') || 0;""", 'broadcast conflict guard')

# Persist dirty state when local saves occur; remote application is excluded.
rep("""window.addEventListener('cb-local-change', e => queuePush(e.detail?.reason));
window.addEventListener('storage', e => {
  if (['cuidarbem_tasks','cuidarbem_completions','cuidarbem_settings','cb_medical_profile','cb_care_events','cb_vitals','cb_vital_freq','cuidarbem_a11y','paciente'].includes(e.key)) queuePush('storage:' + e.key);
});""", """window.addEventListener('cb-local-change', e => {
  if (!sbApplyingRemote) localStorage.setItem(SB_DIRTY_KEY, '1');
  queuePush(e.detail?.reason);
});
window.addEventListener('storage', e => {
  if (['cuidarbem_tasks','cuidarbem_completions','cuidarbem_settings','cb_medical_profile','cb_care_events','cb_vitals','cb_vital_freq','cuidarbem_a11y','paciente'].includes(e.key)) {
    if (!sbApplyingRemote) localStorage.setItem(SB_DIRTY_KEY, '1');
    queuePush('storage:' + e.key);
  }
});""", 'local dirty tracking')

# Startup: never auto-pull over pending offline edits.
old="""if (localStorage.getItem(SB_ENABLED_KEY) === '1' && localStorage.getItem(SB_FAMILY_KEY)) {
  const code = localStorage.getItem(SB_FAMILY_KEY);
  Promise.resolve().then(() => {
    ensureSupabase(code);
    return pullState(code, { apply:true, silent:true });
  }).then(() => startRealtimeListener(code)).then(() => {
    setStatus('✅ Sincronizado em tempo real', 'var(--teal-600)', true);
  }).catch(err => {
    console.warn('[CuidarBem Supabase] auto start error:', err);
    setStatus('❌ Supabase precisa da tabela/regras', 'var(--coral-600)', false);
  });
}"""
new="""if (localStorage.getItem(SB_ENABLED_KEY) === '1' && localStorage.getItem(SB_FAMILY_KEY)) {
  const code = localStorage.getItem(SB_FAMILY_KEY);
  const hasPendingLocal = localStorage.getItem(SB_DIRTY_KEY) === '1';
  Promise.resolve().then(() => {
    ensureSupabase(code);
    return hasPendingLocal ? null : pullState(code, { apply:true, silent:true });
  }).then(() => startRealtimeListener(code)).then(() => {
    if (hasPendingLocal) {
      setStatus('⚠️ Alterações locais aguardando decisão', 'var(--amber-600)', true);
      setLastSync('Escolha Forçar envio (local) ou Entrar / sincronizar (nuvem).');
    } else {
      setStatus('✅ Sincronizado em tempo real', 'var(--teal-600)', true);
    }
  }).catch(err => {
    console.warn('[CuidarBem Supabase] auto start error:', err);
    setStatus('❌ Supabase precisa da tabela/regras', 'var(--coral-600)', false);
  });
}"""
rep(old,new,'startup conflict guard')
p.write_text(s,encoding='utf-8')

swp=Path('sw.js'); w=swp.read_text(encoding='utf-8')
assert "const CACHE_NAME = 'cuidarbem-v54-audit-safety';" in w
w=w.replace("const CACHE_NAME = 'cuidarbem-v54-audit-safety';", "const CACHE_NAME = 'cuidarbem-v55-sync-conflict-guard';",1)
swp.write_text(w,encoding='utf-8')

s2=p.read_text(encoding='utf-8')
for needle in [
  "const SB_DIRTY_KEY = 'cb_supabase_local_dirty';",
  "localStorage.setItem(SB_DIRTY_KEY, '1')",
  "localStorage.setItem(SB_DIRTY_KEY, '0')",
  "Conflito: há alterações locais não enviadas",
  "const hasPendingLocal = localStorage.getItem(SB_DIRTY_KEY) === '1';",
  "return hasPendingLocal ? null : pullState"
]: assert needle in s2, needle
assert 'cuidarbem-v55-sync-conflict-guard' in swp.read_text(encoding='utf-8')
print('CuidarBem sync conflict guard OK')
