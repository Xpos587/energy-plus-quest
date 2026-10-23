#!/usr/bin/env python3
"""Validate the canonical Markdown, roles, local image links and scene 1 copy.

Optionally compare all converted paragraphs and embedded images with the original
DOCX supplied outside the repository. No historical scenario is required.
"""
import argparse
from collections import Counter, defaultdict
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / 'docs/scenario.md'
PATTERN = re.compile(r'<!-- scenario-block id="([^"]+)" role="([^"]+)" origin="([^"]+)" -->\n([\s\S]*?)<!-- /scenario-block -->')
ROLES = {'text', 'visual', 'mechanic', 'scores', 'structure', 'mixed'}
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
MC = '{http://schemas.openxmlformats.org/markup-compatibility/2006}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
V = '{urn:schemas-microsoft-com:vml}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'


def visible_text(node):
    if node.tag in (W + 'del', W + 'moveFrom'):
        return ''
    if node.tag == W + 't':
        return node.text or ''
    if node.tag == W + 'tab':
        return '\t'
    if node.tag in (W + 'br', W + 'cr'):
        return '\n'
    return ''.join(visible_text(child) for child in node)


def normalize(text):
    return ' '.join(text.split())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, help='Optional original final 0810 DOCX for full conversion verification')
    parser.add_argument('--carrier-only', action='store_true', help='Compatibility flag; scene 1 is always checked')
    args = parser.parse_args()
    markdown = CANONICAL.read_text()
    blocks, groups = {}, defaultdict(list)
    for ident, role, origin, body in PATTERN.findall(markdown):
        assert ident not in blocks, f'Duplicate canonical block {ident}'
        assert role in ROLES, f'Unknown role {role}'
        text = '\n'.join(re.sub(r'\\([\\`*_<>{}\[\]])', r'\1', line[2:]) for line in body.splitlines() if line.startswith('> '))
        blocks[ident] = (role, text, origin)
        # Split only the source's "Результат:" metadata from its player text.
        original_id = re.sub(r'-(?:label|text)$', '', ident)
        groups[(origin, original_id)].append(text)
    assert len(blocks) == markdown.count('<!-- scenario-block '), 'Malformed scenario block'
    for ident in ['2A80D000', '6656C720', '512D2AEE', '4264BB8C', '67C929B0', '7E9315CC', '46FE90C1']:
        assert blocks[ident][0] == 'text', f'Carrier player copy {ident} came from a non-text block'
    assert blocks['3B38D1EB'][0] == 'mixed', 'Button source must keep its explicit instruction boundary'
    for ident, (role, text, origin) in blocks.items():
        if origin.startswith('t2/r2/c2'):
            assert role == 'visual', f'Carrier visualization {ident} must not be player copy'
        if text.startswith(('Баллы:', 'Энергия:', 'Энергия +', 'Энергия -', 'Эмпатия:', 'Эффективность:')):
            assert role == 'scores', f'Score paragraph {ident} misclassified'
        if text.startswith(('Иллюстрация:', 'Визуализация:')):
            assert role == 'visual', f'Visual instruction {ident} misclassified'
    image_links = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', markdown)
    for link in image_links:
        assert (CANONICAL.parent / link).is_file(), f'Missing scenario image {link}'
    referenced = {Path(link).name for link in image_links}
    assert referenced == {p.name for p in (ROOT / 'docs/scenario-assets').iterdir()}, 'Unreferenced scenario assets'
    if args.source:
        with ZipFile(args.source) as archive:
            document = ET.fromstring(archive.read('word/document.xml'))
            for parent in list(document.iter()):
                for child in list(parent):
                    if child.tag == MC + 'AlternateContent':
                        choice, fallback = child.find(MC + 'Choice'), child.find(MC + 'Fallback')
                        selected = choice if choice is not None and list(choice.iter(A + 'blip')) else fallback if fallback is not None else choice
                        child[:] = list(selected) if selected is not None else []
            original = Counter(normalize(visible_text(p)) for p in document.iter(W + 'p') if visible_text(p).strip())
            converted = Counter(normalize(' '.join(parts)) for parts in groups.values() if any(parts))
            assert original == converted, f'Paragraph conversion mismatch: missing {original - converted}, extra {converted - original}'
            relations = {r.get('Id'): r.get('Target') for r in ET.fromstring(archive.read('word/_rels/document.xml.rels'))}
            source_images = []
            for node in document.iter():
                rid = node.get(R + 'embed') if node.tag == A + 'blip' else node.get(R + 'id') if node.tag == V + 'imagedata' else None
                if rid:
                    source_images.append(Path(relations[rid]).name)
            assert Counter(source_images) == Counter(Path(link).name for link in image_links), 'Image occurrences differ from DOCX'
            for name in referenced:
                assert (ROOT / 'docs/scenario-assets' / name).read_bytes() == archive.read('word/media/' + name), f'Image differs from original: {name}'
        print(f'Full DOCX fidelity: {sum(original.values())} exact paragraphs, {len(source_images)} image placements')
    print(f'Canonical Markdown verified: {len(blocks)} classified blocks, {len(referenced)} images; scene 1 column boundaries checked')


if __name__ == '__main__':
    main()
