#!/usr/bin/env python3
"""
Generate search-engine pages for GitHub Pages: one static, crawlable HTML page per
Markdown file (in learn/), plus learn/index.html, sitemap.xml, robots.txt and .nojekyll.
Each page carries the full text so search engines can index it, and links into the
interactive reader (index.html).

Run by build_site.py. Edit the .md files, never the generated pages.
(c) 2026 Manikarnika Technologies - manikarnikatechnologies.in
"""
import html
import json
import posixpath
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://abvicky.github.io/FDE-Handbook-by-Vicky/"
REPO = "https://github.com/ABVicky/FDE-Handbook-by-Vicky"
COURSE = "FDE Handbook by Vicky"


def inline(text: str, links: dict) -> str:
    codes = []

    def keep_code(m):
        codes.append("<code>" + html.escape(m.group(1)) + "</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep_code, text)
    raw_tags = []

    def keep_tag(m):
        raw_tags.append(m.group(0))
        return f"\x01{len(raw_tags) - 1}\x01"

    text = re.sub(r"</?(?:br|kbd|sup|sub|strong|em|b|i|span)\b[^>]*>", keep_tag, text)
    text = html.escape(text, quote=False)

    def img(m):
        return f'<img src="{fix_url(m.group(2), links)}" alt="{html.escape(m.group(1))}" loading="lazy">'

    def link(m):
        return f'<a href="{fix_url(m.group(2), links)}">{m.group(1)}</a>'

    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", img, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"\x01(\d+)\x01", lambda m: raw_tags[int(m.group(1))], text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def fix_url(url: str, links: dict) -> str:
    """Point a Markdown link at the right place from a page in learn/."""
    url = html.unescape(url)
    if re.match(r"^(https?:|mailto:|#)", url):
        return html.escape(url)
    base = links.get("__dir__", "")
    target, _, anchor = url.partition("#")
    resolved = posixpath.normpath(posixpath.join(base, target)) if target else links.get("__self__", "")
    if resolved.endswith(".md") and resolved in links:
        return html.escape(links[resolved] + ("#" + anchor if anchor else ""))
    if resolved.startswith("assets/"):
        return "../" + html.escape(resolved)
    kind = "tree" if not posixpath.splitext(resolved)[1] else "blob"
    return html.escape(f"{REPO}/{kind}/main/{resolved}" + ("#" + anchor if anchor else ""))


def heading_id(text: str) -> str:
    t = re.sub(r"<[^>]+>", "", text).lower()
    t = re.sub(r"[^\w\s-]", "", t).strip()
    return re.sub(r"\s", "-", t)


def md_to_html(md: str, links: dict):
    out, toc = [], []
    lines = md.split("\n")
    i = 0
    para = []

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para), links) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s.startswith("```"):
            flush()
            lang = s[3:].strip()
            buf = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            if lang == "mermaid":
                out.append('<p class="diagram-note">📊 This section has a diagram. '
                           '<a href="{reader}">View it in the interactive reader</a>.</p>')
            else:
                out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
        elif not s:
            flush()
        elif re.match(r"^#{1,6} ", s):
            flush()
            level = len(s) - len(s.lstrip("#"))
            text = inline(s[level:].strip(), links)
            hid = heading_id(text)
            if level in (2, 3):
                toc.append((level, hid, re.sub(r"<[^>]+>", "", text)))
            out.append(f'<h{level} id="{hid}">{text}</h{level}>')
        elif re.match(r"^(-{3,}|\*{3,})$", s):
            flush()
            out.append("<hr>")
        elif s.startswith("<"):
            flush()
            buf = [line]
            while i + 1 < len(lines) and lines[i + 1].strip():
                i += 1
                buf.append(lines[i])
            out.append(re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                              lambda m: f'<a href="{fix_url(m.group(2), links)}">{m.group(1)}</a>', "\n".join(buf)))
        elif s.startswith(">"):
            flush()
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            i -= 1
            inner, _ = md_to_html("\n".join(buf), links)
            out.append("<blockquote>" + inner + "</blockquote>")
        elif s.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*:?-{2,}", lines[i + 1].strip()):
            flush()
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            head = cells(s)
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            i -= 1
            t = "<table><thead><tr>" + "".join(f"<th>{inline(c, links)}</th>" for c in head) + "</tr></thead><tbody>"
            t += "".join("<tr>" + "".join(f"<td>{inline(c, links)}</td>" for c in r) + "</tr>" for r in rows)
            out.append('<div class="table-wrap">' + t + "</tbody></table></div>")
        elif re.match(r"^\s*([-*+]|\d+\.)\s", line):
            flush()
            ordered = bool(re.match(r"^\s*\d+\.", line))
            items = []
            while i < len(lines) and (re.match(r"^\s*([-*+]|\d+\.)\s", lines[i])
                                      or (lines[i].startswith("   ") and lines[i].strip() and items)):
                m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", lines[i])
                if m and len(m.group(1)) < 2:
                    items.append([m.group(3)])
                else:
                    items[-1].append(lines[i].strip())
                i += 1
            i -= 1
            tag = "ol" if ordered else "ul"
            lis = []
            for it in items:
                body = inline(it[0], links)
                rest = [x for x in it[1:]]
                if rest:
                    body += "<br>" + "<br>".join(inline(re.sub(r"^([-*+])\s+", "• ", x), links) for x in rest)
                lis.append(f"<li>{body}</li>")
            out.append(f"<{tag}>" + "".join(lis) + f"</{tag}>")
        else:
            para.append(s)
        i += 1
    flush()
    return "\n".join(out), toc


