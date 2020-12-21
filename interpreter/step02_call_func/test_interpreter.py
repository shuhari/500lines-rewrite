import unittest

from .interpreter import Interpreter


class InterpreterTest(unittest.TestCase):
    def exec_interpreter(self, source, local_vars=None, dump_code=False, trace_stack=False):
        interpreter = Interpreter(source,
                                  local_vars=local_vars,
                                  dump_code=dump_code, trace_stack=trace_stack)
        interpreter.exec()
        return interpreter

    def test_add(self):
        source = "n = a + 1"
        interpreter = self.exec_interpreter(source, {'a': 2}, False, False)
        self.assertEqual(3, interpreter.get_local('n'))

    def test_call_func(self):
        source = "n = divmod(a, 2)"
        interpreter = self.exec_interpreter(source, {'a': 11}, False, False)
        self.assertEqual((5, 1), interpreter.get_local('n'))


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    unittest.main()
