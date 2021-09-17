from . import reader
from .utils import shape


class Plan:
    """Calculate makespan and times based on batch & perm"""
    def __init__(self, batch, perm):
        self.batch = batch
        self.perm = perm
        self._times = None
        self._makespan = None

    def makespan(self):
        self.calc()
        return self._makespan

    def get_task_time(self, i, j):
        return self.batch[i][self.perm[j]]

    def get_end_time(self, i, j):
        return self._times[i][j] + self.get_task_time(i, j)

    def calc(self):
        """Calculate array of task times and makespan"""
        if self._makespan is not None:
            return
        num_machines, num_tasks = shape(self.batch)

        def get_time(row, col):
            if row < 0 or col < 0:
                return 0
            return self._times[row][col] + self.get_task_time(row, col)

        self._times = [([0] * num_tasks) for _ in range(num_machines)]
        for i in range(num_machines):
            for j in range(num_tasks):
                self._times[i][j] = max(get_time(i - 1, j), get_time(i, j - 1))
        self._makespan = self.get_end_time(num_machines - 1, num_tasks - 1)

    def machine_stats(self):
        self.calc()
        num_machines, num_tasks = shape(self.batch)
        for i in range(num_machines):
            start_time = self._times[i][0]
            end_time = self.get_end_time(i, num_tasks - 1)
            idle_time = (end_time - start_time) - sum([self.get_task_time(i, j) for j in range(num_tasks)])
            yield i, start_time, end_time, idle_time

    def job_stats(self):
        self.calc()
        num_machines, num_tasks = shape(self.batch)
        for i in range(num_tasks):
            task_idx = self.perm.index(i)
            start_time = self._times[0][task_idx]
            end_time = self.get_end_time(num_machines - 1, task_idx)
            idle_time = (end_time - start_time) - sum(self.get_task_time(j, task_idx) for j in range(num_machines))
            yield i, start_time, end_time, idle_time

    def dump(self):
        """Dump plan result"""

        def print_row(col0, col1, col2, col3):
            row = '%15s%15s%15s%15s' % (str(col0), str(col1), str(col2), str(col3))
            print(row)

        perm_data = ', '.join([str(x + 1) for x in self.perm])
        print(f'Permutation: [{perm_data}]')
        print()
        print(f'Makespan: {self.makespan()}')
        print()

        print_row('Machine', 'Start Time', 'Finish Time', 'Idle Time')
        for mach_idx, start_time, end_time, idle_time in self.machine_stats():
            print_row(mach_idx + 1, start_time, end_time, idle_time)
        print()

        print_row('Job', 'Start Time', 'Finish Time', 'Idle Time')
        for task_idx, start_time, end_time, idle_time in self.job_stats():
            print_row(task_idx + 1, start_time, end_time, idle_time)


def main():
    batch = reader.read_sample_batch()
    perm = [14, 16, 13, 8, 7, 10, 12, 4, 2, 0, 18, 6, 15, 5, 17, 1, 3, 9, 19, 11]
    plan = Plan(batch, perm)
    plan.dump()


if __name__ == '__main__':
    main()