CSS = """
:root{--bg:#F5F4F9;--card:#FFFFFF;--text:#34363D;--muted:#6B6E78;--line:#E4E2EC;--primary:#9E1915;--link:#9E1915;--code:#F0EEF6}
@media (prefers-color-scheme:dark){:root{--bg:#17191F;--card:#20232B;--text:#E8E8EC;--muted:#A3A6B0;--line:#33363F;--primary:#E53935;--link:#FF8A80;--code:#2A2D36}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font:17px/1.7 Inter,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--link)}img{max-width:100%;height:auto}
.top{position:sticky;top:0;z-index:2;background:var(--card);border-bottom:1px solid var(--line)}
.top-in{max-width:860px;margin:0 auto;padding:10px 16px;display:flex;gap:12px;align-items:center;justify-content:space-between}
.brand{font-weight:800;color:var(--text);text-decoration:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.btn{display:inline-block;background:var(--primary);color:#fff;font-weight:700;text-decoration:none;padding:8px 14px;border-radius:10px;white-space:nowrap}
.btn.ghost{background:transparent;color:var(--text);border:1px solid var(--line)}
main{max-width:860px;margin:0 auto;padding:24px 16px 48px}
.crumbs{font-size:14px;color:var(--muted)}.crumbs a{color:var(--muted)}
article{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:8px 24px 24px;margin-top:12px;overflow-wrap:break-word}
h1{font-size:2rem;line-height:1.25}h2{margin-top:2em;line-height:1.3}h3{line-height:1.35}
pre{background:#1E2028;color:#E8E8EC;padding:14px;border-radius:10px;overflow:auto;font-size:14px;line-height:1.55}
code{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:.88em}
:not(pre)>code{background:var(--code);padding:1px 5px;border-radius:5px}
blockquote{margin:1.2em 0;padding:4px 16px;border-left:4px solid var(--primary);background:var(--code);border-radius:0 10px 10px 0}
.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:15px}th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
.cta{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:18px 0;padding:14px 16px;border:1px dashed var(--primary);border-radius:12px}
.toc{font-size:15px}.toc ul{padding-left:18px;margin:6px 0}
.pager{display:flex;justify-content:space-between;gap:12px;margin-top:24px;flex-wrap:wrap}
.diagram-note{color:var(--muted);font-size:15px}
footer{max-width:860px;margin:0 auto;padding:0 16px 40px;color:var(--muted);font-size:14px}
details{border:1px solid var(--line);border-radius:10px;padding:8px 12px}
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Vicky Prasad Mahato">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{course}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}assets/social-card.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{site}assets/social-card.png">
<link rel="icon" type="image/svg+xml" href="../assets/icon.svg">
<link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">
<script type="application/ld+json">{jsonld}</script>
<style>{css}</style>
</head>
<body>
<header class="top"><div class="top-in">
  <a class="brand" href="index.html"><img src="../assets/icon.svg" alt="" width="22" height="22" style="vertical-align:-5px;margin-right:6px">{course}</a>
  <a class="btn" href="{reader}">Open in reader</a>
</div></header>
<main>
<nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">Home</a> › <a href="index.html">All lessons</a> › {label}</nav>
<article>
<div class="cta"><span>📖 This is the text version. The <strong>interactive reader</strong> adds search, diagrams and progress tracking.</span><a class="btn" href="{reader}">Read interactively</a><a class="btn ghost" href="{repo}">⭐ Star on GitHub</a></div>
{toc}
{body}
</article>
<nav class="pager" aria-label="Page navigation">{prev}{next}</nav>
</main>
<footer>
<p>{course} · Author: <a href="https://abvicky.in"><strong>Vicky</strong></a> · Platform built by <a href="https://www.manikarnikatechnologies.in/"><strong>Manikarnika Technologies</strong></a> · © 2026 All rights reserved.</p>
</footer>
</body>
</html>
"""



