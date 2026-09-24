#!/usr/bin/env python3
"""Render the canonical CAE manuscripts as static web pages. Python 3.10+, stdlib only."""
from __future__ import annotations

import argparse
import ast
import hashlib
import html
import json
import re
import shutil
import struct
from pathlib import Path
from site_shell import FONT_URL, SOCIAL_IMAGE_META, navigation, footer

ROOT = Path(__file__).resolve().parents[1]
BASE = '/learning/cae-synopsys/'
REPO = 'https://github.com/abhinavnandwani/cae-synopsys-guides'
GUIDES = {
    'verification': ('Verification', 'VCS · Verdi · URG', 'Compile a test, follow signals through the waveform, catch an injected bug, and inspect coverage.'),
    'rtl': ('RTL Development', 'SystemVerilog · Verdi · Design Vision', 'Read the hardware contract, simulate changes, and inspect the mapped logic and timing.'),
    'pd': ('Synthesis and Physical Design', 'Design Compiler · Design Vision · ICC2', 'Constrain and synthesize the example, build its reference library, and inspect a saved floorplan and initial placement.'),
}

def esc(text):
    return html.escape(str(text), quote=True)

def inline(text):
    pattern = r'(`[^`]+`|\[[^\]]+\]\(https?://[^)]+\)|https?://[^\s]+|\*\*[^*]+\*\*)'
    out = []
    for part in re.split(pattern, text):
        if part.startswith('`') and part.endswith('`'):
            out.append('<code>' + esc(part[1:-1]) + '</code>')
        elif part.startswith('**') and part.endswith('**'):
            out.append('<strong>' + esc(part[2:-2]) + '</strong>')
        elif match := re.fullmatch(r'\[([^\]]+)\]\((https?://[^)]+)\)', part):
            label, url = match.groups()
            out.append(f'<a href="{esc(url)}">{esc(label)}</a>')
        elif part.startswith(('https://', 'http://')):
            url = part.rstrip('.,;')
            tracking = event('GitHub click', 'all') if url.startswith(REPO) else ''
            out.append(f'<a href="{esc(url)}"{tracking}>{esc(url)}</a>{esc(part[len(url):])}')
        else:
            out.append(esc(part))
    return ''.join(out)

def event(name, guide):
    return f' data-umami-event="{esc(name)}" data-umami-event-guide="{esc(guide)}"'

def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def image_size(path):
    """Inspect bytes: some original captures use a .png name for JPEG data."""
    data = path.read_bytes()
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return struct.unpack('>II', data[16:24])
    if data.startswith(b'\xff\xd8'):
        offset = 2
        while offset < len(data):
            if data[offset] != 0xff:
                raise ValueError('Invalid JPEG marker: ' + str(path))
            while data[offset] == 0xff:
                offset += 1
            marker = data[offset]
            offset += 1
            if marker in (0xd8, 0xd9):
                continue
            length = struct.unpack('>H', data[offset:offset+2])[0]
            if marker in (0xc0, 0xc1, 0xc2):
                height, width = struct.unpack('>HH', data[offset+3:offset+7])
                return width, height
            if length < 2:
                break
            offset += length
    raise ValueError('Unsupported screenshot format: ' + str(path))

def crops_from_source(source):
    """Read literal crop definitions without importing or running document builders."""
    crops = {}
    for name in ('build_handouts.py', 'build_guides.py'):
        for node in ast.walk(ast.parse((source / name).read_text())):
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'CROPS' for t in node.targets):
                crops.update(ast.literal_eval(node.value))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'update' and isinstance(node.func.value, ast.Attribute) and node.func.value.attr == 'CROPS':
                crops.update(ast.literal_eval(node.args[0]))
    return crops

