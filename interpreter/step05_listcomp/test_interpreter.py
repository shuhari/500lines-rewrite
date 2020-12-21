import unittest

from .interpreter import Interpreter


class InterpreterTest(unittest.TestCase):
    def exec_interpreter(self, source, local_vars=None, dump_code=False, trace_stack=False):
        interpreter = Interpreter(source, local_vars=local_vars,
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

    def test_if(self):
        source = """
if a > 10:
  b = True
else:
  b = False
                """.strip()
        interpreter = self.exec_interpreter(source, {'a': 11}, False, False)
        self.assertEqual(True, interpreter.get_local('b'))

        interpreter = self.exec_interpreter(source, {'a': 3}, False, False)
        self.assertEqual(False, interpreter.get_local('b'))

    def test_define_func(self):
        source = """
def f(x):
    return x + 1

n = f(a)
        """.strip()
        interpreter = self.exec_interpreter(source, {'a': 11}, False, False)
        self.assertEqual(12, interpreter.get_local('n'))

    def test_list_comprehension(self):
        source = """
n = [x for x in range(a) if x>5]
        """.strip()
        interpreter = self.exec_interpreter(source, {'a': 10}, True, True)
        self.assertEqual([6, 7, 8, 9], interpreter.get_local('n'))


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    unittest.main()
