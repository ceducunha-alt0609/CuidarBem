
// ─── STATE ────────────────────────────────────────────────────────────────
let tasks = JSON.parse(localStorage.getItem('cuidarbem_tasks') || '[]');
let completions = JSON.parse(localStorage.getItem('cuidarbem_completions') || '{}');
let settings = JSON.parse(localStorage.getItem('cuidarbem_settings') || '{"patient":"Maria","caregiver":"","diagnosis":"AVC","notif_med":true,"notif_cons":true,"notif_fisio":false}');
let currentFilter = 'all';
let calFilter_ = 'all';
let selectedType = '';
let selectedCalDay = null;
let currentTaskPhoto = null;
let pendingConfirmId = null;
let photoViewTaskId = null;

// ─── INIT ─────────────────────────────────────────────────────────────────
function init() {
  migrateExamType();
  setGreeting();
  setTodayDate();
  setInterval(() => { setGreeting(); setTodayDate(); }, 30000);
  loadSettings();
  buildWeekStrip();
  renderAll();
  requestNotifPermission();
  setupNotifications();
  if (tasks.length === 0) addSampleTasks();
  // Re-render a cada 60s para atualizar status de "atrasado" dos remédios
  setInterval(() => {
    renderTodayTasks();
    renderAlerts();
    renderNextAlarm();
  }, 60000);
}

// ── Migração: type:'cons' com subtype:'exam'|examType → type:'exam' ────────
function migrateExamType() {
  let changed = 0;
  tasks.forEach(t => {
    if (t.type === 'cons' && (t.subtype === 'exam' || t.examType)) {
      t.type = 'exam';
      changed++;
    }
  });
  if (changed) {
    saveTasks();
    console.log(`[CuidarBem] Migrated ${changed} record(s) to type:exam`);
  }
}

// ── MODO SAMU ─────────────────────────────────────────────────────────────
function openSamuMode() {
  const p  = getProfile();
  const st = JSON.parse(localStorage.getItem('cuidarbem_settings') || '{}');

  // ── Identidade ──────────────────────────────────────────────────────────
  document.getElementById('samu-name').textContent = st.patient || 'Não informado';
  const age = p.birthday ? calcAge(p.birthday) : null;
  const birth = p.birthday ? new Date(p.birthday+'T00:00:00').toLocaleDateString('pt-BR',{day:'numeric',month:'long',year:'numeric'}) : '';
  const sexLabel = {F:'Feminino', M:'Masculino', O:'Outro'}[p.sex] || '';
  document.getElementById('samu-meta').textContent = [
    age ? `${age} anos` : '',
    birth ? `Nascido(a) em ${birth}` : '',
    sexLabel
  ].filter(Boolean).join(' · ') || '—';
  document.getElementById('samu-diagnosis').textContent = st.diagnosis
    ? `Diagnóstico: ${st.diagnosis}` : '';

  // ── Alergias (bloco mais importante) ────────────────────────────────────
  const allergies = [p.allergyMeds, p.allergyFood, p.allergyOther].filter(Boolean);
  const allergyEl = document.getElementById('samu-allergy-block');
  if (allergies.length) {
    allergyEl.innerHTML = `
      <div class="samu-section allergy">
        <div class="samu-section-label">⚠️ ALERGIAS CONHECIDAS</div>
        <div class="samu-section-content">
          ${p.allergyMeds  ? `<div>💊 Medicamentos: <strong>${p.allergyMeds}</strong></div>`  : ''}
          ${p.allergyFood  ? `<div>🍽️ Alimentos: <strong>${p.allergyFood}</strong></div>`      : ''}
          ${p.allergyOther ? `<div>⚗️ Outros: <strong>${p.allergyOther}</strong></div>`         : ''}
        </div>
      </div>`;
  } else {
    allergyEl.innerHTML = `<div class="samu-no-allergy">✅ Nenhuma alergia conhecida informada</div>`;
  }

  // ── Condições ────────────────────────────────────────────────────────────
  const conditionsEl  = document.getElementById('samu-conditions-block');
  const conditionsVal = document.getElementById('samu-conditions');
  const allConditions = [st.diagnosis, p.conditions].filter(Boolean).join(' · ');
  if (allConditions) {
    conditionsEl.style.display = 'block';
    conditionsVal.textContent = allConditions;
  } else conditionsEl.style.display = 'none';

  const essential = [
    p.blood ? `🩸 Tipo sanguíneo: ${p.blood}` : '',
    p.weight ? `⚖️ Peso: ${p.weight}` : '',
    p.height ? `📏 Altura: ${p.height}` : '',
    p.mainDoctor ? `🩺 Médico principal: ${p.mainDoctor}` : ''
  ].filter(Boolean).join('\n');
  const essentialBlock = document.getElementById('samu-essential-block');
  const essentialVal = document.getElementById('samu-essential');
  if (essential) { essentialBlock.style.display = 'block'; essentialVal.textContent = essential; }
  else essentialBlock.style.display = 'none';

  const notesBlock = document.getElementById('samu-notes-block');
  const notesVal = document.getElementById('samu-notes');
  if (p.importantNotes?.trim()) { notesBlock.style.display = 'block'; notesVal.textContent = p.importantNotes.trim(); }
  else notesBlock.style.display = 'none';

  // ── Medicamentos em uso ──────────────────────────────────────────────────
  const meds = tasks.filter(t => t.type === 'med' && (t.repeat === 'daily' || t.date === todayStr()));
  const medsEl = document.getElementById('samu-meds');
  medsEl.innerHTML = meds.length
    ? meds.map(m => `
        <div class="samu-med-row">
          <span>${m.name}</span>
          ${m.dose ? `<span class="samu-med-dose">${m.dose}</span>` : ''}
          ${m.time ? `<span class="samu-med-dose">· ${m.time}</span>` : ''}
        </div>`).join('')
    : `<div style="font-size:15px;color:#888">Nenhum medicamento cadastrado</div>`;

  // ── Cirurgias ─────────────────────────────────────────────────────────────
  const surgeriesEl = document.getElementById('samu-surgeries-block');
  if (p.surgeries?.trim()) {
    surgeriesEl.style.display = 'block';
    document.getElementById('samu-surgeries').textContent = p.surgeries.trim();
  } else surgeriesEl.style.display = 'none';

  // ── Tabagismo + Convênio ──────────────────────────────────────────────────
  const smokeLabels = { no:'🚭 Não fumante', ex:'🕐 Ex-fumante', yes:'🚬 Fumante ativo' };
  document.getElementById('samu-smoking').textContent = smokeLabels[p.smoking||'no'];
  const insText = p.insuranceType === 'conv' && p.convName
    ? `💳 ${p.convName}${p.convNumber ? '\nNº '+p.convNumber : ''}${p.convExpiry ? '\nVal. '+new Date(p.convExpiry+'T00:00:00').toLocaleDateString('pt-BR') : ''}`
    : `🆓 SUS${p.susNumber ? '\n' + p.susNumber : ''}`;
  document.getElementById('samu-insurance').textContent = insText;

  // ── Contato de emergência ─────────────────────────────────────────────────
  const contactBlock = document.getElementById('samu-contact-block');
  if (p.emergName || p.emergPhone) {
    contactBlock.style.display = 'block';
    document.getElementById('samu-contact-name').textContent = p.emergName || '—';
    document.getElementById('samu-contact-detail').textContent = [p.emergRel, p.emergPhone].filter(Boolean).join(' · ');
    document.getElementById('samu-call-label').textContent = p.emergPhone
      ? `LIGAR: ${p.emergPhone}` : 'LIGAR AGORA';
  } else {
    contactBlock.style.display = 'none';
  }

  // ── Abrir ─────────────────────────────────────────────────────────────────
  if (typeof haptic === 'function') haptic([30, 60, 30]);
  document.getElementById('samu-overlay').classList.add('open');
  // Manter tela acesa (se suportado)
  try { if ('wakeLock' in navigator) navigator.wakeLock.request('screen').catch(()=>{}); } catch(e) {}
}

function closeSamuMode() {
  document.getElementById('samu-overlay').classList.remove('open');
}

function samuCall() {
  const p = getProfile();
  const phone = p.emergPhone;
  if (!phone) { showToast('⚠️ Telefone não cadastrado'); return; }
  if (typeof haptic === 'function') haptic([50, 80, 50]);
  window.location.href = `tel:${phone.replace(/\D/g,'')}`;
}

function addSampleTasks() {
  const today = todayStr();
  const tomorrow = new Date(); tomorrow.setDate(tomorrow.getDate()+1);
  const tomorrowStr_ = tomorrow.toISOString().split('T')[0];
  tasks = [
    {id:uid(), demo:true, type:'med',   name:'Losartana 50mg',       dose:'1 comprimido', date:today,       time:'08:00', repeat:'daily',  obs:'Tomar com água em jejum', createdAt: Date.now()},
    {id:uid(), demo:true, type:'med',   name:'AAS 100mg',             dose:'1 comprimido', date:today,       time:'08:00', repeat:'daily',  obs:'', createdAt: Date.now()},
    {id:uid(), demo:true, type:'med',   name:'Clopidogrel 75mg',      dose:'1 comprimido', date:today,       time:'12:00', repeat:'daily',  obs:'', createdAt: Date.now()},
    {id:uid(), demo:true, type:'med',   name:'Atorvastatina 40mg',    dose:'1 comprimido', date:today,       time:'21:00', repeat:'daily',  obs:'Tomar à noite', createdAt: Date.now()},
    {id:uid(), demo:true, type:'fisio', name:'Fisioterapia motora',   dose:'', date:today,       time:'10:00', repeat:'daily',  obs:'30 min com a fisioterapeuta', createdAt: Date.now()},
    {id:uid(), demo:true, type:'exer',  name:'Exercícios de equilíbrio', dose:'', date:today,    time:'15:00', repeat:'daily',  obs:'10 repetições cada lado', createdAt: Date.now()},
    {id:uid(), demo:true, type:'cons', name:'Consulta com neurologista', dose:'', date:tomorrowStr_, time:'09:30', repeat:'none', obs:'Levar últimos exames', local:'Hospital das Clínicas', doctor:'Dr. Carlos Menezes', prep:'Levar exames anteriores e lista de medicamentos', alertMorning:true, alertBefore:true, subtype:'cons', createdAt: Date.now()},
  ];
  saveTasks();
  renderAll();
}

function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2); }
function todayStr() { return new Date().toISOString().split('T')[0]; }

function setGreeting() {
  const h = new Date().getHours();
  const el = document.getElementById('greeting');
  if (h < 12) el.textContent = 'Bom dia ☀️';
  else if (h < 18) el.textContent = 'Boa tarde 🌤️';
  else el.textContent = 'Boa noite 🌙';
}

function setTodayDate() {
  const d = new Date();
  const opts = {weekday:'long', day:'numeric', month:'long'};
  const str = d.toLocaleDateString('pt-BR', opts);
  const time = d.toLocaleTimeString('pt-BR', {hour:'2-digit', minute:'2-digit'});
  const dateEl = document.getElementById('today-date');
  if (dateEl) dateEl.textContent = `${str.charAt(0).toUpperCase() + str.slice(1)} • ${time}`;
  const calMonth = document.getElementById('cal-month');
  if (calMonth) calMonth.textContent = d.toLocaleDateString('pt-BR', {month:'long', year:'numeric'});
}

function loadSettings() {
  document.getElementById('patient-name-input').value = settings.patient || '';
  document.getElementById('caregiver-input').value = settings.caregiver || '';
  document.getElementById('diagnosis-input').value = settings.diagnosis || '';
  document.getElementById('patient-name-pill').textContent = settings.patient || 'Paciente';
  document.getElementById('profile-name').textContent = settings.patient || 'Paciente';
  document.getElementById('notif-med').classList.toggle('on', settings.notif_med !== false);
  document.getElementById('notif-cons').classList.toggle('on', settings.notif_cons !== false);
  const notifExamEl = document.getElementById('notif-exam');
  if (notifExamEl) notifExamEl.classList.toggle('on', settings.notif_exam !== false);
  document.getElementById('notif-fisio').classList.toggle('on', settings.notif_fisio === true);
  document.getElementById('task-date').value = todayStr();
  loadProfile();
  const evDate = document.getElementById('event-date');
  if (evDate && !evDate.value) evDate.value = todayStr();
}

// ── Convênio / SUS ────────────────────────────────────────────────────────

function switchInsurance(type) {
  const isSus = type === 'sus';
  document.getElementById('ins-sus-fields').style.display  = isSus ? 'block' : 'none';
  document.getElementById('ins-conv-fields').style.display = isSus ? 'none'  : 'block';

  const susBt  = document.getElementById('ins-btn-sus');
  const convBt = document.getElementById('ins-btn-conv');
  susBt.style.borderColor  = isSus ? 'var(--teal-400)'   : 'var(--gray-200)';
  susBt.style.background   = isSus ? 'var(--teal-50)'    : 'var(--gray-50)';
  susBt.style.color        = isSus ? 'var(--teal-600)'   : 'var(--text-muted)';
  convBt.style.borderColor = isSus ? 'var(--gray-200)'   : 'var(--purple-400)';
  convBt.style.background  = isSus ? 'var(--gray-50)'    : 'var(--purple-50)';
  convBt.style.color       = isSus ? 'var(--text-muted)' : 'var(--purple-600)';

  const p = getProfile();
  p.insuranceType = type;
  localStorage.setItem('cb_medical_profile', JSON.stringify({...p, ...collectInsuranceFields()}));
}

function collectInsuranceFields() {
  return {
    insuranceType: document.getElementById('ins-sus-fields')?.style.display !== 'none' ? 'sus' : 'conv',
    susNumber:   document.getElementById('sus-number')?.value   || '',
    convName:    document.getElementById('conv-name')?.value    || '',
    convNumber:  document.getElementById('conv-number')?.value  || '',
    convExpiry:  document.getElementById('conv-expiry')?.value  || '',
    convPlan:    document.getElementById('conv-plan')?.value    || '',
  };
}

function triggerInsPhoto(kind) {
  document.getElementById(`${kind}-photo-input`).click();
}

function handleInsPhoto(event, kind) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    const data = e.target.result;
    // store in profile
    const p = getProfile();
    p[`${kind}Photo`] = data;
    localStorage.setItem('cb_medical_profile', JSON.stringify(p));
    // update UI
    const img = document.getElementById(`${kind}-photo-img`);
    const ph  = document.getElementById(`${kind}-photo-placeholder`);
    const rm  = document.getElementById(`${kind}-photo-remove`);
    img.src = data; img.style.display = 'block';
    ph.style.display = 'none'; rm.style.display = 'flex';
    showToast('📷 Foto salva!');
    if (typeof haptic === 'function') haptic([20, 40]);
  };
  reader.readAsDataURL(file);
  event.target.value = '';
}

function removeInsPhoto(kind) {
  const p = getProfile();
  delete p[`${kind}Photo`];
  localStorage.setItem('cb_medical_profile', JSON.stringify(p));
  const img = document.getElementById(`${kind}-photo-img`);
  const ph  = document.getElementById(`${kind}-photo-placeholder`);
  const rm  = document.getElementById(`${kind}-photo-remove`);
  img.src = ''; img.style.display = 'none';
  ph.style.display = 'flex'; rm.style.display = 'none';
  showToast('🗑️ Foto removida');
}

function loadInsuranceFields(p) {
  const type = p.insuranceType || 'sus';
  switchInsurance(type);

  const set = (id, val) => { const el = document.getElementById(id); if (el) el.value = val || ''; };
  set('sus-number',  p.susNumber);
  set('conv-name',   p.convName);
  set('conv-number', p.convNumber);
  set('conv-expiry', p.convExpiry);
  set('conv-plan',   p.convPlan);

  // Restore photos
  ['sus','conv'].forEach(kind => {
    const img = document.getElementById(`${kind}-photo-img`);
    const ph  = document.getElementById(`${kind}-photo-placeholder`);
    const rm  = document.getElementById(`${kind}-photo-remove`);
    if (p[`${kind}Photo`] && img) {
      img.src = p[`${kind}Photo`]; img.style.display = 'block';
      ph.style.display = 'none'; rm.style.display = 'flex';
    }
  });

  // Convênio expiry warning
  if (p.convExpiry && type === 'conv') {
    const today = new Date(todayStr() + 'T00:00:00');
    const exp = new Date(p.convExpiry + 'T00:00:00');
    const days = Math.round((exp - today) / 86400000);
    if (days < 0) showToast('⚠️ Carteirinha do convênio vencida!');
    else if (days <= 30) showToast(`⚠️ Carteirinha vence em ${days} dias`);
  }
}

function getProfile() {
  try { return JSON.parse(localStorage.getItem('cb_medical_profile') || '{}'); } catch(e) { return {}; }
}

function saveProfile() {
  const p = {
    birthday:    document.getElementById('patient-birthday')?.value   || '',
    sex:         document.getElementById('patient-sex')?.value        || '',
    conditions:  document.getElementById('patient-conditions')?.value || '',
    emergName:   document.getElementById('emerg-name')?.value         || '',
    emergRel:    document.getElementById('emerg-rel')?.value          || '',
    emergPhone:  document.getElementById('emerg-phone')?.value        || '',
    allergyMeds: document.getElementById('allergy-meds')?.value       || '',
    allergyFood: document.getElementById('allergy-food')?.value       || '',
    allergyOther:document.getElementById('allergy-other')?.value      || '',
    surgeries:   document.getElementById('patient-surgeries')?.value  || '',
    smoking: document.querySelector('input[name="smoking"]:checked')?.value || 'no',
    ...collectInsuranceFields(),
    // preserve photos already stored
    susPhoto:  getProfile().susPhoto  || '',
    convPhoto: getProfile().convPhoto || '',
  };
  localStorage.setItem('cb_medical_profile', JSON.stringify(p));
  renderEmergCard(p);
  updateAgeLabel(p.birthday);
}

function loadProfile() {
  const p = getProfile();
  const set = (id, val) => { const el = document.getElementById(id); if (el) el.value = val || ''; };
  set('patient-birthday', p.birthday);
  set('patient-sex', p.sex);
  set('patient-conditions', p.conditions);
  set('patient-important-notes', p.importantNotes);
  set('patient-blood', p.blood);
  set('patient-weight', p.weight);
  set('patient-height', p.height);
  set('patient-main-doctor', p.mainDoctor);
  set('emerg-name', p.emergName);
  set('emerg-rel', p.emergRel);
  set('emerg-phone', p.emergPhone);
  set('allergy-meds', p.allergyMeds);
  set('allergy-food', p.allergyFood);
  set('allergy-other', p.allergyOther);
  set('patient-surgeries', p.surgeries);
  const smokeEl = document.getElementById(`smoke-${p.smoking || 'no'}`);
  if (smokeEl) smokeEl.checked = true;
  loadInsuranceFields(p);
  renderEmergCard(p);
  updateAgeLabel(p.birthday);
  renderHistTab('cons');
}

function calcAge(birthday) {
  if (!birthday) return null;
  const birth = new Date(birthday + 'T00:00:00');
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const m = today.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
  return age;
}

function updateAgeLabel(birthday) {
  const el = document.getElementById('profile-age-label');
  if (!el) return;
  if (!birthday) { el.textContent = 'Paciente'; return; }
  const age = calcAge(birthday);
  const birth = new Date(birthday + 'T00:00:00');
  const dateStr = birth.toLocaleDateString('pt-BR', {day:'numeric', month:'long'});
  el.textContent = `${age} anos · 🎂 ${dateStr}`;
}

function renderEmergCard(p) {
  const el = document.getElementById('emerg-card-display');
  if (!el) return;
  if (!p.emergName && !p.emergPhone) { el.style.display = 'none'; return; }
  const smokeLabel = {no:'🚭 Não fumante', ex:'🕐 Ex-fumante', yes:'🚬 Fumante'}[p.smoking||'no'];
  const tags = [];
  if (p.smoking && p.smoking !== 'no') tags.push(`<span class="emerg-tag">${smokeLabel}</span>`);
  if (p.allergyMeds)  tags.push(`<span class="emerg-tag danger">⚠️ Alérgico: ${p.allergyMeds}</span>`);
  if (p.allergyFood)  tags.push(`<span class="emerg-tag">🍽️ ${p.allergyFood}</span>`);
  if (p.allergyOther) tags.push(`<span class="emerg-tag">⚗️ ${p.allergyOther}</span>`);
  if (p.blood) tags.push(`<span class="emerg-tag">🩸 ${p.blood}</span>`);
  if (p.importantNotes) tags.push(`<span class="emerg-tag danger">📌 Obs. crítica</span>`);
  const insuranceLine = (() => {
    if (p.insuranceType === 'conv' && p.convName)
      return `<span class="emerg-tag">💳 ${p.convName}${p.convNumber ? ' · '+p.convNumber : ''}</span>`;
    if (p.susNumber)
      return `<span class="emerg-tag">🆓 SUS · ${p.susNumber}</span>`;
    return `<span class="emerg-tag">🆓 SUS</span>`;
  })();
  tags.push(insuranceLine);
  el.style.display = 'block';
  el.innerHTML = `<div class="emerg-card">
    <div class="emerg-card-title">🆘 Contato de emergência</div>
    <div class="emerg-contact-row">
      <div class="emerg-contact-info">
        <div class="emerg-contact-name">${p.emergName || '—'}</div>
        <div class="emerg-contact-rel">${p.emergRel || ''}</div>
        <div class="emerg-contact-phone">${p.emergPhone || ''}</div>
      </div>
      ${p.emergPhone ? `<button class="btn-call" onclick="callEmergency()" title="Ligar agora">📞</button>` : ''}
    </div>
    ${tags.length ? `<div class="emerg-tags">${tags.join('')}</div>` : ''}
  </div>`;
}

function callEmergency() {
  const p = getProfile();
  const phone = p.emergPhone || document.getElementById('emerg-phone')?.value;
  if (!phone) { showToast('⚠️ Nenhum telefone cadastrado'); return; }
  const clean = phone.replace(/\D/g, '');
  haptic([40, 60, 40]);
  window.location.href = `tel:${clean}`;
}

// ── Histórico de atendimentos ─────────────────────────────────────────────
let currentHistTab = 'cons';

function switchHistTab(type, btn) {
  currentHistTab = type;
  document.querySelectorAll('#hist-tab-cons,#hist-tab-exam,#hist-tab-fisio')
    .forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderHistTab(type);
}

function renderHistTab(type) {
  const el = document.getElementById('hist-list');
  if (!el) return;
  const todayS = todayStr();
  const icons  = { cons:'🩺', exam:'🔬', fisio:'🦾' };
  const past = tasks
    .filter(t => t.type === type && t.date && t.date < todayS && completions[`${t.id}_${t.date}`])
    .sort((a,b) => b.date.localeCompare(a.date))
    .slice(0, 20);

  if (!past.length) {
    el.innerHTML = `<div class="hist-empty">Nenhum registro anterior encontrado.</div>`;
    return;
  }
  el.innerHTML = past.map(t => {
    const dateStr = new Date(t.date+'T00:00:00').toLocaleDateString('pt-BR',{day:'numeric',month:'short',year:'numeric'});
    const sub = [t.doctor||t.examDoctor, t.local, t.examType].filter(Boolean).join(' · ');
    const photos = t.resultPhotos || [];
    const thumbs = type === 'exam' && photos.length
      ? `<div style="display:flex;gap:5px;margin-top:6px;flex-wrap:wrap">
          ${photos.map((p,i) => `<img src="${p.photoData}" style="width:44px;height:44px;border-radius:7px;object-fit:cover;border:1.5px solid var(--blue-100);cursor:pointer" onclick="openResultViewer('${t.id}',${i})">`).join('')}
        </div>` : '';
    const noResultBadge = type === 'exam' && !photos.length
      ? `<span style="font-size:10px;font-weight:700;color:var(--amber-600);background:var(--amber-50);padding:2px 6px;border-radius:5px;margin-top:4px;display:inline-block">📷 Sem resultado</span>` : '';
    return `<div class="hist-item">
      <div class="hist-icon ${type}">${icons[type]||'📋'}</div>
      <div class="hist-body">
        <div class="hist-name">${t.name}</div>
        ${sub ? `<div class="hist-meta">${sub}</div>` : ''}
        <div class="hist-meta">📅 ${dateStr}</div>
        ${thumbs}${noResultBadge}
      </div>
    </div>`;
  }).join('');
}

function saveSettings() {
  settings.patient = document.getElementById('patient-name-input').value;
  settings.caregiver = document.getElementById('caregiver-input').value;
  settings.diagnosis = document.getElementById('diagnosis-input').value;
  localStorage.setItem('cuidarbem_settings', JSON.stringify(settings));
}

function updatePatientName(v) {
  document.getElementById('patient-name-pill').textContent = v || 'Paciente';
  document.getElementById('profile-name').textContent = v || 'Paciente';
  settings.patient = v; saveSettings();
}

function saveTasks() {
  localStorage.setItem('cuidarbem_tasks', JSON.stringify(tasks));
}

function isDemoTask(t) {
  if (!t) return false;
  const demoNames = [
    'Losartana 50mg','AAS 100mg','Clopidogrel 75mg','Atorvastatina 40mg',
    'Fisioterapia motora','Exercícios de equilíbrio','Consulta com neurologista'
  ];
  return t.demo === true || demoNames.includes(t.name);
}

function removeCompletionsForTaskIds(ids) {
  const idSet = new Set(ids);
  Object.keys(completions || {}).forEach(k => {
    const id = k.split('_')[0];
    if (idSet.has(id)) delete completions[k];
  });
  localStorage.setItem('cuidarbem_completions', JSON.stringify(completions));
}

function clearDemoMedications() {
  const removeIds = tasks.filter(t => isDemoTask(t) && t.type === 'med').map(t => t.id);
  if (!removeIds.length) { showToast('✅ Nenhum remédio demo encontrado'); return; }
  if (!confirm('Remover os remédios demonstrativos da tela inicial?')) return;
  tasks = tasks.filter(t => !(isDemoTask(t) && t.type === 'med'));
  removeCompletionsForTaskIds(removeIds);
  saveTasks();
  renderAll(); buildWeekStrip();
  if (typeof scheduleAlarmsOnSW === 'function') scheduleAlarmsOnSW();
  if (typeof window.cbSupabaseQueuePush === 'function') window.cbSupabaseQueuePush('clear-demo-meds');
  showToast('🧹 Remédios demo removidos');
}

function clearDemoTodayTasks() {
  const removeIds = tasks.filter(t => isDemoTask(t)).map(t => t.id);
  if (!removeIds.length) { showToast('✅ Nenhuma tarefa demo encontrada'); return; }
  if (!confirm('Remover remédios, exercícios, fisioterapia e consulta demonstrativos?')) return;
  tasks = tasks.filter(t => !isDemoTask(t));
  removeCompletionsForTaskIds(removeIds);
  saveTasks();
  renderAll(); buildWeekStrip();
  if (typeof scheduleAlarmsOnSW === 'function') scheduleAlarmsOnSW();
  if (typeof window.cbSupabaseQueuePush === 'function') window.cbSupabaseQueuePush('clear-demo-tasks');
  showToast('🧹 Tarefas demo removidas');
}

