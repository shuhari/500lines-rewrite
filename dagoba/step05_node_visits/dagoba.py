def copy_dict(src: dict, *excludes) -> dict:
    return {k: v for k, v in src.items() if k not in excludes}


class Dagoba:
    """Dagoba - in-memory graph database"""
    def __init__(self, nodes=None, edges=None):
        self._nodes = []
        self._nodes_by_id = {}
        self._edges = []
        self._next_id = 1
        self._node_visits = 0
        for node in (nodes or []):
            self.add_node(node)
        for edge in (edges or []):
            self.add_edge(edge)

    def node_visits(self) -> int:
        return self._node_visits

    def reset_visits(self):
        self._node_visits = 0

    def add_node(self, node):
        node = node.copy()
        pk = node.get('_id', None)
        if pk in self._nodes_by_id:
            raise ValueError(f'Node with _id={pk} already exists.')
        if not pk:
            pk = self._next_id
            node['_id'] = pk
            self._next_id += 1
        node['_out'] = []
        node['_in'] = []
        self._nodes.append(node)
        self._nodes_by_id[pk] = node
        return pk

    def add_edge(self, edge):
        from_id = edge.get('_from', None)
        to_id = edge.get('_to', None)
        try:
            from_node = self.node(from_id)
            to_node = self.node(to_id)
            forward = copy_dict(edge, '_backward')
            self._edges.append(forward)
            from_node['_out'].append(forward)
            to_node['_in'].append(forward)

            if '_backward' in edge.keys():
                backward = copy_dict(edge, '_backward')
                backward['_type'] = edge['_backward']
                backward['_from'] = edge['_to']
                backward['_to'] = edge['_from']
                self._edges.append(backward)
                from_node['_in'].append(backward)
                to_node['_out'].append(backward)
        except KeyError:
            raise ValueError(f'Invalid edge: node(_id={from_id}/{to_id}) not exists.')

    def nodes(self):
        """Iterate copy of each nodes"""
        return (x.copy() for x in self._nodes)

    def edges(self):
        """Iterate copy of each edge"""
        return (x.copy() for x in self._edges)

    def node(self, pk: int, visit=False):
        """Get node by primary key, raise KeyError if not found"""
        if visit:
            self._node_visits += 1
        return self._nodes_by_id[pk]

    @classmethod
    def pk(cls, node):
        """Get primary key of node"""
        return node['_id']

    def from_node(self, edge):
        return self.node(edge['_from'], visit=True)

    def to_node(self, edge):
        return self.node(edge['_to'], visit=True)

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
        node = self.node(pk, visit=True)
        return (self.to_node(x) for x in node['_out']
                if Dagoba.is_edge(x, '_from', pk, type_))

    def income(self, pk: int, type_=None):
        node = self.node(pk, visit=True)
        return (self.from_node(x) for x in node['_in']
                if Dagoba.is_edge(x, '_to', pk, type_))


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

    def take(self, count: int):
        self._result = self._result[:count]
        return self


class LazyQuery:
    def __init__(self, db):
        self._db = db
        self._pipeline = []

    def node(self, pk: int):
        def func(arg):
            try:
                result = self._db.node(pk)
                return [result]
            except KeyError:
                return []
        self._pipeline.append(func)
        return self

    def outcome(self, type_=None):
        def func(arg):
            for node in arg:
                pk = Dagoba.pk(node)
                for target_node in self._db.outcome(pk, type_):
                    yield target_node
        self._pipeline.append(func)
        return self

    def income(self, type_=None):
        def func(arg):
            for node in arg:
                pk = Dagoba.pk(node)
                for target_node in self._db.income(pk, type_):
                    yield target_node
        self._pipeline.append(func)
        return self

    def unique(self):
        def func(arg):
            dic = {Dagoba.pk(x): x for x in arg}
            for pk in dic.keys():
                yield dic[pk]
        self._pipeline.append(func)
        return self

    def take(self, count: int):
        def func(arg):
            return [next(arg) for i in range(count)]
        self._pipeline.append(func)
        return self

    def run(self):
        input_, output_ = None, None
        for step in self._pipeline:
            output_ = step(input_)
            input_ = output_
        return list(output_)
