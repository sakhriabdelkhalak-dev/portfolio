"""Check the published HTML's real resources, anchor targets and contact details."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from lxml import html

root = Path(__file__).resolve().parent.parent
source = (root / 'index.html').read_text(encoding='utf-8')
tree = html.fromstring(source)
ids = tree.xpath('//@id')
assert len(ids) == len(set(ids)), 'Duplicate HTML IDs'
assert ids.count('cv') == 1, 'Exactly one CV section is required'
assert len(tree.xpath('//h1')) == 1, 'One primary page heading is required'
cards = tree.xpath('//article[contains(@class,"project-card")]')
assert len(cards) == 6 and cards[0].get('id') == 'finovate'
assert {card.get('id') for card in cards} == {'finovate', 'cap-pro', 'loop-market', 'dar-el-grill', 'marketing-agency', 'avengers'}
for value in ('VOTRE-EMAIL', 'À préciser', 'provisoires', 'cv-sakhri.pdf', 'My CV', 'Ajoute ton CV'):
    assert value not in source, f'Unfinished content: {value}'
for element in tree.xpath('//*[@src or @href or @action]'):
    for attribute in ('src', 'href', 'action'):
        ref = element.get(attribute)
        if not ref:
            continue
        url = urlsplit(ref)
        if url.scheme or url.netloc:
            continue
        if url.path:
            target = root / unquote(url.path)
            assert target.exists(), f'Missing local resource: {ref}'
            if target.is_dir():
                assert (target / 'index.html').is_file(), f'Missing demo index: {ref}'
        elif url.fragment:
            assert unquote(url.fragment) in ids, f'Missing anchor: {ref}'
for element in tree.xpath('//input[not(@type="hidden")] | //textarea'):
    assert tree.xpath(f'//label[@for="{element.get("id")}"]'), 'Missing form label'
assert tree.xpath('//a[@href="tel:+212601345358"]'), 'Wrong contact telephone'
assert tree.xpath('//form[@action="mailto:sakhriabdelkhalak@gmail.com"]'), 'Wrong contact recipient'
cv_links = tree.xpath('//a[contains(@href,".pdf")]/@href')
assert len(cv_links) == 2 and len(set(cv_links)) == 1
print('Portfolio passed: unique IDs, six projects, local assets and anchors, CV links, labelled form and verified contact details.')
