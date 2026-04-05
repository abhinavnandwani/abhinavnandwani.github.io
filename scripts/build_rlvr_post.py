#!/usr/bin/env python3
"""Merge content/notes/rlvr-gpu-costs.md + dashboard snippet into posts/rlvr-training-costs.html"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "content" / "notes" / "rlvr-gpu-costs.md"
DASH_SRC = ROOT / "content" / "notes" / "rlvr-dashboard-source.html"
OUT = ROOT / "posts" / "rlvr-training-costs.html"

FN_RE = re.compile(r"\[\^(\d+)\]")


def footnote_refs(s: str) -> str:
    """Turn [^12] into superscript links to #ref-12."""

    def repl(m: re.Match[str]) -> str:
        n = m.group(1)
        return (
            f'<sup class="footnote-ref"><a href="#ref-{n}" aria-describedby="ref-{n}">{n}</a></sup>'
        )

    return FN_RE.sub(repl, s)


def format_inline_cell(s: str) -> str:
    return footnote_refs(inline_md(html.escape(s)))


def linkify_urls_in_text(s: str) -> str:
    """Linkify https URLs in already-escaped HTML text."""

    def repl(m: re.Match[str]) -> str:
        url = m.group(0)
        return f'<a href="{url}" rel="noopener noreferrer" target="_blank">{url}</a>'

    return re.sub(r'https?://[^\s|<>"]+', repl, s)


MD_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")


def _linkify_bare_urls_after_escape(s: str) -> str:
    """Linkify raw https URLs in escaped HTML, but not inside existing <a>...</a>."""

    def repl(m: re.Match[str]) -> str:
        url = m.group(0)
        return (
            f'<a href="{html.escape(url, quote=True)}" rel="noopener noreferrer" '
            f'target="_blank">{url}</a>'
        )

    parts = re.split(r"(<a\b[^>]*>.*?</a>)", s, flags=re.IGNORECASE | re.DOTALL)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"https?://[^\s<\"'\]]+", repl, parts[i])
    return "".join(parts)


def reference_item_to_html(raw: str) -> str:
    """Turn one reference line into HTML: markdown [label](url), **bold**, bare URLs."""
    out: list[str] = []
    pos = 0
    for m in MD_LINK_RE.finditer(raw):
        chunk = raw[pos : m.start()]
        esc = html.escape(chunk)
        esc = inline_md(esc)
        out.append(_linkify_bare_urls_after_escape(esc))
        label, url = m.group(1), m.group(2)
        label_html = inline_md(html.escape(label))
        out.append(
            f'<a href="{html.escape(url, quote=True)}" rel="noopener noreferrer" '
            f'target="_blank">{label_html}</a>'
        )
        pos = m.end()
    tail = raw[pos:]
    esc = html.escape(tail)
    esc = inline_md(esc)
    out.append(_linkify_bare_urls_after_escape(esc))
    return "".join(out)


def is_sep_row(cells: list[str]) -> bool:
    if not cells:
        return False
    for c in cells:
        t = re.sub(r"\s+", "", c)
        if not re.fullmatch(r":?-{3,}:?", t):
            return False
    return True


def inline_md(s: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)


