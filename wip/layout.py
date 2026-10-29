"""Text-layer readers for the FSM sources (gitlaw-FM). No OCR; no network.

- code_title(pdf_path): a title PDF of the Code of the FSM 2014 Edition (Annotated) -> ordered units
  (chapter / subchapter / part headings and sections) holding the statutory text only. Annotations are dropped:
  "Source:", "Editor's note:", "Cross-reference:", "Case annotations:" and the like run from their keyword to the
  next section or heading, and the chapter tables of contents are skipped.
- public_law(pdf_path): an enrolled FSM public law (Congress PDF) -> its sections, with line numbers, page
  headers and footers removed.
- reflow(lines): hard-wrapped lines -> one paragraph per line.

pdftotext (poppler) -layout -enc UTF-8 is the text extractor; its version is recorded in decisions.
"""
import re
import subprocess

ROMAN = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}
NOTE = re.compile(r"^(Source|Sources|Editor['’]?s\s+notes?|Editors?\s+notes?|Cross[- ]references?|Case\s+annotations?|"
                  r"Annotations?|Note|Notes|Ed\.\s*note)\s*:", re.I)
SEC = re.compile(r'^§\s*(\d+[A-Za-z]?)\.\s(?=\S)(.*)$')
TOC_SEC = re.compile(r'^§\s*\d+[A-Za-z]?\.(\s{2,}.*)?$')
ENUM = re.compile(r'^(\(\s*[0-9]{1,3}[A-Za-z]?\s*\)|\(\s*[a-z]{1,2}\s*\)|\(\s*[ivxlc]{1,6}\s*\)|\(\s*[A-Z]{1,2}\s*\)|'
                  r'[a-z]\)|[0-9]{1,2}\)|[0-9]{1,2}\.\s)')


def pdftotext(path):
    r = subprocess.run(['pdftotext', '-layout', '-enc', 'UTF-8', str(path), '-'], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode('utf-8', 'replace'))
    return r.stdout.decode('utf-8')


def norm(s):
    s = s.replace('\xa0', ' ').replace('­', '').replace('\t', ' ')
    s = s.replace('“', '"').replace('”', '"').replace('„', '"').replace('‘', "'").replace('’', "'")
    s = s.replace('–', '-').replace('—', '-').replace('‑', '-').replace('−', '-').replace('…', '...')
    s = re.sub(r' {2,}', ' ', s)
    return s.strip()


def reflow(lines):
    """[(indent, text)] -> paragraphs. A line starts a new paragraph when the paragraph so far ends with . ; or :
    and the line is indented or opens with an enumerator, or when it ends with "and"/"or" and the line opens with an
    enumerator. Every other line continues the paragraph."""
    paras = []
    for ind, t in lines:
        if not t:
            continue
        if not paras:
            paras.append(t)
            continue
        prev = paras[-1]
        starts_enum = bool(ENUM.match(t))
        p = prev.rstrip()
        new = bool((re.search(r'[.;:]["\']?$', p) and (ind >= 4 or starts_enum))
                   or (re.search(r'\b(and|or)$', p) and starts_enum))
        if new:
            paras.append(t)
        else:
            paras[-1] = prev + ' ' + t
    return [norm(p) for p in paras]


# ---------------------------------------------------------------- 2014 Code titles

def _page_lines(text, title_no):
    out = []
    head = re.compile(rf'^\s*TITLE\s+{title_no}\s*-\s*[A-Z ,&]+\s*$')
    foot = re.compile(rf'^\s*T{title_no}-\d+\s*$')
    for page in text.split('\f'):
        for raw in page.split('\n'):
            if head.match(raw) or foot.match(raw):
                continue
            out.append(raw.rstrip())
    return out


