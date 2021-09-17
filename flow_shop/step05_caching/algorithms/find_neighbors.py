import random
from itertools import combinations, permutations

from .. import params


def rand(ctx, plan, num=1):
    """Shuffle to generate new perm"""
    def shuffle_tasks():
        perm = plan.perm[:]
        random.shuffle(perm)
        return perm
    return [shuffle_tasks() for _ in range(num)]


def swap(ctx, plan):
    """Swap two jobs"""
    def swap_index(i, j):
        perm = plan.perm[:]
        perm[i], perm[j] = perm[j], perm[i]
        return perm
    indexes = range(len(plan.perm))
    return [swap_index(i, j) for i, j in combinations(indexes, 2)]


def lns(ctx, plan, size=3):
    candidates = []
    indexes = range(len(plan.perm))
    neighbors = list(combinations(indexes, size))
    random.shuffle(neighbors)
    best_plan = plan
    for subset in neighbors[:params.MAX_LNS_NEIGHBORS]:
        for ordering in permutations(subset):
            if ordering == subset:
                continue
            perm = plan.perm[:]
            for i in range(len(ordering)):
                perm[subset[i]] = plan.perm[ordering[i]]
            curr_plan = ctx.cache[perm]
            if curr_plan.makespan() < best_plan.makespan():
                best_plan = curr_plan
        candidates.append(best_plan.perm)
    return candidates


def idle(ctx, plan, size=2):
    candidates = []
    stats = list(plan.job_stats())
    stats.sort(key=lambda x: x[3], reverse=True)
    subset = [x[0] for x in stats[:size]]
    for ordering in permutations(subset):
        if ordering == subset:
            continue
        perm = plan.perm[:]
        for i in range(len(ordering)):
            perm[subset[i]] = plan.perm[ordering[i]]
            candidates.append(perm)
    return candidates
