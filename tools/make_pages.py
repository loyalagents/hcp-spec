"""Build the repository pages (RS7): one Markdown file per page, Δ notes removed, citations linked.

Usage: python3 -I tools/make_pages.py SRC OUT VERSION

SRC      source directory in the Draft 3 layout (restructure.FILES)
OUT      directory to write: introduction.md, specification.md, guides.md, path-to-v2-final.md, images/
VERSION  e.g. 2.0-draft-3

The Word document is still built from SRC by build.py; these pages are the same text for reading on GitHub.
"""
import os, re, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import restructure

PAGES = [
    ('introduction.md', 'Introduction', ['intro.md']),
    ('specification.md', 'Specification', ['s1.md', 's2.md'] + [f's{n}.md' for n in range(3, 21)] + ['s21.md', 'appa.md', 'refs.md']),
    ('guides.md', 'Guides', ['g1.md', 'g2.md', 'g3.md', 'g4.md', 'g5.md']),
    ('path-to-v2-final.md', 'Path to v2 Final', ['path.md']),
]
FIGURES = {   # inserted after the paragraph that begins with the key, on the Introduction page
    'In a typical read,': ('images/roles-read.svg', 'The roles in a read, step by step (3.13)'),
    '| Fiduciary governance |': ('images/stack.svg', 'Where HCP sits among neighbouring layers'),
}


def slug(h):
    """GitHub's heading anchor"""
    s = h.strip().lower()
    s = re.sub(r'[^\w\- ]', '', s)
    return s.replace(' ', '-')


def strip_delta(t):
    return re.sub(r'^Δ [^\n]*\n(?:[^\n]+\n)*\n?', '', t, flags=re.M)


def main(src, out, version):
    os.makedirs(os.path.join(out, 'images'), exist_ok=True)
    texts = {}
    anchors = {}   # section number -> (page, anchor)
    for page, title, files in PAGES:
        t = '\n'.join(strip_delta(open(os.path.join(src, f), encoding='utf-8').read()).rstrip('\n') for f in files) + '\n'
        texts[page] = t
        for h in re.findall(r'^#{1,4} (.+)$', t, re.M):
            m = re.match(r'^(Appendix A|(?:[IGP]\d+|A|\d+)(?:\.\d+)*)\.? ', h)
            if m:
                anchors.setdefault(m.group(1), (page, slug(h)))
    for t_page, (page, title, files) in zip(texts, PAGES):
        t = texts[page]

        def link(m):
            items = re.split(r'(, |; )', m.group(1)); outl = []
            for it in items:
                k = it.strip()
                if k in anchors and not k.isdigit() or (k.isdigit() and k in anchors and int(k) <= 21):
                    p, a = anchors[k]
                    outl.append(f'[{it}]({"" if p == page else p}#{a})')
                else:
                    outl.append(it)
            return '(' + ''.join(outl) + ')'
        lines = []
        for line in t.split('\n'):
            if line.startswith('    '):
                lines.append(line); continue
            if not re.fullmatch(r'\|[-| :]+\|', line.strip()):
                line = line.replace('---', '\u2014').replace('--', '\u2013')   # the source's dash convention
            if line.startswith('#'):
                lines.append(line); continue
            lines.append(re.sub(r'\(([^()]*)\)', link, line))
        t = '\n'.join(lines)
        if page == 'introduction.md':
            for key, (img, alt) in FIGURES.items():
                i = t.find('\n' + key)
                assert i >= 0, key
                e = t.find('\n\n', i + 1)
                t = t[:e] + f'\n\n![{alt}]({img})\n\n*{alt}.*' + t[e:]
        head = (f'> **DRAFT \u2014 Not for distribution.** Human Context Protocol (HCP) v2, Draft Specification, version {version}. '
                f'Pages: [Introduction](introduction.md) · [Specification](specification.md) · [Guides](guides.md) · [Path to v2 Final](path-to-v2-final.md)\n\n')
        foot = '\n---\n\nThe specification text is licensed under CC BY 4.0 ([LICENSE-SPEC.md](../../LICENSE-SPEC.md)). These pages are built from the same source as the Word document by `tools/make_pages.py`; where they differ, please report it as an issue.\n'
        open(os.path.join(out, page), 'w', encoding='utf-8').write(head + t.strip('\n') + '\n' + foot)
    for f in ('roles-read.svg', 'stack.svg'):
        shutil.copy(os.path.join(src, 'pages', 'images', f), os.path.join(out, 'images', f))
    return anchors


if __name__ == '__main__':
    main(*sys.argv[1:4])