function clearAllCareData() {
  if (!confirm('Zerar todos os cuidados cadastrados, confirmações, eventos e sinais vitais? A família/Supabase continuará configurada.')) return;
  tasks = []; completions = {};
  localStorage.setItem('cuidarbem_tasks', '[]');
  localStorage.setItem('cuidarbem_completions', '{}');
  localStorage.setItem('cb_care_events', '[]');
  localStorage.setItem('cb_vitals', '[]');
  localStorage.setItem('cb_vital_freq', '{}');
  try { careEvents = []; } catch(e) {}
  renderAll(); buildWeekStrip();
  if (typeof scheduleAlarmsOnSW === 'function') scheduleAlarmsOnSW();
  if (typeof window.cbSupabaseQueuePush === 'function') window.cbSupabaseQueuePush('clear-all-care-data');
  showToast('🧹 Cuidados zerados');
}

// ─── RENDER ALL ───────────────────────────────────────────────────────────
function renderAll() {
  renderTodayTasks();
  renderProgress();
  renderAlerts();
  renderNextAlarm();
  renderCaregiverSummary();
  renderCareEvents();
  renderCalendar();
  renderReports();
}


function shouldShowToday(task) {
  const today = todayStr();
  if (!task) return false;
  if (task.date === today) return true;
  if (task.repeat === 'daily') return true;
  if (task.repeat === 'weekly' && task.date) {
    const base = new Date(task.date + 'T00:00:00');
    const now  = new Date(today + 'T00:00:00');
    return base.getDay() === now.getDay();
  }
  return false;
}

function getTodayTasks() {
  return tasks.filter(t => shouldShowToday(t));
}

function isCompletedToday(task) {
  const key = `${task.id}_${todayStr()}`;
  return completions[key] === true;
}

function renderTodayTasks() {
  const list = document.getElementById('today-tasks-list');
  let items = getTodayTasks();
  if (currentFilter !== 'all') items = items.filter(t => t.type === currentFilter);
  items.sort((a,b) => (a.time||'99:99').localeCompare(b.time||'99:99'));

  if (!items.length) {
    list.innerHTML = `<div class="empty-state"><div class="empty-icon">🌿</div><p>Nenhuma tarefa${currentFilter!=='all'?' nessa categoria':' hoje'}.<br>Toque em <strong>+</strong> para adicionar!</p></div>`;
    return;
  }

  list.innerHTML = items.map(t => {
    const done = isCompletedToday(t);
    const badgeClass = {med:'badge-med',cons:'badge-cons',exam:'badge-exam',fisio:'badge-fisio',exer:'badge-exer'}[t.type]||'';
    const badgeLabel = {med:'💊 Remédio',cons:'🩺 Consulta',exam:'🔬 Exame',fisio:'🦾 Fisio',exer:'🏃 Exercício'}[t.type]||'';
    const isMed  = t.type === 'med';
    const isAppt = t.type === 'cons' || t.type === 'exam';

    // Render appointment/exam as rich card
    if (isAppt) {
      const seen = isCompletedToday(t);
      const isExam = t.type === 'exam';
      const accentColor = isExam ? 'var(--blue-400)' : 'var(--purple-400)';
      const bgColor     = isExam ? 'var(--blue-50)'  : 'var(--purple-50)';
      const icon        = isExam ? '🔬' : '🩺';
      const alertBadges = [];
      if (t.alertMorning) alertBadges.push('🌅 Manhã do dia');
      if (t.alertBefore)  alertBadges.push('⏰ 1h antes');
      const dateStr = t.date ? new Date(t.date+'T00:00:00').toLocaleDateString('pt-BR',{weekday:'short',day:'numeric',month:'short'}) : '';
      return `<div style="background:var(--card-bg);border-radius:var(--radius);margin-bottom:10px;box-shadow:var(--shadow);overflow:hidden">
        <div style="padding:14px 16px 10px;border-left:5px solid ${accentColor};display:flex;align-items:flex-start;gap:12px">
          <div style="width:44px;height:44px;border-radius:12px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:20px;background:${bgColor}">${icon}</div>
          <div style="flex:1;min-width:0">
            <div style="font-size:15px;font-weight:800;color:${seen?'var(--text-light)':'var(--text)'};${seen?'text-decoration:line-through':''}">
              ${t.name}
            </div>
            ${t.local ? `<div style="font-size:12px;color:var(--text-light);margin-top:2px">🏥 ${t.local}</div>` : ''}
            ${t.doctor ? `<div style="font-size:12px;color:var(--text-light)">👨‍⚕️ ${t.doctor}</div>` : ''}
            <div style="font-size:12px;color:var(--text-light);margin-top:2px">📅 ${dateStr} ${t.time ? '· 🕐 '+t.time : ''}</div>
            ${alertBadges.length ? `<div style="display:flex;gap:6px;margin-top:6px;flex-wrap:wrap">${alertBadges.map(a=>`<span style="padding:2px 8px;border-radius:8px;font-size:11px;font-weight:700;background:var(--coral-50);color:var(--coral-600)">${a}</span>`).join('')}</div>` : ''}
          </div>
          <div style="flex-shrink:0">
            <div class="task-check ${seen?'checked':''}" style="border-color:${accentColor.replace('--','var(--')}" onclick="openSeenModal('${t.id}')"></div>
          </div>
        </div>
        ${t.prep ? `<div style="padding:8px 16px;background:var(--amber-50);border-top:1px solid var(--amber-100);font-size:12px;color:var(--amber-600);font-weight:600">⚠️ Preparo: ${t.prep}</div>` : ''}
        ${t.photo ? `<img src="${t.photo}" style="width:100%;max-height:120px;object-fit:cover;border-top:1px solid var(--gray-100);display:block;cursor:pointer" onclick="openPhotoModal('${t.id}')">` : ''}
      </div>`;
    }
    const photoHtml = isMed ? `
      <div class="med-photo-wrap" onclick="event.stopPropagation();${t.photo ? `openPhotoModal('${t.id}')` : `addPhotoToTask('${t.id}')`}" style="width:46px;height:46px;border-radius:10px;margin-right:4px;flex-shrink:0">
        ${t.photo
          ? `<img src="${t.photo}" style="width:100%;height:100%;object-fit:cover">`
          : `<div class="med-photo-placeholder" style="font-size:18px">💊</div><div class="photo-add-badge" style="font-size:10px">+</div>`
        }
      </div>` : '';
    const checkClick = isMed && !done
      ? `openConfirmModal('${t.id}')`
      : `toggleTask('${t.id}')`;
    const proofBadge = (done && t.proofPhotos && t.proofPhotos[todayStr()])
      ? `<div onclick="event.stopPropagation();openProofPhotoModal('${t.id}')" title="Ver comprovante" style="cursor:pointer;display:inline-flex;align-items:center;gap:3px;margin-top:4px;padding:2px 8px;background:var(--teal-50);border-radius:8px;font-size:11px;font-weight:700;color:var(--teal-600)">📷 Comprovante</div>`
      : '';
    // Prescription / pickup alert pills
    const st = getMedStatus(t);
    let alertPills = '';
    if (isMed) {
      if (st.rxExpired) alertPills += `<span class="med-alert-pill alert" onclick="event.stopPropagation();openMedInfo('${t.id}')">📄 Receita vencida</span>`;
      else if (st.rxDays !== null && st.rxDays <= 14) alertPills += `<span class="med-alert-pill warn" onclick="event.stopPropagation();openMedInfo('${t.id}')">📄 Receita: ${st.rxDays}d</span>`;
      if (st.pickupDays !== null && st.pickupDays <= 5) alertPills += `<span class="med-alert-pill ${st.pickupDays <= 0 ? 'alert' : 'warn'}" onclick="event.stopPropagation();openMedInfo('${t.id}')">🏥 Retirar: ${st.pickupDays <= 0 ? 'hoje!' : st.pickupDays + 'd'}</span>`;
    }
    // Exam result badge
    if (t.type === 'exam') {
      const rs = getExamResultStatus(t);
      if (rs) alertPills += `<span class="result-badge ${rs.kind}" onclick="event.stopPropagation();openSeenModal('${t.id}')">${rs.label}</span>`;
    }

    // Determine late status for pending meds
    let medItemClass = '';
    let medNameClass = '';
    let lateBadge    = '';
    if (isMed && !done) {
      const now = new Date();
      const isLate = t.time && (() => {
        const [h, m] = t.time.split(':').map(Number);
        const tt = new Date(); tt.setHours(h, m, 0, 0);
        return now > tt;
      })();
      if (isLate) {
        medItemClass = 'task-item-med-late';
        medNameClass = 'task-name-blink';
        const minsLate = Math.floor((now - (() => { const tt = new Date(); const [h,m] = t.time.split(':').map(Number); tt.setHours(h,m,0,0); return tt; })()) / 60000);
        const lateStr = minsLate < 60 ? `${minsLate}min` : `${Math.floor(minsLate/60)}h${minsLate%60?String(minsLate%60).padStart(2,'0')+'min':''}`;
        lateBadge = `<span class="med-late-badge">⏰ Atrasado ${lateStr}</span>`;
      } else {
        medItemClass = 'task-item-med-pending';
      }
    }

    const isLateUndone = isMed && !done && medItemClass === 'task-item-med-late';
    const quickTakeBtn = isLateUndone
      ? `<button class="btn-quick-take" id="qt-${t.id}" onclick="event.stopPropagation();quickTake('${t.id}',this)">
           <span style="font-size:16px">💊</span> Tomar agora mesmo
         </button>`
      : '';

    return `<div class="task-item ${isMed ? 'task-item-med' : ''} ${medItemClass}" data-type="${t.type}" id="task-card-${t.id}">
      <div class="task-check ${done?'checked':''}" onclick="${checkClick}"></div>
      ${photoHtml}
      <div class="task-body" style="flex:1;min-width:0${isMed?';cursor:pointer':''}">
        <div ${isMed?`onclick="openMedInfo('${t.id}')"`:''}>
          <div class="task-name ${done?'done':''} ${medNameClass}">${t.name}${t.dose ? ` — ${t.dose}` : ''}</div>
          ${t.obs ? `<div class="task-meta">${t.obs}</div>` : ''}
          <span class="task-badge ${badgeClass}">${badgeLabel}</span>
          ${lateBadge}${proofBadge}${alertPills}
        </div>
        ${quickTakeBtn}
      </div>
      <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;flex-shrink:0">
        <div class="task-time" style="${medNameClass?'color:#c0192d;font-weight:900':''}">${t.time||''}</div>
        ${isMed ? `<button class="med-info-btn" onclick="event.stopPropagation();openMedInfo('${t.id}')" title="Ver detalhes do remédio">ℹ</button>` : ''}
      </div>
    </div>`;
  }).join('');
}

function renderProgress() {
  const items = getTodayTasks();
  const total = items.length;
  const done  = items.filter(t => isCompletedToday(t)).length;
  const pct   = total ? Math.round(done/total*100) : 0;
  const circumference = 201;
  const offset = circumference - (pct/100)*circumference;
  // Update both desktop (right panel) and mobile rings
  ['ring-fill','ring-fill-mobile'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.strokeDashoffset = offset;
  });
  ['pct-text','pct-text-mobile'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = pct + '%';
  });
  ['count-text','count-text-mobile'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = `${done} de ${total} tarefas`;
  });
}

function renderAlerts() {
  const container = document.getElementById('alerts-container');
  const items = getTodayTasks();
  const late = items.filter(t => {
    if (isCompletedToday(t) || !t.time) return false;
    const [h,m] = t.time.split(':').map(Number);
    const now = new Date();
    const taskTime = new Date(); taskTime.setHours(h,m,0);
    return now > taskTime;
  });
  if (!late.length) { container.innerHTML=''; }
  else {
    container.innerHTML = late.map(t =>
      `<div class="alert-card"><div class="alert-icon">⚠️</div><div class="alert-text">Pendente: <strong>${t.name}</strong> — previsto às ${t.time}</div></div>`
    ).join('');
  }

  // Alertas de receita e retirada
  const medAlerts = [];
  tasks.filter(t => t.type === 'med').forEach(t => {
    const st = getMedStatus(t);
    if (st.rxExpired) {
      medAlerts.push(`<div class="alert-card" style="cursor:pointer;border-left-color:var(--coral-400)" onclick="openMedInfo('${t.id}')"><div class="alert-icon">📄</div><div class="alert-text"><strong>${t.name}</strong> — Receita <strong style="color:var(--coral-600)">vencida!</strong> Renove com urgência.</div></div>`);
    } else if (st.rxDays !== null && st.rxDays <= 14) {
      medAlerts.push(`<div class="alert-card" style="cursor:pointer" onclick="openMedInfo('${t.id}')"><div class="alert-icon">📄</div><div class="alert-text"><strong>${t.name}</strong> — Receita vence em <strong>${st.rxDays} dia${st.rxDays!==1?'s':''}</strong>. Agende renovação.</div></div>`);
    }
    if (st.pickupDays !== null && st.pickupDays <= 5) {
      const urgText = st.pickupDays <= 0 ? 'hoje ou já passou!' : `em ${st.pickupDays} dia${st.pickupDays!==1?'s':''}`;
      medAlerts.push(`<div class="alert-card" style="cursor:pointer;border-left-color:var(--amber-400)" onclick="openMedInfo('${t.id}')"><div class="alert-icon">🏥</div><div class="alert-text"><strong>${t.name}</strong> — Retirar <strong>${urgText}</strong></div></div>`);
    }
  });
  if (medAlerts.length) container.innerHTML += medAlerts.join('');

  // Alertas de resultado de exame pendente
  const todayS = todayStr();
  const examResultAlerts = [];
  tasks.filter(t => t.type === 'exam' && t.date < todayS && completions[`${t.id}_${t.date}`]).forEach(t => {
    const rs = getExamResultStatus(t);
    if (!rs || rs.kind === 'has') return;
    const color = rs.kind === 'overdue' ? 'var(--coral-400)' : 'var(--amber-400)';
    examResultAlerts.push(`<div class="alert-card" style="cursor:pointer;border-left-color:${color}" onclick="openSeenModal('${t.id}')">
      <div class="alert-icon">🗂️</div>
      <div class="alert-text"><strong>${t.name}</strong> — ${rs.label.replace(/^[^\s]+ /,'')}. Toque para fotografar.</div>
    </div>`);
  });
  if (examResultAlerts.length) container.innerHTML += examResultAlerts.join('');
  if (typeof updateAlertsBell === 'function') updateAlertsBell();
}


function renderNextAlarm() {
  const card = document.getElementById('next-alarm-card');
  const items = getTodayTasks().filter(t => !isCompletedToday(t) && t.time);
  const now = new Date();
  const upcoming = items.filter(t => {
    const [h,m] = t.time.split(':').map(Number);
    const taskTime = new Date(); taskTime.setHours(h,m,0);
    return taskTime > now;
  }).sort((a,b)=>a.time.localeCompare(b.time));

  if (!upcoming.length) { card.style.display='none'; return; }
  card.style.display = 'flex';
  document.getElementById('next-alarm-time').textContent = upcoming[0].time;
  document.getElementById('next-alarm-desc').textContent = upcoming[0].name;
}

// ─── TOGGLE TASK ──────────────────────────────────────────────────────────
function toggleTask(id) {
  const key = `${id}_${todayStr()}`;
  if (completions[key]) {
    delete completions[key];
  } else {
    completions[key] = true;
    showToast('✅ Tarefa concluída!');
  }
  localStorage.setItem('cuidarbem_completions', JSON.stringify(completions));
  renderAll();
  if (typeof scheduleAlarmsOnSW === 'function') scheduleAlarmsOnSW();
}

// ─── FILTER ───────────────────────────────────────────────────────────────
function filterTasks(type, btn) {
  currentFilter = type;
  document.querySelectorAll('.cat-pill').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderTodayTasks();
}

// ─── CALENDAR ─────────────────────────────────────────────────────────────
function buildWeekStrip() {
  const strip = document.getElementById('week-strip');
  const today = new Date();
  const days = ['Dom','Seg','Ter','Qua','Qui','Sex','Sáb'];
  let html = '';
  for (let i=-3; i<=3; i++) {
    const d = new Date(today); d.setDate(today.getDate()+i);
    const ds = d.toISOString().split('T')[0];
    const isToday = i===0;
    const hasTasks = tasks.some(t => t.date===ds || (t.repeat==='daily'));
    html += `<div class="week-day ${isToday?'today':''} ${hasTasks?'has-tasks':''}" onclick="selectDay('${ds}',this)">
      <div class="week-day-name">${days[d.getDay()]}</div>
      <div class="week-day-num">${d.getDate()}</div>
    </div>`;
  }
  strip.innerHTML = html;
  selectedCalDay = todayStr();
}

function selectDay(ds, el) {
  selectedCalDay = ds;
  document.querySelectorAll('.week-day').forEach(d => d.classList.remove('today'));
  el.classList.add('today');
  renderCalendar();
}

function calFilter(type, btn) {
  calFilter_ = type;
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  btn.classList.add('active');
  renderCalendar();
}

function renderCalendar() {
  const list = document.getElementById('cal-tasks-list');
  const day = selectedCalDay || todayStr();
  const dayDate = new Date(day + 'T00:00:00');
  let items = tasks.filter(t => {
    if (t.date === day) return true;
    if (t.repeat === 'daily') return true;
    if (t.repeat === 'weekly') {
      const base = new Date(t.date + 'T00:00:00');
      return base.getDay() === dayDate.getDay();
    }
    return false;
  });
  if (calFilter_ !== 'all') items = items.filter(t => t.type === calFilter_);
  items.sort((a,b)=>(a.time||'99').localeCompare(b.time||'99'));

  if (!items.length) {
    list.innerHTML = `<div class="card"><div class="empty-state"><div class="empty-icon">📅</div><p>Nenhuma tarefa neste dia.</p></div></div>`;
    return;
  }

  const badgeClass = {med:'badge-med',cons:'badge-cons',exam:'badge-exam',fisio:'badge-fisio',exer:'badge-exer'};
  const badgeLabel = {med:'💊 Remédio',cons:'🩺 Consulta',exam:'🔬 Exame',fisio:'🦾 Fisio',exer:'🏃 Exercício'};
  list.innerHTML = `<div class="card">${items.map(t => {
    const done = completions[`${t.id}_${day}`];
    const isMedCal = t.type === 'med';
    const checkClickCal = isMedCal && !done ? `openConfirmModal('${t.id}')` : `toggleTaskDay('${t.id}','${day}')`;
    const photoHtmlCal = isMedCal ? `
      <div class="med-photo-wrap" onclick="event.stopPropagation();${t.photo ? `openPhotoModal('${t.id}')` : `addPhotoToTask('${t.id}')`}" style="width:46px;height:46px;border-radius:10px;margin-right:4px;flex-shrink:0">
        ${t.photo ? `<img src="${t.photo}" style="width:100%;height:100%;object-fit:cover">` : `<div class="med-photo-placeholder" style="font-size:18px">💊</div><div class="photo-add-badge" style="font-size:10px">+</div>`}
      </div>` : '';
    return `<div class="task-item">
      <div class="task-check ${done?'checked':''}" onclick="${checkClickCal}"></div>
      ${photoHtmlCal}
      <div class="task-body">
        <div class="task-name ${done?'done':''}">${t.name}${t.dose?` — ${t.dose}`:''}</div>
        ${t.obs?`<div class="task-meta">${t.obs}</div>`:''}
        <span class="task-badge ${badgeClass[t.type]||''}">${badgeLabel[t.type]||''}</span>
      </div>
      <div class="task-time">${t.time||''}</div>
    </div>`;
  }).join('')}</div>`;
}

function toggleTaskDay(id, day) {
  const key = `${id}_${day}`;
  if (completions[key]) delete completions[key];
  else { completions[key]=true; showToast('✅ Concluído!'); }
  localStorage.setItem('cuidarbem_completions', JSON.stringify(completions));
  renderAll();
  if (typeof scheduleAlarmsOnSW === 'function') scheduleAlarmsOnSW();
}

// ─── REPORTS ──────────────────────────────────────────────────────────────
function renderReports() {
  const today = todayStr();
  const todayTasks = getTodayTasks();
  const medToday = todayTasks.filter(t=>t.type==='med').length;
  const doneToday = todayTasks.filter(t=>isCompletedToday(t)).length;

  // This week
  let weekTotal = 0;
  for (let i=0;i<7;i++) {
    const d = new Date(); d.setDate(d.getDate()-i);
    const ds = d.toISOString().split('T')[0];
    const dayTasks = tasks.filter(t => t.date===ds || t.repeat==='daily');
    weekTotal += dayTasks.filter(t => completions[`${t.id}_${ds}`]).length;
  }

  // Streak
  let streak = 0;
  for (let i=0;i<30;i++) {
    const d = new Date(); d.setDate(d.getDate()-i);
    const ds = d.toISOString().split('T')[0];
    const dayTasks = tasks.filter(t => t.date===ds || t.repeat==='daily');
    if (!dayTasks.length) continue;
    const done = dayTasks.filter(t=>completions[`${t.id}_${ds}`]).length;
    if (done > 0) streak++; else break;
  }

  document.getElementById('stat-med').textContent = medToday;
  document.getElementById('stat-done').textContent = doneToday;
  document.getElementById('stat-week').textContent = weekTotal;
  document.getElementById('stat-streak').textContent = streak;

  // Adherence
  const cats = [{k:'med',l:'💊 Remédios'},{k:'cons',l:'🩺 Consultas'},{k:'exam',l:'🔬 Exames'},{k:'fisio',l:'🦾 Fisioterapia'},{k:'exer',l:'🏃 Exercícios'}];
  const adList = document.getElementById('adherence-list');
  adList.innerHTML = cats.map(cat => {
    let total=0, done=0;
    for (let i=0;i<7;i++) {
      const d = new Date(); d.setDate(d.getDate()-i);
      const ds = d.toISOString().split('T')[0];
      const dayTasks = tasks.filter(t=>(t.date===ds||t.repeat==='daily'||t.repeat==='weekly')&&t.type===cat.k);
      total += dayTasks.length;
      done += dayTasks.filter(t=>completions[`${t.id}_${ds}`]).length;
    }
    const pct = total ? Math.round(done/total*100) : 0;
    const fillClass = pct>=80?'':pct>=50?'mid':'low';
    return `<div style="margin-bottom:14px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
        <span style="font-size:14px;font-weight:700">${cat.l}</span>
        <span style="font-size:13px;font-weight:700;color:var(--text-muted)">${pct}%</span>
      </div>
      <div class="adherence-bar"><div class="adherence-fill ${fillClass}" style="width:${pct}%"></div></div>
      <div style="font-size:11px;color:var(--text-light);margin-top:3px">${done} de ${total} nos últimos 7 dias</div>
    </div>`;
  }).join('');

  // History last 5 days
  const histList = document.getElementById('history-list');
  let histHtml = '';
  for (let i=0;i<5;i++) {
    const d = new Date(); d.setDate(d.getDate()-i);
    const ds = d.toISOString().split('T')[0];
    const label = i===0?'Hoje': i===1?'Ontem': d.toLocaleDateString('pt-BR',{weekday:'short',day:'numeric',month:'short'});
    const dayTasks = tasks.filter(t=>t.date===ds||t.repeat==='daily');
    if (!dayTasks.length) continue;
    const done = dayTasks.filter(t=>completions[`${t.id}_${ds}`]).length;
    const pct_ = Math.round(done/dayTasks.length*100);
    histHtml += `<div style="display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--gray-100)">
      <div>
        <div style="font-weight:700;font-size:14px">${label}</div>
        <div style="font-size:12px;color:var(--text-light)">${done}/${dayTasks.length} tarefas</div>
      </div>
      <div style="font-size:18px;font-weight:800;color:${pct_>=80?'var(--teal-600)':pct_>=50?'var(--amber-600)':'var(--coral-600)'}">${pct_}%</div>
    </div>`;
  }
  histList.innerHTML = histHtml || '<div class="empty-state"><p>Nenhum histórico ainda.</p></div>';
}

// ─── MODAL ────────────────────────────────────────────────────────────────
function openAddModal() {
  selectedType = '';
  currentTaskPhoto = null;
  document.getElementById('task-name').value = '';
  document.getElementById('task-dose').value = '';
  document.getElementById('task-time').value = '';
  document.getElementById('task-obs').value = '';
  document.getElementById('task-date').value = selectedCalDay || todayStr();
  document.getElementById('task-repeat').value = 'none';
  document.querySelectorAll('.type-opt').forEach(o=>o.classList.remove(...['sel-med','sel-cons','sel-fisio','sel-exer']));
  document.getElementById('field-dose').style.display='none';
  document.getElementById('field-photo').style.display='none';
  // Reset photo preview
  document.getElementById('task-photo-placeholder').style.display='flex';
  const prev = document.getElementById('task-photo-preview');
  prev.style.display='none'; prev.src='';
  document.getElementById('add-modal').classList.add('open');
}

function closeModal() { document.getElementById('add-modal').classList.remove('open'); }
function closeModalOut(e) { if (e.target.id==='add-modal') closeModal(); }

function selectType(type) {
  selectedType = type;
  document.querySelectorAll('.type-opt').forEach(o => o.classList.remove('sel-med','sel-cons','sel-fisio','sel-exer','sel-exam'));
  document.querySelector(`[data-type="${type}"]`).classList.add(`sel-${type}`);
  const isMed  = type === 'med';
  const isCons = type === 'cons';
  const isExam = type === 'exam';
  const isAppt = isCons || isExam;
  document.getElementById('field-dose').style.display       = isMed  ? 'block' : 'none';
  document.getElementById('field-photo').style.display      = isMed  ? 'block' : 'none';
  document.getElementById('field-med-extra').style.display  = isMed  ? 'block' : 'none';
  document.getElementById('field-appt-block').style.display = isAppt ? 'block' : 'none';
  if (isAppt) {
    document.getElementById('field-cons-only').style.display = isCons ? 'block' : 'none';
    document.getElementById('field-exam-only').style.display = isExam ? 'block' : 'none';
    document.getElementById('alert-eve-row').style.display   = isExam ? 'flex'  : 'none';
    document.getElementById('label-preparo').textContent     = isExam ? 'Preparo necessário (jejum, hidratação…)' : 'Preparo necessário';
  }
}

function saveTask() {
  const name = document.getElementById('task-name').value.trim();
  if (!selectedType) { showToast('⚠️ Selecione o tipo'); return; }
  if (!name) { showToast('⚠️ Digite o nome'); return; }
  const task = {
    id: uid(),
    type: selectedType,
    name,
    dose: document.getElementById('task-dose').value.trim(),
    date: document.getElementById('task-date').value || todayStr(),
    time: document.getElementById('task-time').value,
    repeat: document.getElementById('task-repeat').value,
    obs: document.getElementById('task-obs').value.trim(),
    photo: currentTaskPhoto || null,
    indication: document.getElementById('task-indication')?.value.trim() || '',
    continuous: document.getElementById('task-continuous')?.checked || false,
    treatmentEnd: document.getElementById('task-treatment-end')?.value || '',
    prescriptionExpiry: document.getElementById('task-rx-expiry')?.value || '',
    pickupSource: document.getElementById('task-pickup-source')?.value || '',
    pickupInterval: parseInt(document.getElementById('task-pickup-interval')?.value) || 0,
    nextPickup: document.getElementById('task-next-pickup')?.value || '',
    // Consulta fields
    doctor:      document.getElementById('task-doctor')?.value.trim()   || '',
    local:       document.getElementById('task-location')?.value.trim() || '',
    prep:        document.getElementById('task-preparo')?.value.trim()  || '',
    obs2:        document.getElementById('task-levar')?.value.trim()    || '',
    alertMorning: document.getElementById('alert-morning')?.checked ?? true,
    alertBefore:  document.getElementById('alert-1h')?.checked ?? true,
    // Exame-only fields
    examType:    document.getElementById('task-exam-type')?.value.trim()    || '',
    examDoctor:  document.getElementById('task-exam-doctor')?.value.trim()  || '',
    resultsDate: document.getElementById('task-results-date')?.value        || '',
    alertEve:    document.getElementById('alert-eve')?.checked ?? false,
    subtype: selectedType === 'exam' ? 'exam' : 'cons',
    createdAt: Date.now()
  };
  tasks.push(task);
  saveTasks();
  closeModal();
  showToast('✅ Tarefa salva!');
  renderAll();
  buildWeekStrip();
  if (Notification.permission === 'granted') setTimeout(scheduleAlarmsOnSW, 300);
}

