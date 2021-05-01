from abc import ABC, abstractmethod

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

    def __str__(self):
        return f'{self.__class__.__name__}(addr={self.addr}, target={self.target}))'

    def get(self):
        assert self.has_value()
        return self.target

    def has_addr(self) -> bool:
        return self.addr != ADDR_NONE

    def has_value(self) -> bool:
        return self.target is not MISSING


class ValueRef(Ref):
    pass


class NodeRef(Ref):
    @classmethod
    def get_node(cls, ref):
        return ref.get() if ref else None

    @classmethod
    def from_addr(cls, addr: int):
        assert isinstance(addr, int)
        return cls(addr=addr) if addr != ADDR_NONE else None


class NodeManager(ABC):
    """"""
    @abstractmethod
    def on_load_value(self, ref: ValueRef):
        pass

    @abstractmethod
    def on_load_node(self, ref: NodeRef):
        pass


class Node:
    """Node of binary tree"""
    def __init__(self, manager: NodeManager, key, value_ref: ValueRef,
                 left_ref: NodeRef = None,
                 right_ref: NodeRef = None):
        assert isinstance(manager, NodeManager)
        assert isinstance(value_ref, ValueRef)
        assert left_ref is None or isinstance(left_ref, NodeRef)
        assert right_ref is None or isinstance(right_ref, NodeRef)
        self.manager = manager
        self.key = key
        self.value_ref = value_ref
        self.left_ref = left_ref
        self.right_ref = right_ref

    def is_leaf(self) -> bool:
        return (self.left is None) and (self.right is None)

    def transform(self, **kwargs):
        """create new node based on current"""
        return Node(manager=self.manager,
                    key=self.key,
                    value_ref=ValueRef.transform(self.value_ref, kwargs, 'value'),
                    left_ref=NodeRef.transform(self.left_ref, kwargs, 'left'),
                    right_ref=NodeRef.transform(self.right_ref, kwargs, 'right'))

    def get_child_node(self, ref: NodeRef):
        if ref:
            self.manager.on_load_node(ref)
            return ref.get()
        return None

    @property
    def value(self):
        self.manager.on_load_value(self.value_ref)
        return self.value_ref.get()

    @property
    def left(self):
        return self.get_child_node(self.left_ref)

    @property
    def right(self):
        return self.get_child_node(self.right_ref)

    @classmethod
    def create(cls, manager: NodeManager, key, value):
        return cls(manager=manager,
                   key=key,
                   value_ref=ValueRef(target=value))

    def serialize_ref(self, data, key, ref: Ref):
        if ref:
            assert ref.has_addr()
            data[key] = ref.addr

    def serialize(self):
        data = {
            'key': self.key,
        }
        self.serialize_ref(data, 'value_addr', self.value_ref)
        self.serialize_ref(data, 'left_addr', self.left_ref)
        self.serialize_ref(data, 'right_addr', self.right_ref)
        return data

    @classmethod
    def deserialize(cls, manager, data):
        key = data['key']
        value_ref = ValueRef(data['value_addr'])
        left_ref = NodeRef.from_addr(data.get('left_addr', ADDR_NONE))
        right_ref = NodeRef.from_addr(data.get('right_addr', ADDR_NONE))
        return Node(manager=manager,
                    key=key,
                    value_ref=value_ref,
                    left_ref=left_ref,
                    right_ref=right_ref)


class BinaryTree(NodeManager):
    def __init__(self, storage):
        self._storage = storage
        self._root_ref = None
        self.reload_root()

    def reload_root(self):
        self._storage.reload()
        root_addr = self._storage.root_addr
        if root_addr == ADDR_NONE:
            self._root_ref = None
        else:
            data = self._storage.read_data(root_addr)
            node = Node.deserialize(self, data)
            self._root_ref = NodeRef(addr=root_addr, target=node)

    @property
    def root_node(self):
        return NodeRef.get_node(self._root_ref)

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
        self.root_node = self._insert(self.root_node, key, value)

    def delete(self, key):
        self.root_node = remove(self.root_node, key)

    def commit(self):
        self.commit_node_ref(self._root_ref)
        self._storage.set_root_addr(self.root_addr)
        self._storage.flush()

    def commit_node_ref(self, ref: NodeRef):
        if not ref or ref.has_addr():
            return
        assert ref.has_value()
        node = ref.get()
        self.commit_value_ref(node.value_ref)
        self.commit_node_ref(node.left_ref)
        self.commit_node_ref(node.right_ref)
        ref.addr = self._storage.write_data(node.serialize())

    def commit_value_ref(self, ref: ValueRef):
        assert ref
        if ref.has_addr():
            return
        assert ref.has_value()
        ref.addr = self._storage.write_data(ref.get())

    def _insert(self, node: Node, key, value) -> Node:
        if not node:
            return Node.create(self, key, value)
        elif key < node.key:
            return node.transform(left=self._insert(node.left, key, value))
        elif key > node.key:
            return node.transform(right=self._insert(node.right, key, value))
        else:  # key == node.key
            if node.value == value:
                return node
            return node.transform(value=value)

    def on_load_value(self, ref: ValueRef):
        if ref.has_value():
            return
        assert ref.has_addr()
        ref.target = self._storage.read_data(ref.addr)

    def on_load_node(self, ref: NodeRef):
        if ref.has_value():
            return
        assert ref.has_addr()
        data = self._storage.read_data(ref.addr)
        node = Node.deserialize(self, data)
        ref.target = node


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
