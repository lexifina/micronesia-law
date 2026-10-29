"""Text-layer readers for the FSM sources (gitlaw-FM). No OCR; no network.

- code_title(pdf_path, title_no): a title PDF of the Code of the FSM 2014 Edition (Annotated) -> ordered units
  (chapter / subchapter / part headings and sections) holding the statutory text only. The edition sets statutory
  text in 12 pt and every annotation ("Source:", "Editor's note:", "Cross-reference:", "Case annotations:") in
  10 pt, with running heads and folios in 11 pt; only 12 pt lines are kept. A section starts at a bold line that
  holds both "§ N." and its catchline; the chapter tables of contents (number and catchline in separate columns)
  are skipped. Read with PyMuPDF (fitz).
- public_law(pdf_path): an enrolled FSM public law (Congress PDF) -> its sections, with printed line numbers, page
  headers and footers removed (read with pdftotext -layout).
- reflow(lines): hard-wrapped lines -> one paragraph per line.
"""
import re
import subprocess

import fitz

ROMAN = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}
HEAD = re.compile(r'^§\s*(\d+[A-Za-z]?)\.\s+(\S.*)$')
ENUM = re.compile(r'^(\(\s*[0-9]{1,3}[A-Za-z]?\s*\)|\(\s*[a-z]{1,2}\s*\)|\(\s*[ivxlc]{1,6}\s*\)|\(\s*[A-Z]{1,2}\s*\)|'
                  r'[a-z]\)|[0-9]{1,2}\)|[0-9]{1,2}\.\s)')


def norm(s):
    s = s.replace('\xa0', ' ').replace('­', '').replace('\t', ' ')
    s = s.replace('“', '"').replace('”', '"').replace('„', '"').replace('‘', "'").replace('’', "'")
    s = s.replace('–', '-').replace('—', '-').replace('‑', '-').replace('−', '-').replace('…', '...')
    s = re.sub(r' {2,}', ' ', s)
    return s.strip()


def reflow(lines):
    """[(indented, text)] -> paragraphs. A line starts a new paragraph when the paragraph so far ends with . ; or :
    and the line is indented or opens with an enumerator, or when it ends with "and"/"or" and the line opens with an
    enumerator. Every other line continues the paragraph."""
    paras = []
    for ind, t in lines:
        if not t:
            continue
        if not paras:
            paras.append(t)
            continue
        p = paras[-1].rstrip()
        starts_enum = bool(ENUM.match(t))
        new = bool((re.search(r'[.;:]["\']?$', p) and (ind or starts_enum))
                   or (re.search(r'\b(and|or)$', p) and starts_enum))
        if new:
            paras.append(t)
        else:
            paras[-1] = p + ' ' + t
    return [norm(p) for p in paras]


# ---------------------------------------------------------------- 2014 Code titles

def _rows(path):
    """Every text row of the PDF in reading order: (page, y, x, size, bold, text, heading_in_one_line)."""
    doc = fitz.open(str(path))
    rows = []
    for pno in range(doc.page_count):
        page_rows = []
        for b in doc[pno].get_text('dict')['blocks']:
            for ln in b.get('lines', []):
                spans = [s for s in ln['spans'] if s['text'].strip()]
                if not spans:
                    continue
                text = ''.join(s['text'] for s in ln['spans'])
                size = max(round(s['size'], 1) for s in spans)
                bold = 'Bold' in spans[0]['font']
                page_rows.append([pno, round(ln['bbox'][1], 1), round(spans[0]['bbox'][0], 1), size, bold, text,
                                  bool(HEAD.match(norm(text)))])
        # merge fitz lines that share a baseline (an enumerator and its text are separate lines)
        page_rows.sort(key=lambda r: (r[1], r[2]))
        merged = []
        for r in page_rows:
            if merged and abs(merged[-1][1] - r[1]) < 2.0 and merged[-1][3] == r[3]:
                merged[-1][5] = merged[-1][5].rstrip() + ' ' + r[5].lstrip()
                continue
            merged.append(r)
        rows.extend(merged)
    return rows