// ─── NOTIFICATIONS ────────────────────────────────────────────────────────

// ── Service Worker externo para PWA, offline e alarmes ──
(function registerAlarmServiceWorker() {
  if (!('serviceWorker' in navigator)) return;
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js', { scope: './' })
      .then(reg => {
        window._swRegistration = reg;
        console.log('[CuidarBem] Service Worker registrado: sw.js');
      })
      .catch(err => console.warn('[CuidarBem] Falha ao registrar Service Worker', err));
  });
})();

function getTaskDateTimeToday(task) {
  if (!task || !task.time) return null;
  const [h, m] = task.time.split(':').map(Number);
  if (Number.isNaN(h) || Number.isNaN(m)) return null;
  const d = new Date();
  d.setHours(h, m, 0, 0);
  return d;
}

function getTaskAlertProfile(task) {
  const isCare = ['med','fisio','exer'].includes(task.type);
  const isAppt = ['cons','exam'].includes(task.type);
  return {
    enabled: isCare || isAppt,
    beforeMin: isCare ? 15 : (task.alertBefore ? 60 : 15),
    afterMin: isCare ? 15 : 0,
    repeatEveryMin: isCare ? 5 : 0,
    repeatForMin: task.type === 'med' ? 180 : (['fisio','exer'].includes(task.type) ? 90 : 0),
    requireInteraction: isCare
  };
}

function buildSmartAlarmPayload(task, fireAt, phase, minutesInfo) {
  const typeEmoji = {med:'💊',fisio:'🦾',exer:'🏃',cons:'🩺',exam:'🔬'}[task.type] || '🔔';
  const typeLabel = {med:'medicamento',fisio:'fisioterapia',exer:'exercício',cons:'consulta',exam:'exame'}[task.type] || 'cuidado';
  let title = `${typeEmoji} CuidarBem`;
  let body = '';
  if (phase === 'before') {
    title = `${typeEmoji} Em ${minutesInfo} min: ${task.name}`;
    body = `Prepare-se para o ${typeLabel} das ${task.time}. ${[task.dose, task.obs].filter(Boolean).join(' · ')}`.trim();
  } else if (phase === 'due') {
    title = `${typeEmoji} Hora de confirmar: ${task.name}`;
    body = `${task.time} · ${[task.dose, task.obs].filter(Boolean).join(' · ') || 'Toque para abrir e confirmar.'}`;
  } else {
    title = `⚠️ Ainda não confirmado: ${task.name}`;
    body = `Previsto às ${task.time}. Abra o CuidarBem e marque como tomado/feito.`;
  }
  return {
    taskId: task.id,
    fireAt,
    title,
    body,
    tag: `cb_${task.id}_${todayStr()}_${phase}_${fireAt}`,
    requireInteraction: !!getTaskAlertProfile(task).requireInteraction,
    renotify: phase !== 'before',
    phase
  };
}

function scheduleAlarmsOnSW() {
  if (!window._swRegistration || !window._swRegistration.active) return;
  const now = new Date();
  const alarms = [];

  getTodayTasks().forEach(t => {
    if (!t.time || isCompletedToday(t)) return;
    const base = getTaskDateTimeToday(t);
    if (!base) return;
    const profile = getTaskAlertProfile(t);
    if (!profile.enabled) return;

    const addAlarm = (dt, phase, minutesInfo) => {
      if (dt <= now) return;
      if (dt.getTime() - now.getTime() > 24 * 60 * 60 * 1000) return;
      alarms.push(buildSmartAlarmPayload(t, dt.getTime(), phase, minutesInfo));
    };

    if (profile.beforeMin > 0) {
      addAlarm(new Date(base.getTime() - profile.beforeMin * 60000), 'before', profile.beforeMin);
    }
    addAlarm(base, 'due', 0);

    if (profile.afterMin > 0) {
      addAlarm(new Date(base.getTime() + profile.afterMin * 60000), 'after', profile.afterMin);
      if (profile.repeatEveryMin > 0 && profile.repeatForMin > profile.afterMin) {
        for (let min = profile.afterMin + profile.repeatEveryMin; min <= profile.repeatForMin; min += profile.repeatEveryMin) {
          addAlarm(new Date(base.getTime() + min * 60000), 'repeat', min);
        }
      }
    }
  });

  window._swRegistration.active.postMessage({ type: 'SCHEDULE_ALARMS', alarms });
}

function requestNotifPermission() {
  if (!('Notification' in window)) return;
  if (Notification.permission === 'default') {
    Notification.requestPermission().then(perm => {
      if (perm === 'granted') {
        showToast('🔔 Alarmes de remédio ativados!');
        scheduleAlarmsOnSW();
      }
    });
  } else if (Notification.permission === 'granted') {
    setTimeout(scheduleAlarmsOnSW, 1500); // SW pode não estar pronto no load
  }
}

function setupNotifications() {
  setInterval(checkNotifications, 60000);
  // Reagendar no SW a cada 5 min (alarmes podem expirar)
  setInterval(() => {
    if (Notification.permission === 'granted') scheduleAlarmsOnSW();
  }, 5 * 60 * 1000);
  checkNotifications();
}

function notifyCareTask(task, title, body, key, requireInteraction = true) {
  if (sessionStorage.getItem(key)) return;
  sessionStorage.setItem(key, '1');
  try {
    new Notification(title, {
      body,
      icon: 'icon-192.png',
      badge: 'icon-192.png',
      tag: key,
      renotify: true,
      requireInteraction,
      vibrate: [200, 100, 200, 100, 200]
    });
  } catch(e) {
    new Notification(title, { body, icon: 'icon-192.png' });
  }
  if (typeof playAlertSound === 'function') playAlertSound();
}

function checkNotifications() {
  if (!('Notification' in window) || Notification.permission !== 'granted') return;
  const now = new Date();
  const today = todayStr();
  const hm = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;

  getTodayTasks().forEach(t => {
    if (!t.time || isCompletedToday(t)) return;
    const base = getTaskDateTimeToday(t);
    if (!base) return;
    const profile = getTaskAlertProfile(t);
    if (!profile.enabled) return;
    const diffMin = Math.floor((now.getTime() - base.getTime()) / 60000);
    const typeEmoji = {med:'💊',fisio:'🦾',exer:'🏃',cons:'🩺',exam:'🔬'}[t.type] || '🔔';

    if (diffMin === -profile.beforeMin) {
      notifyCareTask(
        t,
        `${typeEmoji} Em ${profile.beforeMin} min: ${t.name}`,
        `Previsto para ${t.time}. ${[t.dose, t.obs].filter(Boolean).join(' · ')}`,
        `notif_before_${t.id}_${today}_${profile.beforeMin}`,
        false
      );
    }

    if (diffMin === 0) {
      notifyCareTask(
        t,
        `${typeEmoji} Hora de confirmar: ${t.name}`,
        `${t.time} · ${[t.dose, t.obs].filter(Boolean).join(' · ') || 'Abra o app e confirme.'}`,
        `notif_due_${t.id}_${today}`,
        profile.requireInteraction
      );
    }

    if (profile.afterMin > 0 && diffMin >= profile.afterMin && diffMin <= profile.repeatForMin) {
      if (diffMin === profile.afterMin || (profile.repeatEveryMin > 0 && (diffMin - profile.afterMin) % profile.repeatEveryMin === 0)) {
        notifyCareTask(
          t,
          `⚠️ Ainda não confirmado: ${t.name}`,
          `Previsto às ${t.time}. Marque como tomado/feito para parar os alertas.`,
          `notif_after_${t.id}_${today}_${diffMin}`,
          true
        );
      }
    }
  });

  // Appointment alerts específicos mantidos para consulta/exame
  tasks.forEach(t => {
    if (t.type !== 'cons' && t.type !== 'exam') return;
    if (t.date !== today) return;

    if (t.alertMorning && hm === '07:00') {
      const key = `appt_morning_${t.id}_${today}`;
      notifyCareTask(t, '🩺 Lembrete de hoje', `${t.name}${t.time ? ' às ' + t.time : ''}${t.local ? ' — ' + t.local : ''}`, key, false);
    }
  });
}

// ─── SETTINGS ─────────────────────────────────────────────────────────────
function toggleSetting(btn) {
  btn.classList.toggle('on');
  const id = btn.id;
  if (id==='notif-med') settings.notif_med = btn.classList.contains('on');
  if (id==='notif-cons') settings.notif_cons = btn.classList.contains('on');
  if (id==='notif-exam') settings.notif_exam = btn.classList.contains('on');
  if (id==='notif-fisio') settings.notif_fisio = btn.classList.contains('on');
  saveSettings();
}

function exportData() {
  const today = todayStr();
  let txt = `CuidarBem — Relatório\n`;
  txt += `Paciente: ${settings.patient}\n`;
  txt += `Cuidador(a): ${settings.caregiver}\n`;
  txt += `Data: ${today}\n\n`;
  txt += `TAREFAS:\n`;
  tasks.forEach(t => {
    const done = completions[`${t.id}_${today}`] ? '✓' : '○';
    txt += `${done} [${t.type.toUpperCase()}] ${t.name}${t.dose?' ('+t.dose+')':''} — ${t.time||'sem hora'}\n`;
  });
  const blob = new Blob([txt], {type:'text/plain'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `cuidarbem_${today}.txt`;
  a.click();
  showToast('📤 Relatório exportado!');
}

function clearAll() {
  if (!confirm('Tem certeza? Todos os dados serão apagados.')) return;
  tasks=[]; completions={};
  localStorage.removeItem('cuidarbem_tasks');
  localStorage.removeItem('cuidarbem_completions');
  renderAll();
  showToast('🗑️ Dados apagados');
}

// ─── NAVIGATION ───────────────────────────────────────────────────────────
function goScreen(name, btn) {
  document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));
  document.getElementById(`screen-${name}`).classList.add('active');
  btn.classList.add('active');
  if (name==='reports') renderReports();
  if (name==='calendar') { buildWeekStrip(); renderCalendar(); }
  if (name==='appt') renderApptUpcoming();
  window.scrollTo(0,0);
}

// ─── TOAST ────────────────────────────────────────────────────────────────
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg; t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'), 2200);
}


// ─── PHOTO HANDLING ───────────────────────────────────────────────────────
function handleTaskPhoto(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    currentTaskPhoto = e.target.result;
    document.getElementById('task-photo-placeholder').style.display = 'none';
    const prev = document.getElementById('task-photo-preview');
    prev.src = e.target.result;
    prev.style.display = 'block';
  };
  reader.readAsDataURL(file);
  event.target.value = '';
}

function addPhotoToTask(taskId) {
  const input = document.createElement('input');
  input.type = 'file'; input.accept = 'image/*';
  input.onchange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const task = tasks.find(t => t.id === taskId);
      if (task) { task.photo = ev.target.result; saveTasks(); renderAll(); showToast('📷 Foto adicionada!'); }
    };
    reader.readAsDataURL(file);
  };
  input.click();
}

function openPhotoModal(taskId) {
  photoViewTaskId = taskId;
  const task = tasks.find(t => t.id === taskId);
  if (!task || !task.photo) return;
  document.getElementById('photo-view-img').src = task.photo;
  document.getElementById('photo-view-name').textContent = task.name;
  // Reset buttons to default state
  const modal = document.getElementById('photo-view-modal');
  const changeBtn = modal.querySelector('button[onclick="changeTaskPhoto()"]');
  const removeBtn = modal.querySelector('button[onclick^="removeTaskPhoto"],button[onclick*="removeTaskPhoto"]');
  if (changeBtn) changeBtn.style.display = '';
  if (removeBtn) {
    removeBtn.textContent = '🗑️ Remover';
    removeBtn.onclick = removeTaskPhoto;
  }
  modal.classList.add('open');
}

function closePhotoModal() {
  document.getElementById('photo-view-modal').classList.remove('open');
  photoViewTaskId = null;
}

function changeTaskPhoto() {
  document.getElementById('change-photo-input').click();
}

function handleChangePhoto(event) {
  const file = event.target.files[0];
  if (!file || !photoViewTaskId) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const task = tasks.find(t => t.id === photoViewTaskId);
    if (task) {
      task.photo = e.target.result;
      saveTasks(); renderAll();
      document.getElementById('photo-view-img').src = e.target.result;
      showToast('📷 Foto atualizada!');
    }
  };
  reader.readAsDataURL(file);
  event.target.value = '';
}

function removeTaskPhoto() {
  if (!photoViewTaskId) return;
  const task = tasks.find(t => t.id === photoViewTaskId);
  if (task) { task.photo = null; saveTasks(); renderAll(); }
  closePhotoModal();
  showToast('🗑️ Foto removida');
}

// ── Visualizador de comprovante fotográfico ──
function openProofPhotoModal(taskId) {
  const task = tasks.find(t => t.id === taskId);
  if (!task || !task.proofPhotos) return;
  const today = todayStr();
  const photo = task.proofPhotos[today];
  if (!photo) return;
  photoViewTaskId = taskId;
  document.getElementById('photo-view-img').src = photo;
  document.getElementById('photo-view-name').textContent = `Comprovante — ${task.name}`;
  // Hide the change/remove buttons for proof photos (they're linked to a date)
  const modal = document.getElementById('photo-view-modal');
  modal.querySelector('button[onclick="changeTaskPhoto()"]').style.display = 'none';
  modal.querySelector('button[onclick="removeTaskPhoto()"]').textContent = '🗑️ Remover comprovante';
  modal.querySelector('button[onclick="removeTaskPhoto()"]').onclick = () => {
    if (task.proofPhotos) { delete task.proofPhotos[today]; saveTasks(); renderAll(); }
    closePhotoModal();
    showToast('🗑️ Comprovante removido');
  };
  modal.classList.add('open');
}

// ─── CONFIRM MODAL ────────────────────────────────────────────────────────
let pendingProofPhoto = null;

function openConfirmModal(taskId) {
  const task = tasks.find(t => t.id === taskId);
  if (!task) return;
  pendingConfirmId = taskId;
  pendingProofPhoto = null;

  // Reset proof photo UI
  document.getElementById('proof-photo-preview-wrap').style.display = 'none';
  document.getElementById('proof-photo-preview').src = '';
  document.getElementById('proof-photo-add-btns').style.display = 'flex';

  // Photo
  const photoWrap = document.getElementById('confirm-photo-big-wrap');
  if (task.photo) {
    photoWrap.innerHTML = `<img src="${task.photo}" class="confirm-photo-big" alt="${task.name}">`;
  } else {
    photoWrap.innerHTML = `<div class="confirm-photo-placeholder">💊</div>`;
  }

  document.getElementById('confirm-name').textContent = task.name;
  document.getElementById('confirm-dose').textContent = task.dose || 'Conforme prescrição';

  const timeEl = document.getElementById('confirm-time');
  timeEl.textContent = task.time || 'Agora';

  // Obs
  const obsEl = document.getElementById('confirm-obs');
  if (task.obs) { obsEl.style.display='block'; obsEl.textContent = '⚠️ ' + task.obs; }
  else obsEl.style.display='none';

  // Warning if no photo
  const warnEl = document.getElementById('confirm-warning');
  if (!task.photo) {
    warnEl.style.display='block';
    warnEl.innerHTML = '📷 <strong>Dica:</strong> Adicione uma foto deste comprimido para facilitar a confirmação visual no futuro.';
  } else {
    warnEl.style.display='none';
  }

  document.getElementById('confirm-modal').classList.add('open');

  // ── Checklist de segurança ──────────────────────────────────────────────
  const checkItems = [
    { id: 'chk-name',  q: `O nome na embalagem é`, val: task.name || '—' },
    { id: 'chk-dose',  q: `A dose é`,              val: task.dose || '1 comprimido' },
    { id: 'chk-time',  q: `É o horário das`,       val: task.time || 'agora' }
  ];

  const listEl = document.getElementById('med-checklist-items');
  listEl.innerHTML = checkItems.map(item => `
    <div class="med-check-item" id="${item.id}-row">
      <div class="med-check-question">${item.q} <em>${item.val}</em>?</div>
      <div class="med-check-btns">
        <button class="med-check-btn" id="${item.id}-yes" onclick="medCheckAnswer('${item.id}','yes')" title="Sim">✅</button>
        <button class="med-check-btn" id="${item.id}-no"  onclick="medCheckAnswer('${item.id}','no')"  title="Não">❌</button>
      </div>
    </div>
  `).join('');

  // Reset alert and confirm button state
  document.getElementById('med-checklist-alert').classList.remove('show');
  document.getElementById('confirm-modal').querySelector('.btn-confirm').classList.remove('blocked');
  window._medCheckAnswers = {};
}

function closeConfirmModal() {
  document.getElementById('confirm-modal').classList.remove('open');
  pendingConfirmId = null;
  pendingProofPhoto = null;
  window._medCheckAnswers = {};
}

// ── Funções de comprovante fotográfico ──
function captureProofPhoto(source) {
  const input = document.getElementById('proof-photo-input');
  if (source === 'camera') {
    input.setAttribute('capture', 'environment');
  } else {
    input.removeAttribute('capture');
  }
  input.click();
}

function handleProofPhoto(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    pendingProofPhoto = e.target.result;
    document.getElementById('proof-photo-preview').src = e.target.result;
    document.getElementById('proof-photo-preview-wrap').style.display = 'block';
    document.getElementById('proof-photo-add-btns').style.display = 'none';
  };
  reader.readAsDataURL(file);
  event.target.value = '';
}

function removeProofPhoto() {
  pendingProofPhoto = null;
  document.getElementById('proof-photo-preview').src = '';
  document.getElementById('proof-photo-preview-wrap').style.display = 'none';
  document.getElementById('proof-photo-add-btns').style.display = 'flex';
}

// ─── MED INFO SHEET ──────────────────────────────────────────────────────

function getMedStatus(task) {
  const today = new Date(todayStr() + 'T00:00:00');
  const result = { rxDays: null, pickupDays: null, rxExpired: false };
  if (task.prescriptionExpiry) {
    const exp = new Date(task.prescriptionExpiry + 'T00:00:00');
    result.rxDays = Math.round((exp - today) / 86400000);
    result.rxExpired = result.rxDays < 0;
  }
  if (task.nextPickup) {
    const pu = new Date(task.nextPickup + 'T00:00:00');
    result.pickupDays = Math.round((pu - today) / 86400000);
  }
  return result;
}

function openMedInfo(taskId) {
  const task = tasks.find(t => t.id === taskId);
  if (!task) return;

  const pw = document.getElementById('mi-photo-wrap');
  pw.innerHTML = task.photo
    ? `<img src="${task.photo}" class="med-info-img" alt="${task.name}">`
    : `<div class="med-info-ph">💊</div>`;

  document.getElementById('mi-name').textContent = task.name;
  document.getElementById('mi-dose-sub').textContent = task.dose ? `Dose: ${task.dose}` : 'Dose não informada';
  document.getElementById('mi-detail-dose').textContent = task.dose || 'Conforme prescrição';

  const tw = document.getElementById('mi-times-wrap');
  tw.innerHTML = task.time
    ? `<span style="background:var(--teal-50);color:var(--teal-600);padding:3px 10px;border-radius:12px;font-size:12px;font-weight:700">🕐 ${task.time}</span>`
    : '';

  const secInd = document.getElementById('mi-sec-indication');
  if (task.indication) {
    secInd.style.display = 'block';
    document.getElementById('mi-indication').textContent = task.indication;
  } else secInd.style.display = 'none';

  const rowT = document.getElementById('mi-row-treatend');
  if (task.continuous) {
    document.getElementById('mi-treatend').innerHTML = '♻️ <strong>Uso contínuo</strong>';
    rowT.style.display = 'flex';
  } else if (task.treatmentEnd) {
    const d = new Date(task.treatmentEnd + 'T00:00:00');
    document.getElementById('mi-treatend').textContent = d.toLocaleDateString('pt-BR', {day:'numeric',month:'long',year:'numeric'});
    rowT.style.display = 'flex';
  } else rowT.style.display = 'none';

  const rowO = document.getElementById('mi-row-obs');
  if (task.obs) { rowO.style.display = 'flex'; document.getElementById('mi-obs').textContent = task.obs; }
  else rowO.style.display = 'none';

  const st = getMedStatus(task);
  const secRx = document.getElementById('mi-sec-rx');
  if (task.prescriptionExpiry) {
    secRx.style.display = 'block';
    const expDate = new Date(task.prescriptionExpiry + 'T00:00:00');
    document.getElementById('mi-rx-date').textContent = expDate.toLocaleDateString('pt-BR', {day:'numeric',month:'long',year:'numeric'});
    const rxEl = document.getElementById('mi-rx-status');
    if (st.rxExpired) {
      rxEl.textContent = '🔴 Receita vencida — renove com urgência!';
      rxEl.className = 'rx-pill rx-alert';
    } else if (st.rxDays <= 14) {
      rxEl.textContent = `⚠️ Vence em ${st.rxDays} dia${st.rxDays !== 1 ? 's' : ''}`;
      rxEl.className = 'rx-pill rx-warn';
    } else {
      rxEl.textContent = `✅ Válida por mais ${st.rxDays} dias`;
      rxEl.className = 'rx-pill rx-ok';
    }
    rxEl.style.display = 'inline-flex';
  } else secRx.style.display = 'none';

  const secPu = document.getElementById('mi-sec-pickup');
  if (task.pickupSource) {
    secPu.style.display = 'block';
    const srcLabels = { sus: '🏥 UBS / SUS (gratuito)', farmacia: '💊 Farmácia popular', particular: '🛒 Compra particular' };
    document.getElementById('mi-pickup-source').textContent = srcLabels[task.pickupSource] || task.pickupSource;
    document.getElementById('mi-pickup-interval').textContent = task.pickupInterval ? `A cada ${task.pickupInterval} dias` : '—';
    if (task.nextPickup) {
      const pu = new Date(task.nextPickup + 'T00:00:00');
      document.getElementById('mi-pickup-next').textContent = pu.toLocaleDateString('pt-BR', {day:'numeric',month:'long',year:'numeric'});
      const puEl = document.getElementById('mi-pickup-status');
      if (st.pickupDays <= 0) {
        puEl.textContent = '🔴 Retirar hoje — ou já está atrasado!';
        puEl.className = 'rx-pill rx-alert';
      } else if (st.pickupDays <= 5) {
        puEl.textContent = `⚠️ Retirar em ${st.pickupDays} dia${st.pickupDays !== 1 ? 's' : ''}`;
        puEl.className = 'rx-pill rx-warn';
      } else {
        puEl.textContent = `✅ Em ${st.pickupDays} dias`;
        puEl.className = 'rx-pill rx-ok';
      }
      puEl.style.display = 'inline-flex';
    } else {
      document.getElementById('mi-pickup-next').textContent = 'Não definida';
      document.getElementById('mi-pickup-status').style.display = 'none';
    }
  } else secPu.style.display = 'none';

  if (typeof haptic === 'function') haptic([15]);
  document.getElementById('med-info-sheet').classList.add('open');
}

function closeMedInfo() { document.getElementById('med-info-sheet').classList.remove('open'); }
function closeMedInfoOut(e) { if (e.target.id === 'med-info-sheet') closeMedInfo(); }

// ── Helpers do formulário de remédio ─────────────────────────────────────
function toggleContinuous(cb) {
  const inp = document.getElementById('task-treatment-end');
  inp.disabled = cb.checked;
  if (cb.checked) {
    inp.value = '';
    const rxExp = document.getElementById('task-rx-expiry');
    if (!rxExp.value) {
      const d = new Date(); d.setMonth(d.getMonth() + 6);
      rxExp.value = d.toISOString().split('T')[0];
    }
  }
}
function onPickupSourceChange(val) {
  document.getElementById('pickup-schedule-fields').style.display = val ? 'block' : 'none';
  if (val) calcAndFillPickup();
}
function calcAndFillPickup() {
  const interval = parseInt(document.getElementById('task-pickup-interval')?.value) || 30;
  const d = new Date(); d.setDate(d.getDate() + interval);
  const el = document.getElementById('task-next-pickup');
  if (el) el.value = d.toISOString().split('T')[0];
}

// ── Checklist de segurança: resposta a cada pergunta ─────────────────────
function medCheckAnswer(id, answer) {
  if (!window._medCheckAnswers) window._medCheckAnswers = {};
  window._medCheckAnswers[id] = answer;

  // Visual feedback nos botões
  const yesBtn = document.getElementById(id + '-yes');
  const noBtn  = document.getElementById(id + '-no');
  if (yesBtn) yesBtn.classList.toggle('yes', answer === 'yes');
  if (noBtn)  noBtn.classList.toggle('no',  answer === 'no');

  // Haptic leve
  if (typeof haptic === 'function') haptic([10]);

  // Verificar se há algum ❌ respondido
  const hasNo  = Object.values(window._medCheckAnswers).some(v => v === 'no');
  const alertEl   = document.getElementById('med-checklist-alert');
  const confirmBtn = document.getElementById('confirm-modal').querySelector('.btn-confirm');

  if (alertEl)    alertEl.classList.toggle('show', hasNo);
  if (confirmBtn) confirmBtn.classList.toggle('blocked', hasNo);
}

function confirmTake() {
  if (!pendingConfirmId) return;

  // Bloquear se algum item do checklist foi marcado ❌
  if (window._medCheckAnswers && Object.values(window._medCheckAnswers).some(v => v === 'no')) {
    if (typeof showToast === 'function') showToast('⚠️ Verifique a embalagem antes de confirmar!');
    if (typeof haptic    === 'function') haptic([30, 50, 30]);
    return;
  }

  const task = tasks.find(t => t.id === pendingConfirmId);
  const key = `${pendingConfirmId}_${todayStr()}`;
  completions[key] = true;

  // Se tirou foto como comprovante, salvar no registro de confirmações
  if (pendingProofPhoto && task) {
    if (!task.proofPhotos) task.proofPhotos = {};
    task.proofPhotos[todayStr()] = pendingProofPhoto;
    saveTasks();
    showToast('✅ Remédio confirmado com foto!');
  } else {
    showToast('✅ Remédio confirmado!');
  }

  localStorage.setItem('cuidarbem_completions', JSON.stringify(completions));
  closeConfirmModal();
  renderAll();
  if (typeof scheduleAlarmsOnSW === 'function') scheduleAlarmsOnSW();
}


