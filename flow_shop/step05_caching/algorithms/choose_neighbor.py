import random


def rand(ctx, plan, candidates):
    """Random choose one"""
    return random.choice(candidates)


def hillclimbing(ctx, plan, candidates):
    """Choose which has best makepsan"""
    plans = [ctx.cache[x] for x in candidates]
    plans.sort(key=lambda x: x.makespan())
    return plans[0].perm


def random_hillclimbing(ctx, plan, candidates):
    plans = [ctx.cache[x] for x in candidates]
    plans.sort(key=lambda x: x.makespan())
    subset_size = int(len(plans) / 2)
    subset = plans[:subset_size]
    return random.choice(subset).perm
