"""Renderer for HCP spec .docx files in the v1 Draft 4 house style (restricted Markdown in, docx out).

Shared by build.py (clean documents) and redline.py (redlines). With no change markers and no
Δ lines in the source, output is byte-identical to the Draft 1 build.py.

Supported source: # / ## / ### headings, paragraphs, - bullets (2- or 3-space indent = level 1),
1. numbered lists, 4-space code blocks, pipe tables, ```{=openxml} raw blocks, inline **bold**,
*italic*, `code`. '---' -> em dash, '--' -> en dash.

Redline additions (produced by redline.py, never written by hand):
  INS_ON .. INS_OFF   inserted text        DEL_ON .. DEL_OFF   deleted text
  'Δ ...' lines       change notes; dropped in clean mode, rendered as note paragraphs in redline mode
"""
import os, re, zipfile, html

INS_ON, INS_OFF, DEL_ON, DEL_OFF = '\x0e', '\x0f', '\x10', '\x11'
MARKS = INS_ON + INS_OFF + DEL_ON + DEL_OFF
_MARK_RE = re.compile('([' + MARKS + '])')

# Redline styling. Colour is replaced, not added, so a run never carries two <w:color> elements.
INS_COLOR, DEL_COLOR = '1155CC', 'C00000'
TRACK_AUTHOR = os.environ.get('HCP_TRACK_AUTHOR', 'HCP v2 Draft 2')
TRACK_DATE = os.environ.get('HCP_TRACK_DATE', '2026-10-26T00:00:00Z')

RPR_ORDER = ['rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike', 'dstrike', 'outline',
             'shadow', 'emboss', 'imprint', 'noProof', 'snapToGrid', 'vanish', 'webHidden', 'color', 'spacing',
             'w', 'kern', 'position', 'sz', 'szCs', 'highlight', 'u', 'effect', 'bdr', 'shd', 'fitText',
             'vertAlign', 'rtl', 'cs', 'em', 'lang', 'eastAsianLayout', 'specVanish', 'oMath']


def esc(t):
    return html.escape(t, quote=False).replace('"', '&quot;')


def dashes(t):
    t = t.replace('---', '—').replace('--', '–')
    return t.replace('\\[', '[').replace('\\]', ']')


def _mark_rpr(rpr, state, track):
    """Add redline formatting to a run's properties, keeping schema order."""
    if state is None:
        return rpr
    els = re.findall(r'<w:(\w+)\b[^>]*/>', rpr)
    parts = dict(zip(els, re.findall(r'<w:\w+\b[^>]*/>', rpr)))
    if not track:
        parts['color'] = f'<w:color w:val="{INS_COLOR if state == "ins" else DEL_COLOR}"/>'
        if state == 'ins':
            parts['u'] = '<w:u w:val="single"/>'
        else:
            parts['strike'] = '<w:strike w:val="1"/>'
    return ''.join(parts[k] for k in RPR_ORDER if k in parts)