// ── Tomar agora mesmo (inline, sem modal) ────────────────────────────────
function quickTake(taskId, btn) {
  const task = tasks.find(t => t.id === taskId);
  if (!task) return;

  // Ripple visual feedback
  if (btn) {
    const rect = btn.getBoundingClientRect();
    const ripple = document.createElement('span');
    ripple.className = 'qt-ripple';
    const size = Math.max(btn.offsetWidth, btn.offsetHeight);
    ripple.style.cssText = `width:${size}px;height:${size}px;left:${(btn.offsetWidth-size)/2}px;top:${(btn.offsetHeight-size)/2}px`;
    btn.appendChild(ripple);
    setTimeout(() => ripple.remove(), 520);

    // Flash verde → desaparece
    btn.classList.add('success');
    btn.innerHTML = '<span style="font-size:16px">✅</span> Confirmado!';
    btn.disabled = true;
  }

  haptic([40, 20, 40]);
  if (typeof playAlarmBeep === 'function') {
    playAlarmBeep(660, 0.12);
    setTimeout(() => playAlarmBeep(880, 0.12), 160);
  }

  const key = `${taskId}_${todayStr()}`;
  completions[key] = true;
  localStorage.setItem('cuidarbem_completions', JSON.stringify(completions));

  const now = new Date();
  const timeStr = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  showToast(`✅ ${task.name} — tomado às ${timeStr}!`);

  // Animate card out then re-render
  const card = document.getElementById(`task-card-${taskId}`);
  if (card) {
    card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    card.style.opacity = '0';
    card.style.transform = 'translateX(24px)';
    setTimeout(() => renderAll(), 420);
  } else {
    renderAll();
  }

  // Update streak badge if available
  if (typeof updateStreakBadge === 'function') setTimeout(updateStreakBadge, 450);
  if (typeof doLocalBackup     === 'function') setTimeout(doLocalBackup,     500);
  if (typeof scheduleAlarmsOnSW === 'function') scheduleAlarmsOnSW();
}
let apptOcrImageBase64 = null;
let apptOcrResults = [];
let pendingSeenId = null;
const manualApptData = {};

function openApptOcrCamera() {
  const inp = document.getElementById('appt-file-input');
  inp.setAttribute('capture','environment');
  inp.click();
}

function handleApptFile(event) {
  const file = event.target.files[0]; if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    apptOcrImageBase64 = e.target.result.split(',')[1];
    document.getElementById('appt-preview-img').src = e.target.result;
    document.getElementById('appt-upload-zone').style.display = 'none';
    document.getElementById('appt-preview-zone').style.display = 'block';
    document.getElementById('appt-result-zone').style.display = 'none';
    document.getElementById('appt-loading').style.display = 'none';
    document.getElementById('appt-manual-zone').style.display = 'none';
  };
  reader.readAsDataURL(file);
  event.target.value = '';
}

function resetApptOcr() {
  apptOcrImageBase64 = null; apptOcrResults = [];
  document.getElementById('appt-upload-zone').style.display = 'block';
  document.getElementById('appt-preview-zone').style.display = 'none';
  document.getElementById('appt-result-zone').style.display = 'none';
  document.getElementById('appt-loading').style.display = 'none';
  document.getElementById('appt-manual-zone').style.display = 'none';
  renderApptUpcoming();
}

function openApptManual() {
  document.getElementById('appt-upload-zone').style.display = 'none';
  document.getElementById('appt-manual-zone').style.display = 'block';
  renderManualApptForm([{name:'',subtype:'cons',date:'',time:'',local:'',doctor:'',prep:'',alertMorning:true,alertBefore:true}]);
}

function renderManualApptForm(items) {
  const wrap = document.getElementById('appt-manual-form-wrap');
  wrap.innerHTML = items.map((it, i) => buildApptFormCard(it, i, true)).join('');
  apptOcrResults = items.map(it => ({...it, include:true}));
}

function buildApptFormCard(it, i, isManual) {
  const isExam = it.subtype === 'exam' || it.examType;
  const borderColor = isExam ? 'var(--blue-400)' : 'var(--purple-400)';
  const badgeBg = isExam ? 'var(--blue-50)' : 'var(--purple-50)';
  const badgeColor = isExam ? 'var(--blue-600)' : 'var(--purple-600)';
  const typeLabel = isExam ? '🔬 Exame' : '🩺 Consulta';
  return `
  <div class="appt-ocr-card ${isExam?'exam-type':''}" id="appt-card-${i}">
    <div class="appt-ocr-header">
      <div>
        <select style="padding:4px 10px;border-radius:8px;border:1.5px solid ${borderColor};background:${badgeBg};color:${badgeColor};font-weight:700;font-family:'Nunito',sans-serif;font-size:12px;cursor:pointer"
          onchange="updateApptField(${i},'subtype',this.value);reRenderApptCard(${i})">
          <option value="cons" ${!isExam?'selected':''}>🩺 Consulta</option>
          <option value="exam" ${isExam?'selected':''}>🔬 Exame</option>
        </select>
      </div>
      ${!isManual ? `<button class="toggle ${it.include?'on':''}" onclick="toggleApptInclude(${i})" id="appt-toggle-${i}"></button>` : ''}
    </div>

    <div class="appt-ocr-field">
      <label>Nome / descrição</label>
      <input value="${it.name||''}" placeholder="${isExam?'Ex: Hemograma completo, ECG...':'Ex: Consulta neurologia, Retorno...'}"
        oninput="updateApptField(${i},'name',this.value)">
    </div>
    ${isExam ? `<div class="appt-ocr-field">
      <label>Tipo de exame</label>
      <input value="${it.examType||''}" placeholder="Ex: Sangue, Imagem, Eletro..."
        oninput="updateApptField(${i},'examType',this.value)">
    </div>` : `<div class="appt-ocr-field">
      <label>Médico / especialidade</label>
      <input value="${it.doctor||''}" placeholder="Ex: Dr. João Silva — Neurologia"
        oninput="updateApptField(${i},'doctor',this.value)">
    </div>`}
    <div class="appt-ocr-field">
      <label>Local / clínica / laboratório</label>
      <input value="${it.local||''}" placeholder="Nome e endereço"
        oninput="updateApptField(${i},'local',this.value)">
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
      <div class="appt-ocr-field">
        <label>Data</label>
        <input type="date" value="${it.date||''}" oninput="updateApptField(${i},'date',this.value)">
      </div>
      <div class="appt-ocr-field">
        <label>Horário</label>
        <input type="time" value="${it.time||''}" oninput="updateApptField(${i},'time',this.value)">
      </div>
    </div>
    <div class="appt-ocr-field">
      <label>Preparo necessário</label>
      <input value="${it.prep||''}" placeholder="Ex: Jejum 8h, trazer exames anteriores..."
        oninput="updateApptField(${i},'prep',this.value)">
    </div>
    <div style="margin-top:4px">
      <div style="font-size:11px;font-weight:700;color:var(--text-light);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px">Alertas</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="alert-chip ${it.alertMorning!==false?'active':'inactive'}" onclick="toggleApptAlert(${i},'alertMorning',this)" id="alert-morning-${i}">
          🌅 Manhã do dia (7h)
        </button>
        <button class="alert-chip ${it.alertBefore!==false?'active':'inactive'}" onclick="toggleApptAlert(${i},'alertBefore',this)" id="alert-before-${i}">
          ⏰ 1 hora antes
        </button>
      </div>
    </div>
  </div>`;
}

function updateApptField(i, field, value) {
  if (apptOcrResults[i]) apptOcrResults[i][field] = value;
}

function reRenderApptCard(i) {
  const card = document.getElementById(`appt-card-${i}`);
  if (card) card.outerHTML = buildApptFormCard(apptOcrResults[i], i, false);
}

function toggleApptInclude(i) {
  apptOcrResults[i].include = !apptOcrResults[i].include;
  const card = document.getElementById(`appt-card-${i}`);
  const toggle = document.getElementById(`appt-toggle-${i}`);
  if(card) card.classList.toggle('excluded', !apptOcrResults[i].include);
  if(toggle) toggle.classList.toggle('on', apptOcrResults[i].include);
}

function toggleApptAlert(i, field, btn) {
  const cur = apptOcrResults[i][field] !== false;
  apptOcrResults[i][field] = !cur;
  btn.classList.toggle('active', !cur);
  btn.classList.toggle('inactive', cur);
}

async function analyzeApptRecipe() {
  if (!apptOcrImageBase64) return;
  document.getElementById('appt-preview-zone').style.display = 'none';
  document.getElementById('appt-loading').style.display = 'block';
  document.getElementById('appt-result-zone').style.display = 'none';

  const msgs = ['Lendo o pedido...','Identificando exames...','Extraindo dados...','Quase pronto...'];
  let mi = 0;
  const intv = setInterval(() => {
    mi = (mi+1)%msgs.length;
    const el = document.getElementById('appt-loading-text');
    if(el) el.textContent = msgs[mi];
  }, 2000);

  try {
    const prompt = `Você é um assistente médico-administrativo. Analise esta imagem (pode ser uma guia de consulta, pedido de exame, solicitação médica ou similar).

Extraia TODOS os exames e/ou consultas presentes. Responda SOMENTE com JSON, sem markdown, sem texto extra:

{
  "itens": [
    {
      "subtype": "cons" ou "exam",
      "name": "Nome descritivo (ex: Consulta Neurologia, Hemograma Completo)",
      "examType": "Tipo se for exame (Sangue, Imagem, Eletrocardiograma, etc) — deixe vazio se consulta",
      "doctor": "Nome do médico solicitante ou especialidade se consulta — vazio se exame",
      "local": "Local, clínica, laboratório ou hospital se mencionado",
      "date": "Data no formato YYYY-MM-DD se mencionada, senão vazio",
      "time": "Horário HH:MM se mencionado, senão vazio",
      "prep": "Instruções de preparo (jejum, etc) se mencionadas",
      "alertMorning": true,
      "alertBefore": true
    }
  ],
  "observacoes": "Notas gerais sobre o pedido ou combinação de exames"
}

Se não conseguir ler: {"erro": "Imagem ilegível. Tente uma foto mais nítida."}`;

    const resp = await fetch('https://api.anthropic.com/v1/messages', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        model:'claude-sonnet-4-20250514', max_tokens:1500,
        messages:[{role:'user', content:[
          {type:'image', source:{type:'base64', media_type:'image/jpeg', data:apptOcrImageBase64}},
          {type:'text', text:prompt}
        ]}]
      })
    });
    clearInterval(intv);
    const data = await resp.json();
    const raw = data.content?.find(b=>b.type==='text')?.text||'';
    const parsed = JSON.parse(raw.replace(/```json|```/g,'').trim());
    if (parsed.erro) { showToast('❌ '+parsed.erro); resetApptOcr(); return; }

    apptOcrResults = (parsed.itens||[]).map((it,i) => ({...it, id:'appt_ocr_'+i, include:true}));

    // Build editable result cards
    const listEl = document.getElementById('appt-ocr-list');
    listEl.innerHTML = apptOcrResults.map((it,i) => buildApptFormCard(it, i, false)).join('');

    document.getElementById('appt-loading').style.display = 'none';
    document.getElementById('appt-result-zone').style.display = 'block';

  } catch(e) {
    clearInterval(intv);
    showToast('❌ Erro ao analisar. Tente novamente.');
    resetApptOcr();
  }
}

function addAllAppts() {
  let added = 0;
  const imgSrc = document.getElementById('appt-preview-img')?.src;
  const hasPhoto = imgSrc && imgSrc.startsWith('data:');
  apptOcrResults.forEach(it => {
    if (it.include === false) return;
    if (!it.name) return;
    const isExamItem = it.subtype === 'exam' || !!it.examType;
    tasks.push({
      id: uid(), type: isExamItem ? 'exam' : 'cons',
      name: it.name, subtype: it.subtype || (isExamItem ? 'exam' : 'cons'),
      examType: it.examType||'', doctor: it.doctor||'',
      local: it.local||'', date: it.date||todayStr(),
      time: it.time||'', repeat:'none',
      obs: it.prep||'', prep: it.prep||'',
      alertMorning: it.alertMorning!==false,
      alertBefore: it.alertBefore!==false,
      photo: hasPhoto ? imgSrc : null,
      dose:'', createdAt: Date.now()
    });
    added++;
  });
  saveTasks(); buildWeekStrip();
  showToast(`✅ ${added} evento${added!==1?'s':''} adicionado${added!==1?'s':''}!`);
  setTimeout(()=> {
    resetApptOcr();
    renderAll();
  }, 300);
}

function saveManualAppt() {
  addAllAppts();
  document.getElementById('appt-manual-zone').style.display = 'none';
  document.getElementById('appt-upload-zone').style.display = 'block';
}

function renderApptUpcoming() {
  const todayS = todayStr();

  function buildCard(t) {
    const isExam = t.type === 'exam';
    const seen = completions[`${t.id}_${t.date}`];
    const icon = isExam ? '🔬' : '🩺';
    const borderColor = isExam ? 'var(--blue-400)' : 'var(--purple-400)';
    const dateStr = t.date ? new Date(t.date+'T00:00:00').toLocaleDateString('pt-BR',{weekday:'short',day:'numeric',month:'short'}) : '';
    const resultAlert = isExam && t.resultsDate && t.resultsDate <= todayS && !completions[`res_${t.id}`]
      ? `<div style="padding:8px 16px;background:var(--blue-50);border-top:1px solid var(--blue-100);font-size:12px;color:var(--blue-600);font-weight:700;cursor:pointer">
           🗂️ Resultado disponível — buscar resultado
         </div>` : '';
    const examExtra = isExam && t.examType
      ? `<div style="font-size:12px;color:var(--text-light)">🔬 ${t.examType}</div>` : '';
    const doctorLine = (t.doctor || t.examDoctor)
      ? `<div style="font-size:12px;color:var(--text-light)">👨‍⚕️ ${t.doctor || t.examDoctor}</div>` : '';
    return `<div style="background:var(--card-bg);border-radius:var(--radius);margin-bottom:10px;box-shadow:var(--shadow);overflow:hidden">
      <div style="padding:12px 16px;border-left:5px solid ${borderColor};display:flex;align-items:center;gap:12px">
        <div style="font-size:24px">${icon}</div>
        <div style="flex:1;min-width:0">
          <div style="font-size:14px;font-weight:800;color:${seen?'var(--text-light)':'var(--text)'};${seen?'text-decoration:line-through':''}">${t.name}</div>
          ${examExtra}${doctorLine}
          ${t.local?`<div style="font-size:12px;color:var(--text-light)">🏥 ${t.local}</div>`:''}
          <div style="font-size:12px;color:var(--text-light)">📅 ${dateStr}${t.time?' · 🕐 '+t.time:''}</div>
          ${t.prep?`<div style="font-size:11px;font-weight:700;color:var(--amber-600);margin-top:4px">⚠️ ${t.prep}</div>`:''}
        </div>
        <div class="task-check ${seen?'checked':''}" style="flex-shrink:0" onclick="openSeenModal('${t.id}')"></div>
      </div>
      ${t.photo?`<img src="${t.photo}" style="width:100%;max-height:80px;object-fit:cover;border-top:1px solid var(--gray-100);display:block">` : ''}
      ${resultAlert}
    </div>`;
  }

  const sorted = tasks
    .filter(t => (t.type==='cons'||t.type==='exam') && t.date >= todayS)
    .sort((a,b) => (a.date+a.time).localeCompare(b.date+b.time));

  const consList = sorted.filter(t => t.type === 'cons').slice(0,5);
  const examList = sorted.filter(t => t.type === 'exam').slice(0,5);

  const consEl = document.getElementById('appt-upcoming-cons');
  const examEl = document.getElementById('appt-upcoming-exam');
  if (consEl) consEl.innerHTML = consList.length
    ? consList.map(buildCard).join('')
    : `<div style="font-size:13px;color:var(--text-light);padding:10px 4px">Nenhuma consulta agendada.</div>`;
  if (examEl) examEl.innerHTML = examList.length
    ? examList.map(buildCard).join('')
    : `<div style="font-size:13px;color:var(--text-light);padding:10px 4px">Nenhum exame agendado.</div>`;
}

// ─── SEEN MODAL ───────────────────────────────────────────────────────────
function openSeenModal(taskId) {
  const task = tasks.find(t => t.id === taskId);
  if (!task) return;
  pendingSeenId = taskId;

  const photoWrap = document.getElementById('seen-photo-wrap');
  if (task.photo) {
    photoWrap.innerHTML = `<img src="${task.photo}" class="seen-sheet-photo" alt="${task.name}">`;
  } else {
    const isExam = task.type === 'exam';
    photoWrap.innerHTML = `<div style="width:80px;height:80px;border-radius:16px;background:${isExam?'var(--blue-50)':'var(--purple-50)'};display:flex;align-items:center;justify-content:center;font-size:40px;margin:0 auto 12px">${isExam?'🔬':'🩺'}</div>`;
  }

  const isExam = task.type === 'exam';
  const badge = document.getElementById('seen-type-badge-el');
  badge.textContent = isExam ? '🔬 Exame' : '🩺 Consulta';
  badge.className = 'seen-type-badge' + (isExam?' exam':'');

  document.getElementById('seen-name').textContent = task.name;
  const dateStr = task.date ? new Date(task.date+'T00:00:00').toLocaleDateString('pt-BR',{weekday:'long',day:'numeric',month:'long',year:'numeric'}) : '—';
  document.getElementById('seen-date').textContent = dateStr;
  document.getElementById('seen-time').textContent = task.time || 'Não informado';

  const localRow = document.getElementById('seen-local-row');
  if (task.local) { localRow.style.display='flex'; document.getElementById('seen-local').textContent = task.local; }
  else localRow.style.display='none';

  const doctorRow = document.getElementById('seen-doctor-row');
  const docName = task.doctor || task.examDoctor;
  if (docName) { doctorRow.style.display='flex'; document.getElementById('seen-doctor').textContent = docName; }
  else doctorRow.style.display='none';

  const prepEl = document.getElementById('seen-prep');
  if (task.prep || task.obs) {
    prepEl.style.display='block';
    prepEl.innerHTML = `⚠️ <strong>Preparo:</strong> ${task.prep||task.obs}`;
  } else prepEl.style.display='none';

  // Exam result section
  const resultSection = document.getElementById('seen-result-section');
  const confirmHint   = document.getElementById('seen-confirm-hint');
  if (isExam) {
    resultSection.style.display = 'block';
    confirmHint.innerHTML = '📋 Confirme a realização do exame. <strong>Fotografe o resultado</strong> quando disponível.';
    renderSeenResultStrip(task);
    // Show overdue alert
    const resultAlertEl = document.getElementById('seen-result-alert');
    const todayS = todayStr();
    resultAlertEl.style.display = (task.resultsDate && task.resultsDate <= todayS && !(task.resultPhotos?.length)) ? 'block' : 'none';
  } else {
    resultSection.style.display = 'none';
    confirmHint.innerHTML = 'Confirme que <strong>leu e está ciente</strong> deste compromisso de saúde.';
  }

  const btnEl = document.getElementById('seen-confirm-btn');
  btnEl.textContent = isExam ? '✅ Exame realizado — confirmar' : '👁️ Estou ciente — anotado!';
  btnEl.className = 'btn-seen' + (isExam?' exam-btn':'');

  document.getElementById('seen-modal').classList.add('open');
}

function renderSeenResultStrip(task) {
  const strip = document.getElementById('seen-result-strip');
  const photos = task.resultPhotos || [];
  strip.innerHTML = photos.map((p, i) =>
    `<img class="result-thumb" src="${p.photoData}" alt="Página ${i+1}"
      onclick="openResultViewer('${task.id}',${i})">`
  ).join('') +
  `<div class="result-add-btn" onclick="document.getElementById('seen-result-input').click()">
    📷<span class="result-add-label">${photos.length ? '+ Página' : 'Fotografar'}</span>
  </div>`;
}

function handleResultCapture(event) {
  const file = event.target.files[0];
  if (!file || !pendingSeenId) return;
  const task = tasks.find(t => t.id === pendingSeenId);
  if (!task) return;
  const reader = new FileReader();
  reader.onload = e => {
    if (!task.resultPhotos) task.resultPhotos = [];
    task.resultPhotos.push({ photoData: e.target.result, capturedAt: new Date().toISOString() });
    saveTasks();
    renderSeenResultStrip(task);
    renderAll();
    renderApptUpcoming();
    showToast(`📷 Página ${task.resultPhotos.length} salva!`);
    if (typeof haptic === 'function') haptic([20, 40]);
  };
  reader.readAsDataURL(file);
  event.target.value = '';
}

function confirmSeen() {
  if (!pendingSeenId) return;
  const task = tasks.find(t=>t.id===pendingSeenId);
  const day = task?.date || todayStr();
  completions[`${pendingSeenId}_${day}`] = true;
  localStorage.setItem('cuidarbem_completions', JSON.stringify(completions));
  const isExam = task?.type === 'exam';
  closeSeenModal();
  showToast(isExam ? '🔬 Exame confirmado!' : '👁️ Compromisso confirmado!');
  renderAll();
  renderApptUpcoming();
  if (typeof scheduleAlarmsOnSW === 'function') scheduleAlarmsOnSW();
}

function closeSeenModal() {
  document.getElementById('seen-modal').classList.remove('open');
  pendingSeenId = null;
}

// ── Result viewer ─────────────────────────────────────────────────────────
let rvTaskId = null, rvIndex = 0;

function openResultViewer(taskId, idx) {
  const task = tasks.find(t => t.id === taskId);
  if (!task?.resultPhotos?.length) return;
  rvTaskId = taskId; rvIndex = idx;
  document.getElementById('rv-title').textContent = task.name;
  rvRender();
  document.getElementById('result-viewer').classList.add('open');
}

function rvRender() {
  const task = tasks.find(t => t.id === rvTaskId);
  if (!task?.resultPhotos) return;
  document.getElementById('rv-img').src = task.resultPhotos[rvIndex].photoData;
  document.getElementById('rv-counter').textContent = `${rvIndex+1}/${task.resultPhotos.length}`;
}

function rvNav(dir) {
  const task = tasks.find(t => t.id === rvTaskId);
  if (!task?.resultPhotos) return;
  rvIndex = (rvIndex + dir + task.resultPhotos.length) % task.resultPhotos.length;
  rvRender();
}

function rvDelete() {
  const task = tasks.find(t => t.id === rvTaskId);
  if (!task?.resultPhotos) return;
  if (!confirm(`Remover página ${rvIndex+1}?`)) return;
  task.resultPhotos.splice(rvIndex, 1);
  saveTasks();
  if (!task.resultPhotos.length) { closeResultViewer(); renderAll(); renderApptUpcoming(); return; }
  rvIndex = Math.min(rvIndex, task.resultPhotos.length - 1);
  rvRender();
  if (pendingSeenId === rvTaskId) renderSeenResultStrip(task);
  renderAll(); renderApptUpcoming();
  showToast('🗑️ Página removida');
}

function rvAddMore() {
  closeResultViewer();
  setTimeout(() => document.getElementById('seen-result-input')?.click(), 300);
}

function closeResultViewer() {
  document.getElementById('result-viewer').classList.remove('open');
}

// ── Helpers: result status for a task ────────────────────────────────────
function getExamResultStatus(task) {
  if (task.type !== 'exam') return null;
  const photos = task.resultPhotos || [];
  if (photos.length) return { kind: 'has', label: `📷 ${photos.length} pág. de resultado` };
  const todayS = todayStr();
  if (task.resultsDate) {
    if (task.resultsDate < todayS)  return { kind: 'overdue', label: '🔴 Buscar resultado!' };
    if (task.resultsDate === todayS) return { kind: 'pending', label: '🔔 Resultado hoje' };
    return { kind: 'pending', label: `🗂️ Resultado: ${new Date(task.resultsDate+'T00:00:00').toLocaleDateString('pt-BR',{day:'numeric',month:'short'})}` };
  }
  if (completions[`${task.id}_${task.date}`]) return { kind: 'pending', label: '📷 Sem resultado fotografado' };
  return null;
}

// ─── OCR / AI RECIPE ANALYSIS ─────────────────────────────────────────────
let ocrImageBase64 = null;
let ocrResults = [];

function handleOcrFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const dataUrl = e.target.result;
    ocrImageBase64 = dataUrl.split(',')[1];
    document.getElementById('ocr-preview-img').src = dataUrl;
    document.getElementById('ocr-upload-zone').style.display = 'none';
    document.getElementById('ocr-preview-zone').style.display = 'block';
    document.getElementById('ocr-result-zone').style.display = 'none';
    document.getElementById('ocr-loading').style.display = 'none';
  };
  reader.readAsDataURL(file);
  event.target.value = '';
}

function resetOcr() {
  ocrImageBase64 = null; ocrResults = [];
  document.getElementById('ocr-upload-zone').style.display = 'block';
  document.getElementById('ocr-preview-zone').style.display = 'none';
  document.getElementById('ocr-result-zone').style.display = 'none';
  document.getElementById('ocr-loading').style.display = 'none';
}

async function analyzeRecipe() {
  if (!ocrImageBase64) return;
  document.getElementById('ocr-preview-zone').style.display = 'none';
  document.getElementById('ocr-loading').style.display = 'block';
  document.getElementById('ocr-result-zone').style.display = 'none';

  const loadingMsgs = ['Lendo a receita...','Identificando medicamentos...','Sugerindo horários...','Buscando informações...'];
  let mi = 0;
  const loadInt = setInterval(() => {
    mi = (mi+1) % loadingMsgs.length;
    const el = document.getElementById('ocr-loading-text');
    if (el) el.textContent = loadingMsgs[mi];
  }, 2000);

  try {
    const prompt = `Você é um assistente farmacêutico especializado em auxiliar cuidadores de pacientes com AVC.

Analise esta imagem de receita médica e extraia TODOS os medicamentos presentes.

Para cada medicamento, forneça um JSON com este formato EXATO (responda APENAS com o JSON, sem markdown, sem texto extra):

{
  "medicamentos": [
    {
      "nome": "Nome do medicamento e dose (ex: Losartana 50mg)",
      "dose": "Como tomar (ex: 1 comprimido)",
      "frequencia": "Quantas vezes por dia (ex: 1x ao dia, 2x ao dia)",
      "horarios_sugeridos": ["08:00", "20:00"],
      "para_que_serve": "Explicação simples em 1-2 frases do que esse remédio trata, voltado para leigo",
      "instrucoes": "Instruções especiais de uso (ex: tomar em jejum, com alimento, à noite)",
      "cuidados_avc": "Se relevante para paciente com AVC, mencione cuidados específicos. Se não houver, deixe vazio."
    }
  ],
  "observacoes": "Qualquer observação geral sobre a receita ou combinação de medicamentos. Se não houver, deixe vazio."
}

Regras para sugestão de horários:
- 1x ao dia: prefira 08:00 (exceto se for medicamento que deve ser tomado à noite, aí use 21:00)
- 2x ao dia: 08:00 e 20:00
- 3x ao dia: 08:00, 14:00, 20:00
- 4x ao dia: 08:00, 12:00, 18:00, 22:00
- Se a receita especificar horário, use o horário da receita

Se não conseguir ler a receita claramente, retorne:
{"erro": "Não foi possível ler a receita. Tente uma foto mais nítida e bem iluminada."}`;

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 2000,
        messages: [{
          role: 'user',
          content: [
            { type: 'image', source: { type: 'base64', media_type: 'image/jpeg', data: ocrImageBase64 } },
            { type: 'text', text: prompt }
          ]
        }]
      })
    });

    clearInterval(loadInt);
    const data = await response.json();
    const raw = data.content?.find(b => b.type === 'text')?.text || '';
    const clean = raw.replace(/```json|```/g,'').trim();
    const parsed = JSON.parse(clean);

    if (parsed.erro) {
      showToast('❌ ' + parsed.erro);
      resetOcr();
      return;
    }

    ocrResults = (parsed.medicamentos || []).map((m, i) => ({...m, id: 'ocr_'+i, include: true, selectedTimes: [...(m.horarios_sugeridos||[])]}));
    renderOcrResults(parsed.observacoes);

  } catch(e) {
    clearInterval(loadInt);
    console.error(e);
    showToast('❌ Erro ao analisar. Tente novamente.');
    resetOcr();
  }
}

