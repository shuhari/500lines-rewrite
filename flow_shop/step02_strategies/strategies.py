import random
from collections import UserList
from functools import partial

from .algorithms import find_neighbors as fn
from .algorithms import choose_neighbor as cn


class Strategy:
    def __init__(self, name, finder, chooser):
        self.name = name
        self.finder = finder
        self.chooser = chooser


class StrategyList(UserList):
    def __init__(self):
        finders = [
            ('Random Permutation', partial(fn.rand, num=100)),
        ]
        choosers = [
            ('Random Selection', cn.rand),
        ]
        strategies = [Strategy('%s / %s' % (fname, cname), f, c)
                      for fname, f in finders
                      for cname, c in choosers]
        super().__init__(strategies)

    def pick(self):
        return random.choice(self)
