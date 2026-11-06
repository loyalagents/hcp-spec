"""Draft 3 restructure (Group 8, RS1-RS11): move sections into the four-page order, and renumber.

Usage:
  python3 -I tools/restructure.py SRC OUT [--keep-numbers]

SRC  a source directory in the Draft 2 layout (title_clean.md, s1.md ... s27.md; §28 and §29 inside s27.md)
OUT  directory to write the new layout into (FILES below)

--keep-numbers  move only: every block keeps its text and numbers. This is the redline base, so that each
                moved section is compared against its own origin (RS6).
Otherwise every heading and citation is renumbered with renumber() (RS2).

Old -> new, by section number (MAP); top-level sections map as TOP. Run as a module: import restructure.
"""
import os, re, sys

FILES = ['title_clean.md', 'intro.md', 's1.md', 's2.md'] + [f's{n}.md' for n in range(3, 21)] + \
        ['s21.md', 'appa.md', 'refs.md', 'g1.md', 'g2.md', 'g3.md', 'g4.md', 'g5.md', 'path.md']

# Introduction page: Draft 2 §1 subsections in the new order, then 27.2
INTRO = ['1.1', '1.2', '1.9', '1.10', '1.11', '1.3', '1.4', '1.7', '1.5', '1.6', '1.12', '27.2']
MAP = {old: f'I{i}' for i, old in enumerate(INTRO, 1)}
MAP.update({'1.8': 'P2', '27.1': 'P3'})
TOP = {'1': 'Introduction', '2': '1', '21': 'G1', '22': 'G2', '23': 'G3', '24': 'G4', '25': 'Appendix A',
       '26': 'P1', '27': 'P3', '28': '21', '29': 'G5'}
SUB = {'2': '1', '21': 'G1', '22': 'G2', '23': 'G3', '24': 'G4', '25': 'A', '26': 'P1', '28': '21', '29': 'G5'}


def new_number(num, heads):
    """old section number -> new, or None if it is not a mapped section of the old text"""
    if num in MAP:
        return MAP[num]
    top = num.split('.')[0]
    if '.' not in num:
        return TOP.get(num)
    if top in SUB and num in heads:
        return SUB[top] + num[len(top):]
    return None


def blocks(text):
    """split a file into blocks: (heading-number or None, level, text). A block runs to the next heading
    of level 1 or 2."""
    out, cur = [], None
    for line in text.split('\n'):
        m = re.match(r'^(#{1,2}) (?:(\d+(?:\.\d+)*)\.? )?', line)
        if m:
            if cur: out.append(cur)
            cur = [m.group(2), len(m.group(1)), line + '\n']
        else:
            if cur is None: cur = [None, 0, '']
            cur[2] += line + '\n'
    if cur: out.append(cur)
    return [tuple(b) for b in out]


def load(src):
    rd = lambda f: open(os.path.join(src, f), encoding='utf-8').read()
    B = {}          # key -> text
    order = {}      # file -> [keys]
    for n in range(1, 28):
        f = f's{n}.md'
        keys = []
        for num, lvl, txt in blocks(rd(f)):
            if num is None:
                k = f'{f}:{txt.split(chr(10))[0]}'      # a Part heading or leading text
            else:
                k = num if lvl == 2 or '.' in num else num + '#'
            B[k] = txt; keys.append(k)
        order[f] = keys
    # the closing disclaimer travels at the end of the last block of s27.md
    last = order['s27.md'][-1]
    i = B[last].find('*This document is a working draft')
    B['closing'] = B[last][i:]; B[last] = B[last][:i]
    B['title'] = rd('title_clean.md')
    return B, order


