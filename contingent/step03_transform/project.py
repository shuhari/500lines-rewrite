import os
import shutil
import sys

from .core import BuildContext, Task, AstDoc, Code
from .parser import parse_file
from .transformer import transform


class Project:
    """Manage command line interface of project."""

    def __init__(self, base_dir):
        self.ctx = BuildContext(base_dir)
        self.targets = ('build', 'clean', 'rebuild')
        self.verbose = ('--verbose' in sys.argv)

    def usage(self):
        """Show usage"""
        entry = os.path.basename(sys.argv[0])
        print('Usage:')
        for target in self.targets:
            method = getattr(self, target)
            name, doc = method.__name__, method.__doc__
            print(f'  {entry} {name} - {doc}')
        print('Options:')
        print('  --verbose: Show verbose output')

    def run(self, target):
        """Run specified target"""
        assert target in self.targets, f'Unsupported target: {target}'
        method = getattr(self, target)
        method()

    def build(self):
        """Build project"""
        self.ctx.exec_task(None, Scan())
        self.ctx.exec_tasks(self.ctx.compile_tasks)
        self.ctx.exec_tasks(self.ctx.link_tasks)
        if self.verbose:
            for task in self.ctx.executed_tasks:
                print(f'executed task: {task}')

    def clean(self):
        """Clean intermediate files"""
        shutil.rmtree(self.ctx.build_dir, ignore_errors=True)
        shutil.rmtree(self.ctx.cache_dir, ignore_errors=True)
        print('Cleaned up.')

    def rebuild(self):
        """Force rebuild"""
        self.clean()
        self.build()


class Scan(Task):
    """Scan source directory for rst files"""
    def __str__(self):
        return 'scan'

    def run(self):
        for filename in os.listdir(self.ctx.src_dir):
            if filename.endswith('.rst'):
                self.ctx.add_compile_task(Parse(filename))
                self.ctx.add_link_task(Link(filename))


class Parse(Task):
    """Parse rst file to ast model"""
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return f'parse({self.filename})'

    def run(self):
        full_path = os.path.join(self.ctx.src_dir, self.filename)
        ast = parse_file(full_path)
        self.ctx.add_compile_task(Transform(ast))


class Transform(Task):
    """Transform ast model to code model"""
    def __init__(self, ast: AstDoc):
        self.ast = ast

    def __str__(self):
        return f'transform({self.ast.name})'

    def run(self):
        code = transform(self.ast)
        self.ctx.add_compile_task(WriteCache(code))


class WriteCache(Task):
    """Write code to cache"""
    def __init__(self, code: Code):
        self.code = code

    def __str__(self):
        return f'write_tpl({self.code.name})'

    def run(self):
        self.code.write_cache(self.ctx.cache)
        self.ctx.cache.save()


class Link(Task):
    """Execute link step to generate final output"""
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return f'link({self.filename})'

    def run(self):
        pass
