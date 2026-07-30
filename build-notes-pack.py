#!/usr/bin/env python3
"""Regenerate notes-pack.html from every domain-*/notes.md.

Run from the repo root:  python build-notes-pack.py

Produces a single self-contained HTML file (no CDN, no network) holding all
eight domains' notes, with a domain/section sidebar, full-text search,
scrollspy, light/dark themes, and print styles.

The markdown subset supported here is exactly what the notes files use:
ATX headings, GFM tables, fenced code blocks, blockquotes, ordered and
unordered lists (nested), horizontal rules, and inline **bold**, *italic*,
_italic_, `code`, and [links](...). Underscore emphasis follows CommonMark's
flanking rule so snake_case identifiers survive untouched.

Cross-file links (../domain-N-x/notes.md#slug) are rewritten to in-page
anchors; headings are slugged GitHub-style and namespaced by domain code
(d1-, d2-, ...) so the eight files can share one document without anchor
collisions.
"""
import datetime as dt
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "notes-pack.html"

DOMAIN_META = {
    "domain-1-agents": ("D1", "Agents and Workflows", 14.7),
    "domain-2-applications": ("D2", "Applications and Integration", 33.1),
    "domain-3-claude-code": ("D3", "Claude Code", 3.1),
    "domain-4-eval-testing": ("D4", "Eval, Testing, and Debugging", 2.6),
    "domain-5-model-selection": ("D5", "Model Selection and Optimization", 16.8),
    "domain-6-prompt-context": ("D6", "Prompt and Context Engineering", 11.0),
    "domain-7-security": ("D7", "Security and Safety", 8.1),
    "domain-8-tools-mcps": ("D8", "Tools and MCPs", 10.6),
}

FOLDER_BY_CODE = {code: folder for folder, (code, _, _) in DOMAIN_META.items()}

# ---------------------------------------------------------------------------
# Inline rendering
# ---------------------------------------------------------------------------

CODE_SPAN_RE = re.compile(r"`([^`]+)`")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
ITALIC_RE = re.compile(r"(?<![\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])")
# CommonMark-style flanking rule for `_`: an opening `_` may not follow a word
# character and a closing `_` may not precede one, so snake_case identifiers
# (tool_use, max_tokens) are never treated as emphasis.
ITALIC_U_RE = re.compile(r"(?<![\w*])_(?!\s)([^_\n]+?)(?<!\s)_(?![\w])")
NOTES_LINK_RE = re.compile(r"^\.\./(domain-\d-[a-z0-9-]+)/notes\.md(?:#(.*))?$")


def slugify(text):
    """GitHub-compatible heading slug (matches the anchors already used in the
    notes' cross-references)."""
    t = CODE_SPAN_RE.sub(r"\1", text)
    t = LINK_RE.sub(r"\1", t)
    t = t.replace("**", "").replace("*", "")
    t = t.lower()
    t = re.sub(r"[^\w\s-]", "", t, flags=re.UNICODE)
    return t.strip().replace(" ", "-")


def plain_text(text):
    """Heading text with markup stripped — used for the sidebar and search."""
    t = CODE_SPAN_RE.sub(r"\1", text)
    t = LINK_RE.sub(r"\1", t)
    t = t.replace("**", "").replace("*", "")
    return t.strip()


def rewrite_href(href, code, errors, where):
    """Point cross-file notes links at in-page anchors; keep everything else
    resolvable from the repo root (where notes-pack.html lives)."""
    m = NOTES_LINK_RE.match(href)
    if m:
        folder, frag = m.group(1), m.group(2)
        if folder not in DOMAIN_META:
            errors.append(f"{where} — link to unknown domain folder {folder!r}")
            return href
        target = DOMAIN_META[folder][0].lower()
        return f"#{target}-{frag}" if frag else f"#{target}"
    if href.startswith("#"):
        return f"#{code.lower()}-{href[1:]}"
    if href.startswith("../"):
        # ../capstone-foo.md → capstone-foo.md (pack sits at the repo root)
        return href[3:]
    return href


def inline(text, code, errors, where):
    spans = []

    def stash(m):
        spans.append(m.group(1))
        return f"\x00{len(spans) - 1}\x00"

    text = CODE_SPAN_RE.sub(stash, text)
    text = html.escape(text, quote=False)

    # Generated <a …> open tags are stashed too: they carry attribute text
    # (target="_blank") that the emphasis passes below would otherwise chew up.
    tags = []

    def link(m):
        label, href = m.group(1), m.group(2)
        href = rewrite_href(html.unescape(href), code, errors, where)
        ext = "" if href.startswith("#") else ' target="_blank" rel="noopener"'
        tags.append(f'<a href="{html.escape(href, quote=True)}"{ext}>')
        return f"\x01{len(tags) - 1}\x01{label}</a>"

    text = LINK_RE.sub(link, text)
    text = BOLD_RE.sub(r"<strong>\1</strong>", text)
    text = ITALIC_RE.sub(r"<em>\1</em>", text)
    text = ITALIC_U_RE.sub(r"<em>\1</em>", text)
    text = re.sub(r"\x01(\d+)\x01", lambda m: tags[int(m.group(1))], text)
    text = re.sub(
        r"\x00(\d+)\x00",
        lambda m: f"<code>{html.escape(spans[int(m.group(1))], quote=False)}</code>",
        text,
    )
    return text


