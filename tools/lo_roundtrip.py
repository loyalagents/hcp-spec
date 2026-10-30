"""Check a tracked-changes redline in a real editor (LibreOffice): accept-all must equal the new clean,
reject-all the base clean. Usage: python3 -I tools/lo_roundtrip.py REDLINE.docx NEW_CLEAN.docx BASE_CLEAN.docx
Uses tools/lo_accept_reject.py (UNO) and soffice; Δ notes and the legend are ignored."""
import sys, os, subprocess, tempfile, shutil, difflib
here = os.path.dirname(os.path.abspath(__file__))
red, new, base = sys.argv[1:4]
tmp = tempfile.mkdtemp()
def txt(docx, mode=None):
    src = os.path.join(tmp, ('m_' + (mode or 'c')) + '_' + os.path.basename(docx))
    shutil.copy(docx, src)
    out = src[:-5] + '.txt'
    if mode:
        subprocess.run(['python3', os.path.join(here, 'lo_accept_reject.py'), src, out, mode], timeout=170, capture_output=True)
    else:
        subprocess.run(['soffice', '--headless', '--convert-to', 'txt:Text (encoded):UTF8', '--outdir', tmp, src], timeout=170, capture_output=True)
    return [l.strip() for l in open(out, encoding='utf-8-sig').read().split('\n')
            if l.strip() and not l.strip().startswith(('Δ ', 'Redline against'))]
ok = True
for name, a, b in [('accept-all = new clean', txt(red, 'accept'), txt(new)), ('reject-all = base clean', txt(red, 'reject'), txt(base))]:
    d = [x for x in difflib.unified_diff(a, b, lineterm="", n=3) if not x.startswith(('---', '+++', '@@'))]
    dd = [x for x in d if x[:1] in '+-']
    print(('PASS ' if not dd else 'FAIL ') + f'LibreOffice {name} ({len(a)} vs {len(b)} lines, {len(dd)} differences)')
    if dd: print('\n'.join(d[:14]))
    ok &= not dd
shutil.rmtree(tmp)
sys.exit(0 if ok else 1)
