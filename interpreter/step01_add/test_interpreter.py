import unittest

from .interpreter import Interpreter


class InterpreterTest(unittest.TestCase):
    def test_add(self):
        source = "n = a + 1"
        interpreter = Interpreter(source)
        interpreter.set_local('a', 2)
        interpreter.exec(True, True)
        self.assertEqual(3, interpreter.get_local('n'))


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    unittest.main()
