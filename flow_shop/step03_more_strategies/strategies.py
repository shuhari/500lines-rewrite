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
            ('Swapped Pairs', fn.swap),
            ('Large Neighbourhood Search (3)', partial(fn.lns, size=3)),
            ('Idle Neighbourhood(3)', partial(fn.idle, size=3)),
            ('Idle Neighbourhood(4)', partial(fn.idle, size=4)),
            ('Idle Neighbourhood(5)', partial(fn.idle, size=5)),
        ]
        choosers = [
            ('Random Selection', cn.rand),
            ('Hill Climbing', cn.hillclimbing),
            ('Biased Random Selection', cn.random_hillclimbing),
        ]
        strategies = [Strategy('%s / %s' % (fname, cname), f, c)
                      for fname, f in finders
                      for cname, c in choosers]
        super().__init__(strategies)

    def pick(self):
        return random.choice(self)
