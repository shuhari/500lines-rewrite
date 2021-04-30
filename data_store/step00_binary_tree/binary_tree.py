MISSING = object()


class Node:
    """Node of binary tree"""
    def __init__(self, key, value, left=None, right=None):
        self.key = key
        self.value = value
        self.left = left
        self.right = right

    def is_leaf(self) -> bool:
        return (self.left is None) and (self.right is None)


class BinaryTree:
    def __init__(self):
        self._root = None

    def get(self, key):
        node = find(self._root, key)
        return node.value

    def set(self, key, value):
        self._root = insert(self._root, key, value)

    def delete(self, key):
        self._root = remove(self._root, key)

    def keys(self, order='mid'):
        """
        iterate keys by specified order.
        :param order: pre | post | mid
        """
        return keys(self._root, order)


def find(node, key) -> Node:
    if node is None:
        raise KeyError(f'Key not found: {key}')
    elif node.key == key:
        return node
    elif key < node.key:
        return find(node.left, key)
    else:  # key > node.key
        return find(node.right, key)


def transform(node: Node, value=MISSING, left=MISSING, right=MISSING):
    """create new node based on current"""
    value = node.value if value is MISSING else value
    left = node.left if left is MISSING else left
    right = node.right if right is MISSING else right
    return Node(node.key, value=value, left=left, right=right)


def insert(node: Node, key, value) -> Node:
    if not node:
        return Node(key, value)
    elif key < node.key:
        return transform(node, left=insert(node.left, key, value))
    elif key > node.key:
        return transform(node, right=insert(node.right, key, value))
    else:  # key == node.key
        if node.value == value:
            return node
        return transform(node, value=value)


def find_max(node: Node) -> Node:
    """
    Find child with maximum key below current node.
    It will be used for node deletion
    """
    if node is None:
        return None
    elif node.is_leaf():
        return node
    else:
        return find_max(node.right) or find_max(node.left)


def remove(node: Node, key) -> Node:
    if node is None:
        raise KeyError(f'Key not found: {key}')
    elif key < node.key:
        return transform(node, left=remove(node.left, key))
    elif key > node.key:
        return transform(node, right=remove(node.right, key))
    else:  # key == node.key
        if node.is_leaf():
            return None
        elif node.left and not node.right:
            return node.left
        elif node.right and not node.left:
            return node.right
        else:
            max_node = find_max(node.left)
            return transform(max_node,
                             left=remove(node.left, max_node.key),
                             right=node.right)
