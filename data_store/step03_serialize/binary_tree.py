from abc import ABC, abstractmethod

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

    @classmethod
    def transform(cls, current, new_target):
        return current if new_target is MISSING else cls(target=new_target)

    @classmethod
    def from_addr(cls, addr: int, can_be_none: bool = True):
        if addr == ADDR_NONE:
            assert can_be_none
            return None
        return cls(addr=addr)


class ValueRef(Ref):
    pass


class NodeRef(Ref):
    pass


class NodeManager(ABC):
    @abstractmethod
    def before_load_value(self, ref: ValueRef):
        pass

    @abstractmethod
    def before_load_node(self, ref: NodeRef):
        pass


class Node:
    """Node of binary tree"""
    def __init__(self, manager: NodeManager, key, value_ref: ValueRef, left_ref: NodeRef = None, right_ref: NodeRef = None):
        assert isinstance(manager, NodeManager)
        assert isinstance(value_ref, ValueRef)
        assert left_ref is None or isinstance(left_ref, NodeRef)
        assert right_ref is None or isinstance(right_ref, NodeRef)
        self.callback = manager
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
        return Node(manager=self.callback,
                    key=self.key,
                    value_ref=ValueRef.transform(self.value_ref, value),
                    left_ref=NodeRef.transform(self.left_ref, left),
                    right_ref=NodeRef.transform(self.right_ref, right))

    @property
    def value(self):
        self.callback.before_load_value(self.value_ref)
        return self.value_ref.get()

    def get_child_node(self, ref: NodeRef):
        if ref:
            self.callback.before_load_node(ref)
            return ref.get()
        return None

    @property
    def left(self):
        return self.get_child_node(self.left_ref)

    @property
    def right(self):
        return self.get_child_node(self.right_ref)

    def serialize_ref(self, data: dict, key: str, ref: NodeRef):
        if ref:
            assert ref.is_commited()
            data[key] = ref.addr

    def serialize(self):
        assert self.value_ref.is_commited()
        data = {
            'key': self.key,
            'value_addr': self.value_ref.addr,
        }
        self.serialize_ref(data, 'left_addr', self.left_ref)
        self.serialize_ref(data, 'right_addr', self.right_ref)
        return data

    @classmethod
    def deserialize(cls, manager, data):
        value_ref = ValueRef.from_addr(data['value_addr'], can_be_none=False)
        left_ref = NodeRef.from_addr(data.get('left_addr', ADDR_NONE))
        right_ref = NodeRef.from_addr(data.get('right_addr', ADDR_NONE))
        return Node(manager=manager,
                    key=data['key'],
                    value_ref=value_ref,
                    left_ref=left_ref,
                    right_ref=right_ref)


class BinaryTree(NodeManager):
    def __init__(self, storage):
        self._root_ref = None
        self._storage = storage
        self.load_root()

    def load_root(self):
        root_addr = self._storage.root_addr
        if root_addr == ADDR_NONE:
            self._root_ref = None
        else:
            root_addr = self._storage.root_addr
            data = self._storage.read_data(root_addr)
            node = Node.deserialize(self, data)
            self._root_ref = NodeRef(addr=root_addr, target=node)

    @property
    def root_node(self):
        return self._root_ref.get() if self._root_ref else None

    @root_node.setter
    def root_node(self, value):
        if value == self.root_node:
            return
        self._root_ref = NodeRef(target=value) if value else None

    @property
    def root_addr(self):
        return self._root_ref.addr if self._root_ref else ADDR_NONE

    def get(self, key):
        node = find(self.root_node, key)
        return node.value

    def set(self, key, value):
        self.root_node = self.insert(self.root_node, key, value)

    def delete(self, key):
        self.root_node = remove(self.root_node, key)

    def before_load_value(self, ref: ValueRef):
        if not ref.is_loaded():
            assert ref.is_commited()
            ref.target = self._storage.read_data(ref.addr)

    def before_load_node(self, ref: NodeRef):
        if not ref.is_loaded():
            assert ref.is_commited()
            data = self._storage.read_data(ref.addr)
            node = Node.deserialize(self, data)
            ref.target = node

    def create_node(self, key, value):
        return Node(manager=self,
                    key=key,
                    value_ref=ValueRef(target=value))

    def commit(self):
        self.commit_node_ref(self._root_ref)
        self._storage.set_root_addr(self.root_addr)
        self._storage.flush()

    def commit_node_ref(self, ref: NodeRef):
        if not ref or ref.is_commited():
            return
        assert ref.is_loaded()
        node = ref.get()
        if node is None:
            raise ValueError('node is none')
        self.commit_value_ref(node.value_ref)
        self.commit_node_ref(node.left_ref)
        self.commit_node_ref(node.right_ref)
        ref.addr = self._storage.write_data(node.serialize())

    def commit_value_ref(self, ref: ValueRef):
        if ref.is_commited():
            return
        assert ref.is_loaded()
        ref.addr = self._storage.write_data(ref.get())

    def insert(self, node: Node, key, value) -> Node:
        if not node:
            return self.create_node(key, value)
        elif key < node.key:
            return node.transform(left=self.insert(node.left, key, value))
        elif key > node.key:
            return node.transform(right=self.insert(node.right, key, value))
        else:  # key == node.key
            if node.value == value:
                return node
            return node.transform(value=value)


def find(node, key) -> Node:
    if node is None:
        raise KeyError(f'Key not found: {key}')
    elif node.key == key:
        return node
    elif key < node.key:
        return find(node.left, key)
    else:  # key > node.key
        return find(node.right, key)


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
