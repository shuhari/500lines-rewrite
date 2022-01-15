class Dagoba:
    """Dagoba - in-memory graph database"""

    def __init__(self, nodes=None, edges=None):
        self._nodes = []
        self._nodes_by_id = {}
        self._edges = []
        self._next_id = 1
        for node in (nodes or []):
            self.add_node(node)
        for edge in (edges or []):
            self.add_edge(edge)

    def add_node(self, node):
        node = node.copy()
        pk = node.get('_id', None)
        if pk in self._nodes_by_id:
            raise ValueError(f'Node with _id={pk} already exists.')
        if not pk:
            pk = self._next_id
            node['_id'] = pk
            self._next_id += 1
        self._nodes.append(node)
        self._nodes_by_id[pk] = node
        return pk

    def add_edge(self, edge):
        from_id = edge.get('_from', None)
        to_id = edge.get('_to', None)
        try:
            from_node = self.node(from_id)
            to_node = self.node(to_id)
            self._edges.append(edge.copy())
        except KeyError:
            raise ValueError(f'Invalid edge: node(_id={from_id}/{to_id}) not exists.')

    def nodes(self):
        """Iterate copy of each nodes"""
        return (x.copy() for x in self._nodes)

    def edges(self):
        """Iterate copy of each edge"""
        return (x.copy() for x in self._edges)

    def node(self, pk: int):
        """Get node by primary key, raise KeyError if not found"""
        return self._nodes_by_id[pk]

    @classmethod
    def pk(cls, node):
        """Get primary key of node"""
        return node['_id']

    def from_node(self, edge):
        return self.node(edge['_from'])

    def to_node(self, edge):
        return self.node(edge['_to'])

    def query(self, eager=False):
        return EagerQuery(self) if eager else LazyQuery(self)

    @classmethod
    def is_edge(cls, edge, side, pk: int, type_=None):
        if edge[side] != pk:
            return False
        if type_ and edge.get('_type') != type_:
            return False
        return True

    def outcome(self, pk: int, type_=None):
        return [self.to_node(x) for x in self.edges()
                if Dagoba.is_edge(x, '_from', pk, type_)]

    def income(self, pk: int, type_=None):
        return [self.from_node(x) for x in self.edges()
                if Dagoba.is_edge(x, '_to', pk, type_)]


class EagerQuery:
    def __init__(self, db):
        self._db = db
        self._result = None

    def run(self):
        return self._result

    def node(self, pk: int):
        try:
            self._result = [self._db.node(pk)]
        except KeyError:
            self._result = []
        return self

    def outcome(self, type_=None):
        result = []
        for node in self._result:
            pk = Dagoba.pk(node)
            result.extend(self._db.outcome(pk, type_))
        self._result = result
        return self

    def income(self, type_=None):
        result = []
        for node in self._result:
            pk = Dagoba.pk(node)
            result.extend(self._db.income(pk, type_))
        self._result = result
        return self

    def unique(self):
        d = {}
        for node in self._result:
            pk = Dagoba.pk(node)
            d.setdefault(pk, node)
        self._result = list(d.values())
        return self


class LazyQuery:
    def __init__(self, db):
        self._db = db