def slug(path: str) -> str:
    stem = path[:-3] if path.endswith(".md") else path
    s = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
    return (s or "home") + ".html"


def plain(md: str) -> str:
    t = re.sub(r"`([^`]*)`", r"\1", md)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"<[^>]+>", "", t)
    return re.sub(r"\s+", " ", re.sub(r"[*_>#|]", "", t)).strip()


def describe(md: str, title: str) -> str:
    """First real paragraph, trimmed to about 155 characters."""
    for block in re.split(r"\n\s*\n", md):
        b = block.strip()
        if not b or b.startswith(("#", "|", "```", "<", "---", "- [", "!")) or b.startswith("**Stage:**"):
            continue
        text = plain(b)
        text = re.sub(r"^\W*in plain words:\s*", "", text, flags=re.I)
        if len(text) > 40:
            if len(text) > 155:
                text = text[:152].rsplit(" ", 1)[0] + "…"
            return text
    return f"{title}, part of {COURSE}: learn to become a Forward Deployed Engineer step by step."


def section(path: str) -> str:
    m = re.match(r"modules/(\d\d)-", path)
    if m:
        return f"Module {m.group(1)}"
    top = path.split("/")[0]
    return {"interview-prep": "Interview prep", "case-studies": "Case studies", "templates": "Templates",
            "cookbooks": "Cookbooks", "projects": "AdmitFlow project", "resources": "Resources",
            "field-track": "Field Track", "progress": "Progress"}.get(top, "Handbook")


def ordered_paths(docs: dict) -> list:
    """Markdown files in a sensible reading order: entry pages, modules, then the rest."""
    md = [p for p in docs if p.endswith(".md")]
    first = [p for p in ("README.md", "START-HERE.md", "ROADMAP.md", "GLOSSARY.md", "ABOUT.md") if p in md]

    def key(p):
        if p.startswith("modules/"):
            sub = p.split("/", 2)[-1]
            rank = 0 if sub == "README.md" else 1 if "lessons/" in sub else 2 if "exercises/" in sub else 3
            return (0, p.split("/")[1], rank, p)
        return (1, p.split("/")[0], 0 if p.endswith("README.md") else 1, p)
    return first + sorted((p for p in md if p not in first), key=key)