def md_table_to_html(block: str) -> str:
    lines = [ln.rstrip() for ln in block.strip().splitlines() if ln.strip().startswith("|")]
    if len(lines) < 2:
        return ""
    rows: list[list[str]] = []
    for line in lines:
        parts = [p.strip() for p in line.strip().split("|")]
        rows.append(parts[1:-1] if parts and parts[0] == "" else parts)
    body_start = 1
    if len(rows) > 1 and is_sep_row(rows[1]):
        body_start = 2
    out = ['<div class="table-wrap"><table class="post-table">']
    out.append("<thead><tr>")
    for c in rows[0]:
        out.append(f"<th>{format_inline_cell(c)}</th>")
    out.append("</tr></thead><tbody>")
    for r in rows[body_start:]:
        out.append("<tr>")
        for c in r:
            out.append(f"<td>{format_inline_cell(c)}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def body_to_html(body: str) -> str:
    parts: list[str] = []
    buf: list[str] = []
    in_table = False

    def flush_para():
        nonlocal buf
        t = "\n".join(buf).strip()
        buf = []
        if not t or t == "---":
            return
        if t.startswith("|"):
            parts.append(md_table_to_html(t))
            return
        for para in re.split(r"\n{2,}", t):
            para = para.strip()
            if not para or para == "---":
                continue
            if para.startswith("### "):
                inner = footnote_refs(inline_md(html.escape(para[4:].strip())))
                parts.append(f"<h3>{inner}</h3>")
            elif para.startswith("|"):
                parts.append(md_table_to_html(para))
            elif para.startswith("- "):
                items = re.findall(r"^-\s+(.+)$", para, re.MULTILINE)
                if items:
                    lis = "".join(
                        f"<li>{footnote_refs(inline_md(html.escape(i)))}</li>" for i in items
                    )
                    parts.append(f"<ul>{lis}</ul>")
                else:
                    parts.append(f"<p>{footnote_refs(inline_md(html.escape(para)))}</p>")
            else:
                parts.append(f"<p>{footnote_refs(inline_md(html.escape(para)))}</p>")

    for line in body.splitlines():
        if line.strip().startswith("|"):
            if in_table:
                buf.append(line)
            else:
                flush_para()
                buf = [line]
                in_table = True
            continue
        if in_table and line.strip() == "":
            flush_para()
            t = "\n".join(buf)
            buf = []
            parts.append(md_table_to_html(t))
            in_table = False
            continue
        in_table = False
        buf.append(line)
    if buf:
        if any(b.strip().startswith("|") for b in buf):
            parts.append(md_table_to_html("\n".join(buf)))
        else:
            flush_para()
    return "\n".join(parts)


def references_section_to_html(body: str) -> str:
    body = body.strip()
    pat = re.compile(r"^\[\^(\d+)\]:\s*", re.MULTILINE)
    matches = list(pat.finditer(body))
    if not matches:
        return (
            '<section class="post-section post-references" aria-labelledby="references-heading">'
            '<h2 id="references-heading">References</h2>'
            "<p>(References block was empty.)</p></section>"
        )

    items: list[tuple[int, str]] = []
    for i, m in enumerate(matches):
        n = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        raw = body[start:end].strip()
        safe = reference_item_to_html(raw)
        items.append((n, safe))

    items.sort(key=lambda x: x[0])
    lis = "".join(f'<li id="ref-{n}" value="{n}">{content}</li>' for n, content in items)
    ol = f'<ol class="reference-list">{lis}</ol>'
    return (
        '<section class="post-section post-references" aria-labelledby="references-heading">'
        '<h2 id="references-heading">References</h2>'
        f"{ol}</section>"
    )


def md_section_to_html(sec: str) -> str:
    sec = sec.strip()
    if not sec:
        return ""
    lines = sec.splitlines()
    if lines[0].startswith("# "):
        return ""
    if lines[0].startswith("## "):
        title = lines[0][3:].strip()

        def slug(s: str) -> str:
            s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
            return s[:80] or "section"

        body = "\n".join(lines[1:]).strip()
        if title.lower() == "references":
            return references_section_to_html(body)
        inner = body_to_html(body)
        return f'<h2 id="{slug(title)}">{html.escape(title)}</h2>\n{inner}'
    return body_to_html(sec)


def extract_dashboard(raw: str) -> str:
    raw = raw.strip()
    ei = raw.find("</style>")
    rest = raw[ei + 8 :].strip() if ei >= 0 else raw
    rest = re.sub(
        r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/Chart\.js/[^"]+"></script>\s*',
        "",
        rest,
        count=1,
    )
    return rest


def fix_dashboard_js(rest: str) -> str:
    rest = rest.replace(
        "h100:{name:'H100 SXM',mem:80",
        "h100:{name:'H100 SXM',vendor:'NVIDIA',mem:80",
    )
    rest = rest.replace(
        "h200:{name:'H200 SXM',mem:141",
        "h200:{name:'H200 SXM',vendor:'NVIDIA',mem:141",
    )
    rest = rest.replace(
        "mi300x:{name:'MI300X',mem:192",
        "mi300x:{name:'MI300X',vendor:'AMD',mem:192",
    )
    rest = rest.replace(
        "var dark=matchMedia('(prefers-color-scheme:dark)').matches;",
        "var dark=document.documentElement.getAttribute('data-theme')==='dark';",
    )
    rest = rest.replace(
        "['mSel','algoSel','rollSel','tokSel'].forEach(function(id){document.getElementById(id).addEventListener('change',render);});\nrender();",
        "['mSel','algoSel','rollSel','tokSel'].forEach(function(id){document.getElementById(id).addEventListener('change',render);});\n"
        "window.addEventListener('site-theme-change',function(){killCharts();render();});\nrender();",
    )
    return rest


def main() -> None:
    md_text = MD.read_text(encoding="utf-8")
    dash_raw = DASH_SRC.read_text(encoding="utf-8")
    dash_body = fix_dashboard_js(extract_dashboard(dash_raw))

    md_text = md_text.lstrip("\ufeff")
    if md_text.startswith("# "):
        first_nl = md_text.find("\n")
        title = md_text[2:first_nl].strip()
        rest_md = md_text[first_nl + 1 :].lstrip()
    else:
        title = "RLVR GPU training costs"
        rest_md = md_text

    # Split the lede (text before first ## heading) from the rest
    first_h2 = re.search(r"\n(?=## )", rest_md)
    if first_h2:
        lede_md = rest_md[: first_h2.start()].strip()
        sections_md = rest_md[first_h2.start() :]
    else:
        lede_md = rest_md.strip()
        sections_md = ""

    lede_html = body_to_html(lede_md) if lede_md else ""

    sections = re.split(r"\n(?=## )", sections_md) if sections_md else []
    article_parts: list[str] = []
    ref_html: str | None = None
    for sec in sections:
        h = md_section_to_html(sec)
        if not h:
            continue
        is_ref = h.lstrip().startswith('<section class="post-section post-references"')
        if is_ref:
            ref_html = h
            continue
        if article_parts:
            article_parts.append("<hr>")
        article_parts.append(h)

    desc = (
        "Measured GRPO throughput, cloud GPU pricing (April 2026), published RLVR runs, "
        "cited sources, and an interactive cost estimator for RLVR training."
    )
    slug_url = "rlvr-training-costs.html"
    canonical = f"https://abhinavnandwani.com/posts/{slug_url}"

    lede_indented = "\n".join("                " + l for l in lede_html.splitlines()) if lede_html else ""
    joined = "\n".join("                " + p.replace("\n", "\n                ") for p in article_parts)
    ref_sep = ""
    if ref_html and article_parts:
        ref_sep = "            <hr>\n"
    ref_indented = (
        "\n".join("            " + l for l in ref_html.splitlines()) if ref_html else ""
    )

    shell = f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="/js/theme.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <title>{html.escape(title)} - Abhinav Nandwani</title>
    <meta name="description" content="{html.escape(desc)}">
    <meta property="og:title" content="{html.escape(title)} - Abhinav Nandwani">
    <meta property="og:description" content="{html.escape(desc)}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="https://abhinavnandwani.com/images/profile.png">
    <link rel="canonical" href="{canonical}">
    <link rel="icon" href="/favicon.ico?v=5" sizes="any">
    <link rel="icon" href="/images/favicon.svg?v=5" type="image/svg+xml">
    <link rel="apple-touch-icon" href="/images/favicon-192x192.png?v=5">
    <link rel="stylesheet" href="/css/style.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js" crossorigin="anonymous"></script>
</head>
<body>
    <nav>
        <div class="container">
            <div class="nav-brand">
                <a href="/" class="nav-home">Abhinav Nandwani</a>
                <ul class="nav-inline">
                    <li><a href="/blog.html" class="active">Blog</a></li>
                </ul>
            </div>
            <ul class="nav-links nav-external" aria-label="Site and profiles">
                <li><a href="/resume.html">Resume</a></li>
                <li><a href="mailto:nandwani2@wisc.edu">Email</a></li>
                <li><a href="https://github.com/abhinavnandwani" target="_blank" rel="noopener noreferrer">GitHub</a></li>
                <li><a href="https://www.linkedin.com/in/abhinavnandwani" target="_blank" rel="noopener noreferrer">LinkedIn</a></li>
                <li><a href="https://scholar.google.com/citations?user=KEqTDt4AAAAJ&amp;hl=en" target="_blank" rel="noopener noreferrer">Google Scholar</a></li>
            </ul>
        </div>
    </nav>

    <main class="container">
        <article class="post-content">
            <header class="page-header">
                <h1>{html.escape(title)}</h1>
                <div class="post-meta">
                    <time datetime="2026-04-04">April 4, 2026</time>
                    <span class="post-tag">ML systems · RLVR · GPUs</span>
                </div>
            </header>

            <aside class="post-disclaimer" role="note">All opinions are my own. Generated with Claude Code — watch out for mistakes.</aside>

            <div class="post-lede">
{lede_indented}
            </div>

            <section class="post-section" aria-labelledby="interactive-estimator">
                <h2 id="interactive-estimator">Interactive cost &amp; time estimator</h2>
                <p>Adjust model, algorithm, rollout length, and token target to compare H100, H200, and MI300X. Figures use measured 7B GRPO/PPO baselines where available, rollout-length penalties from the long-form note below, and April 2026 list pricing. <strong>Estimates are illustrative</strong>—see confidence notes under the charts.</p>
                <div class="rlvr-dashboard" role="region" aria-label="RLVR training cost dashboard">
{dash_body}
                </div>
            </section>

            <section class="post-section post-article">
{joined}
            </section>
{ref_sep}{ref_indented}

            <div class="back-link">
                <a href="/blog.html">← Back to Blog</a>
            </div>
        </article>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2026 Abhinav Nandwani</p>
        </div>
    </footer>

    <button type="button" class="theme-toggle" aria-label="Toggle light or dark theme">
        <svg class="sun-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        <svg class="moon-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
    </button>
</body>
</html>
"""
    OUT.write_text(shell, encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
