MISSING = object()
ADDR_NONE = 0


class Ref:
    def __init__(self, addr=ADDR_NONE, target=MISSING):
        assert isinstance(addr, int)
        self.addr = addr
        self.target = target

    def is_commited(self) -> bool:
        return self.addr != ADDR_NONE

    def is_loaded(self) -> bool:
        return self.target is not MISSING

    def get(self):
        assert self.is_loaded()
        return self.target


class ValueRef(Ref):
    @classmethod
    def transform(cls, current, new_value):
        return current if new_value is MISSING else cls(target=new_value)


class NodeRef(Ref):
    @classmethod
    def transform(cls, current, new_node):
        return current if new_node is MISSING else cls(target=new_node)


class Node:
    """Node of binary tree"""
    def __init__(self, key, value_ref: ValueRef, left_ref: NodeRef = None, right_ref: NodeRef = None):
        assert isinstance(value_ref, ValueRef)
        assert left_ref is None or isinstance(left_ref, NodeRef)
        assert right_ref is None or isinstance(right_ref, NodeRef)
        self.key = key
        self.value_ref = value_ref
        self.left_ref = left_ref
        self.right_ref = right_ref

    def is_leaf(self) -> bool:
        return (self.left is None) and (self.right is None)

    def transform(self, value=MISSING, left=MISSING, right=MISSING):
        """create new node based on current"""
        value = self.value if value is MISSING else value
        left = self.left if left is MISSING else left
        right = self.right if right is MISSING else right
        return Node(self.key,
                    value_ref=ValueRef.transform(self.value_ref, value),
                    left_ref=NodeRef.transform(self.left_ref, left),
                    right_ref=NodeRef.transform(self.right_ref, right))

    @property
    def value(self):
        return self.value_ref.get()

    @property
    def left(self):
        return self.left_ref.get() if self.left_ref else None

    @property
    def right(self):
        return self.right_ref.get() if self.right_ref else None

    @classmethod
    def create(cls, key, value):
        return cls(key=key,
                   value_ref=ValueRef(target=value))


class BinaryTree:
    def __init__(self):
        self._root_ref = None

    @property
    def root_node(self):
        return self._root_ref.get() if self._root_ref else None

    @root_node.setter
    def root_node(self, value):
        if value == self.root_node:
            return
        self._root_ref = NodeRef(target=value) if value else None

    def get(self, key):
        node = find(self.root_node, key)
        return node.value

    def set(self, key, value):
        self.root_node = insert(self.root_node, key, value)

    def delete(self, key):
        self.root_node = remove(self.root_node, key)


def find(node, key) -> Node:
    if node is None:
        raise KeyError(f'Key not found: {key}')
    elif node.key == key:
        return node
    elif key < node.key:
        return find(node.left, key)
    else:  # key > node.key
        return find(node.right, key)


def insert(node: Node, key, value) -> Node:
    if not node:
        return Node.create(key, value)
    elif key < node.key:
        return node.transform(left=insert(node.left, key, value))
    elif key > node.key:
        return node.transform(right=insert(node.right, key, value))
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