def render(text, source, crops):
    lines, out, toc, images = text.splitlines(), [], [], set()
    i, section = 0, 'introduction'
    while i < len(lines):
        line = lines[i].strip()
        if not line or line == '<!-- page -->':
            i += 1
            continue
        if line.startswith('## '):
            title = line[3:]
            section = slug(title)
            if section in [key for key, _ in toc]:
                raise ValueError('Duplicate heading: ' + title)
            toc.append((section, title))
            out.append(f'<h2 id="{section}">{inline(title)}</h2>')
            i += 1
        elif line.startswith('```'):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i])
                i += 1
            if i == len(lines):
                raise ValueError('Unclosed code block')
            out.append(f'<div class="code-block" data-section="{section}"><pre><code>{esc(chr(10).join(code))}</code></pre></div>')
            i += 1
        elif match := re.fullmatch(r'!\[(.*?)\]\(([^|)]+)(?:\|([\d.]+))?\)', line):
            caption, name, inches = match.groups()
            image = source / 'assets' / name
            width, height = image_size(image)
            x, y, w, h = crops.get(name, (0, 0, width, height))
            if min(x, y) < 0 or x + w > width or y + h > height:
                raise ValueError('Invalid crop: ' + name)
            url = BASE + 'assets/' + name
            style = f'width:{width/w*100:.6f}%;left:{-x/w*100:.6f}%;top:{-y/h*100:.6f}%;'
            max_width = min(w, float(inches or 6.5) * 130)
            out.append(f'<figure style="max-width:{max_width:g}px"><div class="screenshot-crop" style="aspect-ratio:{w}/{h}"><img src="{url}" alt="{esc(caption)}" width="{width}" height="{height}" loading="lazy" style="{style}"></div><figcaption>{esc(caption)} <a class="screenshot-link" href="{url}" target="_blank" rel="noopener">Open full screenshot</a></figcaption></figure>')
            images.add(name)
            i += 1
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append([cell.strip() for cell in lines[i].strip().strip('|').split('|')])
                i += 1
            if len(rows) < 2 or not all(re.fullmatch(r':?-+:?', c) for c in rows[1]):
                raise ValueError('Invalid table')
            table = '<thead><tr>' + ''.join(f'<th scope="col">{inline(c)}</th>' for c in rows[0]) + '</tr></thead><tbody>'
            for row in rows[2:]:
                if len(row) != len(rows[0]):
                    raise ValueError('Inconsistent table columns')
                table += '<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in row) + '</tr>'
            out.append('<div class="table-scroll" tabindex="0" role="region" aria-label="Reference table"><table>' + table + '</tbody></table></div>')
        elif re.match(r'\d+\. ', line):
            items = []
            start = int(line.split('.')[0])
            while i < len(lines) and (m := re.match(r'\d+\. (.*)', lines[i].strip())):
                items.append('<li>' + inline(m.group(1)) + '</li>')
                i += 1
            out.append(f'<ol start="{start}">' + ''.join(items) + '</ol>')
        else:
            paragraph = []
            while i < len(lines) and lines[i].strip() and not re.match(r'^(#|```|!\[|\||<!--|\d+\. )', lines[i]):
                paragraph.append(lines[i].strip())
                i += 1
            if not paragraph:
                raise ValueError('Unsupported manuscript syntax: ' + line)
            out.append('<p>' + inline(' '.join(paragraph)) + '</p>')
    return '\n'.join(out), toc, images

def actions(key='all'):
    pdf = '' if key == 'all' else f'<a href="{BASE}downloads/cae-{key}-handout.pdf" download{event("PDF download", key)}>Download PDF</a>'
    return f'<div class="guide-actions">{pdf}<a href="{REPO}" target="_blank" rel="noopener"{event("GitHub click", key)}>Lab and sources on GitHub ↗</a></div>'

def source_links(items, guide='all'):
    links = [f'<a href="{REPO}/blob/main/{esc(path)}" target="_blank" rel="noopener"{event("GitHub click", guide)}>{esc(label)}</a>' for label, path in items]
    return '<p class="source-links">Code: ' + ' · '.join(links) + '</p>'