function renderOcrResults(observacoes) {
  document.getElementById('ocr-loading').style.display = 'none';
  document.getElementById('ocr-result-zone').style.display = 'block';

  const list = document.getElementById('ocr-meds-list');
  list.innerHTML = ocrResults.map((m, i) => `
    <div class="ocr-med-card ${m.include?'':'excluded'}" id="ocr-card-${i}">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px">
        <div style="flex:1">
          <div class="ocr-med-name">💊 ${m.nome}</div>
          <div class="ocr-med-dose">${m.dose} · ${m.frequencia}</div>
        </div>
        <button class="toggle ${m.include?'on':''}" onclick="toggleOcrMed(${i})" id="ocr-toggle-${i}"></button>
      </div>

      <div class="ocr-med-para">
        <strong>Para que serve:</strong> ${m.para_que_serve}
        ${m.cuidados_avc ? `<br><br>🧠 <strong>AVC:</strong> ${m.cuidados_avc}` : ''}
      </div>

      ${m.instrucoes ? `<div style="font-size:12px;color:var(--amber-600);background:var(--amber-50);padding:8px 10px;border-radius:8px;margin-bottom:10px">⚠️ ${m.instrucoes}</div>` : ''}

      <div style="font-size:12px;font-weight:700;color:var(--text-muted);margin-bottom:6px">Horários sugeridos (toque para remover/adicionar):</div>
      <div class="ocr-time-row" id="times-${i}">
        ${(m.selectedTimes||[]).map((t,ti) => `<button class="ocr-time-chip" onclick="toggleOcrTime(${i},${ti})" id="time-${i}-${ti}">${t}</button>`).join('')}
      </div>
    </div>
  `).join('');

  const obsCard = document.getElementById('ocr-obs-card');
  if (observacoes && observacoes.trim()) {
    obsCard.style.display = 'block';
    document.getElementById('ocr-obs-text').textContent = observacoes;
  } else { obsCard.style.display = 'none'; }
}

function toggleOcrMed(i) {
  ocrResults[i].include = !ocrResults[i].include;
  const card = document.getElementById(`ocr-card-${i}`);
  const toggle = document.getElementById(`ocr-toggle-${i}`);
  card.classList.toggle('excluded', !ocrResults[i].include);
  toggle.classList.toggle('on', ocrResults[i].include);
}

function toggleOcrTime(medIdx, timeIdx) {
  const chip = document.getElementById(`time-${medIdx}-${timeIdx}`);
  chip.classList.toggle('removed');
  if (chip.classList.contains('removed')) {
    ocrResults[medIdx].selectedTimes[timeIdx] = null;
  } else {
    ocrResults[medIdx].selectedTimes[timeIdx] = ocrResults[medIdx].horarios_sugeridos[timeIdx];
  }
}

function addAllOcrMeds() {
  const today = todayStr();
  let added = 0;
  ocrResults.forEach(m => {
    if (!m.include) return;
    const times = (m.selectedTimes||[]).filter(Boolean);
    if (times.length === 0) {
      tasks.push({
        id: uid(), type:'med', name: m.nome,
        dose: m.dose, date: today, time: '', repeat:'daily',
        obs: [m.instrucoes, m.cuidados_avc].filter(Boolean).join(' | '),
        createdAt: Date.now()
      });
      added++;
    } else {
      times.forEach(time => {
        tasks.push({
          id: uid(), type:'med', name: m.nome,
          dose: m.dose, date: today, time, repeat:'daily',
          obs: [m.instrucoes, m.cuidados_avc].filter(Boolean).join(' | '),
          createdAt: Date.now()
        });
      });
      added += times.length;
    }
  });
  saveTasks();
  showToast(`✅ ${added} lembretes adicionados!`);
  setTimeout(() => goScreen('home', document.getElementById('nav-home')), 400);
  resetOcr();
  renderAll();
}

// ─── PROFILE AUTO-SAVE ────────────────────────────────────────────────────
document.getElementById('caregiver-input').addEventListener('input', e => { settings.caregiver=e.target.value; saveSettings(); });
document.getElementById('diagnosis-input').addEventListener('input', e => { settings.diagnosis=e.target.value; saveSettings(); });

init();

// ═══════════════════════════════════════════════════════════
//  MANIFEST EXTERNO
//  O PWA usa manifest.webmanifest para instalar no PC e no mobile.
// ═══════════════════════════════════════════════════════════

// ═══════════════════════════════════════════════════════════
//  SERVICE WORKER EXTERNO
//  Registro principal feito acima via ./sw.js.
// ═══════════════════════════════════════════════════════════

// ── Desktop home right panel ──────────────────────────────
function renderHomeRightPanel() {
  // Mini stats
  const today = todayStr();
  const todayTasks = getTodayTasks();
  const meds = todayTasks.filter(t => t.type === 'med');
  const done = todayTasks.filter(t => isCompletedToday(t));
  const medEl = document.getElementById('stat-med-home');
  const doneEl = document.getElementById('stat-done-home');
  if (medEl) medEl.textContent = meds.length;
  if (doneEl) doneEl.textContent = done.length;

  // Upcoming appointments
  const apptEl = document.getElementById('home-upcoming-appts');
  if (!apptEl) return;
  const upcoming = tasks
    .filter(t => (t.type === 'cons' || t.type === 'exam') && t.date >= today)
    .sort((a,b) => (a.date||'').localeCompare(b.date||'') || (a.time||'').localeCompare(b.time||''))
    .slice(0, 3);
  if (!upcoming.length) {
    apptEl.innerHTML = '<div style="font-size:13px;color:var(--text-light);padding:12px 0">Nenhuma consulta agendada.</div>';
    return;
  }
  apptEl.innerHTML = upcoming.map(t => {
    const isExam = t.examType || t.subtype === 'exam';
    const color = isExam ? 'var(--blue-400)' : 'var(--purple-400)';
    const bg = isExam ? 'var(--blue-50)' : 'var(--purple-50)';
    const dateStr = t.date ? new Date(t.date+'T00:00:00').toLocaleDateString('pt-BR',{weekday:'short',day:'numeric',month:'short'}) : '';
    return `<div style="display:flex;align-items:flex-start;gap:10px;padding:10px 0;border-bottom:1px solid var(--gray-100)">
      <div style="width:36px;height:36px;border-radius:10px;background:${bg};display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0">${isExam?'🔬':'🩺'}</div>
      <div style="flex:1;min-width:0">
        <div style="font-size:13px;font-weight:800;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${t.name}</div>
        <div style="font-size:11px;color:var(--text-light);margin-top:2px">${dateStr}${t.time?' · '+t.time:''}</div>
        ${t.local?`<div style="font-size:11px;color:var(--text-light)">🏥 ${t.local}</div>`:''}
      </div>
      <div style="width:8px;height:8px;border-radius:50%;background:${color};flex-shrink:0;margin-top:6px"></div>
    </div>`;
  }).join('');
}

let deferredInstallPrompt = null;

// ── Detect iOS Safari ──
const isIOS = /iP(hone|od|ad)/.test(navigator.userAgent) && !window.MSStream;
const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
const isInStandaloneMode = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredInstallPrompt = e;
  // Show install banner after 3s if not already installed
  setTimeout(showInstallBanner, 3000);
});

function showInstallBanner() {
  if (isInStandaloneMode) return; // já instalado
  if (localStorage.getItem('pwa_install_dismissed')) return;
  if (isIOS && isSafari) {
    // iOS: não tem beforeinstallprompt, mostra banner manual
    const banner = document.getElementById('install-banner');
    if (banner) {
      banner.innerHTML = `
        <div class="install-banner-icon">📲</div>
        <div class="install-banner-text">
          <div class="install-banner-title">Instalar no iPhone/iPad</div>
          <div class="install-banner-sub">Toque em <b>compartilhar</b> → "Adicionar à Tela de Início"</div>
        </div>
        <button class="install-banner-close" onclick="dismissInstallBanner()">✕</button>
      `;
      banner.classList.add('show');
    }
    return;
  }
  if (!deferredInstallPrompt) return;
  const banner = document.getElementById('install-banner');
  if (banner) banner.classList.add('show');
}

function installPWA() {
  if (isIOS) {
    openInstallModal();
    return;
  }
  if (!deferredInstallPrompt) {
    openInstallModal();
    return;
  }
  deferredInstallPrompt.prompt();
  deferredInstallPrompt.userChoice.then(choice => {
    if (choice.outcome === 'accepted') {
      showToast('✅ CuidarBem instalado!');
    }
    deferredInstallPrompt = null;
    const banner = document.getElementById('install-banner');
    if (banner) banner.classList.remove('show');
  });
}

function openInstallModal() {
  const modal = document.getElementById('install-modal');
  if (modal) {
    // Esconde botão direto se não houver prompt disponível
    const btn = document.getElementById('install-direct-btn');
    if (btn) {
      btn.style.display = deferredInstallPrompt ? 'flex' : 'none';
    }
    modal.classList.add('open');
  }
}
function closeInstallModal() {
  const modal = document.getElementById('install-modal');
  if (modal) modal.classList.remove('open');
}

function installPWADirect() {
  if (!deferredInstallPrompt) {
    showToast('⚠️ Instalação automática não disponível. Siga as instruções abaixo.');
    return;
  }
  deferredInstallPrompt.prompt();
  deferredInstallPrompt.userChoice.then(choice => {
    if (choice.outcome === 'accepted') {
      showToast('✅ CuidarBem instalado!');
      closeInstallModal();
    }
    deferredInstallPrompt = null;
    const banner = document.getElementById('install-banner');
    if (banner) banner.classList.remove('show');
  });
}

function dismissInstallBanner() {
  const banner = document.getElementById('install-banner');
  if (banner) banner.classList.remove('show');
  localStorage.setItem('pwa_install_dismissed', '1');
}

window.addEventListener('appinstalled', () => {
  showToast('💚 App instalado com sucesso!');
  deferredInstallPrompt = null;
});

// Auto-show iOS banner after 4s on first visit
if (isIOS && isSafari && !isInStandaloneMode) {
  setTimeout(showInstallBanner, 4000);
}

// Update install settings row based on state
document.addEventListener('DOMContentLoaded', () => {
  const desc = document.getElementById('install-setting-desc');
  const row = document.getElementById('install-setting-row');
  if (isInStandaloneMode) {
    if (desc) desc.textContent = '✅ App já instalado!';
    if (row) row.style.opacity = '0.6';
  } else if (isIOS) {
    if (desc) desc.textContent = 'Toque em compartilhar → Adicionar à Tela de Início';
  }
});


// ═══════════════════════════════════════════════════════════
//  ACESSIBILIDADE: DARK MODE, FONT SIZE, LOW STRESS
// ═══════════════════════════════════════════════════════════
let a11yState = JSON.parse(localStorage.getItem('cuidarbem_a11y') || '{"dark":false,"font":"sm","lowstress":false}');

function applyA11y() {
  const body = document.body;
  body.classList.toggle('dark', a11yState.dark);
  body.classList.remove('font-sm','font-md','font-lg');
  if (a11yState.font !== 'sm') body.classList.add('font-' + a11yState.font);
  body.classList.toggle('low-stress', a11yState.lowstress);
  // Update toggle UIs (FAB panel + profile screen)
  ['dark-toggle','dark-toggle-profile'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.toggle('on', a11yState.dark);
  });
  ['lowstress-toggle','lowstress-toggle-profile'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.toggle('on', a11yState.lowstress);
  });
  // Font segments
  ['sm','md','lg'].forEach(s => {
    ['fs-'+s, 'fs-'+s+'-p'].forEach(id => {
      const btn = document.getElementById(id);
      if (btn) btn.classList.toggle('active', a11yState.font === s);
    });
  });
  // Update FAB emoji
  const fab = document.getElementById('a11y-fab');
  if (fab) fab.textContent = a11yState.dark ? '🌙' : '⚙️';
  localStorage.setItem('cuidarbem_a11y', JSON.stringify(a11yState));
}

function toggleA11yPanel() {
  const panel = document.getElementById('a11y-panel');
  panel.classList.toggle('open');
}

function toggleDarkMode() {
  a11yState.dark = !a11yState.dark;
  applyA11y();
}

function setFontSize(size) {
  a11yState.font = size;
  applyA11y();
}

function toggleLowStress() {
  a11yState.lowstress = !a11yState.lowstress;
  applyA11y();
}

// Close a11y panel when clicking outside
document.addEventListener('click', function(e) {
  const panel = document.getElementById('a11y-panel');
  const fab = document.getElementById('a11y-fab');
  if (panel && fab && !panel.contains(e.target) && !fab.contains(e.target)) {
    panel.classList.remove('open');
  }
});

// Apply on load
applyA11y();


// ═══════════════════════════════════════════════════════════
//  DASHBOARD APPLE HEALTH STYLE
// ═══════════════════════════════════════════════════════════
function renderDashboard() {
  const today = todayStr ? todayStr() : new Date().toISOString().split('T')[0];
  const todayTasks = typeof getTodayTasks === 'function' ? getTodayTasks() : [];
  const completionsData = JSON.parse(localStorage.getItem('cuidarbem_completions') || '{}');

  // ── Date label ──
  const dateEl = document.getElementById('dash-date');
  if (dateEl) {
    dateEl.textContent = new Date().toLocaleDateString('pt-BR', {weekday:'long', day:'numeric', month:'long'});
  }

  // ── Count tasks by type ──
  const byType = {med:0, fisio:0, exer:0, cons:0};
  const doneByType = {med:0, fisio:0, exer:0, cons:0};
  todayTasks.forEach(t => {
    const k = `${t.id}_${today}`;
    if (byType[t.type] !== undefined) {
      byType[t.type]++;
      if (completionsData[k]) doneByType[t.type]++;
    }
  });

  const totalToday = todayTasks.length;
  const doneToday = todayTasks.filter(t => completionsData[`${t.id}_${today}`]).length;
  const pctToday = totalToday ? Math.round(doneToday/totalToday*100) : 0;

  // ── Rings row ──
  const ringsEl = document.getElementById('dash-rings');
  if (ringsEl) {
    const rings = [
      { emoji:'💊', label:'Remédios', val: byType.med ? `${doneByType.med}/${byType.med}` : '—', color:'var(--blue-600)', bg:'var(--blue-50)', accent:'#378add' },
      { emoji:'🦾', label:'Fisio',    val: byType.fisio ? `${doneByType.fisio}/${byType.fisio}` : '—', color:'var(--amber-600)', bg:'var(--amber-50)', accent:'#ba7517' },
      { emoji:'🏃', label:'Exercício', val: byType.exer ? `${doneByType.exer}/${byType.exer}` : '—', color:'var(--teal-600)', bg:'var(--teal-50)', accent:'#1d9e75' },
    ];
    ringsEl.innerHTML = rings.map(r => `
      <div class="health-ring-card" style="--card-accent:${r.accent}">
        <div style="font-size:24px">${r.emoji}</div>
        <div class="health-ring-val" style="color:${r.color}">${r.val}</div>
        <div class="health-ring-label">${r.label}</div>
      </div>
    `).join('');
  }

  // ── Trend cards ──
  const trendsEl = document.getElementById('dash-trends');
  if (trendsEl) {
    const categories = [
      { key:'med',   emoji:'💊', label:'Remédios',    color:'var(--blue-600)',   bg:'var(--blue-50)',   fill:'#378add' },
      { key:'fisio', emoji:'🦾', label:'Fisioterapia', color:'var(--amber-600)',  bg:'var(--amber-50)',  fill:'#ba7517' },
      { key:'exer',  emoji:'🏃', label:'Exercícios',   color:'var(--teal-600)',   bg:'var(--teal-50)',   fill:'#1d9e75' },
    ];

    // Compute last 7 days for each category
    const getLast7 = (type) => {
      const arr = [];
      for (let i=6; i>=0; i--) {
        const d = new Date(); d.setDate(d.getDate()-i);
        const ds = d.toISOString().split('T')[0];
        const dayTasks = (JSON.parse(localStorage.getItem('cuidarbem_tasks') || '[]')).filter(t => {
          if (t.type !== type) return false;
          if (t.date === ds) return true;
          if (t.repeat === 'daily') return true;
          return false;
        });
        const total = dayTasks.length;
        const done = dayTasks.filter(t => completionsData[`${t.id}_${ds}`]).length;
        arr.push({ total, done, pct: total ? Math.round(done/total*100) : 0 });
      }
      return arr;
    };

    trendsEl.innerHTML = categories.map(cat => {
      const history = getLast7(cat.key);
      const todayPct = history[6].pct;
      const yesterdayPct = history[5].pct;
      const diff = todayPct - yesterdayPct;
      const changeClass = diff > 0 ? 'up' : diff < 0 ? 'down' : 'neutral';
      const changeLabel = diff > 0 ? `↑${diff}%` : diff < 0 ? `↓${Math.abs(diff)}%` : '—';
      const maxPct = Math.max(...history.map(h => h.pct), 10);

      return `
      <div class="health-trend-card">
        <div class="health-trend-icon" style="background:${cat.bg}">${cat.emoji}</div>
        <div class="health-trend-info">
          <div class="health-trend-title">${cat.label}</div>
          <div class="health-trend-sub">7 dias</div>
          <div class="mini-chart">
            ${history.map(h => `<div class="mini-bar" style="height:${Math.round((h.pct/maxPct)*100)}%;background:${cat.fill};opacity:${0.3 + 0.7*(h.pct/maxPct)}"></div>`).join('')}
          </div>
        </div>
        <div class="health-trend-right">
          <div class="health-trend-pct" style="color:${cat.color}">${todayPct}%</div>
          <div class="health-trend-change ${changeClass}">${changeLabel}</div>
        </div>
      </div>`;
    }).join('');
  }

  // ── Weekly summary ──
  const weeklyEl = document.getElementById('dash-weekly');
  if (weeklyEl) {
    const days = [];
    for (let i=6; i>=0; i--) {
      const d = new Date(); d.setDate(d.getDate()-i);
      const ds = d.toISOString().split('T')[0];
      const allTasks = JSON.parse(localStorage.getItem('cuidarbem_tasks') || '[]').filter(t => {
        if (t.date === ds) return true;
        if (t.repeat === 'daily') return true;
        return false;
      });
      const total = allTasks.length;
      const done = allTasks.filter(t => completionsData[`${t.id}_${ds}`]).length;
      const pct = total ? Math.round(done/total*100) : 0;
      days.push({ d, ds, total, done, pct });
    }
    const maxPct = Math.max(...days.map(d => d.pct), 10);
    const dayNames = ['Dom','Seg','Ter','Qua','Qui','Sex','Sáb'];
    weeklyEl.innerHTML = `
    <div class="health-trend-card" style="flex-direction:column; align-items:stretch; gap:12px">
      <div style="display:flex; justify-content:space-between; align-items:flex-end; height:64px; gap:4px">
        ${days.map(d => {
          const h = Math.round((d.pct/maxPct)*100);
          const color = d.pct >= 80 ? '#1d9e75' : d.pct >= 50 ? '#ba7517' : '#d85a30';
          const isToday = d.ds === today;
          return `<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px">
            <div style="width:100%;border-radius:4px 4px 0 0;background:${color};height:${Math.max(4,h)}%;opacity:${isToday?1:0.6};transition:height 0.5s ease;max-height:52px;min-height:4px"></div>
            <div style="font-size:10px;font-weight:700;color:${isToday?'var(--green-600)':'var(--text-light)'}">${dayNames[d.d.getDay()]}</div>
          </div>`;
        }).join('')}
      </div>
      <div style="display:flex;justify-content:space-between;padding-top:8px;border-top:1px solid var(--gray-100)">
        <div style="font-size:12px;color:var(--text-light)">Melhor dia: <strong style="color:var(--teal-600)">${Math.max(...days.map(d=>d.pct))}%</strong></div>
        <div style="font-size:12px;color:var(--text-light)">Média: <strong style="color:var(--green-600)">${Math.round(days.reduce((s,d)=>s+d.pct,0)/7)}%</strong></div>
      </div>
    </div>`;
  }
}

// Patch goScreen to render dashboard when navigating to it
const _origGoScreen = typeof goScreen === 'function' ? goScreen : null;
if (_origGoScreen) {
  window._patchedGoScreen = true;
}

// Hook into screen navigation to render dashboard
document.addEventListener('DOMContentLoaded', () => {
  // Patch goScreen after original init
  const origGo = window.goScreen;
  if (origGo) {
    window.goScreen = function(name, btn) {
      origGo(name, btn);
      if (name === 'dashboard') renderDashboard();
      if (name === 'home') renderHomeRightPanel();
    };
  }
  // Patch renderAll to also update right panel
  const origRenderAll = window.renderAll;
  if (origRenderAll) {
    window.renderAll = function() {
      origRenderAll();
      renderHomeRightPanel();
    };
  }
  applyA11y();
  // Initial right panel render
  setTimeout(renderHomeRightPanel, 100);
});


document.addEventListener('DOMContentLoaded',function(){
  document.querySelectorAll('.nav-btn').forEach(btn=>{
    btn.addEventListener('click',function(){
      document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));
      this.classList.add('active');

      const target = this.getAttribute('data-screen');
      if(!target) return;

      document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
      const el = document.getElementById(target);
      if(el) el.classList.add('active');
    });
  });
});


// ════════════════════════════════════════════════════════════════════════════
//  CUIDARBEM — FEATURE PACK v2
//  1. Streak counter  2. Haptic  3. Swipe  4. Voice  5. Kiosk  6. Mode
//  7. BP/Glucose  8. PDF export  9. Auto backup  10. Onboarding
//  11. Alarm sound  12. Confirm med with camera photo
// ════════════════════════════════════════════════════════════════════════════

// ── 1. STREAK COUNTER ────────────────────────────────────────────────────────
function calcStreak() {
  let streak = 0;
  const allTasks = JSON.parse(localStorage.getItem('cuidarbem_tasks') || '[]');
  const comp = JSON.parse(localStorage.getItem('cuidarbem_completions') || '{}');
  for (let i = 0; i < 365; i++) {
    const d = new Date(); d.setDate(d.getDate() - i);
    const ds = d.toISOString().split('T')[0];
    const dayTasks = allTasks.filter(t => t.date === ds || t.repeat === 'daily');
    if (!dayTasks.length) { if (i > 0) break; continue; }
    const allDone = dayTasks.every(t => comp[`${t.id}_${ds}`]);
    if (allDone) streak++;
    else if (i > 0) break; // today incomplete is ok, yesterday must be complete
  }
  return streak;
}

function updateStreakBadge() {
  const streak = calcStreak();
  const badge = document.getElementById('streak-badge');
  const count = document.getElementById('streak-count');
  if (badge && count) {
    count.textContent = streak;
    badge.style.display = streak >= 2 ? 'block' : 'none';
  }
}

// ── 2. HAPTIC FEEDBACK ────────────────────────────────────────────────────────
function haptic(pattern = [30]) {
  if ('vibrate' in navigator) navigator.vibrate(pattern);
}

// ── 3. SWIPE BETWEEN SCREENS ─────────────────────────────────────────────────
(function setupSwipe() {
  const screens = ['home','calendar','dashboard','ocr','reports','appt','profile'];
  let startX = 0, startY = 0;

  document.addEventListener('touchstart', e => {
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
  }, { passive: true });

  document.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - startX;
    const dy = e.changedTouches[0].clientY - startY;
    if (Math.abs(dx) < 60 || Math.abs(dy) > Math.abs(dx) * 0.7) return; // not horizontal enough
    if (document.getElementById('kiosk-overlay').style.display !== 'none') return;

    const active = document.querySelector('.screen.active');
    if (!active) return;
    const activeId = active.id.replace('screen-', '');
    const idx = screens.indexOf(activeId);
    if (idx === -1) return;

    let next = -1;
    if (dx < -60 && idx < screens.length - 1) next = idx + 1;
    if (dx > 60 && idx > 0) next = idx - 1;
    if (next === -1) return;

    const nextName = screens[next];
    const btn = document.getElementById(`nav-${nextName}`);
    if (btn) { haptic([15]); goScreen(nextName, btn); }
  }, { passive: true });
})();



