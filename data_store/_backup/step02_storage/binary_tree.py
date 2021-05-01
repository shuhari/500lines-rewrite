MISSING = object()
ADDR_NONE = 0


class ValueRef:
    def __init__(self, addr=ADDR_NONE, value=None):
        self.addr = addr
        self.value = value

    def get(self):
        return self.value

    def transform(self, new_value=MISSING):
        return self if new_value is MISSING else ValueRef(value=new_value)


class NodeRef:
    def __init__(self, addr=ADDR_NONE, node=None):
        self.addr = addr
        self.node = node

    def __bool__(self):
        return (self.addr != ADDR_NONE) or (self.node is not None)

    def get(self):
        return self.node

    def transform(self, node=MISSING):
        return self if node is MISSING else NodeRef(node=node)


NodeRef.none = NodeRef()


class Node:
    """Node of binary tree"""
    def __init__(self, key, value_ref, left_ref=None, right_ref=None):
        assert isinstance(value_ref, ValueRef)
        assert left_ref is None or isinstance(left_ref, NodeRef)
        assert right_ref is None or isinstance(right_ref, NodeRef)
        self.key = key
        self.value_ref = value_ref
        self.left_ref = left_ref or NodeRef.none
        self.right_ref = right_ref or NodeRef.none

    def is_leaf(self) -> bool:
        return not self.left_ref and not self.right_ref

    def transform(self, value=MISSING, left=MISSING, right=MISSING):
        """create new node based on current"""
        return Node(self.key,
                    value_ref=self.value_ref.transform(value),
                    left_ref=self.left_ref.transform(left),
                    right_ref=self.right_ref.transform(right))

    @property
    def value(self):
        return self.value_ref.get()

    @property
    def left(self):
        return self.left_ref.get()

    @property
    def right(self):
        return self.right_ref.get()


class BinaryTree:
    def __init__(self):
        self._root = None

    def get(self, key):
        node = find(self._root, key)
        return node.value

    def set(self, key, value):
        self._root = insert(self, self._root, key, value)

    def delete(self, key):
        self._root = remove(self._root, key)

    def create_node(self, key, value, left=None, right=None) -> Node:
        return Node(key=key,
                    value_ref=ValueRef(value=value),
                    left_ref=NodeRef(left) if left else None,
                    right_ref=NodeRef(right) if right else None)


def find(node: Node, key) -> Node:
    if node is None:
        raise KeyError(f'Key not found: {key}')
    elif node.key == key:
        return node
    elif key < node.key:
        return find(node.left, key)
    else:  # key > node.key
        return find(node.right, key)


def insert(tree: BinaryTree, node: Node, key, value) -> Node:
    if not node:
        return tree.create_node(key, value)
    elif key < node.key:
        return node.transform(left=insert(tree, node.left, key, value))
    elif key > node.key:
        return node.transform(right=insert(tree, node.right, key, value))
    else:  # key == node.key
        if node.value == value:
            return node
        return node.transform(value=value)


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
        return node.transform(left=remove(node.left, key))
    elif key > node.key:
        return node.transform(right=remove(node.right, key))
    else:  # key == node.key
        if node.is_leaf():
            return None
        elif node.left and not node.right:
            return node.left
        elif node.right and not node.left:
            return node.right
        else:
            max_node = find_max(node.left)
            return max_node.transform(left=remove(node.left, max_node.key),
                                      right=node.right)