def page(title, description, path, body, key='all'):
    home = (ROOT / 'index.html').read_text()
    nav = navigation('/learning/')
    bottom = footer()
    tracker = re.search(r'<script defer src="https://cloud.umami.is/script.js"[^>]*></script>', home).group()
    return f'''<!DOCTYPE html>
<!-- Generated by scripts/build_learning.py from the canonical guide repository. -->
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="/js/theme.js?v=20260923"></script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONT_URL}" rel="stylesheet">
<title>{esc(title)} | Abhinav Nandwani</title>
<meta name="description" content="{esc(description)}">
<meta name="author" content="Abhinav Nandwani">
<link rel="canonical" href="https://abhinavnandwani.com{path}">
<meta property="og:title" content="{esc(title)} | Abhinav Nandwani">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="article"><meta property="og:url" content="https://abhinavnandwani.com{path}">
{SOCIAL_IMAGE_META}
<link rel="icon" href="/favicon.ico?v=5" sizes="any"><link rel="icon" href="/images/favicon.svg?v=5" type="image/svg+xml">
<link rel="stylesheet" href="/css/style.css?v=20260923"><link rel="stylesheet" href="/css/learning.css?v=20260923">
{tracker}
<script defer src="/js/learning.js"></script>
</head>
<body id="top" data-guide="{key}">
<a href="#main" class="skip-link">Skip to content</a>
{nav}
<main id="main" class="container learning-main">{body}</main>
<div id="copy-status" role="status" class="sr-only" aria-live="polite"></div>
{bottom}
</body></html>
'''

def cards():
    rows = []
    for number, (key, (title, tools, description)) in enumerate(GUIDES.items(), 1):
        rows.append(f'<article class="resource-row"><span class="number">0{number}</span><div><h2><a href="{BASE}{key}/">{title} →</a></h2><p>{description}</p><p class="tools">{tools}</p></div><a class="pdf-link" href="{BASE}downloads/cae-{key}-handout.pdf" download{event("PDF download", key)}>PDF ↓</a></article>')
    return '<div class="resource-list">' + ''.join(rows) + '</div>'

