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

        self.usage = 0
        self.improvements = 0
        self.time_spent = 0
        self.weight = 1

    def update_usage(self, time_spent, improvements):
        self.usage += 1
        self.time_spent += time_spent
        self.improvements += improvements


class StrategyList(UserList):
    def __init__(self, initList = None):
        if initList is None:
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
            initList = [Strategy('%s / %s' % (fname, cname), f, c)
                          for fname, f in finders
                          for cname, c in choosers]
        super().__init__(initList)

    def update_stats(self):
        strategies = self.copy()
        strategies.sort(key=lambda x: x.improvements, reverse=True)
        for index, s in enumerate(strategies):
            if s.time_spent > 0:
                s.weight += len(strategies) - index
            else:
                s.weight += len(strategies)
            s.improvements = 0
            s.time_spent = 0

    def pick(self):
        strategies = self.copy()
        strategies.sort(key=lambda x: x.weight, reverse=True)
        subset_size = int(len(strategies) / 3)
        subset = strategies[:subset_size]
        return random.choice(subset)

