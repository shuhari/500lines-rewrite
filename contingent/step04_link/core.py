import os
import pickle

from .utils import find_first


class BuildContext:
    """Manage build process"""
    def __init__(self, base_dir, cache_name=None):
        self.src_dir = os.path.join(base_dir, 'src')
        self.cache_dir = os.path.join(base_dir, 'cache')
        self.build_dir = os.path.join(base_dir, 'build')
        self.compile_tasks = []
        self.link_tasks = []
        self.executed_tasks = []
        cache_name = cache_name or 'compile.cache'
        self.cache = CacheFile(os.path.join(self.cache_dir, cache_name))

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

    def get_doc(self, name):
        return self.cache.get_input('doc', name)

    def get_title(self, name):
        return self.cache.get_input('title', name)

    def get_toctree(self, name):
        return self.cache.get_input('toctree', name)


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

    def header_level(self) -> int:
        if self.name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            return int(self.name[1:])
        return 0

    def slug(self):
        return self.data.lower() \
            .replace(' ', '_') \
            .replace(',', '')


class AstDoc(AstNode):
    """root document of ast model"""
    def __init__(self, data):
        super().__init__('doc', data)

    def dump_ast(self):
        return '\n'.join([item.ast_string(depth)
                          for depth, item in self.iter(depth=0)])

    def title(self):
        """get document title"""
        h1 = find_first(self.iter(0), lambda x: x[1].name == 'h1')
        return h1[1].data if h1 else 'Untitled'

    def headers(self):
        """header nodes"""
        return [node for depth, node in self.iter(0) if node.header_level() > 0]


class Code:
    """Code model"""
    def __init__(self):
        self.name = None
        self.title = None
        self.html = []
        self.toctree = []
        self.dependencies = set()

    def add_toctree(self, *args):
        self.toctree.extend(args)

    def add_html(self, *args):
        self.html.extend(args)

    def html_name(self):
        return f'{self.name}.html'

    def add_dependency(self, kind, name):
        self.dependencies.add((kind, name))


class CacheFile:
    def __init__(self, path):
        self.path = path
        self._data = {
            'output': {},
            'input': {}
        }
        if os.path.exists(path):
            self.load()

    def load(self):
        with open(self.path, 'rb') as f:
            self._data = pickle.load(f)

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'wb') as f:
            pickle.dump(self._data, f)

    def set_output(self, name, value):
        self._data['output'][name] = value

    def get_output(self, name):
        return self._data['output'][name]

    def set_input(self, kind, name, data):
        key = (kind, name)
        self._data['input'][key] = data

    def get_input(self, kind, name):
        key = (kind, name)
        return self._data['input'][key]
