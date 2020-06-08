import unittest

from ..webserver import PyLintHandler, UnitTestHandler


class ArtifactParserTest(unittest.TestCase):
    def test_pylint(self):
        data = """\
************* Module main
main.py:1:0: C0114: Missing module docstring (missing-module-docstring)
main.py:3:0: C0103: Constant name "myVar" doesn't conform to UPPER_CASE naming style (invalid-name)
main.py:1:0: W0611: Unused import os (unused-import)"""
        model = PyLintHandler().parse(data)
        self.assertEqual(3, len(model))

        issue = model[0]
        self.assertEqual('main.py', issue.filename)
        self.assertEqual(1, issue.line)
        self.assertEqual(0, issue.column)
        self.assertEqual('C0114', issue.name)
        self.assertTrue(issue.description.startswith('Missing module'))

    def test_unittest(self):
        data = """\
..EF
======================================================================
ERROR: test_error (test_lib.LibTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/yuhao/test-ci/agent1/ac470e74e1a04670b1065c3751f148e9/tests/test_lib.py", line 14, in test_error
    raise Exception('error')
Exception: error"""
        model = UnitTestHandler().parse(data)
        self.assertEqual(2, model.pass_count)
        self.assertEqual(1, model.error_count)
        self.assertEqual(1, model.fail_count)


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    main()
