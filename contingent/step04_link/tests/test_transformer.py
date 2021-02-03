from unittest import TestCase

from .common import transform_test_file, html_lines


class TransformerTest(TestCase):

    def test_transform_install(self):
        code = transform_test_file('install.rst')
        self.assertEqual('install', code.name)
        self.assertEqual('Installation', code.title)
        self.assertEqual(code.toctree, [
            '<ul>',
            '<li><a class="toc-h1" href="install.html">Installation</a></li>',
            '</ul>'
        ])
        self.assertEqual(code.html, html_lines('Installation', [
            '<h1>Installation</h1>',
        ]))
        self.assertEqual(set([
            ('doc', 'install')
        ]), code.dependencies)

    def test_transform_tutorial(self):
        code = transform_test_file('tutorial.rst')
        self.assertEqual('Beginners Tutorial', code.title)
        self.assertEqual(code.toctree, [
            '<ul>',
            '<li>',
            '<a class="toc-h1" href="tutorial.html">Beginners Tutorial</a>',
            '<ul>',
            '<li><a class="toc-h2" href="tutorial.html#hello_world">Hello, World</a></li>',
            '<li><a class="toc-h2" href="tutorial.html#adding_logging">Adding Logging</a></li>',
            '</ul>',
            '</li>',
            '</ul>'
        ])
        self.assertEqual(code.html, html_lines('Beginners Tutorial', [
            '<h1>Beginners Tutorial</h1>',
            '<p>Welcome to the project tutorial!</p>',
            '<p>This text will take you through the basic of ...</p>',
            '<a name="hello_world"/>',
            '<h2>Hello, World</h2>',
            '<a name="adding_logging"/>',
            '<h2>Adding Logging</h2>',
        ]))
        self.assertEqual(set([('doc', 'tutorial')]), code.dependencies)

    def test_transform_api(self):
        code = transform_test_file('api.rst')
        self.assertEqual('API Reference', code.title)
        self.assertEqual(code.toctree, [
            '<ul>',
            '<li>',
            '<a class="toc-h1" href="api.html">API Reference</a>',
            '<ul>',
            '<li><a class="toc-h2" href="api.html#handy_functions">Handy Functions</a></li>',
            '<li><a class="toc-h2" href="api.html#obscure_classes">Obscure Classes</a></li>',
            '</ul>',
            '</li>',
            '</ul>'
        ])
        self.assertEqual(code.html, html_lines('API Reference', [
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
        ]))
        self.assertEqual(set([
            ('doc', 'api'),
            ('title', 'tutorial')
        ]), code.dependencies)

    def test_transform_index(self):
        code = transform_test_file('index.rst')
        self.assertEqual('Table of Contents', code.title)
        self.assertEqual(code.toctree, [
            '<ul>',
            '<li><a class="toc-h1" href="index.html">Table of Contents</a></li>',
            '</ul>',
        ])
        self.assertEqual(code.html, html_lines('Table of Contents', [
            '<h1>Table of Contents</h1>',
            '<ul>',
            "{{ ctx.get_toctree('install') }}",
            "{{ ctx.get_toctree('tutorial') }}",
            "{{ ctx.get_toctree('api') }}",
            '</ul>',
            '<p>This is the main text.</p>',
        ]))
        self.assertEqual(set([
            ('doc', 'index'),
            ('toctree', 'install'),
            ('toctree', 'tutorial'),
            ('toctree', 'api'),
        ]), code.dependencies)
