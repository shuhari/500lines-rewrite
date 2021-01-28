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
        indent = ' ' * (depth * 2)
        result = f'{indent}{self.name}'
        if self.data:
            result += f'({self.data})'
        return result

    def iter(self, depth: int):
        yield depth, self
        for child in self.children or []:
            for descendant in child.iter(depth + 1):
                yield descendant


class AstDoc(AstNode):
    """root document of ast model"""
    def __init__(self, data):
        super().__init__('doc', data)

    def dump_ast(self):
        return '\n'.join([item.ast_string(depth)
                          for depth, item in self.iter(depth=0)])