# ---------------------------------------------------------------------------
# Block rendering
# ---------------------------------------------------------------------------

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*$")
HR_RE = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")
FENCE_RE = re.compile(r"^\s*```+\s*([\w+-]*)\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
LIST_ITEM_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")


class Ctx:
    """Per-file rendering state: domain code, collected TOC, error sink."""

    def __init__(self, code, filename, errors):
        self.code = code
        self.filename = filename
        self.errors = errors
        self.toc = []
        self.seen_slugs = {}

    def anchor(self, raw_title, level):
        base = slugify(raw_title) or "section"
        n = self.seen_slugs.get(base, 0)
        self.seen_slugs[base] = n + 1
        if n:
            base = f"{base}-{n}"
        anchor = f"{self.code.lower()}-{base}"
        if level in (2, 3):
            self.toc.append({"level": level, "title": plain_text(raw_title), "id": anchor})
        return anchor


def split_row(line):
    cells = line.strip()
    if cells.startswith("|"):
        cells = cells[1:]
    if cells.endswith("|"):
        cells = cells[:-1]
    return [c.strip() for c in cells.split("|")]


def render_table(lines, i, ctx):
    header = split_row(lines[i])
    aligns = []
    for spec in split_row(lines[i + 1]):
        left, right = spec.startswith(":"), spec.endswith(":")
        aligns.append("center" if left and right else "right" if right else "left" if left else "")
    i += 2
    rows = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        rows.append(split_row(lines[i]))
        i += 1

    def cell(tag, text, idx):
        a = aligns[idx] if idx < len(aligns) else ""
        style = f' style="text-align:{a}"' if a else ""
        return f"<{tag}{style}>{inline(text, ctx.code, ctx.errors, ctx.filename)}</{tag}>"

    out = ['<div class="table-wrap"><table><thead><tr>']
    out += [cell("th", c, n) for n, c in enumerate(header)]
    out.append("</tr></thead><tbody>")
    for row in rows:
        out.append("<tr>")
        out += [cell("td", c, n) for n, c in enumerate(row)]
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out), i


def collect_list(lines, i):
    """Grab every line belonging to the list starting at lines[i]."""
    base = len(LIST_ITEM_RE.match(lines[i]).group(1))
    block = [lines[i]]
    i += 1
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            # blank continues the list only if an indented line follows
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and (
                len(lines[j]) - len(lines[j].lstrip()) > base
                or (LIST_ITEM_RE.match(lines[j]) and len(LIST_ITEM_RE.match(lines[j]).group(1)) >= base)
            ):
                block.append("")
                i += 1
                continue
            break
        indent = len(line) - len(line.lstrip())
        m = LIST_ITEM_RE.match(line)
        if m and len(m.group(1)) < base:
            break
        if not m and indent <= base:
            break
        block.append(line)
        i += 1
    return block, i


def render_list(block, ctx):
    base = len(LIST_ITEM_RE.match(block[0]).group(1))
    ordered = LIST_ITEM_RE.match(block[0]).group(2)[0].isdigit()
    items, current = [], None
    for line in block:
        m = LIST_ITEM_RE.match(line)
        if m and len(m.group(1)) == base:
            current = [m.group(3)]
            items.append(current)
        elif current is not None:
            current.append(line[base:] if len(line) > base else line.strip())
    out = ["<ol>" if ordered else "<ul>"]
    for item in items:
        inner = render_blocks(item, ctx)
        m = re.fullmatch(r"<p>(.*)</p>", inner, re.DOTALL)
        out.append(f"<li>{m.group(1) if m else inner}</li>")
    out.append("</ol>" if ordered else "</ul>")
    return "".join(out)


