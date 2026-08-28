from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old1="""// Patch goScreen to render dashboard when navigating to it const _origGoScreen = typeof goScreen === 'function' ? goScreen : null; if (_origGoScreen) {   window._patchedGoScreen = true; }  """
if old1 not in s: raise SystemExit('noop goScreen flag block not found')
s=s.replace(old1,'',1)
old2="""// ── 12. CONFIRM MED WITH CAMERA PHOTO ──────────────────────────────────────── // Patch confirmTake to offer camera capture after confirmation const _origConfirmTake = window.confirmTake; if (typeof confirmTake === 'function') {   window.confirmTake = function() {     _origConfirmTake();     // After confirming, show optional camera prompt     setTimeout(() => {       const taskId = pendingConfirmId; // captured before it clears       // already handled by existing photo modal — no extra needed     }, 100);   }; }  """
if old2 not in s: raise SystemExit('noop confirmTake wrapper not found')
s=s.replace(old2,'',1)
old3="""    _origCheckNotif();     window.Notification = _origNew;   }; }"""
new3="""    try {       _origCheckNotif();     } finally {       window.Notification = _origNew;     }   }; }"""
if old3 not in s: raise SystemExit('notification restore anchor not found')
s=s.replace(old3,new3,1)
p.write_text(s,encoding='utf-8')