// ── v30. CENTRAL DE ALERTAS DO SININHO ─────────────────────────────────────
function cbSafeDateFromTime(time){
  if (!time || !/^\d{1,2}:\d{2}$/.test(time)) return null;
  const [h,m] = time.split(':').map(Number);
  const d = new Date(); d.setHours(h, m, 0, 0);
  return d;
}
function cbMinutesDiffFromNow(time){
  const d = cbSafeDateFromTime(time);
  if (!d) return null;
  return Math.round((d.getTime() - Date.now()) / 60000);
}
function cbTypeLabel(t){
  const map = { med:'Medicamento', exer:'Exercício', fisio:'Fisioterapia', cons:'Consulta', exam:'Exame' };
  return map[t && t.type] || 'Cuidado';
}
function cbCollectAlerts(){
  const result = { late: [], next: [], warn: [], sync: [] };
  const today = typeof todayStr === 'function' ? todayStr() : new Date().toISOString().split('T')[0];
  const list = (typeof getTodayTasks === 'function' ? getTodayTasks() : (tasks || []).filter(t => t.date === today || t.repeat === 'daily')) || [];
  const pending = list.filter(t => !(typeof isCompletedToday === 'function' ? isCompletedToday(t) : completions[`${t.id}_${today}`]));
  pending.forEach(t => {
    const diff = cbMinutesDiffFromNow(t.time);
    if (diff === null) return;
    if (diff < 0) {
      result.late.push({ task:t, diff, title:t.name, meta:`${cbTypeLabel(t)} atrasado há ${Math.abs(diff)} min • previsto às ${t.time}` });
    } else if (diff <= 60) {
      result.next.push({ task:t, diff, title:t.name, meta: diff === 0 ? `${cbTypeLabel(t)} é agora • ${t.time}` : `${cbTypeLabel(t)} em ${diff} min • ${t.time}` });
    }
  });
  // Receitas/retiradas próximas
  try {
    (tasks || []).filter(t => t.type === 'med').forEach(t => {
      if (typeof getMedStatus !== 'function') return;
      const st = getMedStatus(t);
      if (st.rxExpired) result.warn.push({ task:t, icon:'📄', title:t.name, meta:'Receita vencida. Renove com urgência.' });
      else if (st.rxDays !== null && st.rxDays <= 14) result.warn.push({ task:t, icon:'📄', title:t.name, meta:`Receita vence em ${st.rxDays} dia${st.rxDays!==1?'s':''}.` });
      if (st.pickupDays !== null && st.pickupDays <= 5) result.warn.push({ task:t, icon:'🏥', title:t.name, meta: st.pickupDays <= 0 ? 'Retirada do medicamento é hoje ou já passou.' : `Retirada do medicamento em ${st.pickupDays} dia${st.pickupDays!==1?'s':''}.` });
    });
  } catch(e) {}
  // Sincronização familiar
  try {
    const fam = JSON.parse(localStorage.getItem('cb_family_sync') || localStorage.getItem('cuidarbem_family_sync') || '{}');
    const last = fam.lastSync || fam.last_sync || localStorage.getItem('cuidarbem_last_sync') || '';
    if (last) result.sync.push({ icon:'🔄', title:'Sincronização familiar', meta:'Última sincronização: agora ou recentemente.' });
    else result.sync.push({ icon:'🔄', title:'Sincronização familiar', meta:'Sem registro recente. Use Forçar envio se necessário.' });
  } catch(e) {
    result.sync.push({ icon:'🔄', title:'Sincronização familiar', meta:'Status não identificado.' });
  }
  result.late.sort((a,b)=>a.diff-b.diff);
  result.next.sort((a,b)=>a.diff-b.diff);
  return result;
}
function cbAlertCount(){
  const a = cbCollectAlerts();
  return a.late.length + a.warn.length;
}
function updateAlertsBell(){
  const btn = document.querySelector('.mobile-bell-btn');
  if (!btn) return;
  const count = cbAlertCount();
  btn.classList.toggle('has-alerts', count > 0);
  btn.setAttribute('title', count > 0 ? `${count} alerta${count>1?'s':''} importante${count>1?'s':''}` : 'Central de alertas');
}
function renderAlertsCenter(){
  const summary = document.getElementById('alerts-center-summary');
  const listEl = document.getElementById('alerts-center-list');
  const sub = document.getElementById('alerts-center-sub');
  if (!summary || !listEl) return;
  const a = cbCollectAlerts();
  const pendingTotal = (typeof getTodayTasks === 'function' ? getTodayTasks() : []).filter(t => !(typeof isCompletedToday === 'function' ? isCompletedToday(t) : false)).length;
  summary.innerHTML = `
    <div class="alerts-center-stat"><strong>${a.late.length}</strong><span>Atrasado</span></div>
    <div class="alerts-center-stat"><strong>${a.next.length}</strong><span>Próximos</span></div>
    <div class="alerts-center-stat"><strong>${pendingTotal}</strong><span>Pendentes</span></div>`;
  const rows = [];
  a.late.slice(0,8).forEach(x => rows.push(cbAlertRow('late','⚠️',x.title,x.meta,x.task && x.task.id ? `onclick="closeAlertsCenter();setTimeout(()=>openTaskQuickAction('${x.task.id}'),120)"` : '')));
  a.next.slice(0,5).forEach(x => rows.push(cbAlertRow('next','⏰',x.title,x.meta,x.task && x.task.id ? `onclick="closeAlertsCenter();setTimeout(()=>openTaskQuickAction('${x.task.id}'),120)"` : '')));
  a.warn.slice(0,6).forEach(x => rows.push(cbAlertRow('warn',x.icon || '📌',x.title,x.meta,x.task && x.task.id && typeof openMedInfo === 'function' ? `onclick="closeAlertsCenter();setTimeout(()=>openMedInfo('${x.task.id}'),120)"` : '')));
  a.sync.slice(0,1).forEach(x => rows.push(cbAlertRow('sync',x.icon || '🔄',x.title,x.meta,'')));
  if (!rows.length) {
    listEl.innerHTML = `<div class="alerts-center-empty"><span class="big">✅</span>Tudo tranquilo por aqui.<br>Sem alertas importantes neste momento.</div>`;
    if (sub) sub.textContent = 'Sem alertas importantes neste momento.';
  } else {
    listEl.innerHTML = rows.join('');
    if (sub) sub.textContent = 'Toque em um item para agir ou conferir detalhes.';
  }
  updateAlertsBell();
}
function cbAlertRow(kind, icon, title, meta, actionAttr){
  const hasAction = !!actionAttr;
  return `<div class="alerts-center-item ${kind}">
    <div class="alerts-center-icon">${icon}</div>
    <div class="alerts-center-body">
      <div class="alerts-center-name">${title || 'Alerta'}</div>
      <div class="alerts-center-meta">${meta || ''}</div>
      ${hasAction ? `<button class="alerts-center-action" ${actionAttr}>Abrir cuidado</button>` : ''}
    </div>
  </div>`;
}
function openAlertsCenter(){
  renderAlertsCenter();
  const el = document.getElementById('alerts-center');
  if (el) {
    el.classList.add('open');
    el.setAttribute('aria-hidden','false');
  }
  if (typeof haptic === 'function') haptic([15,35,15]);
}
function closeAlertsCenter(ev){
  if (ev && ev.target && ev.currentTarget && ev.target !== ev.currentTarget) return;
  const el = document.getElementById('alerts-center');
  if (el) {
    el.classList.remove('open');
    el.setAttribute('aria-hidden','true');
  }
}
function openTaskQuickAction(id){
  const t = (tasks || []).find(x => x.id === id);
  if (!t) return;
  if (t.type === 'med' && typeof openMedConfirm === 'function') return openMedConfirm(id);
  if ((t.type === 'cons' || t.type === 'exam') && typeof openSeenModal === 'function') return openSeenModal(id);
  if (typeof toggleTask === 'function') {
    if (!isCompletedToday(t)) toggleTask(id);
    showToast('✅ Cuidado confirmado');
  }
}
setInterval(updateAlertsBell, 60000);
setTimeout(updateAlertsBell, 800);

// ── 4. VOICE SUMMARY ─────────────────────────────────────────────────────────
function speakSummary() {
  if (!('speechSynthesis' in window)) {
    showToast('⚠️ Voz não suportada neste dispositivo');
    return;
  }
  window.speechSynthesis.cancel();
  const today = typeof todayStr === 'function' ? todayStr() : new Date().toISOString().split('T')[0];
  const comp = JSON.parse(localStorage.getItem('cuidarbem_completions') || '{}');
  const allTasks = JSON.parse(localStorage.getItem('cuidarbem_tasks') || '[]');
  const todayTasks = allTasks.filter(t => t.date === today || t.repeat === 'daily');
  const pending = todayTasks.filter(t => !comp[`${t.id}_${today}`]);
  const done = todayTasks.length - pending.length;

  let text = `CuidarBem. Resumo do dia. `;
  text += `${done} de ${todayTasks.length} tarefas concluídas. `;
  if (pending.length === 0) {
    text += 'Parabéns, todas as tarefas de hoje foram concluídas!';
  } else {
    text += `Ainda pendente${pending.length > 1 ? 's' : ''}: `;
    pending.forEach((t, i) => {
      text += `${t.name}${t.time ? ' às ' + t.time : ''}`;
      if (i < pending.length - 1) text += ', ';
    });
    text += '.';
  }

  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'pt-BR';
  utter.rate = 0.9;
  window.speechSynthesis.speak(utter);
  haptic([20, 40, 20]);
  showToast('🔊 Lendo resumo...');
}

// ── 5. KIOSK MODE ─────────────────────────────────────────────────────────────
function toggleKiosk() {
  const overlay = document.getElementById('kiosk-overlay');
  if (!overlay) return;
  const isOpen = overlay.style.display !== 'none';
  if (isOpen) {
    overlay.style.display = 'none';
    haptic([20]);
  } else {
    renderKiosk();
    overlay.style.display = 'block';
    haptic([30, 50, 30]);
  }
}

function renderKiosk() {
  const today = typeof todayStr === 'function' ? todayStr() : new Date().toISOString().split('T')[0];
  const comp = JSON.parse(localStorage.getItem('cuidarbem_completions') || '{}');
  const allTasks = JSON.parse(localStorage.getItem('cuidarbem_tasks') || '[]');
  const meds = allTasks.filter(t => t.type === 'med' && (t.date === today || t.repeat === 'daily'));
  const settings_ = JSON.parse(localStorage.getItem('cuidarbem_settings') || '{}');

  const nameEl = document.getElementById('kiosk-patient-name');
  const dateEl = document.getElementById('kiosk-date');
  if (nameEl) nameEl.textContent = settings_.patient || 'Paciente';
  if (dateEl) dateEl.textContent = new Date().toLocaleDateString('pt-BR', {weekday:'long', day:'numeric', month:'long'});

  const list = document.getElementById('kiosk-meds-list');
  if (!list) return;
  if (!meds.length) {
    list.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-light)">Nenhum remédio cadastrado hoje.</div>';
    return;
  }
  list.innerHTML = meds.sort((a,b)=>(a.time||'').localeCompare(b.time||'')).map(t => {
    const done = comp[`${t.id}_${today}`];
    return `
    <button class="kiosk-med-btn ${done?'done':''}" onclick="kioskToggle('${t.id}')">
      <div class="k-check">${done ? '✓' : ''}</div>
      <div style="flex:1">
        <div style="font-size:16px;font-weight:800;color:${done?'var(--teal-600)':'var(--text)'}">${t.name}</div>
        <div style="font-size:13px;color:var(--text-light);margin-top:2px">${t.dose||''}${t.time?' · '+t.time:''}</div>
      </div>
      <div style="font-size:22px">${done ? '✅' : '⬜'}</div>
    </button>`;
  }).join('');
}

function kioskToggle(id) {
  haptic([40, 30]);
  if (typeof toggleTask === 'function') toggleTask(id);
  setTimeout(renderKiosk, 100);
}

// ── 6. CAREGIVER / PATIENT MODE ───────────────────────────────────────────────
function toggleCaregiverMode() {
  const btn = document.getElementById('caregiver-toggle');
  const desc = document.getElementById('mode-desc');
  const isCare = btn && btn.classList.contains('on');
  if (btn) btn.classList.toggle('on', !isCare);
  const isPatient = isCare; // flipping
  document.body.classList.toggle('patient-mode', isPatient);
  if (desc) desc.textContent = isPatient ? 'Visão simplificada (paciente ativo)' : 'Exibe todos os dados e controles';
  localStorage.setItem('cb_caregiver_mode', isPatient ? '0' : '1');
  haptic([20]);
  showToast(isPatient ? '👤 Modo paciente ativado' : '👨‍⚕️ Modo cuidador ativado');
}

function loadCaregiverMode() {
  const stored = localStorage.getItem('cb_caregiver_mode');
  const isCare = stored !== '0'; // default: caregiver
  const btn = document.getElementById('caregiver-toggle');
  const desc = document.getElementById('mode-desc');
  if (btn) btn.classList.toggle('on', isCare);
  document.body.classList.toggle('patient-mode', !isCare);
  if (desc) desc.textContent = isCare ? 'Exibe todos os dados e controles' : 'Visão simplificada (paciente ativo)';
}

// Patient mode hides some elements via CSS (add to existing style block)
const patientModeStyle = document.createElement('style');
patientModeStyle.textContent = `
  /* ── Modo Paciente: interface ultra-simplificada ── */

  /* Nav: esconde tudo exceto Início e Perfil */
  body.patient-mode #nav-calendar,
  body.patient-mode #nav-dashboard,
  body.patient-mode #nav-reports,
  body.patient-mode #nav-appt,
  body.patient-mode #nav-ocr { display: none !important; }

  /* Home: esconde filtros, alertas complexos, botão adicionar */
  body.patient-mode .cat-pills { display: none !important; }
  body.patient-mode .btn-add:not(#patient-mode-hint) { display: none !important; }
  body.patient-mode .desktop-right-panel { display: none !important; }
  body.patient-mode #streak-badge { display: none !important; }
  body.patient-mode #alerts-container { display: none !important; }

  /* Tarefas: esconde tudo exceto remédios */
  body.patient-mode .task-item:not([data-type="med"]) { display: none !important; }

  /* Cards de remédio ficam maiores e mais legíveis */
  body.patient-mode .task-item[data-type="med"] .task-name { font-size: 18px !important; }
  body.patient-mode .task-item[data-type="med"] .task-check {
    width: 36px !important; height: 36px !important;
  }
  body.patient-mode .task-item[data-type="med"] .task-time {
    font-size: 16px !important; font-weight: 800 !important;
    color: var(--green-600) !important;
  }

  /* Banner de modo paciente no topo da home */
  body.patient-mode #patient-mode-banner { display: flex !important; }

  /* Badge de modo paciente no header */
  body.patient-mode #patient-mode-header-badge { display: inline-flex !important; }

  /* Perfil: esconde opções avançadas */
  body.patient-mode #profile-advanced-section { display: none !important; }
`;
document.head.appendChild(patientModeStyle);

// ── 7. BP / GLUCOSE TRACKING ──────────────────────────────────────────────────
let currentVitalTab = 'bp';

// ── Classificação Pressão Arterial — SBC 2020 ────────────────────────────
function classifyBP(sys, dia) {
  if (sys < 90 || dia < 60)
    return { label:'Hipotensão', short:'Hipotensão', color:'#378add', bg:'#e6f1fb', emoji:'💙', level:-1 };
  if (sys < 120 && dia < 80)
    return { label:'Ótima', short:'Ótima', color:'#0f6e56', bg:'#e1f5ee', emoji:'💚', level:0 };
  if (sys <= 129 && dia <= 84)
    return { label:'Normal', short:'Normal', color:'#1d9e75', bg:'#e1f5ee', emoji:'✅', level:1 };
  if (sys <= 139 || dia <= 89)
    return { label:'Limítrofe', short:'Limítrofe', color:'#854f0b', bg:'#faeeda', emoji:'🟡', level:2 };
  if (sys <= 159 || dia <= 99)
    return { label:'HAS Estágio 1', short:'HAS 1', color:'#993c1d', bg:'#faece7', emoji:'🟠', level:3 };
  if (sys <= 179 || dia <= 109)
    return { label:'HAS Estágio 2', short:'HAS 2', color:'#a32d2d', bg:'#fcebeb', emoji:'🔴', level:4 };
  return { label:'HAS Estágio 3', short:'HAS 3', color:'#7b1f1f', bg:'#fcebeb', emoji:'🚨', level:5 };
}

// ── Classificação Glicemia — SBD / ADA 2024 ──────────────────────────────
function classifyGluc(val, moment) {
  if (val < 70)
    return { label:'Hipoglicemia', short:'Hipoglicemia', color:'#185fa5', bg:'#e6f1fb', emoji:'💙', level:-1 };
  const fasting = moment === 'jejum';
  const postMeal = ['pos-cafe','pos-almoco','pos-jantar'].includes(moment);
  const preMeal = moment === 'pre-refeicao';

  if (fasting) {
    if (val <= 99)  return { label:'Normal (jejum)',    short:'Normal',      color:'#0f6e56', bg:'#e1f5ee', emoji:'💚', level:0 };
    if (val <= 125) return { label:'Pré-diabetes (jejum)', short:'Pré-DM', color:'#854f0b', bg:'#faeeda', emoji:'⚠️', level:2 };
    return            { label:'Diabetes (jejum)',       short:'DM jejum',    color:'#a32d2d', bg:'#fcebeb', emoji:'🔴', level:4 };
  }
  if (postMeal) {
    if (val < 140)  return { label:'Normal (pós-refeição)',  short:'Normal',  color:'#0f6e56', bg:'#e1f5ee', emoji:'💚', level:0 };
    if (val <= 199) return { label:'Pré-diabetes (pós-ref.)', short:'Pré-DM', color:'#854f0b', bg:'#faeeda', emoji:'⚠️', level:2 };
    return            { label:'Alto — DM (pós-ref.)',   short:'Alto DM',     color:'#a32d2d', bg:'#fcebeb', emoji:'🔴', level:4 };
  }
  if (preMeal) {
    if (val < 100)  return { label:'Normal (pré-ref.)', short:'Normal',      color:'#0f6e56', bg:'#e1f5ee', emoji:'💚', level:0 };
    if (val <= 130) return { label:'Atenção (pré-ref.)',short:'Atenção',     color:'#854f0b', bg:'#faeeda', emoji:'⚠️', level:2 };
    return            { label:'Alto (pré-ref.)',         short:'Alto',        color:'#a32d2d', bg:'#fcebeb', emoji:'🔴', level:4 };
  }
  // outro
  if (val < 140)  return { label:'Normal', short:'Normal', color:'#0f6e56', bg:'#e1f5ee', emoji:'💚', level:0 };
  if (val < 200)  return { label:'Atenção', short:'Atenção', color:'#854f0b', bg:'#faeeda', emoji:'⚠️', level:2 };
  return            { label:'Alto', short:'Alto', color:'#a32d2d', bg:'#fcebeb', emoji:'🔴', level:4 };
}

// ── Pré-visualização ao digitar ──────────────────────────────────────────
function previewBP() {
  const sys = parseInt(document.getElementById('bp-sys').value);
  const dia = parseInt(document.getElementById('bp-dia').value);
  const el = document.getElementById('bp-preview');
  if (!el) return;
  if (!sys || !dia || isNaN(sys) || isNaN(dia)) { el.style.display = 'none'; return; }
  const c = classifyBP(sys, dia);
  el.style.display = 'block';
  el.style.background = c.bg;
  el.style.color = c.color;
  el.textContent = `${c.emoji}  ${sys}/${dia} mmHg — ${c.label}`;
}

function previewGluc() {
  const val = parseInt(document.getElementById('gluc-val').value);
  const moment = document.getElementById('gluc-moment').value;
  const el = document.getElementById('gluc-preview');
  if (!el) return;
  if (!val || isNaN(val)) { el.style.display = 'none'; return; }
  const c = classifyGluc(val, moment);
  el.style.display = 'block';
  el.style.background = c.bg;
  el.style.color = c.color;
  el.textContent = `${c.emoji}  ${val} mg/dL — ${c.label}`;
}

