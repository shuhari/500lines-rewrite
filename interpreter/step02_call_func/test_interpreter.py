import unittest

from .interpreter import Interpreter


class InterpreterTest(unittest.TestCase):
    def exec_interpreter(self, source, locals=None, dump_code=False, trace_stack=False):
        interpreter = Interpreter(source)
        if locals:
            for k, v in locals.items():
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


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    unittest.main()
