from functools import partial
from unittest import TestCase

from .. import reader
from ..plan import Plan
from ..algorithms import find_neighbors as finders
from ..algorithms import choose_neighbor as choosers


def create_test_plan():
    batch = reader.read_sample_batch()
    perm = [14, 16, 13, 8, 7, 10, 12, 4, 2, 0, 18, 6, 15, 5, 17, 1, 3, 9, 19, 11]
    plan = Plan(batch, perm)
    return plan


class FindNeighborsTest(TestCase):
    def setUp(self):
        self.plan = create_test_plan()

    def _test_finder(self, fn):
        candidates = fn(self.plan)
        for perm in candidates:
            self.assertEqual(len(perm), len(self.plan.perm))

    def test_rand(self):
        fn = partial(finders.rand, num=100)
        self._test_finder(fn)

    def test_swap(self):
        fn = finders.swap
        self._test_finder(fn)

    def test_lns(self):
        fn = partial(finders.lns, size=3)
        self._test_finder(fn)

    def test_idle(self):
        fn = partial(finders.idle, size=2)
        self._test_finder(fn)


class ChooseNeighborTest(TestCase):
    def setUp(self):
        self.plan = create_test_plan()
        self.candidates = finders.rand(self.plan, num=100)

    def _test_chooser(self, fn):
        perm = fn(self.plan, self.candidates)
        self.assertIsNotNone(perm)
        self.assertEqual(len(perm), len(self.plan.perm))

    def test_rand(self):
        fn = choosers.rand
        self._test_chooser(fn)

    def test_hillclimbing(self):
        fn = choosers.hillclimbing
        self._test_chooser(fn)

    def test_random_hillclimbing(self):
        fn = choosers.random_hillclimbing
        self._test_chooser(fn)
