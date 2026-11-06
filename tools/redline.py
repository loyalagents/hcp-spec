"""Rolling redline for HCP v2: the current source against a frozen base (the prior draft's clean source).

Usage:
  python3 -I tools/redline.py BASE_DIR NEW_DIR OUT.docx [options]

  BASE_DIR   frozen source of the prior clean (Draft 2: base/src = Draft 1 as shipped)
  NEW_DIR    working source (title_clean.md, s1.md ... s27.md)
Options:
  --files a.md,b.md   files to include, in order (default: title_clean.md s1.md ... s27.md)
  --cover X.md        clean cover notes placed before the redline (review excerpts); not diffed
  --renames R.tsv     rename table (old<TAB>new, literal; 're:' prefix = regex). Sections whose only
                      change is a rename need no Δ note; the redline still marks every rename.
  --track             Word tracked changes (w:ins/w:del) instead of visual markup
  --tag v2-draft-2    Δ tag this round's notes must carry (default v2-draft-2)
  --base-docx F       shipped prior clean; the reject-all view must equal its text (full builds only)
  --header "..."      page header text

Markup: insertions blue underline, deletions red strike; Δ notes are shaded paragraphs placed after the
passage they explain, written in the source as 'Δ CHANGED (v2-draft-2) --- text' (also NEW, REMOVED,
MOVED). build.py drops Δ lines, so the same source builds the clean.

Self-checks (all must pass; exit 1 otherwise):
  1. accept-all text of the redline == text of the clean build of NEW
  2. reject-all text of the redline == text of the clean build of BASE (and of --base-docx if given)
  3. every Δ note carries this round's tag; no other Δ tag survives (rolling: prior markup dropped)
  4. every changed section carries at least one Δ note (rename-only sections excepted with --renames)
  5. no Δ text and no change markers reach the clean build
"""
import os, re, sys, difflib, zipfile, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hcpdoc
from hcpdoc import INS_ON, INS_OFF, DEL_ON, DEL_OFF

LEGEND_MARK = '\x12'
DEFAULT_FILES = ['title_clean.md'] + [f's{n}.md' for n in range(1, 28)]
DELTA_RE = re.compile(r'^Δ (CHANGED|NEW|REMOVED|MOVED) \(([^)]+)\) --- \S')

# ---------------------------------------------------------------------------------------------
# parse source into units (mirrors hcpdoc.render_body's grammar)

def parse(text):
    src = text.split('\n')
    units, i, first_title = [], 0, True
    while i < len(src):
        line = src[i]
        if not line.strip():
            i += 1; continue
        if line.startswith('Δ '):
            buf = [line.strip()]; i += 1
            while i < len(src) and src[i].strip():
                buf.append(src[i].strip()); i += 1
            units.append({'t': 'delta', 'text': ' '.join(buf)}); continue
        if line.startswith('```{=openxml}'):
            raw = [line]; i += 1
            while not src[i].startswith('```'):
                raw.append(src[i]); i += 1
            raw.append(src[i]); i += 1
            units.append({'t': 'raw', 'lines': raw}); continue
        m = re.match(r'^(#{1,3}) (.*)$', line)
        if m:
            units.append({'t': 'heading', 'lvl': len(m.group(1)), 'text': m.group(2).strip()}); i += 1; continue
        if first_title and line.startswith('**') and line.rstrip().endswith('**') and line.count('**') == 2:
            units.append({'t': 'title', 'text': line.strip()[2:-2]}); first_title = False; i += 1; continue
        if line.startswith('|'):
            rows = []
            while i < len(src) and src[i].startswith('|'):
                rows.append(src[i]); i += 1
            sep = rows.pop(1)
            cells = [[c.strip() for c in re.split(r'(?<!\\)\|', r.strip()[1:-1])] for r in rows]
            units.append({'t': 'table', 'sep': sep, 'rows': cells}); continue
        if line.startswith('    '):
            block = []
            while i < len(src) and (src[i].startswith('    ') or (not src[i].strip() and i + 1 < len(src) and src[i + 1].startswith('    '))):
                block.append(src[i][4:]); i += 1
            units.append({'t': 'code', 'lines': block}); continue
        if re.match(r'^(\d+)\. ', line) or line.startswith('- '):
            items = []
            while i < len(src) and src[i].strip():
                mm = re.match(r'^( *)(\d+\.|-) (.*)$', src[i])
                if not mm:
                    items[-1][1] += ' ' + src[i].strip(); i += 1; continue
                indent, marker, text = mm.groups()
                items.append([indent + marker + ' ', text]); i += 1
            units.append({'t': 'list', 'items': items}); continue
        indented = line.startswith('   ') and not line.startswith('    ')
        buf = [line.strip()]; i += 1
        while i < len(src) and src[i].strip() and not src[i].startswith(('#', '|', '- ', '    ', '```', 'Δ ')) and not re.match(r'^\d+\. ', src[i]):
            buf.append(src[i].strip()); i += 1
        units.append({'t': 'para', 'ind': '   ' if indented else '', 'text': ' '.join(buf)})
    return units