def render_blocks(lines, ctx):
    out = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        fence = FENCE_RE.match(line)
        if fence:
            lang = fence.group(1)
            i += 1
            buf = []
            while i < n and not FENCE_RE.match(lines[i]):
                buf.append(lines[i])
                i += 1
            i += 1
            label = f'<span class="code-lang">{html.escape(lang)}</span>' if lang else ""
            out.append(
                f'<div class="code-block">{label}<pre><code>'
                + html.escape("\n".join(buf), quote=False)
                + "</code></pre></div>"
            )
            continue

        head = HEADING_RE.match(line)
        if head:
            level = len(head.group(1))
            title = head.group(2)
            anchor = ctx.anchor(title, level)
            body = inline(title, ctx.code, ctx.errors, ctx.filename)
            if level == 1:
                out.append(f'<h2 class="doc-title" id="{anchor}">{body}</h2>')
            else:
                out.append(
                    f'<h{level} id="{anchor}">'
                    f'<a class="anchor" href="#{anchor}" aria-label="Link to this section">#</a>'
                    f"{body}</h{level}>"
                )
            i += 1
            continue

        if HR_RE.match(line):
            out.append("<hr>")
            i += 1
            continue

        if line.strip().startswith("|") and i + 1 < n and TABLE_SEP_RE.match(lines[i + 1]):
            table_html, i = render_table(lines, i, ctx)
            out.append(table_html)
            continue

        if line.lstrip().startswith(">"):
            quote = []
            while i < n and lines[i].lstrip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append(f'<blockquote>{render_blocks(quote, ctx)}</blockquote>')
            continue

        if LIST_ITEM_RE.match(line):
            block, i = collect_list(lines, i)
            out.append(render_list(block, ctx))
            continue

        para = []
        while i < n and lines[i].strip():
            if (
                HEADING_RE.match(lines[i])
                or HR_RE.match(lines[i])
                or FENCE_RE.match(lines[i])
                or lines[i].lstrip().startswith(">")
                or lines[i].lstrip().startswith("|")
                or LIST_ITEM_RE.match(lines[i])
            ):
                break
            para.append(lines[i].strip())
            i += 1
        if para:
            out.append(f'<p>{inline(" ".join(para), ctx.code, ctx.errors, ctx.filename)}</p>')
    return "".join(out)


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------


def render_domain(folder, code, name, weight, errors):
    path = ROOT / folder / "notes.md"
    if not path.exists():
        errors.append(f"{folder}/notes.md — file not found")
        return None
    text = path.read_text(encoding="utf-8")
    ctx = Ctx(code, f"{folder}/notes.md", errors)
    body = render_blocks(text.splitlines(), ctx)
    words = len(re.findall(r"\w+", text))
    return {
        "code": code,
        "name": name,
        "weight": weight,
        "folder": folder,
        "body": body,
        "toc": ctx.toc,
        "words": words,
        "minutes": max(1, round(words / 220)),
    }


