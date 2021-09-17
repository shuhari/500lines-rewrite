import random
import time

from .import params
from .plan import Plan
from .strategies import StrategyList
from .utils import shape


class Problem:
    """Resolve problem"""

    def __init__(self, batch, time_limit):
        self.batch = batch
        self.time_limit = time_limit
        self.strategies = StrategyList()
        self.iteration = 0

    def solve(self):
        num_machines, num_tasks = shape(self.batch)
        init_perm = list(range(num_tasks))
        random.shuffle(init_perm)
        start_time = time.time()
        best_plan = Plan(self.batch, init_perm)

        # Use strategy to find best plan
        while time.time() - start_time < self.time_limit:
            iteration_start_time = time.time()
            strategy = self.strategies.pick()
            candidates = strategy.finder(best_plan)
            perm = strategy.chooser(best_plan, candidates)
            curr_plan = Plan(self.batch, perm)

            self.iteration += 1
            time_spent = time.time() - iteration_start_time
            improvements = best_plan.makespan() - curr_plan.makespan()
            strategy.update_usage(time_spent, improvements)

            if curr_plan.makespan() < best_plan.makespan():
                best_plan = curr_plan

            if (self.iteration % params.STEP_ITERATIONS) == 0:
                self.strategies.update_stats()
                # show progress
                percent = (time.time() - start_time) / self.time_limit
                print(f'Iteration {self.iteration}, progress {percent * 100:.1f}%, strategy: {strategy.name}...')

        return best_plan

    def dump(self, result_plan):
        print(f'Went through {self.iteration} iterations.')
        print()
        result_plan.dump()
