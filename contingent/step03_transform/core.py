import os
import pickle

from .utils import find_first


class BuildContext:
    """Manage build process"""
    def __init__(self, base_dir):
        self.src_dir = os.path.join(base_dir, 'src')
        self.cache_dir = os.path.join(base_dir, 'cache')
        self.build_dir = os.path.join(base_dir, 'build')
        self.compile_tasks = []
        self.link_tasks = []
        self.executed_tasks = []
        self.cache = CacheFile(os.path.join(self.cache_dir, 'compile.cache'))

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

    def header_level(self) -> int:
        """return 1~6 for h1~h6, 0 otherwise"""
        if self.name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            return int(self.name[1:])
        return 0

    def slug(self):
        """generate reference name of node"""
        return self.data.lower() \
            .replace(' ', '_') \
            .replace(',', '')


class AstDoc(AstNode):
    """root document of ast model"""
    def __init__(self, data):
        super().__init__('doc', data)

    def dump_ast(self):
        """for debug"""
        return '\n'.join([item.ast_string(depth)
                          for depth, item in self.iter(depth=0)])

    def title(self):
        """get document title"""
        h1 = find_first(self.iter(0), lambda x: x[1].name == 'h1')
        return h1[1].data if h1 else 'Untitled'

    def headers(self):
        """iterate header nodes"""
        return [node for depth, node in self.iter(0) if node.header_level() > 0]


class CacheFile:
    """Save code data to cache for later reference"""
    def __init__(self, path):
        self.path = path
        self._data = {
            'dependencies': {},
            'code': {}
        }
        if os.path.exists(path):
            self.load()

    def purge(self):
        if os.path.exists(self.path):
            os.unlink(self.path)
        self._data = {
            'dependencies': {},
            'code': {}
        }

    def load(self):
        """Load from file"""
        with open(self.path, 'rb') as f:
            self._data = pickle.load(f)

    def save(self):
        """Save to file"""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'wb') as f:
            pickle.dump(self._data, f)

    def set_dependencies(self, name, value):
        self._data['dependencies'][name] = value

    def get_dependencies(self, name):
        return self._data['dependencies'][name]

    def set_code(self, kind, name, data):
        key = (kind, name)
        self._data['code'][key] = data

    def get_code(self, kind, name):
        key = (kind, name)
        return self._data['code'][key]


class Code:
    """Code model"""
    def __init__(self, name):
        self.name = name
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

    def write_cache(self, cache: CacheFile):
        cache.set_dependencies(self.name, self.dependencies)
        cache.set_code('doc', self.name, self.html)
        cache.set_code('title', self.name, self.title)
        cache.set_code('toctree', self.name, self.toctree)


