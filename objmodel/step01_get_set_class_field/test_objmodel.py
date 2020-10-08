import unittest

from .objmodel import Class, Instance


class ObjModelTest(unittest.TestCase):
    def test_get_set_field(self):
        # Python
        class A:
            pass
        obj = A()
        obj.a = 1
        self.assertEqual(1, obj.a)

        obj.b = 5
        self.assertEqual((1, 5), (obj.a, obj.b))

        obj.a = 2
        self.assertEqual((2, 5), (obj.a, obj.b))

        # Object Model
        A = Class(name='A')
        obj = Instance(A)
        obj.set_attr('a', 1)
        self.assertEqual(1, obj.get_attr('a'))

        obj.set_attr('b', 5)
        self.assertEqual((1, 5), (obj.get_attr('a'), obj.get_attr('b')))

        obj.set_attr('a', 2)
        self.assertEqual((2, 5), (obj.get_attr('a'), obj.get_attr('b')))

    def test_get_set_field_missing(self):
        # Python
        class A:
            pass
        obj = A()
        with self.assertRaises(AttributeError):
            obj.a

        # Object Model
        A = Class(name='A')
        obj = Instance(A)
        with self.assertRaises(AttributeError):
            obj.get_attr('a')

    def test_get_set_class_field(self):
        # Python
        class A:
            a = 1
        self.assertEqual(1, A.a)

        A.a = 2
        self.assertEqual(2, A.a)

        # Object Model
        A = Class(name='A', fields={'a': 1})
        self.assertEqual(1, A.get_attr('a'))

        A.set_attr('a', 2)
        self.assertEqual(2, A.get_attr('a'))

    def test_get_set_class_field_missing(self):
        # Python
        class A:
            pass
        with self.assertRaises(AttributeError):
            A.a

        # Object Model
        A = Class(name='A')
        with self.assertRaises(AttributeError):
            A.get_attr('a')

    def test_get_class_field_from_instance(self):
        # Python
        class A:
            a = 1
        obj = A()
        self.assertEqual(1, obj.a)

        obj.a = 2
        self.assertEqual(2, obj.a)
        self.assertEqual(1, A.a)

        # Object Model
        A = Class(name='A', fields={'a': 1})
        obj = Instance(A)
        self.assertEqual(1, obj.get_attr('a'))

        obj.set_attr('a', 2)
        self.assertEqual(2, obj.get_attr('a'))
        self.assertEqual(1, A.get_attr('a'))


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    unittest.main()