function switchVitalTab(tab, btn) {
  currentVitalTab = tab;
  document.querySelectorAll('.vital-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('vital-form-bp').style.display   = tab === 'bp'   ? 'block' : 'none';
  document.getElementById('vital-form-gluc').style.display = tab === 'gluc' ? 'block' : 'none';
  renderVitalChart();
  renderVitalHistory();
}

function saveVital(type) {
  haptic([30]);
  const vitals = JSON.parse(localStorage.getItem('cb_vitals') || '[]');
  const now = new Date();
  const entry = {
    type, ts: now.toISOString(),
    date: now.toLocaleDateString('pt-BR'),
    time: now.toLocaleTimeString('pt-BR', {hour:'2-digit', minute:'2-digit'})
  };

  if (type === 'bp') {
    const sys = parseInt(document.getElementById('bp-sys').value);
    const dia = parseInt(document.getElementById('bp-dia').value);
    const pulse = parseInt(document.getElementById('bp-pulse').value) || null;
    if (!sys || !dia || sys < 50 || sys > 260 || dia < 30 || dia > 160) {
      showToast('⚠️ Valores inválidos para pressão'); return;
    }
    const cls = classifyBP(sys, dia);
    entry.sys = sys; entry.dia = dia; entry.pulse = pulse;
    entry.label = `${sys}/${dia} mmHg${pulse ? ` · ${pulse}bpm` : ''}`;
    entry.status = `${cls.emoji} ${cls.label}`;
    entry.cls = cls;
    document.getElementById('bp-sys').value = '';
    document.getElementById('bp-dia').value = '';
    document.getElementById('bp-pulse').value = '';
    document.getElementById('bp-preview').style.display = 'none';
  } else {
    const val = parseInt(document.getElementById('gluc-val').value);
    const moment = document.getElementById('gluc-moment').value;
    if (!val || val < 20 || val > 700) { showToast('⚠️ Valor de glicemia inválido'); return; }
    const cls = classifyGluc(val, moment);
    const momentLabels = { jejum:'Jejum', 'pos-cafe':'Pós-café', 'pos-almoco':'Pós-almoço', 'pos-jantar':'Pós-jantar', 'pre-refeicao':'Pré-refeição', outro:'Outro' };
    entry.val = val; entry.moment = moment;
    entry.label = `${val} mg/dL — ${momentLabels[moment] || moment}`;
    entry.status = `${cls.emoji} ${cls.label}`;
    entry.cls = cls;
    document.getElementById('gluc-val').value = '';
    document.getElementById('gluc-preview').style.display = 'none';
  }

  vitals.unshift(entry);
  if (vitals.length > 300) vitals.length = 300;
  localStorage.setItem('cb_vitals', JSON.stringify(vitals));

  const cls = entry.cls;
  showToast(`${cls.emoji} ${type === 'bp' ? 'Pressão' : 'Glicemia'} salva! ${cls.label}`);
  if (cls.level >= 3) haptic([50, 100, 50]);
  renderVitalChart();
  renderVitalHistory();
}

function renderVitalChart() {
  const canvas = document.getElementById('vital-chart');
  if (!canvas) return;
  const vitals = JSON.parse(localStorage.getItem('cb_vitals') || '[]');
  const data = vitals.filter(v => v.type === currentVitalTab).slice(0, 14).reverse();
  if (data.length < 2) { canvas.style.display = 'none'; return; }
  canvas.style.display = 'block';

  const dpr = window.devicePixelRatio || 1;
  const W = canvas.offsetWidth || 320;
  const H = 100;
  canvas.width  = W * dpr;
  canvas.height = H * dpr;
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, W, H);

  const isBP   = currentVitalTab === 'bp';
  const sysVals = isBP ? data.map(d => d.sys) : data.map(d => d.val);
  const diaVals = isBP ? data.map(d => d.dia) : [];
  const allVals = [...sysVals, ...diaVals].filter(Boolean);

  const padL = 28, padR = 8, padT = 14, padB = 18;
  const cW = W - padL - padR;
  const cH = H - padT - padB;

  const minV = Math.max(0, Math.min(...allVals) - 15);
  const maxV = Math.max(...allVals) + 15;

  const toX = i => padL + (i / Math.max(data.length - 1, 1)) * cW;
  const toY = v => padT + cH - ((v - minV) / (maxV - minV || 1)) * cH;

  // Reference lines
  const refs = isBP
    ? [{ v:120, color:'#3da88a', label:'120' }, { v:140, color:'#d85a30', label:'140' }]
    : [{ v:100, color:'#3da88a', label:'100' }, { v:140, color:'#d85a30', label:'140' }];

  refs.forEach(r => {
    if (r.v < minV || r.v > maxV) return;
    ctx.save();
    ctx.strokeStyle = r.color; ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(padL, toY(r.v)); ctx.lineTo(padL + cW, toY(r.v));
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = r.color; ctx.font = `bold 9px sans-serif`; ctx.textAlign = 'right';
    ctx.fillText(r.label, padL - 2, toY(r.v) + 3);
    ctx.restore();
  });

  // Draw diastolic line (BP only)
  if (isBP && diaVals.length) {
    ctx.strokeStyle = '#e24b4a66'; ctx.lineWidth = 1.5; ctx.lineJoin = 'round';
    ctx.beginPath();
    diaVals.forEach((v, i) => i === 0 ? ctx.moveTo(toX(i), toY(v)) : ctx.lineTo(toX(i), toY(v)));
    ctx.stroke();
  }

  // Draw main line (systolic / glucose)
  const lineColor = isBP ? '#e24b4a' : '#ba7517';
  ctx.strokeStyle = lineColor; ctx.lineWidth = 2.5; ctx.lineJoin = 'round';
  ctx.beginPath();
  sysVals.forEach((v, i) => i === 0 ? ctx.moveTo(toX(i), toY(v)) : ctx.lineTo(toX(i), toY(v)));
  ctx.stroke();

  // Dots + values
  sysVals.forEach((v, i) => {
    const cls = isBP ? classifyBP(v, diaVals[i] || 80) : classifyGluc(v, 'outro');
    ctx.fillStyle = cls.color;
    ctx.beginPath(); ctx.arc(toX(i), toY(v), 4, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#444'; ctx.font = `bold 9px sans-serif`; ctx.textAlign = 'center';
    ctx.fillText(v, toX(i), toY(v) - 7);
  });

  // X-axis labels (date)
  ctx.fillStyle = '#888'; ctx.font = `9px sans-serif`; ctx.textAlign = 'center';
  data.forEach((d, i) => {
    if (i % Math.ceil(data.length / 5) === 0 || i === data.length - 1) {
      ctx.fillText(d.date.slice(0, 5), toX(i), H - 4);
    }
  });
}

// ── Paginação e modo de visualização do histórico ─────────────────────────
let vitalHistPage = 0;
const VITAL_PAGE_SIZE = 10;
let vitalHistViewMode = 'cards'; // 'cards' | 'table'

function toggleVitalHistView() {
  vitalHistViewMode = vitalHistViewMode === 'cards' ? 'table' : 'cards';
  const btn = document.getElementById('vital-hist-view-btn');
  if (btn) btn.textContent = vitalHistViewMode === 'cards' ? '📊 Tabela' : '📋 Cards';
  vitalHistPage = 0;
  renderVitalHistory();
}

function renderVitalHistory() {
  const cardsEl = document.getElementById('vital-history');
  const tableEl = document.getElementById('vital-history-table');
  const pageEl  = document.getElementById('vital-hist-pagination');
  if (!cardsEl) return;

  const vitals = JSON.parse(localStorage.getItem('cb_vitals') || '[]');
  const data = vitals.filter(v => v.type === currentVitalTab);

  // Show frequency alert
  renderVitalFreqAlert(data);

  const total = data.length;
  const totalPages = Math.max(1, Math.ceil(total / VITAL_PAGE_SIZE));
  vitalHistPage = Math.min(vitalHistPage, totalPages - 1);
  const pageData = data.slice(vitalHistPage * VITAL_PAGE_SIZE, (vitalHistPage + 1) * VITAL_PAGE_SIZE);

  const momentLabels = { jejum:'Jejum', 'pos-cafe':'Pós-café', 'pos-almoco':'Pós-almoço', 'pos-jantar':'Pós-jantar', 'pre-refeicao':'Pré-ref.', outro:'Outro' };

  // ── CARDS view ──
  if (vitalHistViewMode === 'cards') {
    cardsEl.style.display = 'block';
    tableEl.style.display = 'none';
    if (!total) {
      cardsEl.innerHTML = '<div style="font-size:13px;color:var(--text-light);padding:10px 0;text-align:center">Nenhum registro ainda. Faça sua primeira medição!</div>';
      if (pageEl) pageEl.innerHTML = '';
      return;
    }
    cardsEl.innerHTML = pageData.map(d => {
      const cls = d.cls || (d.type === 'bp' ? classifyBP(d.sys, d.dia) : classifyGluc(d.val, d.moment || 'outro'));
      const detail = d.type === 'bp'
        ? `<strong>${d.sys}/${d.dia}</strong> mmHg${d.pulse ? ` · <span style="color:var(--text-light)">♥ ${d.pulse}</span>` : ''}`
        : `<strong>${d.val}</strong> mg/dL <span style="color:var(--text-light);font-size:11px">${momentLabels[d.moment] || d.moment}</span>`;
      return `<div style="display:flex;align-items:center;gap:8px;padding:9px 0;border-bottom:1px solid var(--gray-100);font-size:13px">
        <div style="width:8px;height:8px;border-radius:50%;background:${cls.color};flex-shrink:0"></div>
        <div style="flex:1;min-width:0">
          <div style="font-weight:700">${detail}</div>
          <div style="font-size:11px;color:var(--text-light)">${d.date} · ${d.time}</div>
        </div>
        <div style="flex-shrink:0;padding:3px 8px;border-radius:8px;font-size:11px;font-weight:800;background:${cls.bg};color:${cls.color}">${cls.short}</div>
      </div>`;
    }).join('');
  } else {
    // ── TABLE view ──
    cardsEl.style.display = 'none';
    tableEl.style.display = 'block';
    if (!total) {
      tableEl.innerHTML = '<div style="font-size:13px;color:var(--text-light);padding:16px;text-align:center">Nenhum registro ainda.</div>';
      if (pageEl) pageEl.innerHTML = '';
      return;
    }
    const isBP = currentVitalTab === 'bp';
    const headers = isBP
      ? `<tr style="background:var(--gray-100)"><th style="padding:8px 10px;text-align:left;font-size:11px;font-weight:800;color:var(--text-muted)">Data</th><th style="padding:8px 6px;text-align:center;font-size:11px;font-weight:800;color:var(--text-muted)">Hora</th><th style="padding:8px 6px;text-align:center;font-size:11px;font-weight:800;color:var(--coral-600)">Sist.</th><th style="padding:8px 6px;text-align:center;font-size:11px;font-weight:800;color:var(--coral-600)">Diast.</th><th style="padding:8px 6px;text-align:center;font-size:11px;font-weight:800;color:var(--text-muted)">Pulso</th><th style="padding:8px 6px;text-align:center;font-size:11px;font-weight:800;color:var(--text-muted)">Status</th></tr>`
      : `<tr style="background:var(--gray-100)"><th style="padding:8px 10px;text-align:left;font-size:11px;font-weight:800;color:var(--text-muted)">Data</th><th style="padding:8px 6px;text-align:center;font-size:11px;font-weight:800;color:var(--text-muted)">Hora</th><th style="padding:8px 6px;text-align:center;font-size:11px;font-weight:800;color:var(--amber-600)">mg/dL</th><th style="padding:8px 6px;text-align:center;font-size:11px;font-weight:800;color:var(--text-muted)">Momento</th><th style="padding:8px 6px;text-align:center;font-size:11px;font-weight:800;color:var(--text-muted)">Status</th></tr>`;
    const rows = pageData.map(d => {
      const cls = d.cls || (d.type === 'bp' ? classifyBP(d.sys, d.dia) : classifyGluc(d.val, d.moment || 'outro'));
      const statusBadge = `<span style="padding:2px 7px;border-radius:6px;font-size:10px;font-weight:800;background:${cls.bg};color:${cls.color}">${cls.emoji} ${cls.short}</span>`;
      if (isBP) {
        return `<tr style="border-top:1px solid var(--gray-100)">
          <td style="padding:7px 10px;font-size:12px;font-weight:700">${d.date}</td>
          <td style="padding:7px 6px;text-align:center;font-size:12px;color:var(--text-light)">${d.time}</td>
          <td style="padding:7px 6px;text-align:center;font-size:13px;font-weight:800;color:var(--coral-600)">${d.sys}</td>
          <td style="padding:7px 6px;text-align:center;font-size:13px;font-weight:800;color:var(--coral-400)">${d.dia}</td>
          <td style="padding:7px 6px;text-align:center;font-size:12px;color:var(--text-light)">${d.pulse || '—'}</td>
          <td style="padding:7px 6px;text-align:center">${statusBadge}</td>
        </tr>`;
      } else {
        return `<tr style="border-top:1px solid var(--gray-100)">
          <td style="padding:7px 10px;font-size:12px;font-weight:700">${d.date}</td>
          <td style="padding:7px 6px;text-align:center;font-size:12px;color:var(--text-light)">${d.time}</td>
          <td style="padding:7px 6px;text-align:center;font-size:13px;font-weight:800;color:var(--amber-600)">${d.val}</td>
          <td style="padding:7px 6px;text-align:center;font-size:11px;color:var(--text-light)">${momentLabels[d.moment] || d.moment || '—'}</td>
          <td style="padding:7px 6px;text-align:center">${statusBadge}</td>
        </tr>`;
      }
    }).join('');
    tableEl.innerHTML = `<table style="width:100%;border-collapse:collapse"><thead>${headers}</thead><tbody>${rows}</tbody></table>`;
  }

  // ── Paginação ──
  if (pageEl) {
    if (totalPages <= 1) { pageEl.innerHTML = ''; return; }
    const prevBtn = vitalHistPage > 0
      ? `<button onclick="vitalHistPage--;renderVitalHistory()" style="padding:5px 12px;border-radius:8px;background:var(--gray-100);color:var(--text-muted);border:none;cursor:pointer;font-family:'Nunito',sans-serif;font-size:12px;font-weight:700">← Anterior</button>` : '';
    const nextBtn = vitalHistPage < totalPages - 1
      ? `<button onclick="vitalHistPage++;renderVitalHistory()" style="padding:5px 12px;border-radius:8px;background:var(--gray-100);color:var(--text-muted);border:none;cursor:pointer;font-family:'Nunito',sans-serif;font-size:12px;font-weight:700">Próximo →</button>` : '';
    const info = `<span style="font-size:12px;color:var(--text-light)">Pág. ${vitalHistPage+1}/${totalPages} · ${total} registros</span>`;
    pageEl.innerHTML = `${prevBtn}${info}${nextBtn}`;
  }
}

// ── Alerta âmbar quando período sugerido foi pulado ───────────────────────
function renderVitalFreqAlert(data) {
  const alertEl = document.getElementById('vital-freq-alert');
  if (!alertEl) return;
  const freq = getVitalFreq();
  const tab = currentVitalTab;
  const freqConfig = tab === 'bp' ? freq.bp : freq.gluc;
  if (!freqConfig || freqConfig.type === 'off') { alertEl.style.display = 'none'; return; }

  // Get interval in days
  let intervalDays = 1;
  if (freqConfig.type === 'daily' || freqConfig.type === 'daily_fasting' || freqConfig.type === 'daily_multi') intervalDays = 1;
  else if (freqConfig.type === '2x_week') intervalDays = 3;
  else if (freqConfig.type === '3x_week') intervalDays = 2;
  else if (freqConfig.type === 'weekly') intervalDays = 7;
  else if (freqConfig.type === 'custom') intervalDays = freqConfig.days || 2;

  if (!data.length) { alertEl.style.display = 'none'; return; }

  const lastEntry = data[0]; // data is sorted newest first
  const lastDate = new Date(lastEntry.ts);
  const now = new Date();
  const diffHours = (now - lastDate) / (1000 * 60 * 60);
  const diffDays = diffHours / 24;

  // Alert if overdue by more than the interval + a tolerance of 0.5 days
  if (diffDays > intervalDays + 0.5) {
    const daysSince = Math.floor(diffDays);
    const typeLabel = tab === 'bp' ? '🩸 Pressão arterial' : '🍬 Glicemia';
    const freqLabel = intervalDays === 1 ? 'diariamente' : `a cada ${intervalDays} dias`;
    alertEl.style.display = 'block';
    alertEl.innerHTML = `⚠️ <strong>${typeLabel}:</strong> última medição há ${daysSince} dia${daysSince !== 1 ? 's' : ''}. Sua frequência sugerida é <strong>${freqLabel}</strong>. Lembre-se de medir!`;
  } else {
    alertEl.style.display = 'none';
  }
}

// ── Configuração de frequência de medições ───────────────────────────────
function getVitalFreq() {
  try {
    return JSON.parse(localStorage.getItem('cb_vital_freq') || '{}');
  } catch(e) { return {}; }
}

function saveVitalFreqData(data) {
  localStorage.setItem('cb_vital_freq', JSON.stringify(data));
}

function openVitalFreqModal() {
  const freq = getVitalFreq();
  const bpSel = document.getElementById('bp-freq-type');
  const glucSel = document.getElementById('gluc-freq-type');
  if (bpSel && freq.bp) {
    bpSel.value = freq.bp.type || 'daily';
    document.getElementById('bp-freq-custom-days').value = freq.bp.days || 2;
  }
  if (glucSel && freq.gluc) {
    glucSel.value = freq.gluc.type || 'daily_fasting';
    document.getElementById('gluc-freq-custom-days').value = freq.gluc.days || 2;
  }
  onBpFreqChange();
  onGlucFreqChange();
  document.getElementById('vital-freq-modal').classList.add('open');
}

function closeVitalFreqModal() {
  document.getElementById('vital-freq-modal').classList.remove('open');
}

function onBpFreqChange() {
  const sel = document.getElementById('bp-freq-type');
  const wrap = document.getElementById('bp-freq-custom-wrap');
  if (wrap) wrap.style.display = sel && sel.value === 'custom' ? 'block' : 'none';
}

function onGlucFreqChange() {
  const sel = document.getElementById('gluc-freq-type');
  const wrap = document.getElementById('gluc-freq-custom-wrap');
  if (wrap) wrap.style.display = sel && sel.value === 'custom' ? 'block' : 'none';
}

function saveVitalFreq() {
  const bpType = document.getElementById('bp-freq-type')?.value || 'daily';
  const bpDays = parseInt(document.getElementById('bp-freq-custom-days')?.value) || 2;
  const glucType = document.getElementById('gluc-freq-type')?.value || 'daily_fasting';
  const glucDays = parseInt(document.getElementById('gluc-freq-custom-days')?.value) || 2;
  saveVitalFreqData({ bp: { type: bpType, days: bpDays }, gluc: { type: glucType, days: glucDays } });
  closeVitalFreqModal();
  showToast('✅ Frequência de medições salva!');
  renderVitalHistory();
}

// ── 8. PDF / PRINT EXPORT ─────────────────────────────────────────────────────
function exportPDF() {
  const today = typeof todayStr === 'function' ? todayStr() : new Date().toISOString().split('T')[0];
  const comp = JSON.parse(localStorage.getItem('cuidarbem_completions') || '{}');
  const allTasks = JSON.parse(localStorage.getItem('cuidarbem_tasks') || '[]');
  const settings_ = JSON.parse(localStorage.getItem('cuidarbem_settings') || '{}');
  const vitals = JSON.parse(localStorage.getItem('cb_vitals') || '[]');

  const todayTasks = allTasks.filter(t => t.date === today || t.repeat === 'daily');
  const typeLabel = { med: 'Remédio', fisio: 'Fisioterapia', exer: 'Exercício', cons: 'Consulta', exam: 'Exame' };

  const lastBPs = vitals.filter(v => v.type === 'bp').slice(0, 5);
  const lastGluc = vitals.filter(v => v.type === 'gluc').slice(0, 5);

  const bpRows = lastBPs.map(v => {
    const cls = v.cls || classifyBP(v.sys, v.dia);
    return `<tr><td>${v.date} ${v.time}</td><td>${v.sys}/${v.dia} mmHg${v.pulse ? ` · ${v.pulse}bpm` : ''}</td><td>${cls.emoji} ${cls.label}</td></tr>`;
  }).join('') || '<tr><td colspan="3">Nenhum registro</td></tr>';
  const glucRows = lastGluc.map(v => {
    const cls = v.cls || classifyGluc(v.val, v.moment || 'outro');
    return `<tr><td>${v.date} ${v.time}</td><td>${v.val} mg/dL</td><td>${v.moment} — ${cls.emoji} ${cls.label}</td></tr>`;
  }).join('') || '<tr><td colspan="3">Nenhum registro</td></tr>';

  const taskRows = todayTasks.map(t => {
    const done = comp[`${t.id}_${today}`];
    const hasProof = done && t.proofPhotos && t.proofPhotos[today];
    return `<tr class="${done?'done':''}"><td>${done?'✓':'○'}</td><td>${typeLabel[t.type]||t.type}</td><td>${t.name}</td><td>${t.dose||'—'}</td><td>${t.time||'—'}</td><td>${hasProof?'📷 Sim':'—'}</td></tr>`;
  }).join('');

  const streak = calcStreak();

  // Perfil médico para o PDF
  const medProfile = JSON.parse(localStorage.getItem('cb_medical_profile') || '{}');
  const profileAge = medProfile.birthday ? calcAge(medProfile.birthday) : null;
  const smokeLabel = {no:'Não fumante', ex:'Ex-fumante', yes:'Fumante'}[medProfile.smoking||'no'];
  const allergyStr = [medProfile.allergyMeds, medProfile.allergyFood, medProfile.allergyOther].filter(Boolean).join(' | ');
  const profileHtml = [
    profileAge ? `<div style="font-size:14px;margin-bottom:2px"><strong>Idade:</strong> ${profileAge} anos</div>` : '',
    medProfile.conditions ? `<div style="font-size:14px;margin-bottom:2px"><strong>Condições:</strong> ${medProfile.conditions}</div>` : '',
    allergyStr ? `<div style="font-size:14px;margin-bottom:2px;color:#a32d2d"><strong>⚠️ Alergias:</strong> ${allergyStr}</div>` : '',
    medProfile.surgeries ? `<div style="font-size:14px;margin-bottom:2px"><strong>Cirurgias:</strong> ${medProfile.surgeries.replace(/\n/g,' ')}</div>` : '',
    `<div style="font-size:14px;margin-bottom:2px"><strong>Tabagismo:</strong> ${smokeLabel}</div>`,
    medProfile.insuranceType === 'conv' && medProfile.convName
      ? `<div style="font-size:14px;margin-bottom:2px"><strong>💳 Convênio:</strong> ${medProfile.convName}${medProfile.convNumber?' · Nº '+medProfile.convNumber:''}${medProfile.convExpiry?' · Val: '+new Date(medProfile.convExpiry+'T00:00:00').toLocaleDateString('pt-BR'):''}</div>`
      : `<div style="font-size:14px;margin-bottom:2px"><strong>🆓 SUS:</strong> ${medProfile.susNumber || 'Número não informado'}</div>`,
    medProfile.emergName ? `<div style="font-size:14px;margin-bottom:2px"><strong>Emergência:</strong> ${medProfile.emergName}${medProfile.emergRel?' ('+medProfile.emergRel+')':''} — ${medProfile.emergPhone||''}</div>` : ''
  ].filter(Boolean).join('');

  const printEl = document.getElementById('print-zone');
  printEl.innerHTML = `
    <h1>💚 CuidarBem — Relatório Médico</h1>
    <div style="font-size:13px;color:#666;margin-bottom:4px">Gerado em: ${new Date().toLocaleString('pt-BR')}</div>
    <div style="font-size:14px;margin-bottom:2px"><strong>Paciente:</strong> ${settings_.patient || '—'}</div>
    <div style="font-size:14px;margin-bottom:2px"><strong>Cuidador(a):</strong> ${settings_.caregiver || '—'}</div>
    <div style="font-size:14px;margin-bottom:2px"><strong>Diagnóstico:</strong> ${settings_.diagnosis || '—'}</div>
    ${profileHtml}
    <div style="font-size:14px"><strong>Sequência atual:</strong> 🔥 ${streak} dias seguidos</div>

    <div class="pr-section">
      <h2>Tarefas de hoje (${today})</h2>
      <table><thead><tr><th></th><th>Tipo</th><th>Tarefa</th><th>Dose</th><th>Horário</th><th>Comprovante</th></tr></thead>
      <tbody>${taskRows || '<tr><td colspan="5">Nenhuma tarefa hoje</td></tr>'}</tbody></table>
    </div>

    <div class="pr-section">
      <h2>Pressão Arterial (últimas medições)</h2>
      <table><thead><tr><th>Data/Hora</th><th>Valor</th><th>Status</th></tr></thead><tbody>${bpRows}</tbody></table>
    </div>

    <div class="pr-section">
      <h2>Glicemia (últimas medições)</h2>
      <table><thead><tr><th>Data/Hora</th><th>Valor</th><th>Momento</th></tr></thead><tbody>${glucRows}</tbody></table>
    </div>

    <div class="pr-footer">CuidarBem v2.0 — Documento gerado automaticamente para uso médico. Não substitui avaliação profissional.</div>
  `;
  showToast('🖨️ Abrindo impressão...');
  haptic([30, 50]);
  setTimeout(() => window.print(), 300);
}


// ── RESUMO DO CUIDADOR + HISTÓRICO RÁPIDO ─────────────────────────────────
function getCareEvents() {
  try { return JSON.parse(localStorage.getItem('cb_care_events') || '[]'); } catch(e) { return []; }
}
function saveCareEvents(items) { localStorage.setItem('cb_care_events', JSON.stringify(items || [])); }
function addCareEvent() {
  const date = document.getElementById('event-date')?.value || todayStr();
  const type = document.getElementById('event-type')?.value || 'outro';
  const desc = (document.getElementById('event-desc')?.value || '').trim();
  if (!desc) { showToast('⚠️ Descreva o evento'); return; }
  const events = getCareEvents();
  events.unshift({ id: uid(), date, type, desc, createdAt: Date.now() });
  saveCareEvents(events.slice(0, 80));
  document.getElementById('event-desc').value = '';
  renderCareEvents();
  renderCaregiverSummary();
  showToast('✅ Evento registrado');
}
function deleteCareEvent(id) {
  if (!confirm('Apagar este evento do histórico?')) return;
  saveCareEvents(getCareEvents().filter(e => e.id !== id));
  renderCareEvents();
  renderCaregiverSummary();
}
function careEventLabel(t) {
  return {queda:'🚨 Queda', ps:'🏥 Pronto-socorro', remedio:'💊 Alteração de remédio', exame:'🔬 Exame importante', sintoma:'⚠️ Sintoma / alerta', outro:'📝 Outro'}[t] || '📝 Outro';
}
function renderCareEvents() {
  const dateEl = document.getElementById('event-date');
  if (dateEl && !dateEl.value) dateEl.value = todayStr();
  const el = document.getElementById('care-event-list');
  if (!el) return;
  const events = getCareEvents().sort((a,b)=>(b.date||'').localeCompare(a.date||'') || (b.createdAt||0)-(a.createdAt||0)).slice(0, 8);
  if (!events.length) { el.innerHTML = '<div class="hist-empty">Nenhum evento registrado ainda.</div>'; return; }
  el.innerHTML = events.map(ev => {
    const d = ev.date ? new Date(ev.date+'T00:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit',year:'2-digit'}) : '—';
    return `<div class="hist-item">
      <div class="hist-icon" style="background:var(--amber-50)">${careEventLabel(ev.type).split(' ')[0]}</div>
      <div class="hist-body">
        <div class="hist-name">${careEventLabel(ev.type)} · ${d}</div>
        <div class="hist-meta" style="font-size:12px;line-height:1.5;color:var(--text-muted)">${ev.desc}</div>
      </div>
      <button onclick="deleteCareEvent('${ev.id}')" style="border:none;background:var(--red-50);color:var(--red-600);border-radius:8px;padding:6px 8px;font-weight:800;cursor:pointer">✕</button>
    </div>`;
  }).join('');
}
function renderCaregiverSummary() {
  const card = document.getElementById('caregiver-summary-card');
  const el = document.getElementById('caregiver-summary-content');
  if (!card || !el) return;
  const today = todayStr();
  const nowMin = new Date().getHours()*60 + new Date().getMinutes();
  const todayTasks = tasks.filter(t => shouldShowToday(t));
  const pending = todayTasks.filter(t => !completions[`${t.id}_${today}`]);
  const lateMeds = pending.filter(t => t.type === 'med' && t.time && (parseInt(t.time.split(':')[0])*60 + parseInt(t.time.split(':')[1]||'0')) < nowMin);
  const next = pending.filter(t => t.time).sort((a,b)=>(a.time||'').localeCompare(b.time||''))[0];
  const p = getProfile();
  const events = getCareEvents().slice(0,3);
  if (!todayTasks.length && !p.importantNotes && !events.length) { card.style.display = 'none'; return; }
  card.style.display = 'block';
  const chips = [
    `<span style="background:${lateMeds.length?'var(--coral-50)':'var(--teal-50)'};color:${lateMeds.length?'var(--coral-600)':'var(--teal-600)'};padding:6px 10px;border-radius:10px;font-size:12px;font-weight:800">${lateMeds.length ? '🚨 '+lateMeds.length+' remédio(s) atrasado(s)' : '✅ Sem remédio atrasado'}</span>`,
    `<span style="background:var(--blue-50);color:var(--blue-600);padding:6px 10px;border-radius:10px;font-size:12px;font-weight:800">📋 ${pending.length} pendência(s)</span>`
  ].join('');
  el.innerHTML = `
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">${chips}</div>
    ${next ? `<div style="font-size:13px;color:var(--text-muted);margin-bottom:8px"><strong>Próximo:</strong> ${next.time} — ${next.name}</div>` : ''}
    ${p.importantNotes ? `<div style="background:var(--amber-50);color:var(--amber-600);border-radius:10px;padding:9px 10px;font-size:12px;font-weight:700;line-height:1.5;margin-bottom:8px">📌 ${p.importantNotes}</div>` : ''}
    ${events.length ? `<div style="font-size:12px;color:var(--text-muted);line-height:1.6"><strong>Últimos eventos:</strong><br>${events.map(e => `• ${new Date((e.date||today)+'T00:00:00').toLocaleDateString('pt-BR')} — ${careEventLabel(e.type)}: ${e.desc}`).join('<br>')}</div>` : ''}
  `;
}
function exportBackupJSON() {
  const snap = buildSnapshot();
  const name = `CuidarBem-backup-${new Date().toISOString().slice(0,10)}.json`;
  const blob = new Blob([JSON.stringify(snap, null, 2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click();
  setTimeout(()=>{ URL.revokeObjectURL(a.href); a.remove(); }, 500);
  showToast('💾 Backup completo exportado');
}
function importBackupJSON(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    try {
      const snap = JSON.parse(e.target.result);
      if (!snap || !snap.tasks || !snap.settings) throw new Error('Arquivo inválido');
      const ts = snap.ts ? new Date(snap.ts).toLocaleString('pt-BR') : 'data desconhecida';
      if (!confirm(`Importar backup de ${ts}?\n\nIsso substituirá os dados atuais deste aparelho.`)) return;
      applySnapshot(snap);
      localStorage.setItem('cb_auto_backup', JSON.stringify(snap));
      loadSettings();
      renderAll();
      showToast('✅ Backup importado com sucesso');
    } catch(err) { showToast('❌ Backup inválido'); console.warn(err); }
    event.target.value = '';
  };
  reader.readAsText(file);
}

// ── 9. BACKUP — LOCAL + JSONBIN.IO NUVEM ──────────────────────────────────────
//
//  Arquitetura de dois níveis:
//    Nível 1 — localStorage  (instantâneo, sempre disponível, sem rede)
//    Nível 2 — JSONbin.io    (nuvem, sobrevive limpeza de cache, compartilhável)
//
//  Fluxo:
//    • A cada 5 min  → salva local (rápido, silencioso)
//    • A cada 30 min → envia para JSONbin SE a chave API estiver configurada
//    • Botão "Salvar na nuvem agora" → força envio imediato + feedback visual
//    • Botão "Restaurar da nuvem"   → busca o bin mais recente e aplica
//    • Primeiro uso                 → cria um bin novo automaticamente (POST)
//    • Usos seguintes               → atualiza o mesmo bin (PUT)
//
//  Configuração necessária pelo usuário:
//    1. Criar conta grátis em jsonbin.io
//    2. Gerar uma Master Key (ou Access Key) em Account > API Keys
//    3. Colar a chave no campo de configuração do app
//
// ─────────────────────────────────────────────────────────────────────────────

const JSONBIN_API = 'https://api.jsonbin.io/v3';
let autoBackupInterval  = null;
let cloudBackupInterval = null;

// ── Helpers de estado ──────────────────────────────────────────────────────

function getJsonbinKey()   { return localStorage.getItem('cb_jsonbin_key')   || ''; }
function getJsonbinBinId() { return localStorage.getItem('cb_jsonbin_bin_id') || ''; }

function setJsonbinKey(k)     { localStorage.setItem('cb_jsonbin_key',    k.trim()); }
function setJsonbinBinId(id)  { localStorage.setItem('cb_jsonbin_bin_id', id.trim()); }

function buildSnapshot() {
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

// ── Nível 1 — Backup local ─────────────────────────────────────────────────

function doLocalBackup() {
  const snap = buildSnapshot();
  localStorage.setItem('cb_auto_backup', JSON.stringify(snap));
  _updateBackupUI({ local: snap.ts });
}

// ── Nível 2 — JSONbin.io ───────────────────────────────────────────────────

async function doCloudBackup({ silent = false } = {}) {
  const key = getJsonbinKey();
  if (!key) {
    if (!silent) showToast('⚠️ Configure a chave JSONbin primeiro');
    return false;
  }

  const snap    = buildSnapshot();
  const binId   = getJsonbinBinId();
  const url     = binId ? `${JSONBIN_API}/b/${binId}` : `${JSONBIN_API}/b`;
  const method  = binId ? 'PUT' : 'POST';
  const headers = {
    'Content-Type'   : 'application/json',
    'X-Master-Key'   : key,
    'X-Bin-Private'  : 'true',
    ...(method === 'POST' ? { 'X-Bin-Name': `CuidarBem-${settings.patient || 'backup'}` } : {}),
  };

  _setCloudStatus('syncing');
  try {
    const res  = await fetch(url, { method, headers, body: JSON.stringify(snap) });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || `HTTP ${res.status}`);
    }
    const data = await res.json();

    // Na primeira vez guarda o bin ID gerado
    if (method === 'POST' && data.metadata?.id) {
      setJsonbinBinId(data.metadata.id);
    }

    // Guarda snapshot local como cache do que está na nuvem
    localStorage.setItem('cb_auto_backup', JSON.stringify(snap));
    _updateBackupUI({ local: snap.ts, cloud: snap.ts });
    _setCloudStatus('ok');
    if (!silent) showToast('☁️ Backup salvo na nuvem!');
    haptic([20, 40]);
    return true;

  } catch (e) {
    _setCloudStatus('error');
    if (!silent) showToast(`❌ Falha no backup: ${e.message}`);
    console.warn('[CuidarBem] Cloud backup error:', e);
    return false;
  }
}

async function doCloudRestore() {
  const key   = getJsonbinKey();
  const binId = getJsonbinBinId();

  if (!key)   { showToast('⚠️ Configure a chave JSONbin primeiro'); return; }
  if (!binId) { showToast('⚠️ Nenhum backup na nuvem encontrado. Salve primeiro.'); return; }

  _setCloudStatus('syncing');
  try {
    const res = await fetch(`${JSONBIN_API}/b/${binId}/latest`, {
      headers: { 'X-Master-Key': key },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const snap = data.record;

    if (!snap?.tasks) throw new Error('Backup inválido ou vazio');

    const ts = new Date(snap.ts).toLocaleString('pt-BR');
    if (!confirm(`Restaurar backup da nuvem de ${ts}?\n\nIsso substituirá TODOS os dados locais.`)) {
      _setCloudStatus('ok');
      return;
    }

    applySnapshot(snap);
    localStorage.setItem('cb_auto_backup', JSON.stringify(snap));
    _updateBackupUI({ local: snap.ts, cloud: snap.ts });
    _setCloudStatus('ok');
    showToast('✅ Dados restaurados da nuvem!');
    haptic([30, 50, 30]);

  } catch (e) {
    _setCloudStatus('error');
    showToast(`❌ Erro ao restaurar: ${e.message}`);
    console.warn('[CuidarBem] Cloud restore error:', e);
  }
}

// Restaurar do backup LOCAL (fallback sem internet)
function restoreBackup() {
  const raw = localStorage.getItem('cb_auto_backup');
  if (!raw) { showToast('⚠️ Nenhum backup local disponível'); return; }
  const snap = JSON.parse(raw);
  const ts   = new Date(snap.ts).toLocaleString('pt-BR');
  if (!confirm(`Restaurar backup local de ${ts}?\nIsso substituirá os dados atuais.`)) return;
  applySnapshot(snap);
  showToast('✅ Backup local restaurado!');
  haptic([30, 50, 30]);
}

// ── UI helpers ─────────────────────────────────────────────────────────────

function _updateBackupUI({ local, cloud } = {}) {
  const localEl = document.getElementById('backup-local-ts');
  const cloudEl = document.getElementById('backup-cloud-ts');
  if (local && localEl) localEl.textContent = new Date(local).toLocaleString('pt-BR');
  if (cloud && cloudEl) cloudEl.textContent = new Date(cloud).toLocaleString('pt-BR');
  // last-backup-desc backward compat
  const desc = document.getElementById('last-backup-desc');
  if (local && desc) desc.textContent = `Local: ${new Date(local).toLocaleTimeString('pt-BR')}`;
}

function _setCloudStatus(state) {
  // state: 'idle' | 'syncing' | 'ok' | 'error'
  const icons  = { idle:'☁️', syncing:'🔄', ok:'✅', error:'❌' };
  const labels = { idle:'Aguardando', syncing:'Sincronizando…', ok:'Sincronizado', error:'Falha' };
  const colors = { idle:'var(--text-light)', syncing:'var(--amber-600)', ok:'var(--teal-600)', error:'var(--coral-600)' };
  const el = document.getElementById('cloud-status-badge');
  if (el) {
    el.textContent = `${icons[state]} ${labels[state]}`;
    el.style.color  = colors[state];
  }
}

// ── Salvar chave JSONbin (chamado pelo input de configuração) ───────────────

function saveJsonbinKey() {
  const input = document.getElementById('jsonbin-key-input');
  if (!input) return;
  const key = input.value.trim();
  if (!key) { showToast('⚠️ Cole a chave antes de salvar'); return; }
  // Validação básica: Master Keys do JSONbin começam com $2b$
  if (!key.startsWith('$2b$') && !key.startsWith('$2a$')) {
    showToast('⚠️ Chave inválida. Deve começar com $2b$…');
    return;
  }
  setJsonbinKey(key);
  input.value = key.slice(0, 8) + '••••••••••••••••••••'; // mascarar
  showToast('🔑 Chave salva! Fazendo primeiro backup…');
  haptic([20]);
  doCloudBackup({ silent: false }); // testa de imediato
}

function clearJsonbinConfig() {
  if (!confirm('Desconectar do JSONbin?\nSeus backups na nuvem não serão apagados, mas o app deixará de sincronizar.')) return;
  localStorage.removeItem('cb_jsonbin_key');
  localStorage.removeItem('cb_jsonbin_bin_id');
  const input = document.getElementById('jsonbin-key-input');
  if (input) input.value = '';
  _setCloudStatus('idle');
  showToast('🔌 JSONbin desconectado');
}

// ── Controle do toggle de backup automático ────────────────────────────────

function toggleAutoBackup(btn) {
  btn.classList.toggle('on');
  const on = btn.classList.contains('on');
  localStorage.setItem('cb_autobackup_on', on ? '1' : '0');
  if (on) {
    _startBackupTimers();
    showToast('☁️ Backup automático ativado');
  } else {
    _stopBackupTimers();
    showToast('☁️ Backup automático desativado');
  }
}

function _startBackupTimers() {
  _stopBackupTimers();
  doLocalBackup();
  autoBackupInterval  = setInterval(doLocalBackup,  5  * 60 * 1000);  // local  a cada  5 min
  cloudBackupInterval = setInterval(() => doCloudBackup({ silent: true }), 30 * 60 * 1000); // nuvem a cada 30 min
}

function _stopBackupTimers() {
  clearInterval(autoBackupInterval);
  clearInterval(cloudBackupInterval);
  autoBackupInterval  = null;
  cloudBackupInterval = null;
}

// ── Inicialização ──────────────────────────────────────────────────────────

function initAutoBackup() {
  const on  = localStorage.getItem('cb_autobackup_on') !== '0'; // default on
  const btn = document.getElementById('autobackup-toggle');
  if (btn) btn.classList.toggle('on', on);

  // Restaurar timestamps da UI
  const snap = localStorage.getItem('cb_auto_backup');
  if (snap) {
    try { _updateBackupUI({ local: JSON.parse(snap).ts }); } catch(e) {}
  }

  // Mascarar chave se já salva
  const key = getJsonbinKey();
  const inp = document.getElementById('jsonbin-key-input');
  if (key && inp) inp.value = key.slice(0, 8) + '••••••••••••••••••••';

  // Status da nuvem
  if (key && getJsonbinBinId()) {
    _setCloudStatus('ok');
    document.getElementById('backup-cloud-ts') &&
      (document.getElementById('backup-cloud-ts').textContent = 'Conectado');
  } else if (key) {
    _setCloudStatus('idle');
  }

  if (on) _startBackupTimers();
}

// ── 10. ONBOARDING ────────────────────────────────────────────────────────────
let obSlide = 0;
const OB_TOTAL = 4;

function initOnboarding() {
  if (localStorage.getItem('cb_onboarded')) return;
  const overlay = document.getElementById('onboarding-overlay');
  if (overlay) overlay.style.display = 'flex';
}

function onboardingNext() {
  obSlide++;
  if (obSlide >= OB_TOTAL) { finishOnboarding(); return; }
  for (let i = 0; i < OB_TOTAL; i++) {
    const s = document.getElementById(`ob-${i}`);
    const d = document.getElementById(`od-${i}`);
    if (s) s.style.display = i === obSlide ? 'block' : 'none';
    if (d) d.classList.toggle('active', i === obSlide);
  }
  const btn = document.getElementById('ob-next-btn');
  if (btn && obSlide === OB_TOTAL - 1) btn.textContent = '✅ Começar!';
  haptic([15]);
}

function finishOnboarding() {
  localStorage.setItem('cb_onboarded', '1');
  const overlay = document.getElementById('onboarding-overlay');
  if (overlay) {
    overlay.style.opacity = '0';
    overlay.style.transition = 'opacity 0.4s';
    setTimeout(() => overlay.style.display = 'none', 400);
  }
  haptic([30, 50, 30]);
}

// ── 11. ALARM SOUND (AudioContext beep) ───────────────────────────────────────
function playAlarmBeep(freq = 880, duration = 0.3) {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain); gain.connect(ctx.destination);
    osc.frequency.value = freq;
    osc.type = 'sine';
    gain.gain.setValueAtTime(0.3, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + duration);
  } catch(e) {}
}

// Patch the existing toggleTask to add haptic + sound + streak update
const _origToggleTask = window.toggleTask;
if (typeof toggleTask === 'function') {
  window.toggleTask = function(id) {
    const key = `${id}_${(typeof todayStr==='function'?todayStr():new Date().toISOString().split('T')[0])}`;
    const wasCompleted = completions[key];
    _origToggleTask(id);
    if (!wasCompleted) {
      haptic([40, 20, 40]);
      playAlarmBeep(660, 0.15);
      setTimeout(() => playAlarmBeep(880, 0.15), 180);
    }
    setTimeout(updateStreakBadge, 200);
  };
}

// Patch checkNotifications to also play sound
const _origCheckNotif = window.checkNotifications;
if (typeof checkNotifications === 'function') {
  window.checkNotifications = function() {
    const _origNew = window.Notification;
    window.Notification = function(title, opts) {
      playAlarmBeep(440, 0.2);
      setTimeout(() => playAlarmBeep(660, 0.2), 250);
      haptic([50, 100, 50, 100, 50]);
      return new _origNew(title, opts);
    };
    window.Notification.permission = _origNew.permission;
    window.Notification.requestPermission = _origNew.requestPermission.bind(_origNew);
    _origCheckNotif();
    window.Notification = _origNew;
  };
}

// ── 12. CONFIRM MED WITH CAMERA PHOTO ────────────────────────────────────────
// Patch confirmTake to offer camera capture after confirmation
const _origConfirmTake = window.confirmTake;
if (typeof confirmTake === 'function') {
  window.confirmTake = function() {
    _origConfirmTake();
    // After confirming, show optional camera prompt
    setTimeout(() => {
      const taskId = pendingConfirmId; // captured before it clears
      // already handled by existing photo modal — no extra needed
    }, 100);
  };
}

// ── INIT ALL NEW FEATURES ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  updateStreakBadge();
  loadCaregiverMode();
  initAutoBackup();
  initOnboarding();

  // Fechar Modo SAMU com Escape
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && document.getElementById('samu-overlay')?.classList.contains('open')) {
      closeSamuMode();
    }
  });

  // Patch renderAll to also update streak + trigger local backup
  const _origRA = window.renderAll;
  if (_origRA) {
    window.renderAll = function() {
      _origRA();
      updateStreakBadge();
      // Salvar snapshot local sempre que os dados mudam
      doLocalBackup();
    };
  }

  // Init vital chart when dashboard opens (patch goScreen)
  const _origGS = window.goScreen;
  if (_origGS) {
    window.goScreen = function(name, btn) {
      _origGS(name, btn);
      if (name === 'dashboard') {
        setTimeout(() => {
          renderVitalChart();
          renderVitalHistory();
        }, 100);
      }
      if (name === 'profile') {
        setTimeout(() => renderHistTab(currentHistTab || 'cons'), 100);
      }
    };
  }
});


