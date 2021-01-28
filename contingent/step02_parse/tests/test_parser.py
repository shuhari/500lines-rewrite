import os
from unittest import TestCase

from ..core import AstDoc
from ..parser import parse_file


def parse_ast(file_name: str) -> AstDoc:
    file_path = os.path.join(os.path.dirname(__file__), '../../docs/src/' + file_name)
    return parse_file(file_path)


class ParserTest(TestCase):
    def assert_parse(self, file_name, expected_ast):
        ast = parse_ast(file_name)
        self.assertEqual(expected_ast.strip(), ast.dump_ast())

    def test_parse_install(self):
        self.assert_parse('install.rst', """
doc(install)
  h1(Installation)
        """)

    def test_parse_tutorial(self):
        self.assert_parse('tutorial.rst', """
doc(tutorial)
  h1(Beginners Tutorial)
  p
    text(Welcome to the project tutorial!)
  p
    text(This text will take you through the basic of ...)
  h2(Hello, World)
  h2(Adding Logging)
        """)

    def test_parse_api(self):
        self.assert_parse('api.rst', """
doc(api)
  h1(API Reference)
  p
    text(Before reading this, try reading our )
    a(tutorial)
    text(!)
  h2(Handy Functions)
  h2(Obscure Classes)
        """)

    def test_parse_index(self):
        self.assert_parse('index.rst', """
doc(index)
  h1(Table of Contents)
  toctree
    toc(install)
    toc(tutorial)
    toc(api)
  p
    text(This is the main text.)
        """)
