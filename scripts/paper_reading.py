#!/usr/bin/env python3
"""Portable, offline rendering and structural validation for paper-reading.

Python 3.10+, standard library only. Optional pypdf/PyMuPDF for PDF extraction.
This script never calls an AI or verifies the truth of academic claims.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

MODULES = [
    ('01_ARS科研分析', '科研分析', '串联问题、设计、证据与研究启发'),
    ('02_原文对照导读', '原文对照导读', '保留原文，逐段理解推理和关键公式'),
    ('03_批判性阅读', '批判性阅读', '检验假设、替代解释和结论边界'),
    ('04_文献综述视角', '文献综述视角', '定位已有工作与后续阅读方向'),
    ('05_证据链精读', '证据链精读', '逐项追踪主张与支持它的证据'),
    ('06_快速泛读', '快速泛读', '先掌握问题、发现与适用范围'),
    ('07_方法精读', '方法精读', '理解研究设计、测量和推断逻辑'),
    ('08_论文叙事', '论文叙事', '用通俗语言讲清论文的故事与转折'),
]
PLACEHOLDER = re.compile(r'\b(?:TODO|TBD|FIXME)\b|待填写|待补充|在此填写|REPLACE_ME', re.I)
ALLOWED_ASSETS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
ALLOWED_FILES = ALLOWED_ASSETS | {'.pdf', '.html', '.htm', '.txt', '.md', '.json', '.csv'}
E = lambda s: html.escape(str(s), quote=True)

class InputError(ValueError):
    pass

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as e:
        raise InputError(f'{path.name}: {e}') from e

def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def pdf_info(path, extract=False):
    """Return pages and parser provenance; no approximate regex page counts."""
    try:
        import pypdf
        pdf = pypdf.PdfReader(str(path))
        if pdf.is_encrypted and not pdf.decrypt(''):
            raise InputError('PDF已加密，请提供可读取的PDF。')
        pages = [{'page': i + 1, 'text': page.extract_text() or ''} for i, page in enumerate(pdf.pages)] if extract else []
        return len(pdf.pages), 'pypdf', pages
    except ImportError:
        pass
    except Exception as e:
        raise InputError(f'无法读取PDF：{e}') from e
    try:
        import fitz
        with fitz.open(str(path)) as pdf:
            if pdf.needs_pass:
                raise InputError('PDF已加密，请提供可读取的PDF。')
            pages = [{'page': i + 1, 'text': page.get_text()} for i, page in enumerate(pdf)] if extract else []
            return len(pdf), 'PyMuPDF', pages
    except ImportError:
        raise InputError('未找到可选PDF读取库。初始化可显式提供 --pages；文本提取需已有 pypdf 或 PyMuPDF，不会自动安装。')
    except Exception as e:
        raise InputError(f'无法读取PDF：{e}') from e

def safe_path(base, value, extensions=None):
    if not isinstance(value, str) or not value.strip():
        raise InputError('本地文件路径必须为非空字符串')
    # Backslashes and URI-looking strings are rejected consistently on all OSes.
    if '\\' in value or ':' in value or '?' in value or '#' in value:
        raise InputError(f'不是可移植的本地相对路径：{value}')
    rel = Path(value)
    if rel.is_absolute() or '..' in rel.parts:
        raise InputError(f'路径不能离开模块目录：{value}')
    path = (base / rel).resolve()
    if not path.is_relative_to(base.resolve()):
        raise InputError(f'路径或符号链接离开模块目录：{value}')
    if extensions and path.suffix.lower() not in extensions:
        raise InputError(f'不支持的文件类型：{value}')
    if not path.is_file():
        raise InputError(f'本地文件不存在：{value}')
    return path

def text_field(obj, key, where, required=True):
    value = obj.get(key)
    if value is None and not required:
        return
    if not isinstance(value, str) or (required and not value.strip()):
        raise InputError(f'{where}.{key} 必须为非空文本')
    if PLACEHOLDER.search(value or ''):
        raise InputError(f'{where}.{key} 含占位内容')

def check_pages(block, page_count, where):
    pages = block.get('pages', [])
    if not isinstance(pages, list) or any(type(p) is not int or p < 1 or p > page_count for p in pages):
        raise InputError(f'{where}.pages 必须为1至{page_count}的PDF页码列表')
    return len(pages)

def check_blocks(blocks, module_dir, page_count, where='blocks', depth=0):
    if depth > 12:
        raise InputError(f'{where} 嵌套过深')
    if not isinstance(blocks, list) or not blocks:
        raise InputError(f'{where} 不能为空')
    refs = 0
    for i, block in enumerate(blocks):
        here = f'{where}[{i}]'
        if not isinstance(block, dict):
            raise InputError(f'{here} 必须是对象')
        kind = block.get('type')
        refs += check_pages(block, page_count, here)
        if kind in ('paragraph', 'quote', 'formula', 'heading'):
            text_field(block, 'text', here)
            if kind == 'formula':
                text_field(block, 'explanation', here, False)
            if kind == 'heading' and block.get('level', 3) not in (3, 4):
                raise InputError(f'{here}.level 仅支持3或4')
        elif kind == 'list':
            items = block.get('items')
            if not isinstance(items, list) or not items:
                raise InputError(f'{here}.items 不能为空')
            for j, item in enumerate(items):
                text_field({'item': item}, 'item', f'{here}[{j}]')
            if 'ordered' in block and type(block['ordered']) is not bool:
                raise InputError(f'{here}.ordered 必须是布尔值')
        elif kind == 'table':
            headers, rows = block.get('headers'), block.get('rows')
            if not isinstance(headers, list) or not headers or not isinstance(rows, list) or not rows:
                raise InputError(f'{here} 表格需要非空headers和rows')
            for j, cell in enumerate(headers):
                text_field({'cell': cell}, 'cell', f'{here}.headers[{j}]')
            for j, row in enumerate(rows):
                if not isinstance(row, list) or len(row) != len(headers):
                    raise InputError(f'{here}.rows[{j}] 列数与表头不同')
                for k, cell in enumerate(row):
                    if not isinstance(cell, (str, int, float)) or isinstance(cell, bool):
                        raise InputError(f'{here}.rows[{j}][{k}] 必须是文本或数字')
                    text_field({'cell': str(cell)}, 'cell', f'{here}.rows[{j}][{k}]', False)
        elif kind == 'image':
            text_field(block, 'alt', here)
            text_field(block, 'caption', here, False)
            safe_path(module_dir, block.get('src'), ALLOWED_ASSETS)
        elif kind == 'link':
            text_field(block, 'label', here)
            safe_path(module_dir, block.get('path'), ALLOWED_FILES)
        elif kind == 'details':
            text_field(block, 'summary', here)
            refs += check_blocks(block.get('blocks'), module_dir, page_count, here + '.blocks', depth + 1)
        elif kind == 'paragraph_guide':
            for key in ('id', 'original', 'note'):
                text_field(block, key, here)
            if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', block['id']):
                raise InputError(f'{here}.id 需要字母开头的唯一英文/数字编号')
            if block.get('mode', 'skim') not in ('close', 'skim', 'skip'):
                raise InputError(f'{here}.mode 仅支持close/skim/skip')
            text_field(block, 'prompt', here, False)
            if not block.get('pages'):
                raise InputError(f'{here} 原文导读必须标注PDF页码')
            if block.get('blocks'):
                refs += check_blocks(block['blocks'], module_dir, page_count, here + '.blocks', depth + 1)
        else:
            raise InputError(f'{here}: 未知block类型 {kind!r}')
    return refs

def validate_content(content, module_dir, page_count):
    if not isinstance(content, dict) or content.get('schema_version') != 1:
        raise InputError('content.json 需要 schema_version: 1')
    if content.get('status') != 'complete':
        raise InputError('status 不是complete，内容仍待完成')
    text_field(content, 'title', 'content')
    text_field(content, 'summary', 'content')
    sections = content.get('sections')
    if not isinstance(sections, list) or not sections:
        raise InputError('sections 不能为空')
    refs = 0
    ids = []
    def collect_ids(blocks):
        for b in blocks:
            if b.get('type') == 'paragraph_guide':
                ids.append(b['id'])
            if b.get('blocks'):
                collect_ids(b['blocks'])
    for i, section in enumerate(sections):
        if not isinstance(section, dict):
            raise InputError(f'sections[{i}] 必须是对象')
        text_field(section, 'heading', f'sections[{i}]')
        refs += check_blocks(section.get('blocks'), module_dir, page_count, f'sections[{i}].blocks')
        collect_ids(section['blocks'])
    if len(ids) != len(set(ids)):
        raise InputError('paragraph_guide.id 重复')
    if not refs:
        raise InputError('整份模块缺少PDF页码锚点；请标注支持论文事实的页码')
    return {'sections': len(sections), 'page_references': refs, 'guided_paragraphs': len(ids)}

def manifest_at(out):
    m = read_json(out / '00_原文与索引' / 'manifest.json')
    if m.get('schema_version') != 1:
        raise InputError('不支持的manifest版本')
    if type(m.get('source', {}).get('pages')) is not int or m['source']['pages'] < 1:
        raise InputError('manifest缺少有效源PDF页数')
    if m.get('source', {}).get('file') != '00_原文与索引/source.pdf':
        raise InputError('manifest源文件路径无效')
    source = safe_path(out, m['source']['file'], {'.pdf'})
    if sha256(source) != m['source']['sha256']:
        raise InputError('源PDF哈希发生变化；请确认资料来源后重新初始化')
    text_field(m, 'title', 'manifest')
    return m

def init(args):
    paper, out = Path(args.paper).expanduser().resolve(), Path(args.out).expanduser().resolve()
    if not paper.is_file() or paper.suffix.lower() != '.pdf':
        raise InputError('--paper 需要现有PDF文件')
    with paper.open('rb') as stream:
        if not stream.read(1024).lstrip().startswith(b'%PDF-'):
            raise InputError('--paper 内容不是可识别的PDF')
    if out.exists() and not out.is_dir():
        raise InputError('输出路径已经存在且不是目录')
    if out.exists() and any(out.iterdir()):
        raise InputError('输出目录非空；请选择新目录，避免覆盖已有笔记')
    if args.pages is not None:
        if args.pages < 1:
            raise InputError('--pages 必须大于0')
        pages, method = args.pages, 'user-specified; not automatically verified'
        try:
            detected, parser, _ = pdf_info(paper)
            if detected != pages:
                raise InputError(f'--pages={pages} 与解析页数{detected}不同')
            method = parser
        except InputError as e:
            if '未找到可选PDF读取库' not in str(e):
                raise
    else:
        pages, method, _ = pdf_info(paper)
    source_dir = out / '00_原文与索引'
    source_dir.mkdir(parents=True)
    shutil.copy2(paper, source_dir / 'source.pdf')
    m = {'schema_version': 1, 'title': args.title, 'created_at_utc': utc_now(),
         'source': {'file': '00_原文与索引/source.pdf', 'original_filename': paper.name,
                    'sha256': sha256(paper), 'pages': pages, 'page_count_method': method},
         'modules': [name for name, _, _ in MODULES]}
    write_json(source_dir / 'manifest.json', m)
    for name, title, _ in MODULES:
        folder = out / name
        folder.mkdir()
        write_json(folder / 'content.json', {'schema_version': 1, 'status': 'draft', 'title': title, 'summary': '', 'sections': []})
    print(f'已初始化8个模块：{out}\nPDF {pages}页；请由AI阅读后填写各content.json，再render和validate。')

def extract(args):
    pdf = Path(args.pdf).expanduser().resolve()
    count, parser, pages = pdf_info(pdf, True)
    result = {'source_filename': pdf.name, 'source_sha256': sha256(pdf), 'pages': pages,
              'page_count': count, 'parser': parser,
              'warning': '提取文字不能代替图表和公式的原页检查；扫描件可能需要OCR。'}
    write_json(Path(args.out).expanduser(), result)
    empty = sum(not p['text'].strip() for p in pages)
    print(f'已提取{count}页；空文本页{empty}。请对照PDF检查图表、公式与阅读顺序。')

def page_links(block):
    if not block.get('pages'):
        return ''
    links = [f'<a href="../00_原文与索引/source.pdf#page={p}" target="_blank" rel="noopener">p. {p}</a>' for p in dict.fromkeys(block['pages'])]
    return '<span class="refs">原文 ' + ' · '.join(links) + '</span>'

def blocks_html(blocks):
    result = []
    for b in blocks:
        t, ref = b['type'], page_links(b)
        if t == 'paragraph':
            result.append(f'<p>{E(b["text"])}</p>{ref}')
        elif t == 'heading':
            level = b.get('level', 3)
            result.append(f'<h{level}>{E(b["text"])}</h{level}>{ref}')
        elif t == 'quote':
            result.append(f'<blockquote>{E(b["text"])}</blockquote>{ref}')
        elif t == 'formula':
            result.append(f'<div class="formula" role="math">{E(b["text"])}</div>')
            if b.get('explanation'):
                result.append(f'<p class="explanation">{E(b["explanation"])}</p>')
            result.append(ref)
        elif t == 'list':
            tag = 'ol' if b.get('ordered') else 'ul'
            result.append(f'<{tag}>' + ''.join('<li>' + E(x) + '</li>' for x in b['items']) + f'</{tag}>' + ref)
        elif t == 'table':
            result.append('<div class="table-wrap"><table><thead><tr>' + ''.join('<th>' + E(x) + '</th>' for x in b['headers']) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + E(c) + '</td>' for c in row) + '</tr>' for row in b['rows']) + '</tbody></table></div>' + ref)
        elif t == 'image':
            result.append(f'<figure><img src="{E(quote(b["src"], safe="/"))}" alt="{E(b["alt"])}" loading="lazy"><figcaption>{E(b.get("caption", ""))} {ref}</figcaption></figure>')
        elif t == 'link':
            result.append(f'<p><a href="{E(quote(b["path"], safe="/"))}">{E(b["label"])}</a></p>{ref}')
        elif t == 'details':
            result.append(f'<details><summary>{E(b["summary"])}</summary><div class="details-body">{blocks_html(b["blocks"])}</div></details>{ref}')
        elif t == 'paragraph_guide':
            mode = {'close': '精读', 'skim': '泛读', 'skip': '略读'}[b.get('mode', 'skim')]
            result.append(f'<article class="paragraph-guide" id="{E(b["id"])}"><div class="para-label">{E(b["id"])} · {mode} {ref}</div>')
            if b.get('prompt'):
                result.append(f'<p class="prompt"><strong>读前提示</strong> {E(b["prompt"])}</p>')
            result.append(f'<details open><summary>原文</summary><blockquote lang="en">{E(b["original"])}</blockquote></details><div class="note"><strong>中文理解</strong><p>{E(b["note"])}</p></div>')
            result.append(blocks_html(b.get('blocks', [])) + '</article>')
    return '\n'.join(result)

def css_text():
    return (Path(__file__).resolve().parent.parent / 'assets' / 'style.css').read_text(encoding='utf-8')

def page(title, body, css, language='zh-CN'):
    return f'<!doctype html>\n<html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>{E(title)}</title><style>{css}</style></head><body>{body}</body></html>'

def report_html(content, module_name, css):
    toc = ''.join(f'<a href="#s{i}">{E(section["heading"])}</a>' for i, section in enumerate(content['sections'], 1))
    body = '<div class="reader"><nav class="top-nav"><a href="../开始阅读.html">← 学习导航</a><a href="content.json">分析数据</a><a href="../00_原文与索引/source.pdf">论文原文</a></nav>'
    body += f'<header><p class="eyebrow">PAPER READING · {E(module_name[:2])}</p><h1>{E(content["title"])}</h1><p class="lead">{E(content["summary"])}</p></header>'
    body += '<div class="report-layout"><aside class="toc"><span>本页内容</span>' + toc + '</aside><main>'
    for i, section in enumerate(content['sections'], 1):
        body += f'<section id="s{i}"><h2>{E(section["heading"])}</h2>{blocks_html(section["blocks"])}</section>'
    body += '</main></div><footer>页码链接指向本地PDF。学习解释与论文证据请相互核对。</footer></div>'
    return page(content['title'], body, css)

def render(args):
    out = Path(args.out).expanduser().resolve()
    manifest = manifest_at(out)
    css, cards, complete, errors = css_text(), [], 0, []
    for name, title, description in MODULES:
        folder = out / name
        try:
            content = read_json(folder / 'content.json')
            validate_content(content, folder, manifest['source']['pages'])
            (folder / '学习报告.html').write_text(report_html(content, name, css), encoding='utf-8')
            complete += 1
            cards.append(f'<a class="card" href="{quote(name)}/学习报告.html"><span class="number">{name[:2]}</span><div><h2>{E(title)}</h2><p>{E(content["summary"])}</p><span class="status ready">开始阅读 →</span></div></a>')
        except (InputError, OSError) as e:
            errors.append({'module': name, 'error': str(e)})
            # Replace stale outputs with an explicit draft page; never present stale work as current.
            folder.mkdir(exist_ok=True)
            draft = '<div class="reader"><nav class="top-nav"><a href="../开始阅读.html">← 学习导航</a></nav><h1>' + E(title) + '</h1><p class="lead">这个模块尚未完成。</p><p>' + E(str(e)) + '</p></div>'
            (folder / '学习报告.html').write_text(page(title + ' · 待完成', draft, css), encoding='utf-8')
            cards.append(f'<div class="card pending"><span class="number">{name[:2]}</span><div><h2>{E(title)}</h2><p>{E(description)}</p><span class="status">待完成</span></div></div>')
    body = f'<div class="home"><header><p class="eyebrow">PAPER READING · 八种阅读视角</p><h1>{E(manifest["title"])}</h1><p class="lead">从论文故事到原文、方法与证据。按自己的问题选择入口，也可以依次深入。</p><div class="home-meta"><a href="00_原文与索引/source.pdf">打开原论文 · {manifest["source"]["pages"]} 页</a><span>{complete} / 8 个模块可阅读</span></div></header><div class="route"><strong>建议顺序</strong> 论文叙事 → 快速泛读 → 原文对照导读 → 方法精读 → 批判性阅读 → 证据链精读 → 文献综述视角 → 科研分析</div><main class="cards">' + ''.join(cards) + '</main><footer>这些是同一论文的不同学习视角，并不等于独立专家共识。结构检查只能验证文件与引用格式，不能验证学术判断。<br>全部页面离线可读；图表与原文保存在同一目录。</footer></div>'
    (out / '开始阅读.html').write_text(page(manifest['title'] + ' · 学习导航', body, css), encoding='utf-8')
    write_json(out / '00_原文与索引' / 'render_report.json', {'created_at_utc': utc_now(), 'complete_modules': complete, 'module_errors': errors})
    print(f'已渲染导航：{out / "开始阅读.html"}\n可阅读模块 {complete}/8；未完成模块 {len(errors)}。')
    for error in errors:
        print(f'  {error["module"]}: {error["error"]}')

def validate(args):
    out = Path(args.out).expanduser().resolve()
    manifest = manifest_at(out)
    requested = getattr(args, 'modules', None)
    ids = {name[:2]: name for name, _, _ in MODULES}
    if requested is None:
        selected = list(ids.values())
        validation_scope = 'full_package'
    else:
        invalid = [x for x in requested if x not in ids]
        if invalid:
            raise InputError('模块编号无效：' + ', '.join(invalid) + '；可用01至08')
        selected = list(dict.fromkeys(ids[x] for x in requested))
        validation_scope = 'selected_modules'
    errors, stats = [], {}
    for name in selected:
        try:
            stats[name] = validate_content(read_json(out / name / 'content.json'), out / name, manifest['source']['pages'])
        except InputError as e:
            errors.append({'module': name, 'error': str(e)})
    report = {'created_at_utc': utc_now(), 'passed': not errors,
              'validation_scope': validation_scope, 'selected_modules': selected,
              'package_complete': validation_scope == 'full_package' and not errors,
              'modules': stats, 'errors': errors,
              'source_sha256_verified': True, 'scope': '仅结构、页码范围、本地文件、哈希和已知占位符检查；不证明事实、推理或真实阅读质量。'}
    report_name = 'validation_report.json' if validation_scope == 'full_package' else 'validation_selected_report.json'
    write_json(out / '00_原文与索引' / report_name, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init', help='初始化8个模块和可追溯的本地论文副本')
    p.add_argument('--paper', required=True); p.add_argument('--out', required=True)
    p.add_argument('--title', required=True); p.add_argument('--pages', type=int)
    p.set_defaults(func=init)
    p = sub.add_parser('extract', help='用已有的可选库提取逐页文字，不自动安装依赖')
    p.add_argument('--pdf', required=True); p.add_argument('--out', required=True); p.set_defaults(func=extract)
    for command, function in [('render', render), ('validate', validate)]:
        p = sub.add_parser(command); p.add_argument('--out', required=True); p.set_defaults(func=function)
        if command == 'validate':
            p.add_argument('--modules', nargs='+', metavar='ID', help='仅检查指定模块，如08或02 08；不代表全套完成')
    args = parser.parse_args(argv)
    try:
        return args.func(args) or 0
    except (InputError, OSError, KeyError, TypeError) as e:
        print(f'错误：{e}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