def code_title(path, title_no):
    """Ordered units: dicts {key, kind, label, heading, title?, lines: [(indented, text)]}."""
    rows = _rows(path)
    body = [r for r in rows if r[3] >= 11.5]           # statutory text and headings only
    margin = {}
    for r in body:
        margin[r[0]] = min(margin.get(r[0], 1e9), r[2])
    units, cur, pending = [], None, None
    chapter, sub = None, None
    state = 'front'                                    # front | heading | toc | body
    for pno, y, x, size, bold, text, one_line_head in body:
        t = norm(text)
        if not t:
            continue
        indented = (x - margin[pno]) >= 20
        m = re.match(r'^CHAPTER\s+(\d+)$', t) if bold else None
        if m:
            _add_heading(units, pending)
            chapter, sub = int(m.group(1)), None
            pending = {'key': f'ch-{chapter:02d}', 'kind': 'chapter', 'label': f'Chapter {chapter}',
                       'heading': f'Chapter {chapter}', 'lines': []}
            state = 'heading'
            continue
        m = re.match(r'^SUBCHAPTER\s+([IVX]+)$', t) if bold else None
        if m and chapter is not None:
            _add_heading(units, pending)
            sub = ROMAN[m.group(1)]
            pending = {'key': f'ch-{chapter:02d}-sub-{sub:02d}', 'kind': 'subchapter',
                       'label': f'Chapter {chapter}, Subchapter {m.group(1)}', 'heading': f'Subchapter {m.group(1)}',
                       'lines': []}
            state = 'heading'
            continue
        m = re.match(r'^PART\s+(\d+):\s*(.*)$', t) if bold else None
        if m and chapter is not None and sub is not None:
            _add_heading(units, pending)
            pending = {'key': f'ch-{chapter:02d}-sub-{sub:02d}-part-{int(m.group(1)):02d}', 'kind': 'part',
                       'label': f'Chapter {chapter}, Subchapter {sub}, Part {m.group(1)}',
                       'heading': f'Part {m.group(1)}', 'lines': [(0, m.group(2))]}
            state = 'heading'
            continue
        hm = HEAD.match(t)
        is_head = bool(hm and bold and one_line_head and chapter is not None
                       and int(re.match(r'\d+', hm.group(1)).group(0)) // 100 == chapter)
        if state == 'heading':
            if t in ('SECTIONS', 'SUBCHAPTERS', 'PARTS') or t.startswith('§') or not bold:
                _add_heading(units, pending)
                pending = None
                state = 'toc'
            else:
                pending['lines'].append((0, t))
                continue
        if is_head:
            num = hm.group(1)
            digits = re.match(r'\d+', num).group(0)
            cur = {'key': f'sec-{int(digits):04d}{num[len(digits):].lower()}', 'kind': 'sec', 'label': f'§ {num}',
                   'num': num, 'heading': f'§ {num}. {hm.group(2).strip()}', 'lines': [], 'chapter': chapter,
                   'sub': sub}
            units.append(cur)
            state = 'title'
            continue
        if state in ('front', 'toc'):
            continue
        if state == 'title' and bold and not ENUM.match(t) and not re.search(r'\.["\']?$', cur['heading']):
            cur['heading'] += ' ' + t                  # catchline wrapped onto a second bold line
            continue
        state = 'body'
        cur['lines'].append((indented, t))
    _add_heading(units, pending)
    return units


def _add_heading(units, h):
    if h is None:
        return
    title = ' '.join(x for _, x in h['lines']).strip()
    title = re.sub(r'\s*\(§§?.*\)$', '', title)
    h = dict(h, title=title)
    for u in units:
        if u['key'] == h['key']:
            return
    units.append(h)


# ---------------------------------------------------------------- public laws

def pdftotext(path):
    r = subprocess.run(['pdftotext', '-layout', '-enc', 'UTF-8', str(path), '-'], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode('utf-8', 'replace'))
    return r.stdout.decode('utf-8')


def public_law(path):
    """{'header': [lines before Section 1], 'sections': {n: [lines]}, 'date': 'Month D, YYYY' or None}"""
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
            t = re.sub(r'^\d{1,2}(\s+|$)', '', t).strip()   # printed line numbers
            if t:
                body.append(t)
    secs, order, cur, want, header = {}, [], None, 1, []
    for t in body:
        m = re.match(r'^Section\s+(\d+)\.\s*(.*)$', t)
        if m and int(m.group(1)) == want:
            cur = want
            secs[cur] = [m.group(2)] if m.group(2) else []
            order.append(cur)
            want += 1
            continue
        (header if cur is None else secs[cur]).append(t)
    date = None
    if order:
        last = ' '.join(secs[order[-1]])
        m = re.search(r'([A-Z][a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?\s*,\s*(\d{4})', last)
        if m:
            date = f'{m.group(1)} {m.group(2)}, {m.group(3)}'
    return {'header': header, 'sections': secs, 'date': date}