CSS = """
:root{
  --bg:#f6f5f2; --panel:#fffefb; --ink:#1c1b19; --muted:#6b6862; --line:#e2ded4;
  --accent:#bd5b34; --accent-soft:#f4e6de; --code-bg:#f2efe8; --quote-bg:#fbf7ef;
  --mark:#ffe08a; --shadow:0 1px 2px rgba(28,27,25,.06),0 8px 24px rgba(28,27,25,.05);
}
:root[data-theme="dark"]{
  --bg:#16150f; --panel:#1e1d17; --ink:#eeece4; --muted:#a09b8e; --line:#332f26;
  --accent:#e08a5f; --accent-soft:#2e241d; --code-bg:#12110c; --quote-bg:#23211a;
  --mark:#7a5d13; --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.28);
}
*{box-sizing:border-box}
/* --hdr is remeasured from the real header height on load/resize; the 62px
   fallback keeps the sticky sidebar and anchor offsets right without JS. */
:root{--hdr:62px}
html{scroll-behavior:smooth; scroll-padding-top:calc(var(--hdr,62px) + 14px)}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font:16px/1.65 ui-sans-serif,-apple-system,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased;
}
a{color:var(--accent); text-decoration:none}
a:hover{text-decoration:underline}

/* ---------- top bar ---------- */
header.top{
  position:sticky; top:0; z-index:40;
  background:#fffefb; background:var(--panel);   /* opaque even if custom properties are stripped */
  border-bottom:1px solid var(--line); display:flex; align-items:center; flex-wrap:wrap;
  gap:14px 14px; padding:10px 18px;
}
:root[data-theme="dark"] header.top{background:#1e1d17; background:var(--panel)}
.brand{font-weight:700; letter-spacing:-.01em; white-space:nowrap}
.brand span{color:var(--muted); font-weight:500; font-size:13px; margin-left:8px}
.search{flex:1; max-width:520px; position:relative}
.search input{
  width:100%; padding:8px 76px 8px 34px; border:1px solid var(--line); border-radius:8px;
  background:var(--bg); color:var(--ink); font:inherit; font-size:14px;
}
.search .hits{position:absolute; right:58px; top:50%; transform:translateY(-50%);
  color:var(--muted); font-size:11.5px; pointer-events:none; white-space:nowrap;
  font-variant-numeric:tabular-nums}
.search .nav{position:absolute; right:6px; top:50%; transform:translateY(-50%); display:flex; gap:1px}
.search .nav button{
  border:0; background:none; color:var(--muted); font:inherit; font-size:15px; line-height:1;
  padding:3px 5px; border-radius:5px; cursor:pointer;
}
.search .nav button:hover{background:var(--accent-soft); color:var(--accent)}
.search input:focus{outline:2px solid var(--accent); outline-offset:-1px}
.search .icon{position:absolute; left:11px; top:50%; transform:translateY(-50%); color:var(--muted); font-size:13px}
.search .hint{position:absolute; right:10px; top:50%; transform:translateY(-50%); color:var(--muted); font-size:11px; border:1px solid var(--line); border-radius:4px; padding:1px 5px}
.tools{display:flex; gap:8px; margin-left:auto}
button.tool{
  border:1px solid var(--line); background:var(--bg); color:var(--ink); font:inherit; font-size:13px;
  padding:7px 11px; border-radius:8px; cursor:pointer;
}
button.tool:hover{border-color:var(--accent); color:var(--accent)}
#progress{position:fixed; top:0; left:0; height:2px; background:var(--accent); width:0; z-index:60}

/* ---------- layout ---------- */
.wrap{display:grid; grid-template-columns:300px minmax(0,1fr); gap:0; align-items:start}
nav.side{
  position:sticky; top:var(--hdr,62px); height:calc(100vh - var(--hdr,62px)); overflow-y:auto;
  border-right:1px solid var(--line);
  background:#fffefb; background:var(--panel); padding:16px 10px 60px;
}
:root[data-theme="dark"] nav.side{background:#1e1d17; background:var(--panel)}
nav.side::-webkit-scrollbar{width:8px}
nav.side::-webkit-scrollbar-thumb{background:var(--line); border-radius:4px}
.dom{margin-bottom:6px}
.dom > a.dom-link{
  display:flex; align-items:baseline; gap:8px; padding:7px 10px; border-radius:8px;
  color:var(--ink); font-size:14px; font-weight:600;
}
.dom > a.dom-link:hover{background:var(--accent-soft); text-decoration:none}
.dom-code{font-size:11px; font-weight:700; color:#fff; background:var(--accent); border-radius:4px; padding:1px 5px}
.dom-weight{margin-left:auto; font-size:11px; color:var(--muted); font-weight:500}
.toc{list-style:none; margin:2px 0 10px; padding:0 0 0 8px; border-left:1px solid var(--line)}
.toc li a{display:block; padding:4px 8px; font-size:13px; color:var(--muted); border-radius:6px; line-height:1.35}
.toc li a:hover{color:var(--ink); background:var(--accent-soft); text-decoration:none}
.toc li.lvl3 a{padding-left:20px; font-size:12.5px}
.toc li a.active{color:var(--accent); background:var(--accent-soft); font-weight:600}
.toc li.hidden,.dom.hidden{display:none}
.side-empty{color:var(--muted); font-size:13px; padding:10px}

main{width:100%; max-width:900px; margin:0 auto; padding:34px 40px 120px; min-width:0}

/* ---------- cover ---------- */
.cover{border:1px solid var(--line); background:var(--panel); border-radius:14px; padding:26px 28px; box-shadow:var(--shadow); margin-bottom:40px}
.cover h1{margin:0 0 6px; font-size:28px; letter-spacing:-.02em}
.cover .sub{color:var(--muted); margin:0 0 18px; font-size:14px}
.facts{display:flex; flex-wrap:wrap; gap:8px; margin-bottom:20px}
.fact{font-size:12.5px; border:1px solid var(--line); border-radius:999px; padding:4px 11px; color:var(--muted)}
.fact b{color:var(--ink)}
.cover table{margin:0}
.keys{font-size:12.5px; color:var(--muted); margin:0 0 18px}
.keys b{color:var(--ink); font-weight:600}
kbd{font-family:inherit; font-size:11.5px; border:1px solid var(--line); border-bottom-width:2px;
  border-radius:4px; padding:1px 5px; background:var(--bg); color:var(--ink)}
.bar{display:inline-block; height:6px; border-radius:3px; background:var(--accent); vertical-align:middle}

/* ---------- content ---------- */
section.domain{scroll-margin-top:calc(var(--hdr,62px) + 14px); padding-top:8px; min-width:0; max-width:100%}
.code-block,.table-wrap{min-width:0; max-width:100%}
section.domain + section.domain{margin-top:56px; border-top:1px solid var(--line); padding-top:40px}
.doc-title{font-size:25px; letter-spacing:-.02em; margin:0 0 4px; padding-bottom:8px; border-bottom:2px solid var(--accent)}
.eyebrow{display:flex; align-items:center; gap:10px; font-size:12px; color:var(--muted); margin-bottom:14px}
.eyebrow .dom-code{font-size:11px}
h3{font-size:20px; letter-spacing:-.01em; margin:34px 0 10px; padding-top:4px}
h4{font-size:16.5px; margin:26px 0 8px}
h5{font-size:14.5px; margin:20px 0 6px; color:var(--muted); text-transform:uppercase; letter-spacing:.04em}
h6{font-size:14px; margin:18px 0 6px}
h3,h4,h5,h6{scroll-margin-top:calc(var(--hdr,62px) + 14px); position:relative}
.anchor{position:absolute; left:-18px; color:var(--line); font-weight:400; opacity:0; padding-right:6px}
h3:hover .anchor,h4:hover .anchor{opacity:1; text-decoration:none}
p{margin:0 0 13px}
ul,ol{margin:0 0 14px; padding-left:22px}
li{margin:4px 0}
li > ul,li > ol{margin:6px 0 2px}
hr{border:0; border-top:1px solid var(--line); margin:30px 0}
strong{font-weight:650}
code{font-family:ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace; font-size:.875em;
  background:var(--code-bg); border:1px solid var(--line); border-radius:4px; padding:1px 4px}
.code-block{position:relative; margin:0 0 16px}
.code-block pre{margin:0; background:var(--code-bg); border:1px solid var(--line); border-radius:10px;
  padding:14px 16px; overflow-x:auto}
.code-block code{background:none; border:0; padding:0; font-size:13px; line-height:1.55; white-space:pre}
.code-lang{position:absolute; top:8px; right:10px; font-size:10.5px; letter-spacing:.06em;
  text-transform:uppercase; color:var(--muted)}
blockquote{margin:0 0 16px; padding:12px 16px; background:var(--quote-bg);
  border:1px solid var(--line); border-left:3px solid var(--accent); border-radius:0 8px 8px 0}
blockquote > :last-child{margin-bottom:0}
.table-wrap{overflow-x:auto; margin:0 0 18px; border:1px solid var(--line); border-radius:10px; background:var(--panel)}
table{border-collapse:collapse; width:100%; font-size:14px}
th,td{border-bottom:1px solid var(--line); padding:9px 12px; text-align:left; vertical-align:top}
th{background:var(--quote-bg); font-weight:650; font-size:13px; white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:var(--accent-soft)}
mark{background:var(--mark); color:inherit; border-radius:2px; padding:0 1px}
/* search hits — painted via the CSS Custom Highlight API, so no DOM is touched */
::highlight(find){background:var(--mark); color:var(--ink)}
::highlight(find-current){background:var(--accent); color:#fff}

.jump{position:fixed; right:22px; bottom:22px; z-index:30; display:none;
  border:1px solid var(--line); background:var(--panel); color:var(--ink); border-radius:999px;
  padding:9px 15px; font-size:13px; cursor:pointer; box-shadow:var(--shadow)}
.jump.show{display:block}
.noresults{display:none; color:var(--muted); font-size:14px; padding:14px; border:1px dashed var(--line); border-radius:10px}
.nojs{margin:14px 18px; padding:11px 14px; font-size:13.5px; border:1px solid var(--line);
  border-left:3px solid var(--accent); border-radius:0 8px 8px 0; background:#fbf7ef; background:var(--quote-bg)}

/* ---------- responsive ---------- */
@media (max-width:1000px){
  .wrap{grid-template-columns:1fr}
  nav.side{position:static; height:auto; max-height:none; border-right:0; border-bottom:1px solid var(--line)}
  main{padding:24px 18px 90px}
  .search .hint{display:none}
}

/* ---------- print ---------- */
@media print{
  :root{--bg:#fff; --panel:#fff; --ink:#000; --muted:#444; --line:#ccc; --accent:#000;
        --accent-soft:#fff; --code-bg:#f4f4f4; --quote-bg:#f8f8f8; --shadow:none}
  header.top,nav.side,.jump,.anchor,#progress,.keys{display:none !important}
  .wrap{display:block}
  main{max-width:none; padding:0}
  section.domain{break-before:page; border-top:0}
  section.domain:first-of-type{break-before:auto}
  h3,h4{break-after:avoid}
  table,blockquote,.code-block,.table-wrap{break-inside:avoid}
  a{color:#000; text-decoration:underline}
  .cover{border:0; padding:0}
}
"""