function r(min,max){return Math.floor(Math.random()*(max-min+1))+min}
function updateVitals(){
  const hr=document.querySelector('#vital-hr .vital-value');
  if(!hr) return;
  hr.textContent=r(60,100);
  document.querySelector('#vital-bp .vital-value').textContent=r(110,140)+"/"+r(70,90);
  document.querySelector('#vital-o2 .vital-value').textContent=r(95,100)+"%";
  document.querySelector('#vital-temp .vital-value').textContent=(36+Math.random()).toFixed(1)+"°";
}
setInterval(updateVitals,2000);
updateVitals();


function salvarVitais(){
  const p = {
    bpm: Number(document.getElementById('input-bpm').value),
    sistolica: Number(document.getElementById('input-sis').value),
    diastolica: Number(document.getElementById('input-dia').value),
    o2: Number(document.getElementById('input-o2').value),
    temp: Number(document.getElementById('input-temp').value),
    data: new Date().toISOString()
  };

  let historico = JSON.parse(localStorage.getItem('paciente')) || [];
  historico.push(p);
  localStorage.setItem('paciente', JSON.stringify(historico));

  atualizarUIReal(p);
  renderHistorico();
}

function carregarUltimo(){
  const historico = JSON.parse(localStorage.getItem('paciente')) || [];
  if(historico.length){
    atualizarUIReal(historico[historico.length-1]);
  }
}

function atualizarUIReal(p){
  if(!document.getElementById('vital-hr')) return;

  document.querySelector('#vital-hr .vital-value').textContent = p.bpm;
  document.querySelector('#vital-bp .vital-value').textContent = p.sistolica+"/"+p.diastolica;
  document.querySelector('#vital-o2 .vital-value').textContent = p.o2+"%";
  document.querySelector('#vital-temp .vital-value').textContent = p.temp+"°";
}

function renderHistorico(){
  const lista = document.getElementById('historico-lista');
  if(!lista) return;

  const dados = JSON.parse(localStorage.getItem('paciente')) || [];

  lista.innerHTML = dados.slice(-5).reverse().map(p => `
    <div style="font-size:12px;margin-bottom:6px;">
      ${p.bpm} BPM | ${p.sistolica}/${p.diastolica} | ${p.o2}% | ${p.temp}°
    </div>
  `).join('');
}

carregarUltimo();
renderHistorico();


function pararAudio(){
  if ('speechSynthesis' in window){
    speechSynthesis.cancel();
  }
  document.querySelectorAll('audio').forEach(a=>{
    a.pause();
    a.currentTime = 0;
  });
}

function falar(texto){
  if (!('speechSynthesis' in window)) return;

  speechSynthesis.cancel();

  const msg = new SpeechSynthesisUtterance(texto);
  msg.lang = 'pt-BR';
  speechSynthesis.speak(msg);
}


// ── Ponte local para sincronização em nuvem (Supabase Realtime) ─────────────
window.cbCollectSnapshot = function cbCollectSnapshot() {
  return {
    version: 24,
    app: 'CuidarBem',
    ts: new Date().toISOString(),
    tasks      : localStorage.getItem('cuidarbem_tasks')       || '[]',
    completions: localStorage.getItem('cuidarbem_completions') || '{}',
    settings   : localStorage.getItem('cuidarbem_settings')    || '{}',
    profile    : localStorage.getItem('cb_medical_profile')    || '{}',
    careEvents : localStorage.getItem('cb_care_events')        || '[]',
    vitals     : localStorage.getItem('cb_vitals')             || '[]',
    vitalFreq  : localStorage.getItem('cb_vital_freq')         || '{}',
    a11y       : localStorage.getItem('cuidarbem_a11y')        || '{}',
    paciente   : localStorage.getItem('paciente')              || '[]'
  };
};

window.cbApplySnapshot = function cbApplySnapshot(snap, opts = {}) {
  if (!snap || !snap.tasks || !snap.completions) return false;
  localStorage.setItem('cuidarbem_tasks',       snap.tasks);
  localStorage.setItem('cuidarbem_completions', snap.completions);
  if (snap.settings)   localStorage.setItem('cuidarbem_settings', snap.settings);
  if (snap.profile)    localStorage.setItem('cb_medical_profile', snap.profile);
  if (snap.careEvents) localStorage.setItem('cb_care_events', snap.careEvents);
  if (snap.vitals)     localStorage.setItem('cb_vitals', snap.vitals);
  if (snap.vitalFreq)  localStorage.setItem('cb_vital_freq', snap.vitalFreq);
  if (snap.a11y)       localStorage.setItem('cuidarbem_a11y', snap.a11y);
  if (snap.paciente)   localStorage.setItem('paciente', snap.paciente);

  try { tasks = JSON.parse(snap.tasks || '[]'); } catch(e) {}
  try { completions = JSON.parse(snap.completions || '{}'); } catch(e) {}
  try { settings = JSON.parse(snap.settings || '{}'); } catch(e) {}

  if (!opts.silent && typeof showToast === 'function') showToast('🔄 Dados atualizados pela família');
  if (typeof loadSettings === 'function') loadSettings();
  if (typeof renderAll === 'function') renderAll();
  if (typeof buildWeekStrip === 'function') buildWeekStrip();
  if (typeof renderHistorico === 'function') renderHistorico();
  if (typeof carregarUltimo === 'function') carregarUltimo();
  return true;
};

window.cbMarkLocalChange = function cbMarkLocalChange(reason) {
  window.dispatchEvent(new CustomEvent('cb-local-change', { detail: { reason: reason || 'local' } }));
};

(function patchLocalSavesForSupabase(){
  const patch = (name) => {
    const original = window[name];
    if (typeof original !== 'function' || original.__supabasePatched) return;
    const wrapped = function(...args) {
      const result = original.apply(this, args);
      setTimeout(() => window.cbMarkLocalChange(name), 80);
      if (typeof window.cbSupabaseQueuePush === 'function') {
        setTimeout(() => window.cbSupabaseQueuePush(name), 120);
      }
      return result;
    };
    wrapped.__supabasePatched = true;
    window[name] = wrapped;
  };
  ['saveTasks','saveSettings','toggleTask','toggleTaskDay','confirmTake','quickTake','confirmSeen','saveProfile','saveCareEvent','deleteCareEvent','saveVital','saveVitalFreqData','saveVitalFreq'].forEach(patch);
})();


// ── Supabase Realtime sync — CuidarBem v24 — auto sync + intelligent alerts ─────────────────
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.49.8';

const SUPABASE_URL = 'https://lwldroopbooeocchgngg.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx3bGRyb29wYm9vZW9jY2hnbmdnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3MDY3MDUsImV4cCI6MjA5MDI4MjcwNX0.fDWYV4yVLqf4j8Bce_o7denInTvJUxWhqcexND4UOyc';

const SB_FAMILY_KEY = 'cb_supabase_family_code';
const SB_MEMBER_KEY = 'cb_supabase_member_name';
const SB_ENABLED_KEY = 'cb_supabase_sync_enabled';

let sb = null, sbChannel = null;
let sbReadyCode = '', sbApplyingRemote = false, sbSaveTimer = null, sbLastRemoteTs = 0;

function normalizeCode(v) {
  return (v || '').toUpperCase().replace(/[^A-Z0-9-]/g,'').replace(/--+/g,'-').slice(0, 28);
}
function prettyCode(raw) {
  const v = normalizeCode(raw);
  if (!v) return '';
  if (v.startsWith('CUIDAR') && !v.startsWith('CUIDAR-')) return 'CUIDAR-' + v.slice(6);
  return v.startsWith('CUIDAR') ? v.replace(/^CUIDAR-?/, 'CUIDAR-') : v;
}
function randomPart(len=5) {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let out = '';
  for (let i=0;i<len;i++) out += chars[Math.floor(Math.random()*chars.length)];
  return out;
}
function genFamilyCode() {
  return 'CUIDAR-' + Math.floor(1000 + Math.random() * 9000) + '-' + randomPart(5);
}
function getSecretFromCode(code) {
  const parts = prettyCode(code).split('-').filter(Boolean);
  return parts.length >= 3 ? parts[parts.length - 1] : '';
}
function setStatus(text, color = 'var(--text-light)', toggleOn = null) {
  const el = document.getElementById('supabase-sync-status');
  if (el) { el.textContent = text; el.style.color = color; }
  const tog = document.getElementById('supabase-sync-toggle');
  if (tog && toggleOn !== null) tog.classList.toggle('on', !!toggleOn);
}
function setLastSync(text) {
  const el = document.getElementById('supabase-last-sync');
  if (el) el.textContent = text;
}
function readSupabaseForm() {
  const familyCode = prettyCode(document.getElementById('supabase-family-code')?.value || '');
  const memberName = document.getElementById('supabase-member-name')?.value.trim() || 'Cuidador/Familiar';
  return { familyCode, memberName };
}
function validateFamilyCode(familyCode) {
  if (!familyCode) throw new Error('Informe ou crie o código da família.');
  if (!getSecretFromCode(familyCode)) throw new Error('Use o código completo, no formato CUIDAR-4829-ABCD.');
}
function saveSupabaseForm() {
  const { familyCode, memberName } = readSupabaseForm();
  if (familyCode) localStorage.setItem(SB_FAMILY_KEY, familyCode);
  localStorage.setItem(SB_MEMBER_KEY, memberName);
  return { familyCode, memberName };
}
function loadSupabaseForm() {
  const fam = document.getElementById('supabase-family-code'); if (fam) fam.value = localStorage.getItem(SB_FAMILY_KEY) || '';
  const mem = document.getElementById('supabase-member-name'); if (mem) mem.value = localStorage.getItem(SB_MEMBER_KEY) || (JSON.parse(localStorage.getItem('cuidarbem_settings') || '{}').caregiver || '');
  const enabled = localStorage.getItem(SB_ENABLED_KEY) === '1';
  setStatus(enabled ? '🟡 Supabase configurado, conectando…' : '⚪ Não conectado ao Supabase', enabled ? 'var(--amber-600)' : 'var(--text-light)', enabled);
}
function ensureSupabase(familyCode) {
  validateFamilyCode(familyCode);
  const secret = getSecretFromCode(familyCode);
  if (sb && sbReadyCode === familyCode) return sb;
  if (sbChannel && sb) { try { sb.removeChannel(sbChannel); } catch(e) {} sbChannel = null; }
  sb = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    global: { headers: { 'x-cb-family-secret': secret } },
    realtime: { params: { eventsPerSecond: 10 } }
  });
  sbReadyCode = familyCode;
  return sb;
}
function buildCloudPayload() {
  const memberName = localStorage.getItem(SB_MEMBER_KEY) || 'Cuidador/Familiar';
  return {
    snapshot: window.cbCollectSnapshot(),
    updated_at_client: new Date().toISOString(),
    updated_by: memberName
  };
}
async function pullState(familyCode, {apply=true, silent=false} = {}) {
  const client = ensureSupabase(familyCode);
  const { data, error } = await client
    .from('cuidarbem_family_state')
    .select('family_code,state,updated_by,updated_at_client,updated_at')
    .eq('family_code', familyCode)
    .maybeSingle();
  if (error) throw error;
  if (data?.state && apply) {
    const remoteTs = Date.parse(data.updated_at_client || data.updated_at || '') || 0;
    sbLastRemoteTs = Math.max(sbLastRemoteTs, remoteTs);
    sbApplyingRemote = true;
    try {
      window.cbApplySnapshot(data.state, { silent });
      setLastSync('Dados recebidos: ' + new Date().toLocaleString('pt-BR') + (data.updated_by ? ' · por ' + data.updated_by : ''));
    } finally {
      setTimeout(() => { sbApplyingRemote = false; }, 1200);
    }
  }
  return data;
}
async function pushStateNow({silent=false} = {}) {
  const { familyCode, memberName } = saveSupabaseForm();
  validateFamilyCode(familyCode);
  const secret = getSecretFromCode(familyCode);
  const client = ensureSupabase(familyCode);
  const payload = buildCloudPayload();
  setStatus('🔄 Enviando dados para a família…', 'var(--amber-600)', true);
  const { error } = await client
    .from('cuidarbem_family_state')
    .upsert({
      family_code: familyCode,
      family_secret: secret,
      state: payload.snapshot,
      updated_by: memberName,
      updated_at_client: payload.updated_at_client
    }, { onConflict: 'family_code' });
  if (error) throw error;
  localStorage.setItem(SB_ENABLED_KEY, '1');
  setStatus('✅ Sincronizado em tempo real', 'var(--teal-600)', true);
  setLastSync('Última sincronização enviada: ' + new Date().toLocaleString('pt-BR'));
  if (sbChannel) {
    sbChannel.send({ type:'broadcast', event:'state-updated', payload: { familyCode, updated_at_client: payload.updated_at_client, updated_by: memberName } }).catch(()=>{});
  }
  if (!silent && typeof showToast === 'function') showToast('☁️ Dados enviados para a família');
}
function queuePush(reason) {
  if (sbApplyingRemote || localStorage.getItem(SB_ENABLED_KEY) !== '1') return;
  const code = localStorage.getItem(SB_FAMILY_KEY);
  if (!code) return;
  clearTimeout(sbSaveTimer);
  const fast = String(reason || '').includes('completions') || String(reason || '').includes('toggleTask') || String(reason || '').includes('quickTake') || String(reason || '').includes('confirmTake');
  sbSaveTimer = setTimeout(() => pushStateNow({silent:true}).catch(err => {
    console.warn('[CuidarBem Supabase] Falha ao sincronizar:', err);
    setStatus('❌ Falha ao sincronizar', 'var(--coral-600)', true);
  }), fast ? 250 : 750);
}
window.cbSupabaseQueuePush = queuePush;

(function installSupabaseAutoStorageSync(){
  if (window.__cbSupabaseAutoStorageSync) return;
  window.__cbSupabaseAutoStorageSync = true;
  const syncKeys = new Set([
    'cuidarbem_tasks',
    'cuidarbem_completions',
    'cuidarbem_settings',
    'cb_medical_profile',
    'cb_care_events',
    'cb_vitals',
    'cb_vital_freq',
    'cuidarbem_a11y',
    'paciente'
  ]);
  const nativeSetItem = Storage.prototype.setItem;
  Storage.prototype.setItem = function(key, value) {
    const oldValue = this === localStorage ? this.getItem(key) : null;
    const result = nativeSetItem.apply(this, arguments);
    try {
      if (this === localStorage && syncKeys.has(key) && oldValue !== String(value)) {
        setTimeout(() => queuePush('localStorage:' + key), 40);
      }
    } catch(e) {}
    return result;
  };
  const nativeRemoveItem = Storage.prototype.removeItem;
  Storage.prototype.removeItem = function(key) {
    const hadValue = this === localStorage && this.getItem(key) !== null;
    const result = nativeRemoveItem.apply(this, arguments);
    try {
      if (this === localStorage && syncKeys.has(key) && hadValue) {
        setTimeout(() => queuePush('localStorage-remove:' + key), 40);
      }
    } catch(e) {}
    return result;
  };
})();
async function startRealtimeListener(familyCode) {
  const client = ensureSupabase(familyCode);
  if (sbChannel) { try { client.removeChannel(sbChannel); } catch(e) {} sbChannel = null; }
  sbChannel = client.channel('cuidarbem-' + familyCode, { config: { broadcast: { self: false } } })
    .on('broadcast', { event: 'state-updated' }, async ({ payload }) => {
      if (!payload || payload.familyCode !== familyCode) return;
      const remoteTs = Date.parse(payload.updated_at_client || '') || 0;
      if (remoteTs && remoteTs <= sbLastRemoteTs) return;
      try {
        await pullState(familyCode, { apply:true, silent:false });
        setStatus('✅ Sincronizado em tempo real', 'var(--teal-600)', true);
      } catch(err) {
        console.warn('[CuidarBem Supabase] Pull after broadcast error:', err);
        setStatus('❌ Falha ao receber atualização', 'var(--coral-600)', true);
      }
    })
    .subscribe(status => {
      if (status === 'SUBSCRIBED') setStatus('✅ Sincronizado em tempo real', 'var(--teal-600)', true);
      if (status === 'CHANNEL_ERROR') setStatus('❌ Canal em tempo real indisponível', 'var(--coral-600)', true);
    });
}

window.createSupabaseFamily = async function createSupabaseFamily() {
  try {
    const famEl = document.getElementById('supabase-family-code');
    if (!famEl.value.trim()) famEl.value = genFamilyCode();
    const { familyCode } = saveSupabaseForm();
    validateFamilyCode(familyCode);
    ensureSupabase(familyCode);
    await pushStateNow({silent:true});
    await startRealtimeListener(familyCode);
    localStorage.setItem(SB_ENABLED_KEY, '1');
    setStatus('✅ Família criada e sincronizada', 'var(--teal-600)', true);
    setLastSync('Código da família: ' + familyCode + ' · compartilhe este código completo');
    if (typeof showToast === 'function') showToast('👨‍👩‍👧 Família criada: ' + familyCode);
  } catch(err) {
    console.warn('[CuidarBem Supabase] create error:', err);
    setStatus('❌ ' + (err.message || err), 'var(--coral-600)', false);
    if (typeof showToast === 'function') showToast('❌ ' + (err.message || err));
  }
};

window.joinSupabaseFamily = async function joinSupabaseFamily() {
  try {
    const { familyCode } = saveSupabaseForm();
    validateFamilyCode(familyCode);
    ensureSupabase(familyCode);
    const current = await pullState(familyCode, { apply:true, silent:true });
    if (!current) await pushStateNow({silent:true});
    await startRealtimeListener(familyCode);
    localStorage.setItem(SB_ENABLED_KEY, '1');
    setStatus('✅ Acompanhamento familiar ativo', 'var(--teal-600)', true);
    if (typeof showToast === 'function') showToast('✅ Sincronização familiar ativa');
  } catch(err) {
    console.warn('[CuidarBem Supabase] join error:', err);
    setStatus('❌ ' + (err.message || err), 'var(--coral-600)', false);
    if (typeof showToast === 'function') showToast('❌ ' + (err.message || err));
  }
};

window.pushSupabaseNow = async function pushSupabaseNow() {
  try { await pushStateNow({silent:false}); }
  catch(err) { setStatus('❌ ' + (err.message || err), 'var(--coral-600)', true); if (typeof showToast === 'function') showToast('❌ ' + (err.message || err)); }
};

window.disconnectSupabaseSync = function disconnectSupabaseSync() {
  if (sbChannel && sb) { try { sb.removeChannel(sbChannel); } catch(e) {} sbChannel = null; }
  localStorage.setItem(SB_ENABLED_KEY, '0');
  setStatus('⚪ Desconectado do modo família', 'var(--text-light)', false);
  setLastSync('Última sincronização: pausada neste aparelho');
  if (typeof showToast === 'function') showToast('☁️ Sincronização pausada');
};

window.toggleSupabaseSync = function toggleSupabaseSync() {
  const enabled = localStorage.getItem(SB_ENABLED_KEY) === '1';
  if (enabled) disconnectSupabaseSync();
  else joinSupabaseFamily();
};

window.addEventListener('cb-local-change', e => queuePush(e.detail?.reason));
window.addEventListener('storage', e => {
  if (['cuidarbem_tasks','cuidarbem_completions','cuidarbem_settings','cb_medical_profile','cb_care_events','cb_vitals','cb_vital_freq','cuidarbem_a11y','paciente'].includes(e.key)) queuePush('storage:' + e.key);
});

loadSupabaseForm();
if (localStorage.getItem(SB_ENABLED_KEY) === '1' && localStorage.getItem(SB_FAMILY_KEY)) {
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
}
