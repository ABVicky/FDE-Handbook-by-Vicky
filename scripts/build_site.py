#!/usr/bin/env python3
"""
Builder script to generate index.html for the FDE Handbook by Vicky.
Embeds all markdown files, code files, sample datasets, metadata, and interactive views.
"""
import os
import re
import json
import csv
from pathlib import Path

import seo_pages  # static, crawlable pages for search engines (learn/)

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

def extract_title(content, filename):
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            t = line[2:].strip()
            t = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', t)
            t = re.sub(r'[*_`]', '', t).strip()
            return t
    clean_name = Path(filename).stem.replace('-', ' ').replace('_', ' ').capitalize()
    return clean_name

def extract_headings(content):
    headings = []
    slug_counts = {}
    for line in content.splitlines():
        line = line.strip()
        m = re.match(r'^(#{2,3})\s+(.+)$', line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            clean_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
            clean_text = re.sub(r'[*_`]', '', clean_text).strip()
            
            slug = clean_text.lower()
            slug = re.sub(r'[^\w\s-]', '', slug)
            slug = re.sub(r'[\s_]+', '-', slug).strip('-')
            
            if not slug:
                slug = f"section-{len(headings)}"
            if slug in slug_counts:
                slug_counts[slug] += 1
                slug = f"{slug}-{slug_counts[slug]}"
            else:
                slug_counts[slug] = 0
            headings.append({'level': level, 'text': clean_text, 'slug': slug})
    return headings

def extract_module_syllabi(roadmap_content):
    syllabi = {}
    pattern = re.compile(r'### (Module (\d\d) [^\n]+)\n(.*?)(?=\n### Module \d\d|\n---|\Z)', re.DOTALL)
    for title, num, body in pattern.findall(roadmap_content):
        syllabi[num] = {
            'title': title.strip(),
            'body': body.strip()
        }
    return syllabi

def collect_all_data():
    docs = {}
    ignore_dirs = {'.git', '.gemini', 'scripts', 'learn', 'assets', 'node_modules'}
    
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        dirs[:] = sorted(d for d in dirs if d not in ignore_dirs and not d.startswith('.'))
        for f in sorted(files):  # sorted, so the build is identical on every operating system
            if f == 'index.html' or f.startswith('.'):
                continue
            full_path = Path(root) / f
            rel_path = full_path.relative_to(WORKSPACE_ROOT).as_posix()
            ext = full_path.suffix.lower()
            
            if ext in ('.md', '.py', '.sh', '.csv'):
                try:
                    with open(full_path, 'r', encoding='utf-8') as fh:
                        content = fh.read()
                except Exception as e:
                    print(f"Error reading {rel_path}: {e}")
                    continue
                
                title = extract_title(content, f) if ext == '.md' else f
                headings = extract_headings(content) if ext == '.md' else []
                word_count = len(re.findall(r'\w+', content))
                read_time = max(1, round(word_count / 180))
                
                docs[rel_path] = {
                    'path': rel_path,
                    'title': title,
                    'ext': ext,
                    'content': content,
                    'headings': headings,
                    'words': word_count,
                    'readTime': read_time
                }
                
    leads_sample = []
    csv_path = WORKSPACE_ROOT / 'projects' / 'admitflow' / 'data' / 'leads_sample.csv'
    if csv_path.exists():
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                leads_sample.append(row)
                
    roadmap_content = docs.get('ROADMAP.md', {}).get('content', '')
    syllabi = extract_module_syllabi(roadmap_content)
    
    return docs, syllabi, leads_sample

def get_icon_for_path(path):
    p = path.lower()
    if p == 'readme.md': return 'bookOpen'
    if p == 'roadmap.md': return 'map'
    if p == 'contributing.md': return 'gitPull'
    if p == 'about.md': return 'info'
    if p == 'glossary.md': return 'bookmark'
    if p == 'security.md': return 'shield'
    if p == 'code_of_conduct.md': return 'award'
    if 'checkpoint' in p or 'quiz' in p: return 'helpCircle'
    if 'lessons/' in p: return 'book'
    if 'exercises/' in p: return 'activity'
    if 'break-and-fix' in p or 'bug' in p: return 'bug'
    if 'build' in p: return 'hammer'
    if 'capstones/' in p or 'capstone' in p: return 'award'
    if 'field-track' in p: return 'compass'
    if 'resources' in p or 'job-descriptions' in p: return 'bookmark'
    if p.endswith('.py'): return 'fileCode'
    if p.endswith('.sh'): return 'terminal'
    if p.endswith('.csv'): return 'table'
    if 'case-studies' in p: return 'fileText'
    if 'templates' in p: return 'layers'
    if 'cookbooks' in p: return 'zap'
    if 'progress' in p or 'self-assessment' in p: return 'target'
    if 'interview-prep' in p: return 'award'
    if 'admitflow' in p: return 'cpu'
    return 'fileText'

STAGE_INFO = [
    ('s1', 'Stage 1', 'Foundations', 'The job, the computer, and programming.', range(1, 4)),
    ('s2', 'Stage 2', 'Engineering', 'Web apps, data, and the cloud.', range(4, 7)),
    ('s3', 'Stage 3', 'AI', 'Machine learning and building with LLMs.', range(7, 9)),
    ('s4', 'Stage 4', 'Real-world ready', 'Integrations, production, clients, career.', range(9, 13)),
]


def _strip_prefix(title):
    t = re.sub(r'^Module \d\d\s*[—–-]\s*', '', title)
    t = re.sub(r'^Module \d\d\s+', '', t)
    return t.strip()


def _numbered(title):
    """'Lesson 03 — FDE vs. roles' -> ('03', 'FDE vs. roles')."""
    m = re.match(r'^(?:Lesson|Exercise set|Exercise)\s+(\d+)\s*[—–:-]\s*(.+)$', title)
    return (m.group(1), m.group(2).strip()) if m else (None, title)


def _item(docs, path, title=None, icon=None, extra=False):
    t = title or (docs[path]['title'] if path.endswith('.md') else os.path.basename(path))
    num, t = _numbered(_strip_prefix(t)) if title is None else (None, t)
    it = {'path': path, 'title': t, 'icon': icon or get_icon_for_path(path)}
    if num:
        it['num'] = num
    if extra:
        it['extra'] = True
    return it


def build_module(docs, m_dir, m_num):
    """One module: its overview page plus pages grouped under plain-language headings."""
    m_path = f'modules/{m_dir}'
    files = [p for p in docs if p.startswith(m_path + '/')]
    readme = f'{m_path}/README.md'
    content = docs.get(readme, {}).get('content', '')
    title = _strip_prefix(docs.get(readme, {}).get('title', m_dir))
    time_m = re.search(r'\*\*Time:\*\*\s*([^·*\n]+?)\s+at\b', content) or re.search(r'\*\*Time:\*\*\s*([^·*\n]+)', content)
    lessons = sorted(p for p in files if '/lessons/' in p)
    meta = ' · '.join(x for x in [time_m.group(1).strip() if time_m else '', f'{len(lessons)} lessons' if lessons else ''] if x)

    def sub(p):
        return p[len(m_path) + 1:]

    def is_extra(p):
        sp = sub(p)
        return (not p.endswith('.md') or '/solutions/' in p or '/solution/' in p or sp == 'build-solution.md'
                or sp.endswith('SOLUTION.md') or (sp.startswith('break-and-fix/') and sp != 'break-and-fix/README.md'))

    sections = []
    top = []
    if f'{m_path}/setup.md' in docs:
        top.append(_item(docs, f'{m_path}/setup.md', 'Set up your computer', 'terminal'))
    if top:
        sections.append({'title': 'Before you start', 'items': top})
    if lessons:
        sections.append({'title': 'Lessons', 'items': [_item(docs, p) for p in lessons]})
    practice = []
    if f'{m_path}/exercises/README.md' in docs:
        practice.append(_item(docs, f'{m_path}/exercises/README.md', 'All exercises: how they work', 'activity'))
    practice += [_item(docs, p) for p in sorted(p for p in files if '/exercises/' in p and not is_extra(p)
                                                 and sub(p) != 'exercises/README.md')]
    if practice:
        sections.append({'title': 'Practice', 'items': practice})
    apply_it = []
    if f'{m_path}/capstones/README.md' in docs:
        apply_it.append(_item(docs, f'{m_path}/capstones/README.md', 'Capstone: choose your project', 'award'))
        apply_it += [_item(docs, p, icon='award') for p in sorted(p for p in files if '/capstones/' in p and not p.endswith('capstones/README.md'))]
    for name, label, icon in [('build.md', 'Build', 'hammer'), ('break-and-fix/README.md', 'Break & fix', 'bug'),
                              ('field-track.md', 'Field Track', 'compass')]:
        p = f'{m_path}/{name}'
        if p in docs:
            t = _strip_prefix(docs[p]['title'])
            t = re.sub(r'^(Build|Break & Fix|Field Track)\s*[—–:-]\s*', '', t)
            apply_it.append(_item(docs, p, f'{label}: {t}', icon))
    if apply_it:
        sections.append({'title': 'Apply it', 'items': apply_it})
    check = []
    if f'{m_path}/checkpoint.md' in docs:
        check.append(_item(docs, f'{m_path}/checkpoint.md', 'Checkpoint quiz', 'helpCircle'))
    if f'{m_path}/resources.md' in docs:
        check.append(_item(docs, f'{m_path}/resources.md', 'Further reading', 'bookmark'))
    if check:
        sections.append({'title': 'Check yourself', 'items': check})
    extras = sorted((p for p in files if is_extra(p)), key=lambda p: (not p.endswith('.md'), p))
    if extras:
        def answer_title(p):
            sp = sub(p)
            if sp == 'build-solution.md': return 'Build: my reference answer'
            if sp.endswith('SOLUTION.md'): return 'Break & fix: answer'
            if sp == 'exercises/solutions/README.md': return 'Exercise answers'
            m = re.match(r'exercises/solutions/(\d+)-', sp)
            if m and p.endswith('.md'): return f'Exercise {m.group(1)}: model answer'
            return None
        sections.append({'title': 'Answers & code', 'extra': True,
                         'items': [_item(docs, p, answer_title(p), extra=True) for p in extras]})
    def box(label):
        m = re.search(r'> \*\*' + re.escape(label) + r':\*\*\s*(.+)', content)
        return re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', m.group(1)).strip() if m else ''
    plain = box('In plain words')
    first = re.split(r'(?<=[.!?])\s+', plain)[0] if plain else ''
    icons = {1: 'sparkles', 2: 'cpu', 3: 'code', 4: 'layers', 5: 'database', 6: 'cloud', 7: 'brain', 8: 'bot',
             9: 'zap', 10: 'shieldCheck', 11: 'briefcase', 12: 'award'}
    return {'id': f'm{m_num:02d}', 'num': f'{m_num:02d}', 'title': title, 'path': readme, 'meta': meta,
            'time': time_m.group(1).strip() if time_m else '', 'lessons': len(lessons), 'icon': icons.get(m_num, 'book'),
            'desc': first, 'build': box("What you'll build"), 'sections': sections}


def build_dynamic_navigation(docs):
    """Sidebar tree: quick links, stages -> modules -> headed sections, then 'more' collections."""
    quick = [{'path': p, 'title': t, 'icon': i} for p, t, i in [
        ('START-HERE.md', 'Start here', 'rocket'), ('GLOSSARY.md', 'Glossary', 'bookmark')] if p in docs]

    modules_dir = WORKSPACE_ROOT / 'modules'
    mods = {}
    for d in sorted(os.listdir(modules_dir)):
        if (modules_dir / d).is_dir() and d[:2].isdigit():
            mods[int(d[:2])] = build_module(docs, d, int(d[:2]))
    stages = [{'id': sid, 'label': label, 'name': name, 'desc': desc, 'modules': [mods[n] for n in rng if n in mods]}
              for sid, label, name, desc, rng in STAGE_INFO]

    def coll(cid, title, icon, desc, sections):
        sections = [s for s in sections if s['items']]
        return {'id': cid, 'title': title, 'icon': icon, 'desc': desc, 'sections': sections} if sections else None

    af = [p for p in docs if p.startswith('projects/admitflow/')]
    more = [
        coll('admitflow', 'AdmitFlow project', 'cpu', 'My finished version of the system you build.', [
            {'title': 'Read first', 'items': [_item(docs, p, t, i) for p, t, i in [
                ('projects/admitflow/README.md', 'Project overview', 'bookOpen'),
                ('projects/admitflow/BRIEF.md', 'The client brief', 'fileText'),
                ('projects/practice/README.md', 'Practice projects', 'layers')] if p in docs]},
            {'title': 'Design docs & runbooks', 'items': [_item(docs, p) for p in sorted(af) if ('/docs/' in p or '/deploy/' in p) and p.endswith('.md')]},
            {'title': 'Assistant knowledge base', 'extra': True, 'items': [_item(docs, p, extra=True) for p in sorted(af) if '/course_docs/' in p]},
            {'title': 'Source code', 'extra': True, 'items': [_item(docs, p, extra=True) for p in sorted(af)
                                                             if p.endswith('.py') and 'test' not in p and '__init__' not in p]},
            {'title': 'Tests', 'extra': True, 'items': [_item(docs, p, extra=True) for p in sorted(af) if p.endswith('.py') and 'test' in p]},
            {'title': 'Sample data', 'extra': True, 'items': [_item(docs, p, extra=True) for p in sorted(af) if p.endswith('.csv')]},
        ]),
        coll('interview', 'Interview prep', 'award', 'Practice for every FDE interview round.', [
            {'title': 'Rounds', 'items': [_item(docs, 'interview-prep/README.md', 'How FDE interviews work', 'award')] +
             [_item(docs, p) for p in sorted(p for p in docs if p.startswith('interview-prep/') and p.endswith('.md')
                                             and '/solutions/' not in p and p != 'interview-prep/README.md')]},
            {'title': 'Model answers', 'extra': True, 'items': [_item(docs, p, extra=True) for p in sorted(
                p for p in docs if p.startswith('interview-prep/solutions/'))]},
        ]),
        coll('cases', 'Case studies', 'fileText', 'Real-style FDE engagements to learn from.', [
            {'title': 'Case studies', 'items': [_item(docs, p) for p in sorted(p for p in docs if p.startswith('case-studies/'))]}]),
        coll('templates', 'Templates', 'layers', 'Ready-to-copy documents for client work.', [
            {'title': 'Templates', 'items': [_item(docs, p) for p in sorted(p for p in docs if p.startswith('templates/'))]}]),
        coll('cookbooks', 'Cookbooks', 'zap', 'Patterns and fixes you will reuse.', [
            {'title': 'Cookbooks', 'items': [_item(docs, p) for p in sorted(p for p in docs if p.startswith('cookbooks/'))]}]),
        coll('extras', 'Resources & progress', 'compass', 'Your checklist, Field Track, and reading list.', [
            {'title': 'Resources', 'items': [_item(docs, p) for p in ['progress/self-assessment.md', 'field-track/README.md',
                                                                     'resources/README.md', 'resources/job-descriptions/README.md'] if p in docs]}]),
        coll('about', 'About this handbook', 'info', 'Who made it, and how to help.', [
            {'title': 'About', 'items': [_item(docs, p, t, i) for p, t, i in [
                ('README.md', 'Handbook overview', 'bookOpen'), ('ROADMAP.md', 'The full roadmap (detailed plan)', 'map'),
                ('ABOUT.md', 'About the handbook', 'info'), ('CONTRIBUTING.md', 'How to contribute', 'gitPull'),
                ('CODE_OF_CONDUCT.md', 'Code of conduct', 'award'), ('SECURITY.md', 'Security policy', 'shield')] if p in docs]}]),
    ]
    return {'quick': quick, 'stages': stages, 'more': [c for c in more if c]}


def safe_json(obj):
    s = json.dumps(obj, ensure_ascii=False)
    # Replace < and > with Unicode escape sequences so that strings like
    # </script> or <!-- can never break out of the HTML <script> block.
    return s.replace('<', '\\u003c').replace('>', '\\u003e')

def build():
    print("Collecting files...")
    docs, syllabi, leads_sample = collect_all_data()
    nav = build_dynamic_navigation(docs)
    print(f"Total documents: {len(docs)}")
    
    template_path = WORKSPACE_ROOT / 'scripts' / 'template.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    readme = docs.get('README.md')
    if readme:
        lines = readme['content'].split('\n')
        readme['content'] = '\n'.join(l for l in lines if not l.startswith('[![') and 'Read it online' not in l)
    docs_json = safe_json(docs)
    syllabi_json = safe_json(syllabi)
    leads_json = safe_json(leads_sample)
    nav_json = safe_json(nav)

    html = template.replace('/*{{DOCS_JSON}}*/{}', docs_json)
    html = html.replace('/*{{SYLLABI_JSON}}*/{}', syllabi_json)
    html = html.replace('/*{{LEADS_JSON}}*/[]', leads_json)
    html = html.replace('/*{{NAV_JSON}}*/{}', nav_json)
    html = html.replace('%%SITE%%', seo_pages.SITE)
    html = html.replace('%%DOC_COUNT%%', str(len(docs)))

    out_path = WORKSPACE_ROOT / 'index.html'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Successfully generated index.html ({len(html)} bytes) at {out_path}")

    count = seo_pages.build(docs)
    print(f"Generated {count} search-engine pages in learn/, plus sitemap.xml and robots.txt")

if __name__ == '__main__':
    build()