JS = """
(function(){
  var root=document.documentElement;
  var saved=localStorage.getItem('ccdvf-notes-theme');
  if(saved) root.setAttribute('data-theme',saved);
  else if(window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches) root.setAttribute('data-theme','dark');

  /* keep the sticky-sidebar offset and anchor scroll padding tied to the header's
     real height — it changes with font size and when the bar wraps on narrow screens */
  var hdr=document.querySelector('header.top');
  function measureHeader(){
    var h=Math.round(hdr.getBoundingClientRect().height);
    if(h) root.style.setProperty('--hdr', h+'px');
  }
  measureHeader();
  window.addEventListener('resize', measureHeader);
  if(window.ResizeObserver) new ResizeObserver(measureHeader).observe(hdr);

  var themeBtn=document.getElementById('theme');
  function paintTheme(){ themeBtn.textContent = root.getAttribute('data-theme')==='dark' ? 'Light' : 'Dark'; }
  paintTheme();
  themeBtn.addEventListener('click',function(){
    var next = root.getAttribute('data-theme')==='dark' ? 'light' : 'dark';
    root.setAttribute('data-theme',next);
    localStorage.setItem('ccdvf-notes-theme',next);
    paintTheme();
  });

  document.getElementById('print').addEventListener('click',function(){ window.print(); });

  /* ---- reading progress + back to top ---- */
  var bar=document.getElementById('progress'), jump=document.querySelector('.jump');
  function onScroll(){
    var h=document.documentElement.scrollHeight-window.innerHeight;
    bar.style.width = (h>0 ? (window.scrollY/h*100) : 0)+'%';
    jump.classList.toggle('show', window.scrollY>600);
  }
  window.addEventListener('scroll',onScroll,{passive:true}); onScroll();
  jump.addEventListener('click',function(){ window.scrollTo({top:0,behavior:'smooth'}); });

  /* ---- scrollspy ---- */
  var side=document.querySelector('nav.side');
  var links={}, targets=[];
  document.querySelectorAll('.toc a').forEach(function(a){
    var id=a.getAttribute('href').slice(1); links[id]=a;
    var el=document.getElementById(id); if(el) targets.push(el);
  });
  /* Keep the active entry visible by moving the sidebar's OWN scrollTop.
     scrollIntoView() is wrong here: it scrolls every scrollable ancestor,
     the document included, so as soon as the spy fired mid-navigation it
     hijacked the in-flight anchor scroll and yanked the reader back up to
     the sidebar — i.e. clicking a sub-entry appeared to jump to the top.
     On the narrow layout the sidebar is static and not a scroll container,
     so scrollHeight === clientHeight and this is a no-op. */
  function revealInSide(a){
    if(side.scrollHeight<=side.clientHeight) return;
    var box=a.getBoundingClientRect(), pane=side.getBoundingClientRect();
    if(box.top>=pane.top && box.bottom<=pane.bottom) return;
    side.scrollTop += (box.top-pane.top) - (pane.height-box.height)/2;
  }
  var active=null;
  var spy=new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(!e.isIntersecting) return;
      var a=links[e.target.id]; if(!a||a===active) return;
      if(active) active.classList.remove('active');
      a.classList.add('active'); active=a;
      revealInSide(a);
    });
  },{rootMargin:'-70px 0px -75% 0px'});
  targets.forEach(function(t){ spy.observe(t); });

  /* ---- search ----------------------------------------------------------
     Everything a keystroke needs is precomputed once into plain strings, so
     a query is a handful of String.includes() calls. Nothing in here mutates
     the DOM: matches are painted with the CSS Custom Highlight API, which
     needs no <mark> elements and therefore triggers no reflow. (An earlier
     version wrapped every hit in a <mark> and re-read innerText per section
     per keystroke — ~860 ms of blocking work for a common term like "re".) */
  var input=document.getElementById('q'), none=document.querySelector('.noresults');
  var counter=document.getElementById('hits');
  var MAX_HL=600, MIN_TERM=2, timer=null, idx=null, lastFirst=null, lastTerm=null;
  var matches=[], cur=-1;         /* every hit, in document order, + the one you're on */

  var supported = !!(window.CSS && CSS.highlights && window.Highlight);
  var hl = supported ? new Highlight() : null;        /* all hits */
  var hlCur = supported ? new Highlight() : null;     /* the current hit, painted on top */
  if(supported){
    CSS.highlights.set('find', hl);
    CSS.highlights.set('find-current', hlCur);
    hlCur.priority = 1;
  }

  function buildIndex(){
    if(idx) return idx;
    idx={sections:[], entries:[], nodes:[]};
    document.querySelectorAll('section.domain').forEach(function(sec){
      idx.sections.push({el:sec, code:(sec.dataset.code||'').toLowerCase(),
                         name:(sec.dataset.name||'').toLowerCase(),
                         text:sec.textContent.toLowerCase(), shown:true});
    });
    /* each sidebar entry carries the text of its own heading + the content
       under it, so "does this section match?" is one string test later */
    document.querySelectorAll('.toc a').forEach(function(a){
      var id=a.getAttribute('href').slice(1), h=document.getElementById(id);
      if(!h) return;
      var lvl=parseInt(h.tagName.slice(1),10), buf=[h.textContent], n=h.nextElementSibling;
      while(n){
        if(/^H[1-6]$/.test(n.tagName) && parseInt(n.tagName.slice(1),10)<=lvl) break;
        buf.push(n.textContent); n=n.nextElementSibling;
      }
      idx.entries.push({li:a.parentNode, dom:id.slice(0,2), text:buf.join(' ').toLowerCase()});
    });
    idx.doms=[].map.call(document.querySelectorAll('.dom'),function(d){
      return {el:d, code:(d.dataset.code||'').toLowerCase()};
    });
    if(hl){                       /* text nodes cached once for range building */
      var w=document.createTreeWalker(document.querySelector('main'),NodeFilter.SHOW_TEXT), n;
      while((n=w.nextNode())){
        var v=n.nodeValue;
        if(v && v.trim().length>1) idx.nodes.push({node:n, low:v.toLowerCase()});
      }
    }
    return idx;
  }
  if(window.requestIdleCallback) requestIdleCallback(buildIndex); else setTimeout(buildIndex,600);

  /* collect every hit as a Range, in document order (idx.nodes is already in
     document order, so `matches` doubles as the next/previous hit list) */
  function paint(term){
    matches=[]; cur=-1;
    if(!hl) return 0;
    hl.clear(); hlCur.clear();
    if(!term) return 0;
    for(var i=0;i<idx.nodes.length;i++){
      var rec=idx.nodes[i], from=0, j;
      while((j=rec.low.indexOf(term,from))!==-1){
        var r=document.createRange();
        r.setStart(rec.node,j); r.setEnd(rec.node,j+term.length);
        hl.add(r); matches.push(r); from=j+term.length;
        if(matches.length>=MAX_HL) return matches.length;
      }
    }
    return matches.length;
  }

  function label(){
    if(!matches.length){ counter.textContent = input.value.trim().length>=MIN_TERM ? '' : ''; return; }
    var total = matches.length>=MAX_HL ? MAX_HL+'+' : String(matches.length);
    counter.textContent = (cur<0 ? total + (matches.length===1?' hit':' hits')
                                 : (cur+1) + ' / ' + total);
  }

  /* step to the next/previous hit, wrapping at either end */
  function go(step){
    if(!matches.length) return;
    cur = (cur + step + matches.length) % matches.length;
    var r = matches[cur];
    hlCur.clear(); hlCur.add(r);
    var rect = r.getBoundingClientRect();
    if(rect.height || rect.width){
      var hdrH = parseInt(getComputedStyle(root).getPropertyValue('--hdr'),10) || 62;
      var top = window.scrollY + rect.top - Math.max(hdrH + 24, innerHeight*0.38);
      window.scrollTo({top: Math.max(0, top), behavior:'smooth'});
    }
    label();
  }

  function reset(){
    if(hl){ hl.clear(); hlCur.clear(); }
    matches=[]; cur=-1;
    if(idx){
      idx.sections.forEach(function(s){ s.el.style.display=''; s.shown=true; });
      idx.entries.forEach(function(e){ e.li.classList.remove('hidden'); });
      idx.doms.forEach(function(d){ d.el.classList.remove('hidden'); });
    }
    none.style.display='none';
    counter.textContent='';
    lastFirst=null; lastTerm=null;
  }

  function run(){
    var term=input.value.trim().toLowerCase();
    if(term.length<MIN_TERM){ reset(); return; }
    buildIndex();
    lastTerm=term;
    var any=false, first=null;
    idx.sections.forEach(function(s){
      var hit = s.text.indexOf(term)!==-1 || s.name.indexOf(term)!==-1 || s.code===term;
      if(hit!==s.shown){ s.el.style.display = hit ? '' : 'none'; s.shown=hit; }
      if(hit){ any=true; if(!first) first=s; }
    });
    idx.entries.forEach(function(e){
      e.li.classList.toggle('hidden', e.text.indexOf(term)===-1);
    });
    idx.doms.forEach(function(d){
      var sec=idx.sections.filter(function(s){ return s.code===d.code; })[0];
      d.el.classList.toggle('hidden', !(sec && sec.shown));
    });
    paint(term);
    none.style.display = any ? 'none' : 'block';
    label();
    /* only re-scroll when the winning section actually changed, so typing
       another letter inside the same result doesn't yank the page around */
    if(first && first!==lastFirst){
      lastFirst=first;
      window.scrollTo({top: Math.max(0, first.el.offsetTop - 80)});
    }
  }

  input.addEventListener('input',function(){ clearTimeout(timer); timer=setTimeout(run,150); });
  input.addEventListener('keydown',function(e){
    if(e.key==='Escape'){ clearTimeout(timer); input.value=''; reset(); input.blur(); return; }
    /* Enter / ↓ = next hit, Shift+Enter / ↑ = previous — the find-in-page idiom */
    if(e.key==='Enter'||e.key==='ArrowDown'||e.key==='ArrowUp'){
      e.preventDefault();
      /* flush a pending debounce so Enter is never early — but only re-run when
         the term actually changed, otherwise paint() would reset the cursor and
         every Enter would land back on hit 1 */
      if(input.value.trim().toLowerCase()!==lastTerm){ clearTimeout(timer); run(); }
      go((e.key==='ArrowUp'||e.shiftKey) ? -1 : 1);
    }
  });
  document.getElementById('prev').addEventListener('click',function(){ go(-1); });
  document.getElementById('next').addEventListener('click',function(){ go(1); });

  document.addEventListener('keydown',function(e){
    if(e.target.tagName==='INPUT') return;
    if(e.key==='/'){ e.preventDefault(); input.focus(); }
    if(e.key==='t'){ themeBtn.click(); }
    /* n / N step through hits without going back to the box */
    if((e.key==='n'||e.key==='N') && matches.length){ e.preventDefault(); go(e.shiftKey?-1:1); }
  });
})();
"""


