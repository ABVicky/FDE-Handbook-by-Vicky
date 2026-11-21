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
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        for f in files:
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

def build_dynamic_navigation(docs):
    nav = []

    # 1. Start Here
    nav.append({
        "id": "start",
        "title": "Start Here",
        "icon": "rocket",
        "items": [
            {"path": "README.md", "title": "Handbook Overview", "badge": "Guide", "icon": "bookOpen"},
            {"path": "START-HERE.md", "title": "Start Here", "badge": "Begin", "icon": "rocket"},
            {"path": "ROADMAP.md", "title": "Master Roadmap", "badge": "Core", "icon": "map"},
            {"path": "ABOUT.md", "title": "About & Infrastructure", "badge": "About", "icon": "info"},
            {"path": "GLOSSARY.md", "title": "FDE Glossary", "badge": "Glossary", "icon": "bookmark"},
            {"path": "CONTRIBUTING.md", "title": "Contributing", "badge": "Community", "icon": "gitPull"},
            {"path": "SECURITY.md", "title": "Security Policy", "badge": "Security", "icon": "shield"},
            {"path": "CODE_OF_CONDUCT.md", "title": "Code of Conduct", "badge": "Community", "icon": "award"}
        ]
    })

    # 2. Stages 1 to 4
    stages = {
        'stage1': {'id': 'stage1', 'title': 'Stage 1 — Foundations', 'icon': 'terminal', 'items': []},
        'stage2': {'id': 'stage2', 'title': 'Stage 2 — Engineering', 'icon': 'layers', 'items': []},
        'stage3': {'id': 'stage3', 'title': 'Stage 3 — AI & ML', 'icon': 'brain', 'items': []},
        'stage4': {'id': 'stage4', 'title': 'Stage 4 — Field-Ready', 'icon': 'shieldCheck', 'items': []}
    }

    # Discover all modules in modules/
    modules_dir = WORKSPACE_ROOT / 'modules'
    if modules_dir.exists():
        mod_dirs = sorted([d for d in os.listdir(modules_dir) if (modules_dir / d).is_dir() and not d.startswith('.')])
        for m in mod_dirs:
            try:
                m_num = int(m.split('-')[0])
            except ValueError:
                continue

            stage_key = 'stage1' if m_num <= 3 else ('stage2' if m_num <= 6 else ('stage3' if m_num <= 8 else 'stage4'))
            m_path = f'modules/{m}'
            m_files = [p for p in docs if p.startswith(m_path + '/')]
            
            # Module Title
            readme_title = docs.get(f'{m_path}/README.md', {}).get('title', m.replace('-', ' ').title())
            clean_title = re.sub(r'^(Module \d\d\s*[—–-]\s*)', '', readme_title).strip()
            
            # Assign appropriate module icon
            m_icon = 'sparkles' if m_num == 1 else ('cpu' if m_num == 2 else ('code' if m_num == 3 else ('layers' if m_num == 4 else ('database' if m_num == 5 else ('cloud' if m_num == 6 else ('brain' if m_num == 7 else ('bot' if m_num == 8 else 'shieldCheck')))))))

            # Learning order inside a module: the path a learner follows with "Next".
            # Answers, materials and code files go into a separate, clearly labelled list
            # at the end, so nobody meets a solution before the lesson.
            def is_extra(p):
                sub = p[len(m_path) + 1:]
                return (not p.endswith('.md') or '/solutions/' in p or '/solution/' in p
                        or sub == 'build-solution.md' or sub.endswith('SOLUTION.md')
                        or (sub.startswith('break-and-fix/') and sub != 'break-and-fix/README.md'))

            def path_rank(p):
                sub = p[len(m_path) + 1:]
                order = [('README.md', 0), ('setup.md', 1)]
                for name, rank in order:
                    if sub == name:
                        return (rank, sub)
                if sub.startswith('lessons/'): return (2, sub)
                if sub == 'exercises/README.md': return (3, '')
                if sub.startswith('exercises/'): return (4, sub)
                if sub == 'capstones/README.md': return (5, '')
                if sub.startswith('capstones/'): return (6, sub)
                if sub == 'build.md': return (7, sub)
                if sub == 'break-and-fix/README.md': return (8, sub)
                if sub == 'field-track.md': return (9, sub)
                if sub == 'checkpoint.md': return (10, sub)
                if sub == 'resources.md': return (11, sub)
                return (12, sub)

            def short_title(p):
                sub = p[len(m_path) + 1:]
                if sub == 'README.md': return 'Start: module overview'
                if sub == 'exercises/README.md': return 'Exercises: overview'
                if sub == 'checkpoint.md': return 'Checkpoint quiz'
                if sub == 'resources.md': return 'Resources'
                t = docs[p]['title'] if p.endswith('.md') else os.path.basename(p)
                t = re.sub(r'^Module \d\d\s*[—–-]\s*', '', t)
                t = re.sub(r'^Module \d\d\s+', '', t)
                return t

            main_files = sorted((f for f in m_files if not is_extra(f)), key=path_rank)
            extra_files = sorted((f for f in m_files if is_extra(f)), key=lambda f: (not f.endswith('.md'), f))

            group = {
                'type': 'group',
                'title': f'Module {m_num:02d}: {clean_title}',
                'icon': m_icon,
                'items': [{'path': f, 'title': short_title(f), 'icon': get_icon_for_path(f)} for f in main_files]
            }
            if extra_files:
                group['items'].append({'type': 'label', 'title': 'Answers, materials & code'})
                group['items'] += [{'path': f, 'title': short_title(f), 'icon': get_icon_for_path(f), 'extra': True}
                                   for f in extra_files]
            stages[stage_key]['items'].append(group)

    for s in stages.values():
        if s['items']:
            nav.append(s)

    # 3. Running Project: AdmitFlow
    admitflow_files = [p for p in docs if p.startswith('projects/admitflow/')]
    admitflow_group = {
        'id': 'admitflow',
        'title': 'Project AdmitFlow',
        'icon': 'cpu',
        'items': [
            {'path': 'projects/admitflow/README.md', 'title': 'AdmitFlow Overview', 'badge': 'Project', 'icon': 'bookOpen'},
            {'path': 'projects/admitflow/BRIEF.md', 'title': 'Client Brief: Northbridge', 'badge': 'Spec', 'icon': 'fileText'}
        ]
    }

    # Python source files
    py_files = [p for p in admitflow_files if p.endswith('.py') and not 'test' in p and not '__init__' in p]
    if py_files:
        admitflow_group['items'].append({
            'type': 'group',
            'title': 'AdmitFlow Python Core',
            'badge': 'Code',
            'icon': 'fileCode',
            'items': [{'path': p, 'title': os.path.basename(p), 'icon': 'fileCode'} for p in sorted(py_files)]
        })

    # Datasets
    csv_files = [p for p in admitflow_files if p.endswith('.csv')]
    if csv_files:
        admitflow_group['items'].append({
            'type': 'group',
            'title': 'Synthetic Datasets',
            'badge': 'CSV',
            'icon': 'table',
            'items': [{'path': p, 'title': os.path.basename(p), 'icon': 'table'} for p in sorted(csv_files)]
        })

    # Tests
    test_files = [p for p in admitflow_files if 'test' in p]
    if test_files:
        admitflow_group['items'].append({
            'type': 'group',
            'title': 'Test Suite',
            'badge': 'Tests',
            'icon': 'activity',
            'items': [{'path': p, 'title': os.path.basename(p), 'icon': 'activity'} for p in sorted(test_files)]
        })

    # Architecture, ADRs & Runbooks
    doc_files = [p for p in admitflow_files if p.startswith('projects/admitflow/docs/')]
    if doc_files:
        admitflow_group['items'].append({
            'type': 'group',
            'title': 'Architecture & Runbooks',
            'badge': 'Docs',
            'icon': 'fileText',
            'items': [{'path': p, 'title': docs[p]['title'], 'icon': 'fileText'} for p in sorted(doc_files)]
        })

    if 'projects/practice/README.md' in docs:
        admitflow_group['items'].append({'path': 'projects/practice/README.md', 'title': 'Practice Ladder Projects', 'badge': 'Ladder', 'icon': 'layers'})

    nav.append(admitflow_group)

    # 4. Interview Preparation
    interview_files = sorted([p for p in docs if p.startswith('interview-prep/') and p != 'interview-prep/README.md'])
    if 'interview-prep/README.md' in docs:
        nav.append({
            'id': 'interview',
            'title': 'Interview Preparation',
            'icon': 'award',
            'items': [
                {'path': 'interview-prep/README.md', 'title': 'Interview Prep Overview', 'badge': 'Guide', 'icon': 'award'}
            ] + [{'path': p, 'title': docs[p]['title'], 'icon': get_icon_for_path(p)} for p in interview_files]
        })

    # 5. Case Studies
    case_files = sorted([p for p in docs if p.startswith('case-studies/')])
    if case_files:
        nav.append({
            'id': 'cases',
            'title': 'Case Studies',
            'icon': 'fileText',
            'items': [{'path': p, 'title': docs[p]['title'], 'icon': 'fileText'} for p in case_files]
        })

    # 6. Documentation Kit & Templates
    tmpl_files = sorted([p for p in docs if p.startswith('templates/')])
    if tmpl_files:
        nav.append({
            'id': 'templates',
            'title': 'Documentation Kit',
            'icon': 'layers',
            'items': [{'path': p, 'title': docs[p]['title'], 'icon': 'layers'} for p in tmpl_files]
        })

    # 7. Cookbooks
    cookbook_files = sorted([p for p in docs if p.startswith('cookbooks/')])
    if cookbook_files:
        nav.append({
            'id': 'cookbooks',
            'title': 'Cookbooks & Patterns',
            'icon': 'zap',
            'items': [{'path': p, 'title': docs[p]['title'], 'icon': 'zap'} for p in cookbook_files]
        })

    # 8. Resources & Progress
    resource_items = []
    for p in ['field-track/README.md', 'resources/README.md', 'resources/job-descriptions/README.md', 'progress/self-assessment.md']:
        if p in docs:
            resource_items.append({'path': p, 'title': docs[p]['title'], 'icon': get_icon_for_path(p)})
    if resource_items:
        nav.append({
            'id': 'resources',
            'title': 'Resources & Prep',
            'icon': 'compass',
            'items': resource_items
        })

    return nav

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
    html = html.replace('/*{{NAV_JSON}}*/[]', nav_json)
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