def code_title(path, title_no):
    """Ordered list of units: dicts {key, kind, label, heading, lines:[(indent, text)]}."""
    lines = _page_lines(pdftotext(path), title_no)
    units, cur = [], None
    state = 'front'          # front | toc | body | note | heading
    chapter, sub, pending = None, None, None
    for raw in lines:
        t = norm(raw)
        ind = len(raw) - len(raw.lstrip(' '))
        if not t:
            continue
        toc = bool(TOC_SEC.match(raw.strip().replace(' ', ' ')))
        m = re.match(r'^CHAPTER\s+(\d+)$', t)
        if m:
            _add_heading(units, pending)
            chapter, sub = int(m.group(1)), None
            pending = {'key': f'ch-{chapter:02d}', 'kind': 'chapter', 'label': f'Chapter {chapter}',
                       'heading': f'Chapter {chapter}', 'lines': []}
            state = 'heading'
            continue
        m = re.match(r'^SUBCHAPTER\s+([IVX]+)$', t)
        if m and chapter is not None:
            _add_heading(units, pending)
            sub = ROMAN[m.group(1)]
            pending = {'key': f'ch-{chapter:02d}-sub-{sub:02d}', 'kind': 'subchapter',
                       'label': f'Chapter {chapter}, Subchapter {m.group(1)}', 'heading': f'Subchapter {m.group(1)}',
                       'lines': []}
            state = 'heading'
            continue
        m = re.match(r'^PART\s+(\d+):\s*(.*)$', t)
        if m and chapter is not None and sub is not None:
            _add_heading(units, pending)
            pending = {'key': f'ch-{chapter:02d}-sub-{sub:02d}-part-{int(m.group(1)):02d}', 'kind': 'part',
                       'label': f'Chapter {chapter}, Subchapter {sub}, Part {m.group(1)}',
                       'heading': f'Part {m.group(1)}', 'lines': [(0, m.group(2))]}
            state = 'heading'
            continue
        if state == 'heading':
            if t == 'SECTIONS' or t.startswith('SECTIONS ') or NOTE.match(t) or toc or SEC.match(t) \
                    or re.match(r'^(SUBCHAPTERS|PARTS)$', t):
                _add_heading(units, pending)
                pending = None
                state = 'toc' if (t.startswith('SECTIONS') or toc or t in ('SUBCHAPTERS', 'PARTS')) else state
                if NOTE.match(t):
                    state = 'note'
                    continue
                if not SEC.match(t) or toc:
                    continue
            else:
                pending['lines'].append((0, t))
                continue
        if state == 'front':
            continue
        m = SEC.match(t)
        if m and not toc and chapter is not None and int(re.match(r'\d+', m.group(1)).group(0)) // 100 == chapter:
            num = m.group(1)
            cur = {'key': f'sec-{int(re.match(r"\d+", num).group(0)):04d}{num[len(re.match(r"\d+", num).group(0)):].lower()}',
                   'kind': 'sec', 'label': f'§ {num}', 'num': num, 'heading': f'§ {num}. {m.group(2).strip()}',
                   'lines': [], 'chapter': chapter, 'sub': sub}
            units.append(cur)
            state = 'title'
            continue
        if state == 'toc':
            continue
        if NOTE.match(t):
            state = 'note'
            continue
        if state == 'note':
            continue
        if state in ('title', 'body') and cur is not None:
            if state == 'title' and not re.search(r'\.["\']?$', cur['heading']) and not ENUM.match(t) and ind < 8 \
                    and len(cur['heading']) < 120:
                cur['heading'] += ' ' + t      # heading wrapped onto the next line
                continue
            state = 'body'
            cur['lines'].append((ind, t))
    if pending:
        _add_heading(units, pending)
    return units


def _add_heading(units, h):
    if h is None:
        return
    title = ' '.join(x for _, x in h['lines']).strip()
    title = re.sub(r'\s*\(§§?.*\)$', '', title)
    h = dict(h, title=title)
    for i, u in enumerate(units):
        if u['key'] == h['key']:
            return   # a heading met again (chapter table of contents first, then the chapter): keep the first
    units.append(h)


# ---------------------------------------------------------------- public laws

def public_law(path):
    """{'header': [...], 'sections': {n: [lines]}, 'date': 'Month D, YYYY' or None, 'lines': [...]}"""
    text = pdftotext(path)
    body = []
    for page in text.split('\f'):
        for raw in page.split('\n'):
            t = raw.strip()
            if not t:
                continue
            if re.match(r'^(P\.?\s?C\.?\s*NO\.|PC NO\.|CONGRESSIONAL BILL NO\.|PUBLIC LAW NO\.|CBL\b|C\.B\.L\.)', t, re.I) \
                    or re.match(r'^\d+\s+of\s+\d+$', t):
                continue
            if re.search(r'(CONGRESSIONAL BILL NO\.|PUBLIC LAW NO\.)', t) and re.match(r'^(P\.?C\.?|PC)', t):
                continue
            t = re.sub(r'^\d{1,2}(\s+|$)', '', t).strip()   # printed line numbers
            if t:
                body.append(t)
    secs, order, cur = {}, [], None
    want = 1
    header = []
    for t in body:
        m = re.match(r'^Section\s+(\d+)\.\s*(.*)$', t)
        if m and int(m.group(1)) == want:
            cur = want
            secs[cur] = [m.group(2)] if m.group(2) else []
            order.append(cur)
            want += 1
            continue
        if cur is None:
            header.append(t)
        else:
            secs[cur].append(t)
    date = None
    if order:
        last = ' '.join(secs[order[-1]])
        m = re.search(r'([A-Z][a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?\s*,\s*(\d{4})', last)
        if m:
            date = f'{m.group(1)} {m.group(2)}, {m.group(3)}'
    return {'header': header, 'sections': secs, 'date': date}
