"""Export the public stest WordPress pages for GitHub Pages; no login cookies."""
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote, quote
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor
from lxml import html
import html as html_std
import posixpath
import re

ROOT = Path(__file__).resolve().parent.parent / 'demos' / 'avengers'
BASE = 'http://localhost/stest/'
PAGES = {
    '/stest/': 'index.html',
    '/stest/index.php/all/': 'all/index.html',
    '/stest/index.php/hulk/': 'hulk/index.html',
    '/stest/index.php/iron-man/': 'iron-man/index.html',
    '/stest/index.php/thor/': 'thor/index.html',
}
pending = {}
downloaded = set()
failures = []

def fetch(url):
    p = urlsplit(url)
    # WordPress uses https asset URLs locally; request the same files over HTTP.
    url = 'http://localhost' + quote(unquote(p.path), safe='/:@') + ('?' + p.query if p.query else '')
    with urlopen(Request(url, headers={'User-Agent': 'Portfolio-static-export/1.0'}), timeout=90) as response:
        return response.read(), response.headers.get_content_type()

def local(url):
    return urlsplit(url).hostname in ('localhost', '127.0.0.1')

def asset_path(url):
    path = unquote(urlsplit(url).path)
    prefix = '/stest/'
    if not path.startswith(prefix):
        return None
    path = path[len(prefix):]
    if not path.startswith(('wp-content/', 'wp-includes/')) or '..' in Path(path).parts:
        return None
    return 'assets/' + path

def relative(target, output):
    return posixpath.relpath(target, posixpath.dirname(output) or '.')

def rewrite(raw, base, output):
    if not raw or raw.startswith(('#', 'data:', 'mailto:', 'tel:', 'javascript:')):
        return raw
    absolute = urljoin(base, html_std.unescape(raw))
    if not local(absolute):
        return raw
    p = urlsplit(absolute)
    target = asset_path(absolute)
    if target:
        pending.setdefault(target, absolute)
        return relative(target, output) + ('#' + p.fragment if p.fragment else '')
    path = p.path.rstrip('/') + '/'
    if path == '/stest/index.php/':
        path = '/stest/'
    if path in PAGES:
        return relative(PAGES[path], output) + ('#' + p.fragment if p.fragment else '')
    # Unused WordPress service endpoints are never published as localhost links.
    return '#'

def rewrite_embedded(text, base, output, css=False):
    def css_url(match):
        url = match.group(2).strip()
        return 'url("' + rewrite(url, base, output) + '")'
    if css:
        text = re.sub(r'url\(\s*([\'\"]?)(.*?)\1\s*\)', css_url, text, flags=re.I)
    # Elementor's runtime config uses JSON escaped URLs for dynamic JS chunks.
    for scheme in ('http', 'https'):
        for prefix in ('wp-content/', 'wp-includes/'):
            old = f'{scheme}://localhost/stest/{prefix}'
            new = relative('assets/' + prefix.rstrip('/'), output) + '/'
            text = text.replace(old, new).replace(old.replace('/', '\\/'), new.replace('/', '\\/'))
        old = f'{scheme}://localhost/stest/'
        new = relative('index.html', output).removesuffix('index.html') or './'
        text = text.replace(old, new).replace(old.replace('/', '\\/'), new.replace('/', '\\/'))
    return text

def render_page(item):
    source, output = item
    url = 'http://localhost' + source
    data, _ = fetch(url)
    tree = html.fromstring(data)
    for element in list(tree.xpath('//link[@rel="https://api.w.org/"] | //link[@rel="EditURI"] | //link[@rel="pingback"] | //link[@rel="alternate"] | //*[@id="wpadminbar"] | //script[@id="wp-api-request-js"] | //script[@id="wp-api-request-js-extra"] | //script[@type="speculationrules"]')):
        element.drop_tree()
    for element in tree.iter():
        for attr in ('href', 'src', 'poster', 'data-src'):
            if attr in element.attrib:
                element.set(attr, rewrite(element.get(attr), url, output))
        if 'srcset' in element.attrib:
            entries = []
            for entry in element.get('srcset').split(','):
                parts = entry.strip().split()
                if parts:
                    entries.append(' '.join([rewrite(parts[0], url, output)] + parts[1:]))
            element.set('srcset', ', '.join(entries))
        if 'style' in element.attrib:
            element.set('style', rewrite_embedded(element.get('style'), url, output, css=True))
        if element.tag in ('script', 'style') and element.text:
            element.text = rewrite_embedded(element.text, url, output, css=element.tag == 'style')
    for element in tree.xpath('//body'):
        classes = element.get('class', '').split()
        element.set('class', ' '.join(x for x in classes if x not in ('admin-bar', 'logged-in')))
    tree.find('head').append(html.fromstring('<meta name="description" content="Avengers Assemble — projet personnel WordPress et Elementor de Sakhri Abdelkhalak.">'))
    destination = ROOT / output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(b'<!DOCTYPE html>\n' + html.tostring(tree, encoding='utf-8', method='html'))
    print('Page ready:', output, flush=True)

def download_asset(item):
    output, url = item
    try:
        data, content_type = fetch(url)
        if content_type == 'text/html':
            raise ValueError('HTML returned for asset')
        return output, url, data, None
    except Exception as error:
        return output, url, None, type(error).__name__

ROOT.mkdir(parents=True, exist_ok=True)
# Page parsing mutates a small shared asset queue, so process pages sequentially.
for item in PAGES.items():
    render_page(item)

# Elementor loads widget handlers on demand. Include the installed runtime's
# bundles so tabs, galleries, video and text widgets also work after export.
bundle_directory = Path('C:/laragon/www/stest/wp-content/plugins/elementor/assets/js')
for bundle in bundle_directory.glob('*.bundle.min.js'):
    name = bundle.name
    url = BASE + 'wp-content/plugins/elementor/assets/js/' + name
    pending[asset_path(url)] = url

while batch := [(path, url) for path, url in pending.items() if path not in downloaded]:
    downloaded.update(path for path, _ in batch)
    with ThreadPoolExecutor(max_workers=6) as executor:
        for output, url, data, error in executor.map(download_asset, batch):
            if error:
                failures.append((output, error))
                continue
            destination = ROOT / output
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.suffix.lower() in ('.css', '.js'):
                text = data.decode('utf-8-sig')
                text = rewrite_embedded(text, url, output, css=destination.suffix.lower() == '.css')
                data = text.encode('utf-8')
            destination.write_bytes(data)
    print(f'Assets processed: {len(downloaded)}; failures: {len(failures)}', flush=True)

print('Export complete. Failures:', failures, flush=True)
if failures:
    raise SystemExit(1)