def assemble(B, order):
    part = lambda f, head: next(k for k in order[f] if k.startswith(f + ':' + head))
    sub = lambda top: [k for k in B if re.match(rf'^{top}\.\d+$', k)]
    num_sort = lambda ks: sorted(ks, key=lambda k: [int(x) for x in k.split('.')])
    files = {}
    files['title_clean.md'] = B['title']
    get = lambda k: B.get(k, '')
    files['intro.md'] = ''.join([B[part('s1.md', '# Start Here')], B['1#']] + [get(k) for k in INTRO])
    files['s1.md'] = ''.join(B[k] for k in order['s2.md'])
    for n in range(3, 21):
        files[f's{n}.md'] = ''.join(B[k] for k in order[f's{n}.md'])
    files['s21.md'] = ''.join([get('28#')] + [B[k] for k in num_sort(sub('28'))])
    files['appa.md'] = ''.join(B[k] for k in order['s25.md'])
    files['g1.md'] = ''.join(B[k] for k in order['s21.md'])
    for g, n in (('g2', 22), ('g3', 23), ('g4', 24)):
        files[g + '.md'] = ''.join(B[k] for k in order[f's{n}.md'])
    files['g5.md'] = ''.join([get('29#')] + [B[k] for k in num_sort(sub('29'))])
    files['path.md'] = ''.join([B[k] for k in order['s26.md']] + [get('1.8'), B['27#'], B['27.1'], B['closing']])
    used = {k for f in ('s2.md', 's25.md', 's26.md', 's21.md', 's22.md', 's23.md', 's24.md') for k in order[f]}
    used |= {k for n in range(3, 21) for k in order[f's{n}.md']}
    used |= set(INTRO) | {'1#', '1.8', '27#', '27.1', '28#', '29#', 'closing', 'title', part('s1.md', '# Start Here')}
    used |= set(sub('28')) | set(sub('29'))
    missing = [k for k in B if k not in used and B[k].strip()]
    assert not missing, f'blocks not placed: {missing}'
    return files


CODE = re.compile(r'^(    .*|```.*)$')


def renumber(text, heads):
    """rewrite headings and citations from old to new numbers; code lines are left alone"""
    out = []
    for line in text.split('\n'):
        if CODE.match(line):
            out.append(line); continue
        m = re.match(r'^(#{1,4}) (\d+(?:\.\d+)*)(\.?) (.*)$', line)
        if m:
            nn = new_number(m.group(2), heads)
            if nn:
                dot = m.group(3) if not nn.startswith('Appendix') else '.'
                line = f'{m.group(1)} {nn}{dot} {m.group(4)}'
            out.append(line); continue
        out.append(cite(line, heads))
    return '\n'.join(out)


def cite(line, heads):
    # dotted numbers anywhere in prose (not versions such as 2.0-draft-3 or v1.0)
    def dotted(m):
        nn = new_number(m.group(1), heads)
        return nn if nn and '.' in m.group(1) else m.group(0)
    line = re.sub(r'(?<![\w./\-§])(\d+\.\d+(?:\.\d+)*)(?![\w\-]|\.\d)', dotted, line)

    # bare numbers inside a parenthesised citation list: (26), (22, 23), (4.1.1, 25), (2, 3), (21--24)
    def group(m):
        items = re.split(r'(, |; )', m.group(1))
        res = []
        for it in items:
            mm = re.fullmatch(r'(\d+)(--(\d+))?', it)
            if mm and mm.group(1) in TOP:
                a = TOP[mm.group(1)]
                it = a + ('--' + TOP.get(mm.group(3), mm.group(3)) if mm.group(2) else '')
            res.append(it)
        return '(' + ''.join(res) + ')'
    line = re.sub(r'\(([^()]*)\)', group, line)

    # table cells holding section lists: | 2.7, 25 |  | 6.1.6, 24 |
    def cell(m):
        c = m.group(1)
        if ',' not in c: return m.group(0)
        parts = c.split(', ')
        if not all(re.fullmatch(r'\d+(?:\.\d+)*|[IGPA][\d.]+|Appendix A|Introduction|[A-Za-z][\w ]*Profile', p) for p in parts):
            return m.group(0)
        return '| ' + ', '.join(TOP.get(p, p) for p in parts) + ' |'
    line = re.sub(r'\| ([^|]+?) \|(?=$|\s)', cell, line)
    # a few prose forms
    line = re.sub(r'\bSection (2[1-9])\b', lambda m: 'Section ' + TOP[m.group(1)], line)
    line = re.sub(r'\bThe patterns in (24)\b', lambda m: 'The patterns in ' + TOP[m.group(1)], line)
    return line


def old_heads(src):
    hs = set()
    for n in range(1, 28):
        hs |= set(re.findall(r'^#{1,4} (\d+(?:\.\d+)*)\.? ', open(os.path.join(src, f's{n}.md'), encoding='utf-8').read(), re.M))
    return hs


def run(src, out, keep_numbers=False):
    B, order = load(src)
    files = assemble(B, order)
    heads = old_heads(src)
    os.makedirs(out, exist_ok=True)
    for f in FILES:
        t = files.get(f, '')   # s2.md (Terms) and refs.md are new in Group 8b
        if not keep_numbers and f != 'title_clean.md':
            t = renumber(t, heads)
        open(os.path.join(out, f), 'w', encoding='utf-8').write(t.rstrip('\n') + '\n' if t.strip() else '')
    return files


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2], '--keep-numbers' in sys.argv)


