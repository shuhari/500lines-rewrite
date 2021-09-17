from . import reader
from .problem import Problem


def main():
    batch = reader.read_sample_batch()
    problem = Problem(batch, time_limit=300)
    plan = problem.solve()
    problem.dump(plan)


if __name__ == '__main__':
    main()
