import ast
from unittest import TestCase

from astxml import AstXml
from models import AnalysisContext
from visitors import LineLengthVisitor, ExceptionTypeVisitor, VariableUsageVisitor, PreferIsNotVisitor


class VisitorTestMixin:
    visitor_type = None

    def run_visitor(self, code: str, xml_filename: str = None):
        """Execute visitor on ast node, dump result to file if specified"""
        self.assertIsNotNone(self.visitor_type, 'Visitor type not defined.')
        self.ctx = AnalysisContext('test.py')
        visitor = self.visitor_type(self.ctx)
        ast_node = ast.parse(code)
        visitor.visit(ast_node)
        if xml_filename:
            AstXml(ast_node).save_file('dump/' + xml_filename)

    def assert_no_issue(self):
        issue_count = len(self.ctx.issues)
        self.assertEqual(0, issue_count, f'Expected no issue, actual: {issue_count}')

    def assert_found_issue(self, lineno: int, code: str):
        for issue in self.ctx.issues:
            if issue.line == lineno and issue.code == code:
                return
        issues = '\n'.join([str(x) for x in self.ctx.issues])
        self.fail(f"Expect issue {code} in line {lineno}, actual: {issues}")


class LineLengthVisitorTest(TestCase, VisitorTestMixin):
    visitor_type = LineLengthVisitor

    def test_visit(self):
        code = """
print('short line')
print('this is a very, very, very, very, very, very, very, very, very, very, very, very long line...')
        """.strip()
        self.run_visitor(code, xml_filename='line-length.xml')
        self.assert_found_issue(2, 'W0001')

    def test_visit_docstring(self):
        code = """
def fn():
   '''
   This is a very, very, very, very, very, very, very, very, very, very, very, very long doc string
   The second line
   '''
   pass        
        """.strip()
        self.run_visitor(code, xml_filename='doc-string-length.xml')
        self.assert_found_issue(3, 'W0001')


class ExceptionTypeVisitorTest(TestCase, VisitorTestMixin):
    visitor_type = ExceptionTypeVisitor

    def test_no_handler(self):
        code = """print('hello')""".strip()
        self.run_visitor(code, xml_filename='exception-no-handler.xml')
        self.assert_no_issue()

    def test_handler_generic(self):
        code = """
try:
   calc()
except Exception as e:
   print(e)
        """.strip()
        self.run_visitor(code, xml_filename='exception-catch-generic.xml')
        self.assert_found_issue(3, 'W0002')

    def test_catch_specific(self):
        code = """
try:
   calc()
except ValueError as e:
   print(e)
        """.strip()
        self.run_visitor(code, xml_filename='exception-catch-specific.xml')
        self.assert_no_issue()

    def test_catch_no_type(self):
        code = """
try:
   calc()
except:
   print(e)
                """.strip()
        self.run_visitor(code, xml_filename='exception-catch-no-type.xml')
        self.assert_found_issue(3, 'W0002')

    def test_catch_multiple_types_no_issue(self):
        code = """
try:
   calc()
except (ValueError, KeyError) as e:
   print(e)
                """.strip()
        self.run_visitor(code, xml_filename='exception-catch-multi-no-issue.xml')
        self.assert_no_issue()

    def test_catch_multiple_types_with_issue(self):
        code = """
try:
   calc()
except (Exception, ValueError) as e:
   print(e)
                """.strip()
        self.run_visitor(code, xml_filename='exception-catch-multi-with-issue.xml')
        self.assert_found_issue(3, 'W0002')


class VariableUsageVisitorTest(TestCase, VisitorTestMixin):
    visitor_type = VariableUsageVisitor

    def test_no_func(self):
        code = """print('hello')""".strip()
        self.run_visitor(code, xml_filename='var-no-func.xml')
        self.assert_no_issue()

    def test_global_vars_used(self):
        code = """
name = 'user'
print(name)        
        """.strip()
        self.run_visitor(code, xml_filename='global-vars-used.xml')
        self.assert_no_issue()

    def test_global_vars_unused(self):
        code = """
name = 'user'
print('hello')        
        """.strip()
        self.run_visitor(code, xml_filename='global-vars-unused.xml')
        self.assert_found_issue(1, 'W0003')

    def test_local_vars_used(self):
        code = """
def fn():        
    name = 'user'
    print(name)        
        """.strip()
        self.run_visitor(code, xml_filename='local-vars-used.xml')
        self.assert_no_issue()

    def test_local_vars_unused(self):
        code = """
def fn():        
    name = 'user'
    print('hello')        
        """.strip()
        self.run_visitor(code, xml_filename='local-vars-unused.xml')
        self.assert_found_issue(2, 'W0003')

    def test_nested_funcs(self):
        code = """
def outer():
  def inner():
      name = 'inner'
      print('hello')
  name = 'outer'
  print(name)
        """.strip()
        self.run_visitor(code, xml_filename='vars-nested-func.xml')
        self.assert_found_issue(3, 'W0003')


class PreferIsNotVisitorTest(TestCase, VisitorTestMixin):
    visitor_type = PreferIsNotVisitor

    def test_is_not(self):
        code = """
if a is not None:
    print(a)
        """.strip()
        self.run_visitor(code, xml_filename='is-not.xml')
        self.assert_no_issue()

    def test_not_is(self):
        code = """
if not a is None:
    print(a)
        """.strip()
        self.run_visitor(code, xml_filename='not-is.xml')
        self.assert_found_issue(1, 'W0004')
