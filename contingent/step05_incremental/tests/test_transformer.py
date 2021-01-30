from unittest import TestCase

from .common import parse_ast
from ..transformer import transform


class TransformerTest(TestCase):
    def test_transform_install(self):
        ast = parse_ast('install.rst')
        code = transform(ast)
        self.assertEqual('install', code.name)
        self.assertEqual('Installation', code.title)
        toctree = [
            '<ul>',
            '<li><a class="toc-h1" href="install.html">Installation</a></li>',
            '</ul>'
        ]
        self.assertEqual(toctree, code.toctree)
        html = [
            '<html>',
            '<head>',
            '<title>Installation</title>',
            '</head>',
            '<body>',
            '<h1>Installation</h1>',
            '</body>',
            '</html>'
        ]
        self.assertEqual(html, code.html)
        self.assertEqual(set([('doc', 'install')]), code.dependencies)

    def test_transform_tutorial(self):
        ast = parse_ast('tutorial.rst')
        code = transform(ast)
        self.assertEqual('Beginners Tutorial', code.title)
        toctree = [
            '<ul>',
            '<li>',
            '<a class="toc-h1" href="tutorial.html">Beginners Tutorial</a>',
            '<ul>',
            '<li><a class="toc-h2" href="tutorial.html#hello_world">Hello, World</a></li>',
            '<li><a class="toc-h2" href="tutorial.html#adding_logging">Adding Logging</a></li>',
            '</ul>',
            '</li>',
            '</ul>'
        ]
        self.assertEqual(toctree, code.toctree)
        html = [
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
        self.assertEqual(html, code.html)
        self.assertEqual(set([('doc', 'tutorial')]), code.dependencies)

    def test_transform_api(self):
        ast = parse_ast('api.rst')
        code = transform(ast)
        self.assertEqual('API Reference', code.title)
        toctree = [
            '<ul>',
            '<li>',
            '<a class="toc-h1" href="api.html">API Reference</a>',
            '<ul>',
            '<li><a class="toc-h2" href="api.html#handy_functions">Handy Functions</a></li>',
            '<li><a class="toc-h2" href="api.html#obscure_classes">Obscure Classes</a></li>',
            '</ul>',
            '</li>',
            '</ul>'
        ]
        self.assertEqual(toctree, code.toctree)
        html = [
            '<html>',
            '<head>',
            '<title>API Reference</title>',
            '</head>',
            '<body>',
            '<h1>API Reference</h1>',
            '<p>',
            'Before reading this, try reading our ',
            '<a href="tutorial.html>',
            '{{ ctx.get_title("tutorial") }}',
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
        self.assertEqual(html, code.html)
        self.assertEqual(set([
            ('doc', 'api'),
            ('title', 'tutorial')
        ]), code.dependencies)

    def test_transform_index(self):
        ast = parse_ast('index.rst')
        code = transform(ast)
        self.assertEqual('Table of Contents', code.title)
        toctree = [
            '<ul>',
            '<li><a class="toc-h1" href="index.html">Table of Contents</a></li>',
            '</ul>',
        ]
        self.assertEqual(toctree, code.toctree)
        html = [
            '<html>',
            '<head>',
            '<title>Table of Contents</title>',
            '</head>',
            '<body>',
            '<h1>Table of Contents</h1>',
            '<ul>',
            "{{ ctx.get_toctree('install') }}",
            "{{ ctx.get_toctree('tutorial') }}",
            "{{ ctx.get_toctree('api') }}",
            '</ul>',
            '<p>This is the main text.</p>',
            '</body>',
            '</html>'
        ]
        self.assertEqual(html, code.html)
        self.assertEqual(set([
            ('doc', 'index'),
            ('toctree', 'install'),
            ('toctree', 'tutorial'),
            ('toctree', 'api'),
        ]), code.dependencies)
