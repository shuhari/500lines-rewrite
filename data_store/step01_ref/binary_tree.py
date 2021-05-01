MISSING = object()
ADDR_NONE = 0


class Ref:
    def __init__(self, addr=ADDR_NONE, target=MISSING):
        assert isinstance(addr, int)
        self.addr = addr
        self.target = target

    @classmethod
    def transform(cls, current, data, key):
        return cls(target=data[key]) if key in data else current

    def get(self):
        assert self.target is not MISSING
        return self.target


class ValueRef(Ref):
    pass


class NodeRef(Ref):
    @classmethod
    def get_node(cls, ref):
        return ref.get() if ref else None


class Node:
    """Node of binary tree"""
    def __init__(self, key, value_ref: ValueRef,
                 left_ref: NodeRef = None,
                 right_ref: NodeRef = None):
        assert isinstance(value_ref, ValueRef)
        assert left_ref is None or isinstance(left_ref, NodeRef)
        assert right_ref is None or isinstance(right_ref, NodeRef)
        self.key = key
        self.value_ref = value_ref
        self.left_ref = left_ref
        self.right_ref = right_ref

    def is_leaf(self) -> bool:
        return (self.left is None) and (self.right is None)

    def transform(self, **kwargs):
        """create new node based on current"""
        return Node(self.key,
                    value_ref=ValueRef.transform(self.value_ref, kwargs, 'value'),
                    left_ref=NodeRef.transform(self.left_ref, kwargs, 'left'),
                    right_ref=NodeRef.transform(self.right_ref, kwargs, 'right'))

    @property
    def value(self):
        return self.value_ref.get()

    @property
    def left(self):
        return NodeRef.get_node(self.left_ref)

    @property
    def right(self):
        return NodeRef.get_node(self.right_ref)

    @classmethod
    def create(cls, key, value):
        return cls(key=key,
                   value_ref=ValueRef(target=value))


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