def key(u):
    t = u['t']
    if t in ('para',): return (t, u['ind'], u['text'])
    if t in ('heading',): return (t, u['lvl'], u['text'])
    if t in ('title', 'delta'): return (t, u['text'])
    if t == 'table': return (t, tuple(tuple(r) for r in u['rows']))
    if t == 'code': return (t, tuple(u['lines']))
    if t == 'list': return (t, tuple(tuple(x) for x in u['items']))
    return (t, tuple(u['lines']))


def flat(u):
    t = u['t']
    if t in ('para', 'heading', 'title', 'delta'): return u['text']
    if t == 'table': return '\n'.join(' | '.join(r) for r in u['rows'])
    if t == 'code': return '\n'.join(u['lines'])
    if t == 'list': return '\n'.join(x[1] for x in u['items'])
    return '\n'.join(u['lines'])

# ---------------------------------------------------------------------------------------------
# word-level diff

PROSE_TOK = re.compile(r'`[^`]+`|\*\*[^*]+\*\*|\*[^*\s][^*]*\*|\s+|-{2,3}|\\[\[\]|]|\w(?:[\w\-]|[.:/](?=\w))*|[^\w\s]')
CODE_TOK = re.compile(r'\s+|\w+|[^\w\s]')


def word_diff(a, b, tok=PROSE_TOK):
    """Return b with change markers showing a -> b. Whole tokens only, so markup spans never split."""
    if a == b:
        return b
    ta, tb = tok.findall(a), tok.findall(b)
    assert ''.join(ta) == a and ''.join(tb) == b, 'tokenizer lost text'
    ops = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        ops.append([op, ''.join(ta[i1:i2]), ''.join(tb[j1:j2])])
    # semantic cleanup: fold short equal runs sitting between two changes into the change
    changed = True
    while changed:
        changed = False
        for k in range(1, len(ops) - 1):
            if ops[k][0] == 'equal' and ops[k - 1][0] != 'equal' and ops[k + 1][0] != 'equal':
                s = ops[k][1]
                if not s.strip() or (len(s.strip()) <= 3 and len(tok.findall(s.strip())) <= 1):
                    p, q, n = ops[k - 1], ops[k], ops[k + 1]
                    ops[k - 1:k + 2] = [['replace', p[1] + q[1] + n[1], p[2] + q[2] + n[2]]]
                    changed = True
                    break
    out = []
    for op, x, y in ops:
        if op == 'equal':
            out.append(y)
        else:
            if x: out.append(DEL_ON + x + DEL_OFF)
            if y: out.append(INS_ON + y + INS_OFF)
    return ''.join(out)


def whole(text, on, off):
    return on + text + off if text else text

# ---------------------------------------------------------------------------------------------
# alignment

def sim(a, b):
    if a['t'] != b['t']:
        return 0.0
    if a['t'] == 'para' and a['ind'] != b['ind']:
        return 0.0
    if a['t'] == 'heading' and a['lvl'] != b['lvl']:
        return 0.0
    if a['t'] == 'table' and len(a['rows'][0]) != len(b['rows'][0]):
        return 0.0
    if a['t'] in ('delta', 'raw'):
        return 0.0
    ta, tb = PROSE_TOK.findall(flat(a)), PROSE_TOK.findall(flat(b))
    return difflib.SequenceMatcher(None, ta, tb, autojunk=False).ratio()


