"""Export the public stest WordPress pages for GitHub Pages; no login cookies."""
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote, quote, parse_qs
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor
from lxml import html
import html as html_std
import posixpath
import re
import argparse

parser = argparse.ArgumentParser(description='Export public WordPress portfolio demos.')
parser.add_argument('--site', choices=['avengers', 'marketing', 'finovate'], default='avengers')
SITE = parser.parse_args().site
SLUG = {'avengers': 'stest', 'marketing': 'test', 'finovate': 'fox'}[SITE]
DEMO = {'avengers': 'avengers', 'marketing': 'marketing-agency', 'finovate': 'finovate'}[SITE]
ROOT = Path(__file__).resolve().parent.parent / 'demos' / DEMO
BASE = f'http://localhost/{SLUG}/'
PAGES = {
    '/stest/': 'index.html',
    '/stest/index.php/all/': 'all/index.html',
    '/stest/index.php/hulk/': 'hulk/index.html',
    '/stest/index.php/iron-man/': 'iron-man/index.html',
    '/stest/index.php/thor/': 'thor/index.html',
}
ALIASES = {}
if SITE == 'marketing':
    PAGES = {
        '/test/': 'index.html',
        '/test/?page_id=9': 'about/index.html',
        '/test/?page_id=11': 'portofolio/index.html',
        '/test/?page_id=12': 'project-details/index.html',
        '/test/?page_id=13': 'blog/index.html',
        '/test/?page_id=10': 'contact/index.html',
        '/test/?p=1': 'blog/hello-world/index.html',
    }
    ALIASES = {f'/test/{slug}/': route for slug, route in [
        ('about', '/test/?page_id=9'), ('portofolio', '/test/?page_id=11'),
        ('project-details', '/test/?page_id=12'), ('blog', '/test/?page_id=13'),
        ('contact', '/test/?page_id=10'), ('hello-world', '/test/?p=1'),
    ]}
elif SITE == 'finovate':
    PAGES = {
        '/fox/?page_id=23': 'index.html',
        '/fox/?page_id=26': 'services/index.html',
        '/fox/?page_id=37': 'about/index.html',
        '/fox/?page_id=39': 'insights/index.html',
        '/fox/?page_id=41': 'testimonial/index.html',
        '/fox/?page_id=43': 'contact/index.html',
        '/fox/?page_id=49': 'home-1/index.html',
        '/fox/?page_id=51': 'home-2/index.html',
        '/fox/?page_id=15': 'the-new-page/index.html',
    }
    ALIASES = {'/fox/': '/fox/?page_id=23'}
    ALIASES.update({f'/fox/{slug}/': route for slug, route in [
        ('home', '/fox/?page_id=23'), ('services', '/fox/?page_id=26'),
        ('about', '/fox/?page_id=37'), ('insights', '/fox/?page_id=39'),
        ('testimonial', '/fox/?page_id=41'), ('contact', '/fox/?page_id=43'),
        ('1-2', '/fox/?page_id=49'), ('2-2', '/fox/?page_id=51'),
        ('the-new-page', '/fox/?page_id=15'),
    ]})
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
    prefix = f'/{SLUG}/'
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
    if path == f'/{SLUG}/index.php/':
        path = f'/{SLUG}/'
    query = parse_qs(p.query)
    for key in ('page_id', 'p'):
        if key in query:
            path += '?' + key + '=' + query[key][0]
            break
    if SITE == 'marketing' and any(key in query for key in ('author', 'cat')):
        path = '/test/?page_id=13'
    path = ALIASES.get(path, path)
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
            old = f'{scheme}://localhost/{SLUG}/{prefix}'
            new = relative('assets/' + prefix.rstrip('/'), output) + '/'
            text = text.replace(old, new).replace(old.replace('/', '\\/'), new.replace('/', '\\/'))
        old = f'{scheme}://localhost/{SLUG}/'
        new = relative('index.html', output).removesuffix('index.html') or './'
        text = text.replace(old, new).replace(old.replace('/', '\\/'), new.replace('/', '\\/'))
    return text

