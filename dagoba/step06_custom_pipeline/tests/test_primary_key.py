from unittest import TestCase

from ..dagoba import Dagoba
from . import fixtures


class PrimaryKeyTest(TestCase, fixtures.TestMixin):
    def setUp(self):
        self.db = Dagoba()
        self.pk1 = self.db.add_node({'name': 'foo'})
        self.pk2 = self.db.add_node({'name': 'bar'})
        self.db.add_edge({'_from': self.pk1, '_to': self.pk2})

    def test_nodes(self):
        self.assertTrue(self.pk1 > 0)
        self.assertIsNotNone(self.db.node(self.pk1))
        self.assertTrue(self.pk2 > 0)
        self.assertIsNotNone(self.db.node(self.pk2))
        self.assertTrue(self.pk1 != self.pk2)

    def test_edge(self):
        edge = self.get_item(self.db.edges(), _from=self.pk1, _to=self.pk2)
        self.assertIsNotNone(edge)

