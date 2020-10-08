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

    def test_call_method(self):
        # Python
        class A:
            def f(self):
                return self.x + 1
        obj = A()
        obj.x = 1
        self.assertEqual(2, obj.f())

        class B(A): pass
        obj = B()
        obj.x = 2
        self.assertEqual(3, obj.f())

        # Object Model
        def f_A(self):
            return self.get_attr('x') + 1
        A = define_class(name='A', fields={'f': f_A})
        obj = create_instance(A)
        obj.set_attr('x', 1)
        self.assertEqual(2, obj.call_method('f'))

        B = define_class(name='B', base=A)
        obj = create_instance(B)
        obj.set_attr('x', 2)
        self.assertEqual(3, obj.call_method('f'))

    def test_call_method_with_args(self):
        # Python
        class A:
            def f(self, delta):
                return self.x + delta
        obj = A()
        obj.x = 1
        self.assertEqual(3, obj.f(2))

        # Object Model
        def f_A(self, delta):
            return self.get_attr('x') + delta
        A = define_class(name='A', fields={'f': f_A})
        obj = create_instance(A)
        obj.set_attr('x', 1)
        self.assertEqual(3, obj.call_method('f', 2))

    def test_call_method_by_attr(self):
        # Python
        class A:
            def f(self):
                return self.x + 1
        obj = A()
        obj.x = 1
        method = obj.f
        self.assertEqual(2, method())

        # Object Model
        def f_A(self):
            return self.get_attr('x') + 1
        A = define_class(name='A', fields={'f': f_A})
        obj = create_instance(A)
        obj.set_attr('x', 1)
        method = obj.get_attr('f')
        self.assertEqual(2, method())


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    unittest.main()
