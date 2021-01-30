from unittest import TestCase

from .common import link_test_file, html_lines


class LinkerTest(TestCase):
    def test_link_install(self):
        self.assertEqual(link_test_file('install.rst'), html_lines('Installation', [
            '<h1>Installation</h1>',
        ]))

    def test_link_tutorial(self):
        self.assertEqual(link_test_file('tutorial'), html_lines('Beginners Tutorial', [
            '<h1>Beginners Tutorial</h1>',
            '<p>Welcome to the project tutorial!</p>',
            '<p>This text will take you through the basic of ...</p>',
            '<a name="hello_world"/>',
            '<h2>Hello, World</h2>',
            '<a name="adding_logging"/>',
            '<h2>Adding Logging</h2>',
        ]))

    def test_link_api(self):
        self.assertEqual(link_test_file('api'), html_lines('API Reference', [
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
        ]))

    def test_link_index(self):
        self.assertEqual(link_test_file('index.rst'), html_lines('Table of Contents', [
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
        ]))
