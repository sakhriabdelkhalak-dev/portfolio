from pathlib import Path
from urllib.parse import urlsplit, unquote
from lxml import html
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--site', choices=['avengers', 'marketing'], default='avengers')
site = parser.parse_args().site
root = Path(__file__).resolve().parent.parent / 'demos' / ('avengers' if site == 'avengers' else 'marketing-agency')
errors = []
for page in root.rglob('*.html'):
    text = page.read_text(encoding='utf-8')
    if 'localhost' in text:
        errors.append(f'{page.relative_to(root)}: localhost reference')
    tree = html.fromstring(text)
    refs = tree.xpath('//@src | //@href | //@poster')
    for srcset in tree.xpath('//@srcset'):
        refs.extend(entry.strip().split()[0] for entry in srcset.split(',') if entry.strip())
    for ref in refs:
        url = urlsplit(ref)
        if url.scheme or url.netloc or not url.path:
            continue
        target = (page.parent / unquote(url.path)).resolve()
        if not target.is_file():
            errors.append(f'{page.relative_to(root)}: missing {ref}')
for css in root.rglob('*.css'):
    for match in re.finditer(r'url\(\s*[\'\"]?([^\)\'\"]+)', css.read_text(encoding='utf-8')):
        ref = match.group(1).strip()
        url = urlsplit(ref)
        if url.scheme or url.netloc or not url.path:
            continue
        if not (css.parent / unquote(url.path)).is_file():
            errors.append(f'{css.relative_to(root)}: missing {ref}')
print(f'Checked {len(list(root.rglob("*.html")))} pages and their local links, scripts, images, styles and fonts.')
print('\n'.join(errors) if errors else 'All local references resolve; no localhost links.')
raise SystemExit(bool(errors))
