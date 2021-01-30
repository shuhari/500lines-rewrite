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

    def exec_task(self, task_list, task):
        """Run a single task, record as executed, and remove from task list"""
        task.exec(self)
        if task_list:
            task_list.remove(task)
        self.executed_tasks.append(task)

    def exec_tasks(self, task_list):
        """execute all until no task pending"""
        while task_list:
            for task in task_list[:]:
                self.exec_task(task_list, task)


class Task:
    """Abstract base class of task"""
    def exec(self, ctx: BuildContext):
        self.ctx = ctx
        self.run()

    def run(self):
        raise NotImplementedError()


class AstNode:
    """node of ast model"""
    def __init__(self, name, data=None):
        self.name = name
        self.data = data
        self.children = None

    def append_child(self, child):
        self.children = self.children or []
        self.children.append(child)

    def ast_string(self, depth: int):
        """Show content with indent for debug"""
        indent = ' ' * (depth * 2)
        result = f'{indent}{self.name}'
        if self.data:
            result += f'({self.data})'
        return result

    def iter(self, depth: int):
        """Iterate all nodes recursively"""
        yield depth, self
        for child in self.children or []:
            for descendant in child.iter(depth + 1):
                yield descendant


class AstDoc(AstNode):
    """root document of ast model"""
    def __init__(self, data):
        super().__init__('doc', data)

    def dump_ast(self):
        """for debug"""
        return '\n'.join([item.ast_string(depth)
                          for depth, item in self.iter(depth=0)])
