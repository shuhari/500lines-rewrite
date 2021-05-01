import random
from unittest import TestCase

from ..binary_tree import ADDR_NONE, BinaryTree, Node, NodeRef, ValueRef
from .. import storage


class NodeTest(TestCase):
    def serialize_deserialize(self, key, value_addr,
                              left_addr=ADDR_NONE, right_addr=ADDR_NONE):
        tree = BinaryTree(storage.memory())
        node = Node(manager=tree, key=key,
                    value_ref=ValueRef.from_addr(value_addr),
                    left_ref=NodeRef.from_addr(left_addr),
                    right_ref=NodeRef.from_addr(right_addr))
        data = node.serialize()

        deserialized = Node.deserialize(tree, data)
        return deserialized

    def test_serialize_leaf(self):
        node = self.serialize_deserialize(key='k',
                                          value_addr=1)
        self.assertEqual('k', node.key)
        self.assertEqual(1, node.value_ref.addr)
        self.assertIsNone(node.left_ref)
        self.assertIsNone(node.right_ref)

    def test_serialize_left_only(self):
        node = self.serialize_deserialize(key='k',
                                          value_addr=1,
                                          left_addr=2)
        self.assertEqual('k', node.key)
        self.assertEqual(1, node.value_ref.addr)
        self.assertEqual(2, node.left_ref.addr)
        self.assertIsNone(node.right_ref)

    def test_serialize_full(self):
        node = self.serialize_deserialize(key='k',
                                          value_addr=1,
                                          left_addr=2,
                                          right_addr=3)
        self.assertEqual('k', node.key)
        self.assertEqual(1, node.value_ref.addr)
        self.assertEqual(2, node.left_ref.addr)
        self.assertEqual(3, node.right_ref.addr)


class BinaryTreeTest(TestCase):
    def setUp(self):
        self.tree = BinaryTree(storage.memory())

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


class BinaryTreeSerializeTest(TestCase):
    def save_load(self, pairs) -> BinaryTree:
        save_storage = storage.memory()
        tree = BinaryTree(save_storage)
        for k, v in pairs:
            tree.set(k, v)
        tree.commit()

        load_storage = save_storage.copy()
        load_tree = BinaryTree(load_storage)
        for k, v in pairs:
            self.assertEqual(v, load_tree.get(k))
        return load_tree

    def test_no_root(self):
        self.save_load([])

    def test_single(self):
        self.save_load([
            ('k', 'v')
        ])

    def test_full(self):
        self.save_load([
            ('k4', 'v4'),
            ('k2', 'v2'),
            ('k1', 'v1'),
            ('k3', 'v3'),
            ('k6', 'v6'),
            ('k5', 'v5'),
            ('k7', 'v7'),
        ])