class Renderer:
    def __init__(self, mode='clean', track=False):
        assert mode in ('clean', 'redline')
        self.mode, self.track = mode, track
        self.state = None          # None | 'ins' | 'del' (carried across runs within a block)
        self.rev_id = 1000
        self.pstat = set()         # states of the text runs in the current paragraph (tracked mode)
        self.plast = self.pmark = None       # state of this paragraph's last text run, and of its mark
        self.prev_last = self.prev_mark = None

    # -- inline ------------------------------------------------------------------------------
    def _emit(self, out, text, rpr):
        for piece in _MARK_RE.split(text):
            if piece in (INS_ON, DEL_ON):
                self.state = 'ins' if piece == INS_ON else 'del'; continue
            if piece in (INS_OFF, DEL_OFF):
                self.state = None; continue
            if not piece:
                continue
            st = self.state
            if piece.strip():
                self.pstat.add(st); self.plast = st
            r_rpr = _mark_rpr(rpr, st, self.track)
            if self.track and st == 'del':
                r = f'<w:r><w:rPr>{r_rpr}</w:rPr><w:delText xml:space="preserve">{esc(piece)}</w:delText></w:r>'
            else:
                r = f'<w:r><w:rPr>{r_rpr}</w:rPr><w:t xml:space="preserve">{esc(piece)}</w:t></w:r>'
            if self.track and st:
                self.rev_id += 1
                tag = 'w:ins' if st == 'ins' else 'w:del'
                r = f'<{tag} w:id="{self.rev_id}" w:author="{TRACK_AUTHOR}" w:date="{TRACK_DATE}">{r}</{tag}>'
            out.append(r)

    def _start(self):
        self.prev_last, self.prev_mark = self.plast, self.pmark
        self.state = None; self.pstat = set(); self.plast = self.pmark = None

    def _pmark(self, ppr):
        """Tracked mode: mark the paragraph mark itself when the whole paragraph is inserted or deleted,
        so that accepting or rejecting removes the paragraph rather than leaving it empty."""
        if not self.track or len(self.pstat) != 1 or None in self.pstat:
            return ppr
        st = next(iter(self.pstat))
        # (redline.py never places a wholly inserted paragraph after a paragraph that ends in inserted
        #  text in tracked mode; some editors read that pair as one insertion and lose a break on reject)
        self.pmark = st; self.rev_id += 1
        tag = 'w:ins' if st == 'ins' else 'w:del'
        return ppr + f'<w:rPr><{tag} w:id="{self.rev_id}" w:author="{TRACK_AUTHOR}" w:date="{TRACK_DATE}"/></w:rPr>'

    def runs(self, text, base=''):
        """Inline markup -> runs. base: extra rPr for every run (e.g. table size)."""
        out = []
        parts = re.split(r'(`[^`]+`)', text)
        for part in parts:
            if part.startswith('`') and part.endswith('`') and len(part) > 1:
                code_rpr = CODE_RPR if not base else CODE_RPR.replace('w:val="18"', 'w:val="17"')
                self._emit(out, part[1:-1], code_rpr)
                continue
            part = dashes(part)
            for seg in re.split(r'(\*\*[^*]+\*\*|\*[^*\s][^*]*\*)', part):
                if not seg:
                    continue
                rpr = base
                if seg.startswith('**') and seg.endswith('**'):
                    seg = seg[2:-2]; rpr = '<w:b w:val="1"/><w:bCs w:val="1"/>' + base
                elif seg.startswith('*') and seg.endswith('*') and len(seg) > 2:
                    seg = seg[1:-1]; rpr = '<w:i w:val="1"/><w:iCs w:val="1"/>' + base
                self._emit(out, seg, rpr)
        return ''.join(out)

    def plain_runs(self, text, rpr):
        out = []
        self._emit(out, text, rpr)
        return ''.join(out)

    # -- blocks ------------------------------------------------------------------------------
    def para(self, text, ppr=None):
        ppr = BODY_PPR if ppr is None else ppr
        self._start()
        r = self.runs(text)
        return f'<w:p><w:pPr>{self._pmark(ppr)}</w:pPr>{r}</w:p>'

    def heading(self, level, text):
        style, size, before = {1: ('Heading1', 30, 320), 2: ('Heading2', 25, 240), 3: ('Heading3', 22, 240)}[level]
        self._start()
        text = dashes(text)
        rpr = f'<w:b w:val="1"/><w:bCs w:val="1"/><w:color w:val="1f3864"/><w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
        r = self.plain_runs(text, rpr)
        ppr = self._pmark(f'<w:pStyle w:val="{style}"/><w:keepNext/><w:spacing w:after="120" w:before="{before}" w:lineRule="auto"/>')
        p = f'<w:p><w:pPr>{ppr}</w:pPr>{r}</w:p>'
        return ('\u0002' + p) if level == 1 else p

    def title(self, text):
        self.state = None
        r = self.plain_runs(dashes(text), '<w:b w:val="1"/><w:bCs w:val="1"/><w:color w:val="1f3864"/><w:sz w:val="44"/><w:szCs w:val="44"/>')
        return f'<w:p><w:pPr><w:spacing w:after="240" w:before="0" w:lineRule="auto"/></w:pPr>{r}</w:p>'

    def list_item(self, text, num_id, ilvl):
        ind = 720 + 720 * ilvl
        self._start()
        ppr = (f'<w:numPr><w:ilvl w:val="{ilvl}"/><w:numId w:val="{num_id}"/></w:numPr>'
               f'<w:spacing w:after="40" w:before="40" w:line="276" w:lineRule="auto"/><w:ind w:left="{ind}" w:hanging="360"/><w:jc w:val="left"/>')
        r = self.runs(text)
        return f'<w:p><w:pPr>{self._pmark(ppr)}</w:pPr>{r}</w:p>'

    def code_line(self, text, first, last):
        self._start()
        sp = f'<w:spacing w:after="{120 if last else 0}" w:before="{60 if first else 0}" w:lineRule="auto"/>'
        rpr = '<w:rFonts w:ascii="Consolas" w:cs="Consolas" w:eastAsia="Consolas" w:hAnsi="Consolas"/><w:sz w:val="16"/><w:szCs w:val="16"/>'
        if text and _MARK_RE.search(text):
            body = self.plain_runs(text, rpr)
        else:
            body = f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{esc(text) if text else ""}</w:t></w:r>'
        ppr = self._pmark(f'<w:shd w:fill="f4f5f7" w:val="clear"/>{sp}<w:ind w:left="220" w:right="220" w:firstLine="0"/>')
        return f'<w:p><w:pPr>{ppr}</w:pPr>{body}</w:p>'

    def cell(self, text, w, header):
        shd = '<w:shd w:fill="e8eef7" w:val="clear"/>' if header else ''
        tcpr = (f'<w:tcPr><w:tcW w:w="{w}" w:type="dxa"/><w:tcBorders>'
                + ''.join(f'<w:{s} w:color="b8c8dc" w:space="0" w:sz="4" w:val="single"/>' for s in ('top', 'left', 'bottom', 'right'))
                + f'</w:tcBorders>{shd}<w:tcMar><w:top w:w="60" w:type="dxa"/><w:left w:w="110" w:type="dxa"/><w:bottom w:w="60" w:type="dxa"/><w:right w:w="110" w:type="dxa"/></w:tcMar></w:tcPr>')
        base = ('<w:b w:val="1"/><w:bCs w:val="1"/>' if header else '') + '<w:sz w:val="19"/><w:szCs w:val="19"/>'
        self._start()
        r = self.runs(text.strip(), base)
        self.cell_stats.append(set(self.pstat))
        return f'<w:tc>{tcpr}<w:p><w:pPr><w:spacing w:after="20" w:before="20" w:lineRule="auto"/></w:pPr>{r}</w:p></w:tc>'

    def table(self, rows, seps):
        total = 9360
        weights = [max(len(s.strip()), 3) for s in seps]
        widths = [int(total * w / sum(weights)) for w in weights]
        widths[-1] = total - sum(widths[:-1])
        grid = ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths)
        tblpr = ('<w:tblPr><w:tblW w:w="9360" w:type="dxa"/><w:jc w:val="left"/><w:tblBorders>'
                 + ''.join(f'<w:{s} w:color="b8c8dc" w:space="0" w:sz="4" w:val="single"/>' for s in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'))
                 + '</w:tblBorders><w:tblLayout w:type="fixed"/><w:tblLook w:val="0000"/></w:tblPr>')
        out = [f'<w:tbl>{tblpr}<w:tblGrid>{grid}</w:tblGrid>']
        row_tags = []
        for i, r in enumerate(rows):
            self.cell_stats = []
            cells = ''.join(self.cell(c, widths[j], i == 0) for j, c in enumerate(r))
            hdr = '<w:tblHeader/>' if i == 0 else ''
            mark = ''
            nonempty = [s for s in self.cell_stats if s]
            if self.track and nonempty and all(s == nonempty[0] for s in nonempty) and len(nonempty[0]) == 1 and None not in nonempty[0]:
                self.rev_id += 1
                tag = 'w:ins' if 'ins' in nonempty[0] else 'w:del'
                mark = f'<{tag} w:id="{self.rev_id}" w:author="{TRACK_AUTHOR}" w:date="{TRACK_DATE}"/>'
            row_tags.append(tag if mark else None)
            out.append(f'<w:tr><w:trPr><w:cantSplit/>{hdr}{mark}</w:trPr>' + cells + '</w:tr>')
        out.append('</w:tbl>')
        # the spacer after a wholly inserted or deleted table belongs to the change, so that
        # rejecting (or accepting) it leaves no stray paragraph behind
        spacer_mark = ''
        if self.track and row_tags and row_tags[0] and all(t == row_tags[0] for t in row_tags):
            self.rev_id += 1
            spacer_mark = f'<w:rPr><{row_tags[0]} w:id="{self.rev_id}" w:author="{TRACK_AUTHOR}" w:date="{TRACK_DATE}"/></w:rPr>'
        out.append(f'<w:p><w:pPr><w:spacing w:after="60" w:before="60" w:lineRule="auto"/>{spacer_mark}</w:pPr></w:p>')
        return ''.join(out)

    def delta_note(self, text):
        """A Δ note: shaded, italic, set off from the text it explains. Redline only."""
        self._start()
        ppr = ('<w:pBdr><w:left w:color="C55A11" w:space="6" w:sz="18" w:val="single"/></w:pBdr>'
               '<w:shd w:fill="FBF1E8" w:val="clear"/><w:spacing w:after="120" w:before="40" w:lineRule="auto"/>'
               '<w:ind w:left="220" w:right="220"/><w:jc w:val="left"/>')
        base = '<w:color w:val="843C0C"/><w:sz w:val="18"/><w:szCs w:val="18"/>'
        out = []
        for seg in re.split(r'(`[^`]+`)', text):
            if seg.startswith('`') and seg.endswith('`') and len(seg) > 1:
                out.append(f'<w:r><w:rPr>{CODE_RPR.replace("<w:sz", "<w:color w:val=\"843C0C\"/><w:sz")}</w:rPr><w:t xml:space="preserve">{esc(seg[1:-1])}</w:t></w:r>')
            elif seg:
                m = re.match(r'^(Δ \w+ \([^)]*\))(.*)$', seg, re.S)
                if m:
                    out.append(f'<w:r><w:rPr><w:b w:val="1"/><w:bCs w:val="1"/>{base}</w:rPr><w:t xml:space="preserve">{esc(m.group(1))}</w:t></w:r>')
                    seg = m.group(2)
                if seg:
                    out.append(f'<w:r><w:rPr><w:i w:val="1"/><w:iCs w:val="1"/>{base}</w:rPr><w:t xml:space="preserve">{esc(dashes(seg))}</w:t></w:r>')
        return f'<w:p><w:pPr>{ppr}</w:pPr>{"".join(out)}</w:p>'


CODE_RPR = '<w:rFonts w:ascii="Consolas" w:cs="Consolas" w:eastAsia="Consolas" w:hAnsi="Consolas"/><w:sz w:val="18"/><w:szCs w:val="18"/>'
BODY_PPR = '<w:spacing w:after="120" w:before="60" w:lineRule="auto"/><w:jc w:val="left"/>'
DIVIDER = '<w:p><w:pPr><w:pBdr><w:bottom w:color="b8c8dc" w:space="0" w:sz="6" w:val="single"/></w:pBdr><w:spacing w:after="160" w:before="120" w:lineRule="auto"/></w:pPr></w:p>'


def split_row(line):
    line = line.strip()
    assert line.startswith('|') and line.endswith('|'), line
    return [c for c in re.split(r'(?<!\\)\|', line[1:-1])]


def render_body(src, R):
    """Source lines -> (list of block XML strings, numbered-list numIds)."""
    body = []
    num_lists = []
    next_num = 2
    i = 0
    first_title = True
    while i < len(src):
        line = src[i]
        if not line.strip():
            i += 1; continue
        if line.startswith('Δ '):
            if R.mode == 'redline':
                buf = [line.strip()]; i += 1
                while i < len(src) and src[i].strip():
                    buf.append(src[i].strip()); i += 1
                body.append(R.delta_note(' '.join(buf)))
            else:
                i += 1
                while i < len(src) and src[i].strip():
                    i += 1
            continue
        if line.startswith('```{=openxml}'):
            i += 1; raw = []
            while not src[i].startswith('```'):
                raw.append(src[i]); i += 1
            body.append(''.join(raw)); i += 1; continue
        m = re.match(r'^(#{1,3}) (.*)$', line)
        if m:
            body.append(R.heading(len(m.group(1)), m.group(2).strip())); i += 1; continue
        if first_title and line.startswith('**') and line.rstrip().endswith('**') and line.count('**') == 2:
            body.append(R.title(line.strip()[2:-2])); first_title = False; i += 1; continue
        if line.startswith('|'):
            rows = []
            while i < len(src) and src[i].startswith('|'):
                rows.append(split_row(src[i].replace('\\|', '\u0001'))); i += 1
            seps = rows.pop(1)
            rows = [[c.replace('\u0001', '|') for c in r] for r in rows]
            assert all(len(r) == len(seps) for r in rows), rows
            body.append(R.table(rows, seps)); continue
        if line.startswith('    '):
            block = []
            while i < len(src) and (src[i].startswith('    ') or (not src[i].strip() and i + 1 < len(src) and src[i + 1].startswith('    '))):
                block.append(src[i][4:]); i += 1
            for k, b in enumerate(block):
                body.append(R.code_line(b, k == 0, k == len(block) - 1))
            continue
        if re.match(r'^(\d+)\. ', line) or line.startswith('- '):
            numbered = bool(re.match(r'^\d+\. ', line))
            if numbered:
                start_n = int(re.match(r'^(\d+)\.', line).group(1))
                if start_n > 1 and num_lists:
                    nid = num_lists[-1]          # continue the previous numbered list
                else:
                    num_lists.append(next_num); nid = next_num; next_num += 1
            else:
                nid = 1
            while i < len(src) and src[i].strip():
                l = src[i]
                mm = re.match(r'^( *)(\d+\.|-) (.*)$', l)
                if not mm:
                    body[-1] = body[-1].replace('</w:p>', R.runs(' ' + l.strip()) + '</w:p>'); i += 1; continue
                indent, marker, text = mm.groups()
                if indent:
                    body.append(R.list_item(text, 1, 1))
                else:
                    body.append(R.list_item(text, nid if numbered else 1, 0))
                i += 1
            continue
        indented = line.startswith('   ') and not line.startswith('    ')
        buf = [line.strip()]; i += 1
        while i < len(src) and src[i].strip() and not src[i].startswith(('#', '|', '- ', '    ', '```', 'Δ ')) and not re.match(r'^\d+\. ', src[i]):
            buf.append(src[i].strip()); i += 1
        text = ' '.join(buf)
        if indented:
            body.append(R.para(text, '<w:spacing w:after="80" w:before="40" w:lineRule="auto"/><w:ind w:left="720"/><w:jc w:val="left"/>'))
        else:
            body.append(R.para(text))
    return body, num_lists


def build(tpl, src_text, out, header, mode='clean', track=False, doc_title='Human Context Protocol (HCP) v2 Draft Specification'):
    R = Renderer(mode, track)
    body, num_lists = render_body(src_text.split('\n'), R)
    zin = zipfile.ZipFile(tpl)
    doc = zin.read('word/document.xml').decode('utf-8')
    head = doc[:doc.find('<w:body>') + len('<w:body>')]
    sect = doc[doc.rfind("<w:sectPr"):]
    if "w:gutter" not in sect:
        sect = sect.replace("<w:pgMar ", "<w:pgMar w:gutter=\"0\" ")
    joined = ''
    for k, blk in enumerate(body):
        if blk.startswith('\u0002'):
            prev_h1 = k > 0 and body[k - 1].startswith('\u0002')
            blk = blk[1:] if prev_h1 else DIVIDER + blk[1:]
        joined += blk
    new_doc = head + joined + sect

    numbering = zin.read('word/numbering.xml').decode('utf-8')
    dec = ('<w:abstractNum w:abstractNumId="2"><w:multiLevelType w:val="hybridMultilevel"/>'
           '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl>'
           '<w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="○"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="1440" w:hanging="360"/></w:pPr></w:lvl>'
           '</w:abstractNum>')
    nums = ''.join(f'<w:num w:numId="{n}"><w:abstractNumId w:val="2"/><w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride></w:num>' for n in num_lists)
    numbering = numbering.replace('<w:num w:numId="1">', dec + '<w:num w:numId="1">', 1)
    numbering = numbering.replace('</w:numbering>', nums + '</w:numbering>')

    hdr = zin.read('word/header1.xml').decode('utf-8')
    hdr = re.sub(r'Human Context Protocol \(HCP\) v1[^<]*', esc(header), hdr)

    zout = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == 'word/document.xml':
            data = new_doc.encode('utf-8')
        elif item.filename == 'word/numbering.xml':
            data = numbering.encode('utf-8')
        elif item.filename == 'word/header1.xml':
            data = hdr.encode('utf-8')
        elif item.filename == 'docProps/core.xml':
            s = data.decode('utf-8')
            s = re.sub(r'<dc:title>[^<]*</dc:title>', f'<dc:title>{esc(doc_title)}</dc:title>', s)
            data = s.encode('utf-8')
        zout.writestr(item, data)
    zout.close()
    return len(body)
