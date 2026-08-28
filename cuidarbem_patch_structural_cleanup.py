from pathlib import Path
import re
p=Path('index.html')
s=p.read_text(encoding='utf-8')
pat1=r"\n// Patch goScreen to render dashboard when navigating to it\nconst _origGoScreen = typeof goScreen === 'function' \? goScreen : null;\nif \(_origGoScreen\) \{\n  window\._patchedGoScreen = true;\n\}\n"
s,n=re.subn(pat1,'\n',s,count=1)
if n!=1: raise SystemExit('noop goScreen flag block not found')
pat2=r"\n// ── 12\. CONFIRM MED WITH CAMERA PHOTO [^\n]*\n// Patch confirmTake to offer camera capture after confirmation\nconst _origConfirmTake = window\.confirmTake;\nif \(typeof confirmTake === 'function'\) \{\n  window\.confirmTake = function\(\) \{\n    _origConfirmTake\(\);\n    // After confirming, show optional camera prompt\n    setTimeout\(\(\) => \{\n      const taskId = pendingConfirmId; // captured before it clears\n      // already handled by existing photo modal — no extra needed\n    \}, 100\);\n  \};\n\}\n"
s,n=re.subn(pat2,'\n',s,count=1)
if n!=1: raise SystemExit('noop confirmTake wrapper not found')
old="""    window.Notification.permission = _origNew.permission;
    window.Notification.requestPermission = _origNew.requestPermission.bind(_origNew);
    _origCheckNotif();
    window.Notification = _origNew;
  };"""
new="""    window.Notification.permission = _origNew.permission;
    window.Notification.requestPermission = _origNew.requestPermission.bind(_origNew);
    try {
      _origCheckNotif();
    } finally {
      window.Notification = _origNew;
    }
  };"""
if old not in s: raise SystemExit('notification restore anchor not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
# trigger structural cleanup workflow v3
