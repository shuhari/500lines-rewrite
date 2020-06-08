import unittest
import lib


class LibTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(3, lib.add(1, 2))

    def test_add_negative(self):
        self.assertEqual(1, lib.add(2, -1))

    def test_error(self):
        raise ValueError('test error')

    def test_fail(self):
        self.fail('failure')