def align(A, B, keyf=key, simf=sim, thr=0.45):
    """-> list of (a_or_None, b_or_None). Exact matches by LCS, then DP pairing inside changed runs."""
    out = []
    sm = difflib.SequenceMatcher(None, [keyf(x) for x in A], [keyf(x) for x in B], autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            out += [(A[i], B[j]) for i, j in zip(range(i1, i2), range(j1, j2))]
            continue
        a, b = A[i1:i2], B[j1:j2]
        n, m = len(a), len(b)
        S = [[simf(a[i], b[j]) for j in range(m)] for i in range(n)]
        D = [[0.0] * (m + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                best = max(D[i - 1][j], D[i][j - 1])
                if S[i - 1][j - 1] >= thr:
                    best = max(best, D[i - 1][j - 1] + S[i - 1][j - 1])
                D[i][j] = best
        i, j, seg = n, m, []
        while i > 0 or j > 0:
            if i > 0 and j > 0 and S[i - 1][j - 1] >= thr and abs(D[i][j] - (D[i - 1][j - 1] + S[i - 1][j - 1])) < 1e-12:
                seg.append((a[i - 1], b[j - 1])); i -= 1; j -= 1
            elif i > 0 and (j == 0 or D[i - 1][j] >= D[i][j - 1]):
                seg.append((a[i - 1], None)); i -= 1
            else:
                seg.append((None, b[j - 1])); j -= 1
        out += seg[::-1]
    return out

# ---------------------------------------------------------------------------------------------
# emit annotated source

def emit_unit(u, how, other=None):
    """how: 'same' | 'del' | 'ins' | 'diff' (u = new, other = old). Returns (lines, changed?)."""
    t = u['t']
    W = (lambda s: whole(s, DEL_ON, DEL_OFF)) if how == 'del' else (lambda s: whole(s, INS_ON, INS_OFF)) if how == 'ins' else None
    if how == 'same':
        return render_plain(u), False
    if t == 'delta':
        return [u['text']], False
    if t == 'raw':
        if how == 'del':
            return [], True
        return list(u['lines']), True
    if how in ('del', 'ins'):
        if t == 'para': return [u['ind'] + W(u['text'])], True
        if t == 'heading': return ['#' * u['lvl'] + ' ' + W(u['text'])], True
        if t == 'title': return ['**' + W(u['text']) + '**'], True
        if t == 'list': return [p + W(x) for p, x in u['items']], True
        if t == 'code': return ['    ' + (W(l) if l.strip() else l) for l in u['lines']], True
        if t == 'table':
            rows = ['| ' + ' | '.join(W(c) for c in r) + ' |' for r in u['rows']]
            return [rows[0], u['sep']] + rows[1:], True
    o = other
    if t == 'para': return [u['ind'] + word_diff(o['text'], u['text'])], True
    if t == 'heading': return ['#' * u['lvl'] + ' ' + word_diff(o['text'], u['text'])], True
    if t == 'title': return ['**' + word_diff(o['text'], u['text']) + '**'], True
    if t == 'list':
        lines = []
        def ksim(x, y):
            if x['p'].strip('-0123456789. ') != y['p'].strip('-0123456789. ') or len(x['p']) - len(x['p'].lstrip()) != len(y['p']) - len(y['p'].lstrip()):
                pass
            ta, tb = PROSE_TOK.findall(x['x']), PROSE_TOK.findall(y['x'])
            return difflib.SequenceMatcher(None, ta, tb, autojunk=False).ratio()
        A = [{'p': p, 'x': x} for p, x in o['items']]
        B = [{'p': p, 'x': x} for p, x in u['items']]
        ip = align(A, B, keyf=lambda z: (z['p'].lstrip()[0] == '-', len(z['p']) - len(z['p'].lstrip()), z['x']), simf=ksim, thr=0.4)
        for k, (a, b) in enumerate(ip):
            if a and b:
                lines.append(b['p'] + word_diff(a['x'], b['x']))
            elif a: lines.append(a['p'] + whole(a['x'], DEL_ON, DEL_OFF))
            else: lines.append(b['p'] + whole(b['x'], INS_ON, INS_OFF))
        # numbering follows the first item of the emitted list
        return lines, True
    if t == 'code':
        lines = []
        A = [{'x': l} for l in o['lines']]; B = [{'x': l} for l in u['lines']]
        def csim(x, y):
            return difflib.SequenceMatcher(None, x['x'], y['x'], autojunk=False).ratio()
        for a, b in align(A, B, keyf=lambda z: z['x'], simf=csim, thr=0.5):
            if a and b: lines.append('    ' + word_diff(a['x'], b['x'], CODE_TOK))
            elif a: lines.append('    ' + (whole(a['x'], DEL_ON, DEL_OFF) if a['x'].strip() else a['x']))
            else: lines.append('    ' + (whole(b['x'], INS_ON, INS_OFF) if b['x'].strip() else b['x']))
        return lines, True
    if t == 'table':
        A = [{'r': r} for r in o['rows'][1:]]; B = [{'r': r} for r in u['rows'][1:]]
        def rsim(x, y):
            ta, tb = PROSE_TOK.findall(' | '.join(x['r'])), PROSE_TOK.findall(' | '.join(y['r']))
            return difflib.SequenceMatcher(None, ta, tb, autojunk=False).ratio()
        def row(a, b):
            if a and b: return '| ' + ' | '.join(word_diff(x, y) for x, y in zip(a, b)) + ' |'
            if a: return '| ' + ' | '.join(whole(x, DEL_ON, DEL_OFF) for x in a) + ' |'
            return '| ' + ' | '.join(whole(y, INS_ON, INS_OFF) for y in b) + ' |'
        lines = [row(o['rows'][0], u['rows'][0]), u['sep']]
        for a, b in align(A, B, keyf=lambda z: tuple(z['r']), simf=rsim, thr=0.6):
            lines.append(row(a and a['r'], b and b['r']))
        return lines, True
    raise ValueError(t)


def render_plain(u):
    t = u['t']
    if t == 'para': return [u['ind'] + u['text']]
    if t == 'heading': return ['#' * u['lvl'] + ' ' + u['text']]
    if t == 'title': return ['**' + u['text'] + '**']
    if t == 'delta': return [u['text']]
    if t == 'list': return [p + x for p, x in u['items']]
    if t == 'code': return ['    ' + l for l in u['lines']]
    if t == 'table':
        rows = ['| ' + ' | '.join(r) + ' |' for r in u['rows']]
        return [rows[0], u['sep']] + rows[1:]
    return list(u['lines'])


TRACK = False         # --track: avoid a paragraph ending in an insertion just before a wholly inserted one
INCREMENTAL = False   # --since: the base is an approved snapshot carrying earlier Δ notes
PLAIN_NEW = False     # --plain-new (excerpts only): a wholly new section is shown without insertion markup, under its Δ NEW note

LINE_PREFIX = re.compile(r'^(#{1,3} |\s*(?:\d+\.|-) |    |   )?')
_SEG = re.compile('(' + re.escape(INS_ON) + '.*?' + re.escape(INS_OFF) + '|' + re.escape(DEL_ON) + '.*?' + re.escape(DEL_OFF) + ')', re.S)


def fix_track_adjacency(text):
    """Tracked mode. Some editors read a paragraph that ends in inserted text, followed by a wholly inserted
    paragraph, as one insertion, and rejecting it then removes the first paragraph's break. Wherever that
    pattern occurs, the first paragraph is shown instead as deleted and reinserted whole."""
    lines = text.split('\n')
    def body(l):
        return l[LINE_PREFIX.match(l).end():]
    def wholly_ins(l):
        b = body(l)
        return bool(b) and all(s.startswith(INS_ON) for s in _SEG.findall(b)) and not _SEG.sub('', b).strip()
    def ends_ins_mixed(l):
        b = body(l)
        return b.endswith(INS_OFF) and not wholly_ins(l) and (DEL_ON in b or _SEG.sub('', b).strip())
    out = []
    for i, l in enumerate(lines):
        if l and not l.startswith(('|', 'Δ ', '**', '```')) and ends_ins_mixed(l):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and not lines[j].startswith(('|', 'Δ ', '```')) and wholly_ins(lines[j]):
                pre, b = l[:LINE_PREFIX.match(l).end()], body(l)
                old = _SEG.sub(lambda m: m.group(0)[1:-1] if m.group(0).startswith(DEL_ON) else '', b)
                new = _SEG.sub(lambda m: m.group(0)[1:-1] if m.group(0).startswith(INS_ON) else '', b)
                sep = [''] if pre in ('', '   ') or pre.startswith('#') else []
                out += [pre + whole(old, DEL_ON, DEL_OFF)] + sep + [pre + whole(new, INS_ON, INS_OFF)]
                continue
        out.append(l)
    return '\n'.join(out)


def redline_units(old_text, new_text, changed_only=False, skip=frozenset()):
    """-> (annotated source text, [(section, changed, n_delta)]).
    changed_only: keep only sections with a change or a Δ note, plus level-1 headings (review excerpts)."""
    A, B = parse(old_text), parse(new_text)
    out, secs, cur = [], [], ['(before first heading)', False, 0, []]
    chunks = []          # (section index, is_h1, text)
    def close():
        secs.append(tuple(cur[:3]))
    pairs = align(A, B)
    has_old = set()     # sections holding any unit of the base: not wholly new
    for k, (a, b) in enumerate(pairs):
        u = b or a
        # a section starts at a numbered heading (or a level-1/2 heading) of the new text;
        # unnumbered subheadings and deleted headings stay inside the section around them
        if b is not None and b['t'] == 'heading' and (b['lvl'] <= 2 or re.match(r'^\d', b['text'])):
            close(); cur[:] = [b['text'].translate({ord(c): None for c in hcpdoc.MARKS}), False, 0, []]
        if INCREMENTAL and (a or b)['t'] == 'delta' and not (b and not (a and key(a) == key(b))):
            # an earlier round's Δ note, unchanged or since removed: not shown in an incremental excerpt
            chunks.append((len(secs), False, '')); continue
        if a and not (a.get('text', '').lstrip('*_').startswith(('This document is a working draft', 'DRAFT')) and b and key(a) == key(b)):
            # the closing note moves to whichever section ends the document; it does not make that section old
            has_old.add(len(secs))
        if a and b:
            lines, ch = emit_unit(b, 'same' if key(a) == key(b) else 'diff', a)
        elif a:
            lines, ch = emit_unit(a, 'del')
        else:
            lines, ch = emit_unit(b, 'ins')
            if b['t'] == 'delta':
                cur[2] += 1; ch = False
        cur[1] |= ch
        out.append('\n'.join(lines))
        chunks.append((len(secs), bool(b and b['t'] == 'heading' and b['lvl'] == 1), '\n'.join(lines)))
    close()
    if changed_only:
        keep = {k for k, (s, ch, nd) in enumerate(secs) if (ch or nd) and s not in skip}
        if PLAIN_NEW:
            strip = {ord(INS_ON): None, ord(INS_OFF): None}
            chunks = [(k, h1, txt.translate(strip) if k not in has_old and k in keep and not h1 else txt) for k, h1, txt in chunks]
        out = [txt for k, h1, txt in chunks if k in keep or h1]
    res = '\n\n'.join(out) + '\n'
    return (fix_track_adjacency(res) if TRACK else res), secs

# ---------------------------------------------------------------------------------------------
# docx text views for self-checks

def views(docx):
    """-> (accept-all paragraphs, reject-all paragraphs); Δ and legend paragraphs dropped, empties dropped."""
    x = zipfile.ZipFile(docx).read('word/document.xml').decode('utf-8')
    acc, rej = [], []
    for p in re.findall(r'<w:p>.*?</w:p>|<w:p .*?</w:p>', x, flags=re.S):
        if 'w:fill="FBF1E8"' in p or 'w:fill="EEF3FA"' in p:
            continue
        a = r_ = ''
        for wrap, r in re.findall(r'(<w:ins [^>]*>|<w:del [^>]*>)?(<w:r>.*?</w:r>)', p, flags=re.S):
            t = ''.join(re.findall(r'<w:(?:t|delText)[^>]*>([^<]*)</w:(?:t|delText)>', r))
            ins = wrap.startswith('<w:ins') or ('w:val="%s"' % hcpdoc.INS_COLOR in r and '<w:u w:val="single"/>' in r)
            dele = wrap.startswith('<w:del') or ('w:val="%s"' % hcpdoc.DEL_COLOR in r and '<w:strike w:val="1"/>' in r)
            if not dele: a += t
            if not ins: r_ += t
        if a: acc.append(a)
        if r_: rej.append(r_)
    return acc, rej


def clean_paras(docx):
    return views(docx)[0]

# ---------------------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('base'); ap.add_argument('new'); ap.add_argument('out')
    ap.add_argument('--files'); ap.add_argument('--cover'); ap.add_argument('--renames')
    ap.add_argument('--renumber', action='store_true', help='the base is a moved base (restructure.py --keep-numbers): renumbering counts as a rename, and the shipped prior clean is compared paragraph for paragraph regardless of order')
    ap.add_argument('--track', action='store_true'); ap.add_argument('--tag', default='v2-draft-2')
    ap.add_argument('--base-docx'); ap.add_argument('--template', default='template/template.docx')
    ap.add_argument('--header', default='Human Context Protocol (HCP) v2  |  Draft Specification (redline)  |  October 2026')
    ap.add_argument('--legend', default='Redline against 2.0-draft-1 (clean, as shipped Oct 11, 2026). Inserted text is underlined in blue; deleted text is struck through in red. A Δ note under each changed heading explains the change.')
    ap.add_argument('--keep', help='directory for intermediate files')
    ap.add_argument('--since', action='store_true', help='base is an approved snapshot (incremental review excerpt): earlier Δ notes are hidden; new or revised ones shown')
    ap.add_argument('--skip-rename-only', action='store_true', help='with --changed-only and --renames: leave out sections whose only change is a rename')
    ap.add_argument('--plain-new', action='store_true', help='with --changed-only: show wholly new sections as plain text under their Δ NEW note')
    ap.add_argument('--changed-only', action='store_true', help='review excerpt: only changed sections; views are checked on the full build')
    o = ap.parse_args()
    global INCREMENTAL, TRACK, PLAIN_NEW
    INCREMENTAL = o.since
    PLAIN_NEW = o.plain_new and o.changed_only
    TRACK = o.track
    files = o.files.split(',') if o.files else DEFAULT_FILES
    tmp = o.keep or os.path.join(os.path.dirname(os.path.abspath(o.out)), '.redline_tmp')
    os.makedirs(tmp, exist_ok=True)

    renames = []
    if o.renames:
        for ln in open(o.renames, encoding='utf-8'):
            if ln.strip() and not ln.startswith('#'):
                old, new = ln.rstrip('\n').split('\t')[:2]
                renames.append((old, new))
    if o.renumber:
        import restructure
        heads = set()
        for f in (o.files.split(',') if o.files else DEFAULT_FILES):
            p = os.path.join(o.base, f)
            if os.path.exists(p):
                heads |= set(re.findall(r'^#{1,4} (\d+(?:\.\d+)*)\.? ', open(p, encoding='utf-8').read(), re.M))
    def apply_renames(t):
        if o.renumber:
            t = restructure.renumber(t, heads)
        for old, new in renames:
            t = re.sub(old[3:], new, t) if old.startswith('re:') else t.replace(old, new)
        return t

    read = lambda d, f: open(os.path.join(d, f), encoding='utf-8').read() if os.path.exists(os.path.join(d, f)) else ''
    ok = True
    def check(c, msg):
        nonlocal ok
        print(('PASS ' if c else 'FAIL ') + msg); ok &= bool(c)

    parts, base_parts, new_parts, report = [], [], [], []
    for f in files:
        old, new = read(o.base, f), read(o.new, f)
        if not o.since:
            check(not re.search(r'^Δ ', old, re.M), f'{f}: base carries no Δ notes (rolling redline starts from a clean)')
        ann, secs = redline_units(old, new, o.changed_only)
        if renames or o.renumber:
            _, secs_r = redline_units(apply_renames(old), new)
            subst = {s for s, ch, _ in secs_r if ch}
            if o.skip_rename_only:
                ann, _ = redline_units(old, new, o.changed_only, frozenset(s for s, ch, nd in secs if ch and s not in subst and not nd))
            secs = [(s, ch, nd, ch and s not in subst) for s, ch, nd in secs]
        else:
            secs = [(s, ch, nd, False) for s, ch, nd in secs]
        report += [(f,) + s for s in secs]
        parts.append(ann); base_parts.append(old); new_parts.append(new)

    # legend after the title block (first unit run before the first heading of the first file)
    if files[0] == 'title_clean.md':
        parts[0] = parts[0].rstrip('\n') + '\n\n' + LEGEND_MARK + o.legend + '\n'
    cover = open(o.cover, encoding='utf-8').read().rstrip('\n') + '\n\n' if o.cover else ''
    red_src = cover + '\n'.join(parts)
    open(os.path.join(tmp, 'redline_src.md'), 'w', encoding='utf-8').write(red_src)

    # render: legend lines become a shaded note paragraph
    def build_redline(src, out):
        hcpdoc.build(o.template, src, out, o.header, mode='redline', track=o.track,
                     doc_title='Human Context Protocol (HCP) v2 Draft Specification (redline)')
    # legend handled by replacing the marker line with a Δ-styled paragraph through a raw block
    R0 = hcpdoc.Renderer('redline')
    legend_xml = R0.delta_note(o.legend).replace('w:fill="FBF1E8"', 'w:fill="EEF3FA"').replace('C55A11', '2F5597').replace('843C0C', '1F3864').replace('<w:b w:val="1"/><w:bCs w:val="1"/>', '')
    red_src = red_src.replace(LEGEND_MARK + o.legend, '```{=openxml}\n' + legend_xml + '\n```')
    build_redline(red_src, o.out)

    clean_new = os.path.join(tmp, 'clean_new.docx'); clean_old = os.path.join(tmp, 'clean_base.docx')
    hcpdoc.build(o.template, '\n'.join(new_parts), clean_new, 'x')
    hcpdoc.build(o.template, '\n'.join(base_parts), clean_old, 'x')
    acc, rej = views(o.out)
    if o.changed_only:
        print('NOTE excerpt: accept/reject views are checked on the full build (make_d2.sh)')
    if o.cover:
        cov = clean_paras_from_src(o.template, cover, tmp)
        acc, rej = acc[len(cov):], rej[len(cov):]
    cn, co = clean_paras(clean_new), clean_paras(clean_old)
    if not o.changed_only:
      check(acc == cn, f'accept-all view equals the clean build of the new source ({len(acc)} vs {len(cn)} paragraphs){first_diff(acc, cn)}')
      check(rej == co, f'reject-all view equals the clean build of the base ({len(rej)} vs {len(co)} paragraphs){first_diff(rej, co)}')
    if o.base_docx and o.renumber:
        from collections import Counter
        shipped = clean_paras(o.base_docx)
        check(Counter(rej) == Counter(shipped) if not o.changed_only else True, f'reject-all view holds every paragraph of the shipped prior clean, moved ({len(rej)} vs {len(shipped)})')
    elif o.base_docx:
        check(rej == clean_paras(o.base_docx), 'reject-all view equals the shipped prior clean')

    deltas = re.findall(r'^Δ .*$', '\n'.join(new_parts), re.M)
    bad = [d[:80] for d in deltas if not DELTA_RE.match(d) or DELTA_RE.match(d).group(2) != o.tag]
    check(not bad, f'{len(deltas)} Δ notes, all well-formed and tagged ({o.tag}) {bad[:5]}')
    missing = [(f, s) for f, s, ch, nd, ro in report if ch and nd == 0 and not ro and f != 'title_clean.md']
    check(not missing, f'every changed section has a Δ note (missing: {missing[:10]}{"..." if len(missing) > 10 else ""})')
    xml = zipfile.ZipFile(clean_new).read('word/document.xml').decode('utf-8')
    check('Δ ' not in xml and not re.search('[' + hcpdoc.MARKS + ']', xml), 'clean build carries no Δ notes or change markers')
    changed = [(f, s, nd, ro) for f, s, ch, nd, ro in report if ch]
    print(f'changed sections: {len(changed)}' + (f' (rename-only: {sum(1 for c in changed if c[3])})' if renames or o.renumber else ''))
    for f, s, nd, ro in changed:
        print(f'   {f:15s} {s[:70]:70s} Δ×{nd}{"  rename-only" if ro else ""}')
    print('ALL PASS' if ok else 'FAILURES')
    sys.exit(0 if ok else 1)


def first_diff(a, b):
    for k, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return f'\n      first difference at paragraph {k}:\n      redline: {x[:160]!r}\n      clean:   {y[:160]!r}'
    return '' if len(a) == len(b) else f'\n      lengths differ; extra: {(a[len(b):] or b[len(a):])[:2]!r}'


def clean_paras_from_src(tpl, src, tmp):
    p = os.path.join(tmp, 'cover.docx')
    hcpdoc.build(tpl, src, p, 'x')
    return clean_paras(p)


if __name__ == '__main__':
    main()
