import os
import re

from .core import AstDoc, AstNode
from .utils import find_index


def parse_file(file_path) -> AstDoc:
    """parse rst file to ast model"""
    name = os.path.splitext(os.path.basename(file_path))[0]
    with open(file_path, 'r') as f:
        lines = [x.rstrip() for x in f.readlines()]
        doc = parse(name, lines)
    return doc


def parse(name, lines) -> AstDoc:
    """parse lines to ast model"""
    doc = AstDoc(name)
    items = list(parse_headers(lines))
    items = list(parse_toctree(items))
    items = list(parse_paragraphs(items))
    for item in items:
        doc.append_child(item)
    return doc


def parse_headers(lines):
    """line followed by multiple =/- treated as header"""
    index = len(lines) - 1
    nodes = []
    while index >= 0:
        line = lines[index].rstrip()
        if set(line) == set('=') and index > 0:
            nodes.insert(0, AstNode('h1', lines[index - 1].strip()))
            index -= 2
        elif set(line) == set('-') and index > 0:
            nodes.insert(0, AstNode('h2', lines[index - 1].strip()))
            index -= 2
        else:
            nodes.insert(0, line)
            index -= 1
    return nodes


def parse_toctree(items):
    """content between toctree:: and fist non-indent line treated as toctree"""

    def is_start(x):
        return isinstance(x, str) and x.strip() == '.. toctree::'

    def is_end(x):
        return isinstance(x, AstNode) or \
                (isinstance(x, str) and x.strip() and re.search(r'^([ \t]+)', x) is None)

    start = find_index(items, is_start)
    if start < 0:
        for item in items:
            yield item
    else:
        end = find_index(items[start + 1:], is_end)
        end = start + end if end >= 0 else len(items)
        for i in range(start):
            yield items[i]
        toctree = AstNode('toctree')
        for i in range(start + 1, end):
            if isinstance(items[i], str) and items[i].strip():
                toctree.append_child(AstNode('toc', items[i].strip()))
        yield toctree
        for i in range(end + 1, len(items)):
            yield items[i]


def parse_paragraphs(items):
    """Convert origin string lines to <p> node, already parsed nodes leave as is"""
    for item in items:
        if isinstance(item, AstNode):
            yield item
        elif isinstance(item, str) and item.strip():
            p = AstNode('p')
            for part in re.split(r'(:doc:`.+`)', item.strip()):
                m = re.match(r':doc:`(.+)`', part)
                if m:
                    p.append_child(AstNode('a', m.group(1)))
                else:
                    p.append_child(AstNode('text', part))
            yield p