def render_page(item):
    source, output = item
    url = 'http://localhost' + source
    data, _ = fetch(url)
    if b'wp-emoji-release.min.js' in data:
        emoji_url = BASE + 'wp-includes/js/wp-emoji-release.min.js'
        pending[asset_path(emoji_url)] = emoji_url
    tree = html.fromstring(data)
    for element in list(tree.xpath('//link[@rel="https://api.w.org/"] | //link[@rel="EditURI"] | //link[@rel="pingback"] | //link[@rel="alternate"] | //*[@id="wpadminbar"] | //script[@id="wp-api-request-js"] | //script[@id="wp-api-request-js-extra"] | //script[@type="speculationrules"]')):
        element.drop_tree()
    if SITE != 'avengers':
        for script in list(tree.xpath('//script[contains(@src,"contact-form-7") or contains(@id,"contact-form-7") or contains(@src,"/swv/")]')):
            script.drop_tree()
        for form in tree.xpath('//form'):
            form.set('action', '#')
            form.set('onsubmit', 'return false')
            for field in list(form.xpath('.//input[@type="hidden"]')):
                field.drop_tree()
            for button in form.xpath('.//input[@type="submit"] | .//button[@type="submit"]'):
                button.set('disabled', 'disabled')
                if button.tag == 'input':
                    button.set('value', 'Demo — sending disabled')
                else:
                    button.text = 'Demo — sending disabled'
            note = html.fromstring('<p role="note" style="font-size:14px;padding:12px;border-left:3px solid #1976b9;background:#f3f7fa;color:#233">Demonstration form — no messages or comments are sent from this portfolio demo.</p>')
            form.insert(0, note)
    if SITE == 'finovate':
        body = tree.find('body')
        # Fixed overlays must not inherit Elementor container transforms.
        for overlay in tree.xpath('//*[@id="contactPanel" or @id="openPanel"]'):
            overlay.getparent().remove(overlay)
            body.append(overlay)
        for script in list(tree.xpath('//script')):
            if 'openPanel' in (script.text or '') and 'addEventListener' in (script.text or ''):
                script.getparent().remove(script)
                body.append(script)
        for image in tree.xpath('//img[contains(@src,"via.placeholder.com")]'):
            image.set('src', BASE + 'wp-content/uploads/2025/10/pexels-fauxels-3182781-1024x683.jpg')
        for anchor in tree.xpath('//a'):
            label = ' '.join(anchor.text_content().split()).lower()
            if label in ("let's get started", 'schedule a call', 'get in touch today →'):
                anchor.set('href', BASE + '?page_id=43')
                anchor.set('class', anchor.get('class', '') + ' demo-contact-link')
            elif label in ('learn more', 'our philosophy'):
                anchor.set('href', BASE + '?page_id=37')
            elif 'finovate.vamtam.com/services/' in anchor.get('href', ''):
                anchor.set('href', BASE + '?page_id=26')
        fixes = html.Element('style')
        fixes.text = '.entry-header{display:none}.elementor-23 .elementor-element.elementor-element-a086beb{color:#1a3b34!important;opacity:1!important;visibility:visible!important;transform:none!important}.elementor-23 .elementor-element-a086beb h1{color:#1a3b34!important}.demo-contact-link,.demo-contact-link *{color:#1a3b34!important}.contact-panel{max-width:100vw;box-sizing:border-box;height:100vh!important;visibility:hidden}.contact-panel.active{visibility:visible}.contact-panel a.demo-contact-link,.contact-panel a.demo-contact-link *{color:#fff!important}body:has(.contact-panel.active) #openPanel{display:none}@media(max-width:767px){.hfe-dropdown{background:#fff!important;z-index:1000!important}.elementor-23 .elementor-element-04313c3{z-index:1001}}'
        tree.find('head').append(fixes)
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
    description = {'avengers': 'Avengers Assemble', 'marketing': 'Marketing Agency', 'finovate': 'Finovate'}[SITE]
    tree.find('head').append(html.fromstring(f'<meta name="description" content="{description} — projet personnel WordPress de Sakhri Abdelkhalak.">'))
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
bundle_directory = Path(f'C:/laragon/www/{SLUG}/wp-content/plugins/elementor/assets/js')
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
