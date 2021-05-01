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

    def is_commited(self) -> bool:
        return self.addr != ADDR_NONE

    @classmethod
    def deserialize(cls, addr: int):
        assert isinstance(addr, int)
        return cls(addr=addr)


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

    def is_commited(self) -> bool:
        return self.addr != ADDR_NONE

    @classmethod
    def deserialize(cls, addr: int):
        assert isinstance(addr, int)
        return cls(addr=addr) if addr != ADDR_NONE else cls.none


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

    def serialize(self):
        assert self.value_ref.is_commited()
        data = {
            'key': self.key,
            'value_addr': self.value_ref.addr,
        }
        if self.left_ref:
            assert self.left_ref.is_commited()
            data['left_addr'] = self.left_ref.addr
        if self.right_ref:
            assert self.right_ref.is_commited()
            data['right_addr'] = self.right_ref.addr
        return data

    @classmethod
    def deserialize(cls, data):
        return Node(key=data['key'],
                    value_ref=ValueRef.deserialize(data['value_addr']),
                    left_ref=NodeRef.deserialize(data.get('left_addr', ADDR_NONE)),
                    right_ref=NodeRef.deserialize(data.get('right_addr', ADDR_NONE)))


class BinaryTree:
    def __init__(self, storage):
        self._root_ref = NodeRef.none
        self._storage = storage

    def get(self, key):
        node = find(self._root_ref, key)
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

    def commit(self):
        root_addr = self.commit_node(self._root)
        self._storage.set_root_addr(root_addr)

    def commit_node(self, node: Node) -> int:
        if not node:
            return ADDR_NONE
        self.commit_value(node.value_ref)
        self.commit_node_ref(node.left_ref)
        self.commit_node_ref(node.right_ref)


def find(ref: NodeRef, key) -> Node:
    if not ref:
        raise KeyError(f'Key not found: {key}')
    node = ref.node
    if node.key == key:
        return ref.node
    elif key < node.key:
        return find(node.left_ref, key)
    else:  # key > node.key
        return find(node.right_ref, key)


def insert(tree: BinaryTree, ref: NodeRef, key, value) -> NodeRef:
    if not ref:
        node = tree.create_node(key, value)
        return NodeRef(key=key,)
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