def build_cover(domains, generated):
    rows = []
    total_words = sum(d["words"] for d in domains)
    total_minutes = sum(d["minutes"] for d in domains)
    for d in domains:
        bar_w = round(d["weight"] / 33.1 * 110)
        rows.append(
            f'<tr><td><span class="dom-code">{d["code"]}</span></td>'
            f'<td><a href="#{d["code"].lower()}">{html.escape(d["name"])}</a></td>'
            f'<td style="text-align:right">{d["weight"]}%</td>'
            f'<td><span class="bar" style="width:{bar_w}px"></span></td>'
            f'<td style="text-align:right">{d["words"]:,} words</td>'
            f'<td style="text-align:right">~{d["minutes"]} min</td></tr>'
        )
    return f"""<div class="cover">
  <h1>CCDV-F Notes Pack</h1>
  <p class="sub">Every <code>notes.md</code> from the eight domain folders, in one file — offline, searchable, printable.
     Generated {generated} · source of truth stays in the markdown.</p>
  <div class="facts">
    <span class="fact"><b>53</b> items</span>
    <span class="fact"><b>120</b> minutes</span>
    <span class="fact">pass at <b>720</b> / 1000</span>
    <span class="fact">exam code <b>CCDV-F v1.0</b></span>
    <span class="fact"><b>{total_words:,}</b> words total</span>
    <span class="fact">~<b>{total_minutes}</b> min read</span>
  </div>
  <p class="keys"><b>Keys:</b> <kbd>/</kbd> search · <kbd>Enter</kbd> next hit ·
     <kbd>Shift</kbd>+<kbd>Enter</kbd> previous · <kbd>n</kbd> / <kbd>N</kbd> next-previous while reading ·
     <kbd>Esc</kbd> clear · <kbd>t</kbd> theme</p>
  <div class="table-wrap"><table><thead><tr>
    <th></th><th>Domain</th><th style="text-align:right">Weight</th><th></th>
    <th style="text-align:right">Size</th><th style="text-align:right">Read</th>
  </tr></thead><tbody>{''.join(rows)}</tbody></table></div>
</div>"""


