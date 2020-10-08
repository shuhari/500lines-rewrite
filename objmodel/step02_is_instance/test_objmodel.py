import unittest

from .objmodel import define_class, create_instance, is_instance, Object, Type


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
        A = define_class(name='A')
        obj = create_instance(A)
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
        A = define_class(name='A')
        obj = create_instance(A)
        with self.assertRaises(AttributeError):
            obj.get_attr('a')

    def test_get_setdefine_class_field(self):
        # Python
        class A:
            a = 1
        self.assertEqual(1, A.a)

        A.a = 2
        self.assertEqual(2, A.a)

        # Object Model
        A = define_class(name='A', fields={'a': 1})
        self.assertEqual(1, A.get_attr('a'))

        A.set_attr('a', 2)
        self.assertEqual(2, A.get_attr('a'))

    def test_get_setdefine_class_field_missing(self):
        # Python
        class A:
            pass
        with self.assertRaises(AttributeError):
            A.a

        # Object Model
        A = define_class(name='A')
        with self.assertRaises(AttributeError):
            A.get_attr('a')

    def test_getdefine_class_field_fromcreate_instance(self):
        # Python
        class A:
            a = 1
        obj = A()
        self.assertEqual(1, obj.a)

        obj.a = 2
        self.assertEqual(2, obj.a)
        self.assertEqual(1, A.a)

        # Object Model
        A = define_class(name='A', fields={'a': 1})
        obj = create_instance(A)
        self.assertEqual(1, obj.get_attr('a'))

        obj.set_attr('a', 2)
        self.assertEqual(2, obj.get_attr('a'))
        self.assertEqual(1, A.get_attr('a'))

    def test_iscreate_instance(self):
        # Python
        class A: pass
        class B(A): pass
        b = B()
        self.assertTrue(isinstance(b, B))
        self.assertTrue(isinstance(b, A))
        self.assertTrue(isinstance(b, object))
        self.assertFalse(isinstance(b, type))

        # Object Model
        A = define_class(name='A')
        B = define_class(name='B', base=A)
        b = create_instance(B)
        self.assertTrue(is_instance(b, B))
        self.assertTrue(is_instance(b, A))
        self.assertTrue(is_instance(b, Object))
        self.assertFalse(is_instance(b, Type))

    def test_isinstancedefine_class(self):
        # Python
        class A: pass
        class B(A): pass
        self.assertTrue(isinstance(B, type))
        self.assertTrue(isinstance(A, type))

        # Object Model
        A = define_class(name='A')
        B = define_class(name='B', base=A)
        self.assertTrue(is_instance(B, Type))
        self.assertTrue(is_instance(A, Type))


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    unittest.main()
