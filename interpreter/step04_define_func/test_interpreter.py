import unittest

from .interpreter import Interpreter


class InterpreterTest(unittest.TestCase):
    def exec_interpreter(self, source, local_vars=None, dump_code=False, trace_stack=False):
        interpreter = Interpreter(source)
        if locals:
            for k, v in local_vars.items():
                interpreter.set_local(k, v)
        interpreter.exec(dump_code=dump_code, trace_stack=trace_stack)
        return interpreter

    def test_add(self):
        source = "n = a + 1"
        interpreter = self.exec_interpreter(source, {'a': 2}, dump_code=False, trace_stack=False)
        self.assertEqual(3, interpreter.get_local('n'))

    def test_call_func(self):
        source = "n = divmod(a, 2)"
        interpreter = self.exec_interpreter(source, {'a': 11}, dump_code=False, trace_stack=False)
        self.assertEqual((5, 1), interpreter.get_local('n'))

    def test_if(self):
        source = """
if a > 10:
  b = True
else:
  b = False
                """.strip()
        interpreter = self.exec_interpreter(source, {'a': 11}, dump_code=False, trace_stack=False)
        self.assertEqual(True, interpreter.get_local('b'))

        interpreter = self.exec_interpreter(source, {'a': 3}, dump_code=False, trace_stack=False)
        self.assertEqual(False, interpreter.get_local('b'))

    def test_define_func(self):
        source = """
def f(x):
    return x + 1

n = f(a)
        """.strip()
        interpreter = self.exec_interpreter(source, {'a': 11}, dump_code=True, trace_stack=True)
        self.assertEqual(12, interpreter.get_local('n'))


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    unittest.main()