def build_sidebar(domains):
    out = []
    for d in domains:
        items = []
        for entry in d["toc"]:
            cls = "lvl2" if entry["level"] == 2 else "lvl3"
            items.append(
                f'<li class="{cls}"><a href="#{entry["id"]}">{html.escape(entry["title"])}</a></li>'
            )
        out.append(
            f'<div class="dom" data-code="{d["code"]}">'
            f'<a class="dom-link" href="#{d["code"].lower()}">'
            f'<span class="dom-code">{d["code"]}</span>{html.escape(d["name"])}'
            f'<span class="dom-weight">{d["weight"]}%</span></a>'
            f'<ul class="toc">{"".join(items)}</ul></div>'
        )
    return "".join(out)


def build_body(domains):
    out = []
    for d in domains:
        out.append(
            f'<section class="domain" id="{d["code"].lower()}" data-code="{d["code"]}" '
            f'data-name="{html.escape(d["name"], quote=True)}">'
            f'<div class="eyebrow"><span class="dom-code">{d["code"]}</span>'
            f'<span>{d["weight"]}% of the exam</span><span>·</span>'
            f'<span>{d["words"]:,} words · ~{d["minutes"]} min</span><span>·</span>'
            f'<a href="{d["folder"]}/notes.md">{d["folder"]}/notes.md</a></div>'
            f'{d["body"]}</section>'
        )
    return "".join(out)


