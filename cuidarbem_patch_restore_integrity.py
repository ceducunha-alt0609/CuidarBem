from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""function buildSnapshot() {
  return {
    appVersion : '3.0',
    ts         : new Date().toISOString(),
    tasks      : localStorage.getItem('cuidarbem_tasks')       || '[]',
    completions: localStorage.getItem('cuidarbem_completions') || '{}',
    settings   : localStorage.getItem('cuidarbem_settings')    || '{}',
    profile    : localStorage.getItem('cb_medical_profile')     || '{}',
    careEvents : localStorage.getItem('cb_care_events')         || '[]',
    vitals     : localStorage.getItem('cb_vitals')             || '[]',
    vitalFreq  : localStorage.getItem('cb_vital_freq')         || '{}',
    a11y       : localStorage.getItem('cuidarbem_a11y')         || '{}',
  };
}

function applySnapshot(snap) {
  localStorage.setItem('cuidarbem_tasks',        snap.tasks);
  localStorage.setItem('cuidarbem_completions',  snap.completions);
  localStorage.setItem('cuidarbem_settings',     snap.settings);
  if (snap.profile) localStorage.setItem('cb_medical_profile', snap.profile);
  if (snap.careEvents) localStorage.setItem('cb_care_events', snap.careEvents);
  if (snap.vitals) localStorage.setItem('cb_vitals', snap.vitals);
  if (snap.vitalFreq) localStorage.setItem('cb_vital_freq', snap.vitalFreq);
  if (snap.a11y) localStorage.setItem('cuidarbem_a11y', snap.a11y);
  tasks       = JSON.parse(snap.tasks);
  completions = JSON.parse(snap.completions);
  settings    = JSON.parse(snap.settings);
  if (typeof renderAll === 'function') renderAll();
}
"""
new="""function buildSnapshot() {
  return {
    app        : 'CuidarBem',
    backupVersion: 2,
    appVersion : '3.0',
    ts         : new Date().toISOString(),
    tasks      : localStorage.getItem('cuidarbem_tasks')       || '[]',
    completions: localStorage.getItem('cuidarbem_completions') || '{}',
    settings   : localStorage.getItem('cuidarbem_settings')    || '{}',
    profile    : localStorage.getItem('cb_medical_profile')     || '{}',
    careEvents : localStorage.getItem('cb_care_events')         || '[]',
    vitals     : localStorage.getItem('cb_vitals')             || '[]',
    vitalFreq  : localStorage.getItem('cb_vital_freq')         || '{}',
    a11y       : localStorage.getItem('cuidarbem_a11y')         || '{}',
    paciente   : localStorage.getItem('paciente')               || '[]',
  };
}

function validateSnapshot(snap) {
  if (!snap || typeof snap !== 'object' || Array.isArray(snap)) throw new Error('Backup inválido');
  if (snap.app && snap.app !== 'CuidarBem') throw new Error('Este backup pertence a outro aplicativo');

  const parseField = (name, type, required = false) => {
    const raw = snap[name];
    if (raw === undefined || raw === null || raw === '') {
      if (required) throw new Error(`Campo obrigatório ausente: ${name}`);
      return null;
    }
    if (typeof raw !== 'string') throw new Error(`Campo inválido: ${name}`);
    let value;
    try { value = JSON.parse(raw); } catch (_) { throw new Error(`JSON inválido no campo: ${name}`); }
    if (type === 'array' && !Array.isArray(value)) throw new Error(`Campo ${name} deveria ser uma lista`);
    if (type === 'object' && (!value || typeof value !== 'object' || Array.isArray(value))) throw new Error(`Campo ${name} deveria ser um objeto`);
    return value;
  };

  const parsed = {
    tasks: parseField('tasks', 'array', true),
    completions: parseField('completions', 'object', true),
    settings: parseField('settings', 'object', true),
    profile: parseField('profile', 'object'),
    careEvents: parseField('careEvents', 'array'),
    vitals: parseField('vitals', 'array'),
    vitalFreq: parseField('vitalFreq', 'object'),
    a11y: parseField('a11y', 'object'),
    paciente: parseField('paciente', 'array')
  };

  const seen = new Set();
  parsed.tasks.forEach((task, i) => {
    if (!task || typeof task !== 'object' || Array.isArray(task)) throw new Error(`Tarefa inválida na posição ${i + 1}`);
    if (task.id !== undefined && task.id !== null && task.id !== '') {
      const id = String(task.id);
      if (seen.has(id)) throw new Error(`ID de tarefa duplicado: ${id}`);
      seen.add(id);
    }
    if (task.time) {
      const m = /^(\\d{2}):(\\d{2})$/.exec(String(task.time));
      if (!m || Number(m[1]) > 23 || Number(m[2]) > 59) throw new Error(`Horário inválido em tarefa: ${task.time}`);
    }
  });
  return parsed;
}

function applySnapshot(snap) {
  const parsed = validateSnapshot(snap); // valida tudo antes de substituir qualquer dado
  localStorage.setItem('cuidarbem_tasks',        snap.tasks);
  localStorage.setItem('cuidarbem_completions',  snap.completions);
  localStorage.setItem('cuidarbem_settings',     snap.settings);
  if (snap.profile) localStorage.setItem('cb_medical_profile', snap.profile);
  if (snap.careEvents) localStorage.setItem('cb_care_events', snap.careEvents);
  if (snap.vitals) localStorage.setItem('cb_vitals', snap.vitals);
  if (snap.vitalFreq) localStorage.setItem('cb_vital_freq', snap.vitalFreq);
  if (snap.a11y) localStorage.setItem('cuidarbem_a11y', snap.a11y);
  if (snap.paciente) localStorage.setItem('paciente', snap.paciente);
  tasks       = parsed.tasks;
  completions = parsed.completions;
  settings    = parsed.settings;
  if (typeof renderAll === 'function') renderAll();
  if (typeof renderHistorico === 'function') renderHistorico();
  if (typeof carregarUltimo === 'function') carregarUltimo();
}
"""
if old not in s: raise SystemExit('snapshot anchor not found')
s=s.replace(old,new,1)
# Strengthen manual import precheck; applySnapshot remains the final gate for all restore paths.
s=s.replace("if (!snap || !snap.tasks || !snap.settings) throw new Error('Arquivo inválido');", "validateSnapshot(snap);", 1)
p.write_text(s,encoding='utf-8')

p=Path('sw.js')
s=p.read_text(encoding='utf-8')
s=s.replace("const CACHE_NAME = 'cuidarbem-v56-alarm-lifecycle-guard';","const CACHE_NAME = 'cuidarbem-v57-restore-integrity';")
p.write_text(s,encoding='utf-8')
