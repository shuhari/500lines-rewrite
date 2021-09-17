from unittest import TestCase

from ..plan import Plan
from .. import reader


class PlanTest(TestCase):
    def test_makespan(self):
        batch = reader.read_sample_batch()
        perm = [14, 16, 13, 8, 7, 10, 12, 4, 2, 0, 18, 6, 15, 5, 17, 1, 3, 9, 19, 11]
        plan = Plan(batch, perm)
        self.assertEqual(1294, plan.makespan())
