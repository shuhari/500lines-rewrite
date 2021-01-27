import os


class BuildContext:
    """Manage build process"""
    def __init__(self, base_dir):
        self.src_dir = os.path.join(base_dir, 'src')
        self.cache_dir = os.path.join(base_dir, 'cache')
        self.build_dir = os.path.join(base_dir, 'build')
        self.compile_tasks = []
        self.link_tasks = []
        self.executed_tasks = []

    def add_compile_task(self, task):
        self.compile_tasks.append(task)

    def add_link_task(self, task):
        self.link_tasks.append(task)

    def run_task(self, task_list, task):
        task.exec(self)
        if task_list:
            task_list.remove(task)
        self.executed_tasks.append(task)

    def run_tasks(self, task_list):
        while task_list:
            for task in task_list[:]:
                self.run_task(task_list, task)


class Task:
    """Abstract task base class"""
    def exec(self, ctx: BuildContext):
        self.ctx = ctx
        self.run()

    def run(self):
        raise NotImplementedError()