def build(docs: dict) -> int:
    paths = ordered_paths(docs)
    links = {p: slug(p) for p in paths}
    out_dir = ROOT / "learn"
    out_dir.mkdir(exist_ok=True)
    for old in out_dir.glob("*.html"):
        old.unlink()
    today = date.today().isoformat()

    for k, p in enumerate(paths):
        md = docs[p]["content"]
        title_text = docs[p]["title"]
        body_md = re.sub(r"^# .*\n", "", md, count=1)
        links["__dir__"] = posixpath.dirname(p)
        links["__self__"] = p
        reader = "../index.html#" + p
        body, toc = md_to_html(body_md, links)
        body = body.replace("{reader}", reader)
        body = re.sub(r'(src|href)="(?:\./)?assets/', r'\1="../assets/', body)
        h1 = f"<h1>{html.escape(title_text)}</h1>"
        toc_html = ""
        if len(toc) > 2:
            toc_html = '<details class="toc"><summary>On this page</summary><ul>' + "".join(
                f'<li><a href="#{h}">{html.escape(t)}</a></li>' for lvl, h, t in toc if lvl == 2) + "</ul></details>"
        url = SITE + "learn/" + slug(p)
        sec = section(p)
        title = f"{title_text} | {COURSE}" if p != "README.md" else f"{COURSE}: Learn to Become a Forward Deployed Engineer"
        desc = describe(body_md, title_text)
        jsonld = {
            "@context": "https://schema.org", "@type": "LearningResource",
            "name": title_text, "description": desc, "url": url, "inLanguage": "en",
            "learningResourceType": "Handbook chapter",
            "author": {"@type": "Person", "name": "Vicky Prasad Mahato", "url": "https://abvicky.in"},
            "isPartOf": {"@type": "Course", "name": COURSE, "url": SITE},
            "image": SITE + "assets/social-card.png",
        }
        prev = (f'<a class="btn ghost" href="{slug(paths[k - 1])}">← {html.escape(docs[paths[k - 1]]["title"])}</a>'
                if k > 0 else "<span></span>")
        nxt = (f'<a class="btn ghost" href="{slug(paths[k + 1])}">{html.escape(docs[paths[k + 1]]["title"])} →</a>'
               if k + 1 < len(paths) else "")
        page = PAGE.format(
            title=html.escape(title), desc=html.escape(desc), url=url, site=SITE, course=COURSE,
            reader=reader, repo=REPO, label=html.escape(sec), toc=toc_html,
            body=h1 + "\n" + body, prev=prev, next=nxt, css=CSS,
            jsonld=json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/"))
        (out_dir / slug(p)).write_text(page, encoding="utf-8")

    groups = {}
    for p in paths:
        groups.setdefault(section(p), []).append(p)
    lists = "".join(
        f"<h2>{html.escape(g)}</h2><ul>" + "".join(
            f'<li><a href="{slug(p)}">{html.escape(docs[p]["title"])}</a></li>' for p in ps) + "</ul>"
        for g, ps in groups.items())
    idx_json = {
        "@context": "https://schema.org", "@type": "ItemList", "name": f"{COURSE}: all pages",
        "itemListElement": [{"@type": "ListItem", "position": n + 1, "url": SITE + "learn/" + slug(p),
                             "name": docs[p]["title"]} for n, p in enumerate(paths)],
    }
    page = PAGE.format(
        title=f"All Lessons | {COURSE}",
        desc=html.escape(f"Every page of {COURSE}: {len(paths)} lessons, exercises, builds and guides for becoming a "
                         "Forward Deployed Engineer, from client discovery to AI agents and interview prep."),
        url=SITE + "learn/", site=SITE, course=COURSE, reader="../index.html", repo=REPO, label="All pages",
        toc="", body=f"<h1>All lessons and guides</h1>{lists}", prev="", next="", css=CSS,
        jsonld=json.dumps(idx_json, ensure_ascii=False))
    (out_dir / "index.html").write_text(page, encoding="utf-8")

    def url_entry(loc, prio, freq="monthly"):
        return ["  <url>", f"    <loc>{loc}</loc>", f"    <lastmod>{today}</lastmod>",
                f"    <changefreq>{freq}</changefreq>", f"    <priority>{prio}</priority>", "  </url>"]

    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
          "  <url>", f"    <loc>{SITE}</loc>", f"    <lastmod>{today}</lastmod>", "    <changefreq>weekly</changefreq>",
          "    <priority>1.0</priority>", "    <image:image>", f"      <image:loc>{SITE}assets/social-card.png</image:loc>",
          f"      <image:title>{COURSE}</image:title>", "    </image:image>", "  </url>"]
    sm += url_entry(SITE + "learn/", "0.9", "weekly")
    for p in paths:
        if p in ("README.md", "START-HERE.md", "ROADMAP.md") or re.match(r"modules/\d\d-[^/]+/README\.md$", p):
            prio = "0.85"
        elif p.startswith(("modules/", "interview-prep/")):
            prio = "0.7"
        else:
            prio = "0.5"
        sm += url_entry(SITE + "learn/" + slug(p), prio)
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n", encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    return len(paths) + 1
