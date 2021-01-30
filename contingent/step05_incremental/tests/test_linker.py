import os
from unittest import TestCase

from ..core import BuildContext
from .common import parse_ast
from ..transformer import transform
from ..linker import link


def preprocess_link(ctx, name):
    ast = parse_ast(name + '.rst')
    code = transform(ast)
    ctx.cache.set_output(code.name, code.dependencies)
    ctx.cache.set_input('doc', code.name, code.html)
    ctx.cache.set_input('title', code.name, code.title)
    ctx.cache.set_input('toctree', code.name, code.toctree)


class LinkerTest(TestCase):
    def run_link(self, name):
        base_dir = os.path.join(os.path.dirname(__file__), '../../docs')
        ctx = BuildContext(base_dir, cache_name='test.cache')
        preprocess_link(ctx, 'index')
        preprocess_link(ctx, 'install')
        preprocess_link(ctx, 'api')
        preprocess_link(ctx, 'tutorial')
        return link(ctx, name)

    def test_link_install(self):
        lines = [
            '<html>',
            '<head>',
            '<title>Installation</title>',
            '</head>',
            '<body>',
            '<h1>Installation</h1>',
            '</body>',
            '</html>'
        ]
        self.assertEqual(lines, self.run_link('install'))

    def test_link_tutorial(self):
        lines = [
            '<html>',
            '<head>',
            '<title>Beginners Tutorial</title>',
            '</head>',
            '<body>',
            '<h1>Beginners Tutorial</h1>',
            '<p>Welcome to the project tutorial!</p>',
            '<p>This text will take you through the basic of ...</p>',
            '<a name="hello_world"/>',
            '<h2>Hello, World</h2>',
            '<a name="adding_logging"/>',
            '<h2>Adding Logging</h2>',
            '</body>',
            '</html>'
        ]
        self.assertEqual(lines, self.run_link('tutorial'))

    def test_link_api(self):
        lines = [
            '<html>',
            '<head>',
            '<title>API Reference</title>',
            '</head>',
            '<body>',
            '<h1>API Reference</h1>',
            '<p>',
            'Before reading this, try reading our ',
            '<a href="tutorial.html>',
            'Beginners Tutorial',
            '</a>',
            '!',
            '</p>',
            '<a name="handy_functions"/>',
            '<h2>Handy Functions</h2>',
            '<a name="obscure_classes"/>',
            '<h2>Obscure Classes</h2>',
            '</body>',
            '</html>'
        ]
        self.assertEqual(lines, self.run_link('api'))

    def test_link_index(self):
        lines = [
            '<html>',
            '<head>',
            '<title>Table of Contents</title>',
            '</head>',
            '<body>',
            '<h1>Table of Contents</h1>',
            '<ul>',
            '<ul>',
            '<li><a class="toc-h1" href="install.html">Installation</a></li>',
            '</ul>',
            '<ul>',
            '<li>',
            '<a class="toc-h1" href="tutorial.html">Beginners Tutorial</a>',
            '<ul>',
            '<li><a class="toc-h2" href="tutorial.html#hello_world">Hello, World</a></li>',
            '<li><a class="toc-h2" href="tutorial.html#adding_logging">Adding Logging</a></li>',
            '</ul>',
            '</li>',
            '</ul>',
            '<ul>',
            '<li>',
            '<a class="toc-h1" href="api.html">API Reference</a>',
            '<ul>',
            '<li><a class="toc-h2" href="api.html#handy_functions">Handy Functions</a></li>',
            '<li><a class="toc-h2" href="api.html#obscure_classes">Obscure Classes</a></li>',
            '</ul>',
            '</li>',
            '</ul>',
            '</ul>',
            '<p>This is the main text.</p>',
            '</body>',
            '</html>'
        ]
        self.assertEqual(lines, self.run_link('index'))
