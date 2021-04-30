import random
from unittest import TestCase

from ..binary_tree import BinaryTree


class BinaryTreeTest(TestCase):
    def setUp(self):
        self.tree = BinaryTree()

    def expect_key_error(self, key):
        with self.assertRaises(KeyError):
            self.tree.get(key)

    def test_get_missing_key(self):
        self.expect_key_error('invalid_key')

    def test_set_get_key(self):
        self.tree.set('a', 'b')
        self.assertEqual('b', self.tree.get('a'))

    def test_set_get_random_keys(self):
        candidates = list(range(10000))
        pairs = list(zip(random.sample(candidates, 100), random.sample(candidates, 100)))
        for k, v in pairs:
            self.tree.set(k, v)
        random.shuffle(pairs)
        for k, v in pairs:
            self.assertEqual(v, self.tree.get(k))

    def test_overwrite_key(self):
        self.tree.set('a', 'b')
        self.tree.set('a', 'c')
        self.assertEqual('c', self.tree.get('a'))

    def test_delete_key_not_exist(self):
        with self.assertRaises(KeyError):
            self.tree.delete('b')

    def test_delete_leaf(self):
        self.tree.set('b', 2)
        self.tree.delete('b')
        self.expect_key_error('b')

    def test_delete_left(self):
        self.tree.set('b', 2)
        self.tree.set('a', 1)
        self.tree.delete('a')
        self.assertEqual(2, self.tree.get('b'))
        self.expect_key_error('a')

    def test_delete_right(self):
        self.tree.set('b', 2)
        self.tree.set('c', 3)
        self.tree.delete('c')
        self.assertEqual(2, self.tree.get('b'))
        self.expect_key_error('c')

    def test_delete_root(self):
        self.tree.set('b', 2)
        self.tree.set('c', 3)
        self.tree.set('a', 1)
        self.tree.delete('b')
        self.expect_key_error('b')
        self.assertEqual([3, 1],
                         [self.tree.get('c'), self.tree.get('a')])

    def test_delete_mid_node(self):
        self.tree.set('c', 3)
        self.tree.set('b', 2)
        self.tree.set('d', 4)
        self.tree.set('a', 1)
        self.tree.delete('b')
        self.expect_key_error('b')
        self.assertEqual([1, 3, 4],
                         [self.tree.get('a'), self.tree.get('c'), self.tree.get('d')])
