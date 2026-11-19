# -*- coding: utf-8 -*-
import os

SRC = r"D:\stock\make_t_test\index.html"
DST = r"D:\stock\make_t_test_andorid\zuot-build\app\assets\index.html"

with open(SRC, 'r', encoding='utf-8') as f:
    html = f.read()

old = """    const csv = rows.map(r=>r.map(function(c){ return '"'+c+'"'; }).join(',')).join('\\r\\n');
    const blob = new Blob(['\ufeff'+csv], {type:'text/csv;charset=utf-8'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = '做T交易记录_'+fmtDate(Date.now())+'.csv';
    document.body.appendChild(a); a.click(); a.remove();"""

new = """    const csv = rows.map(r=>r.map(function(c){ return '"'+c+'"'; }).join(',')).join('\\r\\n');
    const filename = '做T交易记录_'+fmtDate(Date.now())+'.csv';
    if(window.Android && typeof window.Android.saveCSV === 'function'){
      window.Android.saveCSV('\\uFEFF'+csv, filename);
      return;
    }
    const blob = new Blob(['\ufeff'+csv], {type:'text/csv;charset=utf-8'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a); a.click(); a.remove();"""

if old not in html:
    raise SystemExit('ERROR: exportCSV block not found in source')

html = html.replace(old, new)

os.makedirs(os.path.dirname(DST), exist_ok=True)
with open(DST, 'w', encoding='utf-8') as f:
    f.write(html)
print('patched ->', DST)
