from unittest import TestCase

from ..dagoba import Dagoba


class EagerQueryTest(TestCase):
    nodes = [
        {'_id': 1, 'name': 'Fred'},
        {'_id': 2, 'name': 'Bob'},
        {'_id': 3, 'name': 'Tom'},
        {'_id': 4, 'name': 'Dick'},
        {'_id': 5, 'name': 'Harry'},
        {'_id': 6, 'name': 'Lucy'},
    ]
    edges = [
        {'_from': 1, '_to': 2, '_type': 'son'},
        {'_from': 2, '_to': 3, '_type': 'son'},
        {'_from': 2, '_to': 4, '_type': 'son'},
        {'_from': 2, '_to': 5, '_type': 'son'},
        {'_from': 2, '_to': 6, '_type': 'daughter'},
        {'_from': 3, '_to': 4, '_type': 'brother', '_backward': 'brother'},
        {'_from': 4, '_to': 5, '_type': 'brother', '_backward': 'brother'},
        {'_from': 5, '_to': 3, '_type': 'brother', '_backward': 'brother'},
        {'_from': 3, '_to': 6, '_type': 'sister', '_backward': 'brother'},
        {'_from': 4, '_to': 6, '_type': 'sister', '_backward': 'brother'},
        {'_from': 5, '_to': 6, '_type': 'sister', '_backward': 'brother'},
    ]

    def setUp(self):
        self.db = Dagoba(self.nodes, self.edges)
        self.q = self.db.query(eager=True)

    def assert_nodes(self, nodes, pks):
        ids = set([Dagoba.pk(x) for x in nodes])
        self.assertEqual(ids, set(pks))

    def test_grandkids(self):
        nodes = self.q.node(1).outcome().outcome().run()
        self.assert_nodes(nodes, [3, 4, 5, 6])

    def test_sons_father(self):
        nodes = self.q.node(1).outcome().income().outcome().run()
        self.assert_nodes(nodes, [2])

    def test_granddaughters(self):
        nodes = self.q.node(1).outcome().outcome(type_='daughter').run()
        self.assert_nodes(nodes, [6])

    def test_toms_sisters(self):
        nodes = self.q.node(3).outcome('sister').run()
        self.assert_nodes(nodes, [6])

    def test_toms_brothers_grandfater(self):
        nodes = self.q.node(3).outcome().income('son').income('son').run()
        self.assert_nodes(nodes, [1])

    def test_grandfater_unique(self):
        nodes = self.q.node(3).outcome().income('son').income('son').unique().run()
        self.assertEqual(1, len(nodes))
        self.assertEqual(1, Dagoba.pk(nodes[0]))