def main():
    errors = []
    domains = []
    for folder, (code, name, weight) in DOMAIN_META.items():
        d = render_domain(folder, code, name, weight, errors)
        if d:
            domains.append(d)

    for d in domains:
        print(f"  {d['code']}: {d['words']:,} words, {len(d['toc'])} TOC entries")

    if errors:
        print(f"\n{len(errors)} problem(s) — notes-pack.html NOT written:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    generated = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CCDV-F Notes Pack — all eight domains</title>
<style>{CSS}</style>
</head>
<body>
<div id="progress"></div>
<header class="top">
  <div class="brand">CCDV-F Notes Pack<span>all 8 domains</span></div>
  <div class="search">
    <span class="icon">&#9906;</span>
    <input id="q" type="search" placeholder="Search all notes…" autocomplete="off" spellcheck="false"
           title="Enter = next hit · Shift+Enter = previous · Esc = clear">
    <span class="hits" id="hits"></span>
    <span class="nav">
      <button type="button" id="prev" title="Previous hit (Shift+Enter)" aria-label="Previous hit">&#8249;</button>
      <button type="button" id="next" title="Next hit (Enter)" aria-label="Next hit">&#8250;</button>
    </span>
  </div>
  <div class="tools">
    <button class="tool" id="theme">Dark</button>
    <button class="tool" id="print">Print</button>
  </div>
</header>
<noscript><div class="nojs">Search, the theme toggle, and section highlighting need JavaScript.
This preview has it disabled — open <code>notes-pack.html</code> directly in a browser for the
full pack. All the notes themselves are below either way.</div></noscript>
<div class="wrap">
  <nav class="side">{build_sidebar(domains)}</nav>
  <main>
    {build_cover(domains, generated)}
    <div class="noresults">No section matches that search.</div>
    {build_body(domains)}
  </main>
</div>
<button class="jump" title="Back to top">&#8593; Top</button>
<script>{JS}</script>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"\nWrote {OUT.name} ({len(page):,} bytes).")


if __name__ == "__main__":
    main()
