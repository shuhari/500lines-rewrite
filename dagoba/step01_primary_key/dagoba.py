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

    def pk(self, node):
        """Get primary key of node"""
        return node['_id']