# ---------------------------------------------------------------------------------------------
# the inverse: rebuild the Draft 2 layout and numbering from a source in the new layout, so that the
# checks written for the old layout (verify_excerpt.py, check_schemas.py) run unchanged

TOP_INV = {v: k for k, v in TOP.items() if k != '27'}
TOP_INV['P3'] = '27'
SUB_INV = {v: k for k, v in SUB.items()}


def inverse_map(newdir):
    """new section number -> old, for every heading in the new layout"""
    inv = {v: k for k, v in MAP.items()}
    for f in FILES[1:]:
        p = os.path.join(newdir, f)
        if not os.path.exists(p) or f in ('s2.md', 'refs.md'): continue
        for h in re.findall(r'^#{1,4} ((?:[IGP]\d+|A|\d+)(?:\.\d+)*)\.? ', open(p, encoding='utf-8').read(), re.M):
            if h in inv or h in TOP_INV: continue
            top = h.split('.')[0]
            if top in SUB_INV and '.' in h:
                inv[h] = SUB_INV[top] + h[len(top):]
    return inv


def unrenumber(text, inv):
    out = []
    for line in text.split('\n'):
        if CODE.match(line):
            out.append(line); continue
        m = re.match(r'^(#{1,4}) (Appendix A|(?:[IGP]\d+|A|\d+)(?:\.\d+)*)(\.?) (.*)$', line)
        if m:
            k = m.group(2)
            o = TOP_INV.get(k) if k in TOP_INV and k not in inv else inv.get(k)
            if o:
                line = f'{m.group(1)} {o}{"." if "." not in o else ""} {m.group(4)}'
            out.append(line); continue
        line = re.sub(r'(?<![\w./\-§])((?:[IGP]\d+|A)(?:\.\d+)+|[IGP]\d+|\d+\.\d+(?:\.\d+)*)(?![\w\-]|\.\d)',
                      lambda mm: inv.get(mm.group(1), mm.group(1)), line)
        def group(mm):
            items = re.split(r'(, |; )', mm.group(1))
            res = []
            for it in items:
                r = re.fullmatch(r'(Appendix A|Introduction|\d+|[IGP]\d+)(--(\S+))?', it)
                if r and r.group(1) in TOP_INV and r.group(1) not in inv:
                    it = TOP_INV[r.group(1)] + ('--' + TOP_INV.get(r.group(3), r.group(3)) if r.group(2) else '')
                res.append(it)
            return '(' + ''.join(res) + ')'
        line = re.sub(r'\(([^()]*)\)', group, line)
        def cell(mm):
            parts = mm.group(1).split(', ')
            if len(parts) < 2: return mm.group(0)
            return '| ' + ', '.join(TOP_INV.get(p, p) if p in TOP_INV and p not in inv else p for p in parts) + ' |'
        line = re.sub(r'\| ([^|]+?) \|(?=$|\s)', cell, line)
        line = re.sub(r'\bSection (21|G[1-5])\b', lambda mm: 'Section ' + TOP_INV[mm.group(1)], line)
        line = re.sub(r'\bThe patterns in (G4)\b', lambda mm: 'The patterns in ' + TOP_INV[mm.group(1)], line)
        out.append(line)
    return '\n'.join(out)


def old_layout(newdir):
    """{old file name: text in the old numbering} from a source in the new layout"""
    rd = lambda f: open(os.path.join(newdir, f), encoding='utf-8').read() if os.path.exists(os.path.join(newdir, f)) else ''
    inv = inverse_map(newdir)
    u = lambda t: unrenumber(t, inv)
    intro, path = rd('intro.md'), rd('path.md')
    i12 = intro.find('## I12 ')
    p2 = path.find('# P2. ')
    p3 = path.find('# P3. ')
    changes = u(path[p2:p3]).replace('# 1.8 Changes from v1', '## 1.8 Changes from v1', 1) if p2 >= 0 else ''
    old = {'title_clean.md': rd('title_clean.md'), 's1.md': u(intro[:i12]) + '\n' + changes, 's2.md': u(rd('s1.md'))}
    for n in range(3, 21):
        old[f's{n}.md'] = u(rd(f's{n}.md'))
    for n, g in zip((21, 22, 23, 24), ('g1', 'g2', 'g3', 'g4')):
        old[f's{n}.md'] = u(rd(g + '.md'))
    old['s25.md'] = u(rd('appa.md'))
    old['s26.md'] = u(path[:p2])
    old['s27.md'] = u(path[p3:]) + '\n' + u(intro[i12:]) + '\n' + u(rd('s21.md')) + '\n' + u(rd('g5.md'))
    return old