def build(source):
    source = source.resolve()
    crops = crops_from_source(source)
    common = (source / 'manuscripts/common-access.md').read_text()
    code_links = json.loads((source / 'manuscripts/code-links.json').read_text())
    out = ROOT / BASE.strip('/')
    (out / 'assets').mkdir(parents=True, exist_ok=True)
    (out / 'downloads').mkdir(exist_ok=True)
    used_images = set()
    records = {}
    for key, (title, tools, description) in GUIDES.items():
        manuscript = (source / f'manuscripts/{key}.md').read_text().replace('{{ACCESS}}', common)
        manuscript = manuscript.replace('{{CODE_LINKS}}', '\n\n'.join(label + ': ' + REPO + '/blob/main/' + path for label, path in code_links[key]))
        if re.search(r'\{\{[A-Z_]+\}\}', manuscript):
            raise ValueError('Unresolved template')
        # Title, author, and introductory paragraph are rendered in the page header.
        intro, body = manuscript.split('## ', 1)
        intro_text = '\n'.join(intro.splitlines()[3:]).strip()
        rendered, toc, images = render('## ' + body, source, crops)
        rendered = rendered.replace('data-umami-event-guide="all"', f'data-umami-event-guide="{key}"')
        used_images |= images
        toc_html = '<ol>' + ''.join(f'<li><a href="#{anchor}">{esc(label)}</a></li>' for anchor, label in toc) + '</ol>'
        content = f'''<div class="breadcrumbs"><a href="/learning/">Learning Resources</a> / <a href="{BASE}">CAE Synopsys</a> / {title}</div>
<header class="learning-header"><p class="eyebrow">CAE lab notes · {tools}</p><h1>{title} on CAE</h1><p class="lede">{inline(intro_text)}</p><p class="guide-meta">By Abhinav Nandwani · Tested on CAE, 23 September 2026</p>{actions(key)}{source_links(code_links[key], key)}</header>
<div class="guide-layout"><aside class="guide-toc" aria-label="Guide sections"><details open><summary>On this page</summary>{toc_html}</details></aside><article class="guide-content">{rendered}<div class="guide-end"><p><a href="{BASE}">← All CAE guides</a></p>{actions(key)}</div></article></div>'''
        target = out / key / 'index.html'
        target.parent.mkdir(exist_ok=True)
        target.write_text(page(title + ' on CAE', description, BASE + key + '/', content, key))
        pdf = source / f'guides/cae-{key}-handout.pdf'
        shutil.copy2(pdf, out / 'downloads' / pdf.name)
        records[key] = {'sections': len(toc), 'code_blocks': len(re.findall(r'^```[^\n]*\n', manuscript, re.M)) // 2, 'expanded_manuscript_sha256': hashlib.sha256(manuscript.encode()).hexdigest(), 'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest()}
    for name in sorted(used_images):
        shutil.copy2(source / 'assets' / name, out / 'assets' / name)
    overview = f'''<div class="breadcrumbs"><a href="/learning/">Learning Resources</a> / CAE Synopsys</div>
<header class="learning-header"><p class="eyebrow">Terminal + GUI · UW–Madison CAE</p><h1>Synopsys on CAE</h1><p class="lede">Get from a browser login to a working chip design tool flow. These three guides walk through the same small register example, with real screenshots and commands you can run yourself.</p><p class="guide-meta">By Abhinav Nandwani · Tested on CAE, 23 September 2026</p>{actions()}</header>
{cards()}
<section class="overview-body"><h2>Start with access</h2><p>Use your own UW NetID to open <a href="https://guacamole.cae.wisc.edu">CAE Guacamole</a>. Complete the UW web sign-in and then the Linux desktop login. Each guide includes the full access walkthrough, terminal basics, and the Synopsys environment setup.</p><p>You need CAE access and its licensed tool environment. The teaching source is public; the tools and libraries stay on CAE. See the <a href="https://kb.wisc.edu/cae/163323">official CAE login instructions</a> if you cannot reach the desktop.</p>
<h2>One lab, three ways to explore it</h2><p>Verification follows stimulus and checks through simulation. RTL connects source behavior to mapped hardware. Synthesis and physical design follow constraints, reports, and initial placement. You can work through your guide independently.</p><div class="guide-note"><p>This is a one-register teaching exercise. Initial placement is not a completed place-and-route or signoff flow, and its timing and area are not accelerator PPA estimates. The <a href="{REPO}/blob/main/VALIDATION.md"{event('GitHub click', 'all')}>validation record</a> lists what was tested and the remaining limits.</p></div>
<h2>Example code</h2>{source_links(code_links['rtl'] + code_links['pd'][2:])}<p>The HTML pages and PDFs use the same manuscripts. Screenshots retain the original demonstration folder; use the paths in the command blocks.</p></section>'''
    (out / 'index.html').write_text(page('Synopsys on CAE', 'Visual guides to verification, RTL development, synthesis and physical design on UW–Madison CAE.', BASE, overview))
    index = f'''<header class="learning-header"><p class="eyebrow">Notes, walkthroughs, and runnable examples</p><h1>Learning Resources</h1><p class="lede">Notes from the workbench. Detailed walkthroughs, real screenshots, and the code to put things into practice.</p></header>
<div class="resource-list"><article class="resource-row"><span class="number">01</span><div><h2><a href="{BASE}">Synopsys on CAE →</a></h2><p>Three detailed guides to verification, RTL development, and synthesis and physical design on UW–Madison CAE. Includes Guacamole access, terminal commands, GUI walkthroughs, and a shared register lab.</p><p class="tools">3 guides · HTML + PDF · Runnable lab on GitHub</p></div></article></div>'''
    (ROOT / 'learning/index.html').write_text(page('Learning Resources', 'Hands-on engineering guides by Abhinav Nandwani, with screenshots, command-line examples, PDFs, and companion code.', '/learning/', index))
    manifest = {'source_repository': REPO, 'guides': records, 'images': sorted(used_images)}
    (out / 'source-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Built 5 pages, 3 PDFs, and {len(used_images)} original screenshots.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT.parent / 'cae-synopsys-guides')
    build(parser.parse_args().source)
