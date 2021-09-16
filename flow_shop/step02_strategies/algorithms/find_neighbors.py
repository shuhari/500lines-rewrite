import random


def rand(plan, num=1):
    def shuffle_tasks():
        perm = plan.perm[:]
        random.shuffle(perm)
        return perm
    return [shuffle_tasks() for _ in range(num)]
