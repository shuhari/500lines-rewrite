import os
import shutil
import sys

from .core import BuildContext, Task


class Project:
    """Mange build process."""

    def __init__(self, base_dir):
        self.ctx = BuildContext(base_dir)
        self.supported_targets = ('build', 'clean', 'rebuild')
        self.verbose = ('--verbose' in sys.argv)

    def usage(self):
        """Show usage"""
        entry = sys.argv[0]
        print('Usage:')
        for target_name in self.supported_targets:
            method = getattr(self, target_name)
            name, doc = method.__name__, method.__doc__
            print(f'  {entry} {name} - {doc}')
        print('Options:')
        print('  --verbose: Show verbose output')

    def run(self, target_name):
        """Run specified target"""
        assert target_name in self.supported_targets, f'Unsupported target: {target_name}'
        method = getattr(self, target_name)
        method()

    def build(self):
        """Build project"""
        self.ctx.run_task(None, Scan())
        self.ctx.run_tasks(self.ctx.compile_tasks)
        self.ctx.run_tasks(self.ctx.link_tasks)
        if self.verbose:
            for task in self.ctx.executed_tasks:
                print(f'  executed task: {task}')

    def clean(self):
        """Clean intermedate files"""
        shutil.rmtree(self.ctx.build_dir, ignore_errors=True)
        shutil.rmtree(self.ctx.cache_dir, ignore_errors=True)
        print('Cleaned up.')

    def rebuild(self):
        """Force rebuild"""
        self.clean()
        self.build()


class Scan(Task):
    def __str__(self):
        return 'scan'

    def run(self):
        for filename in os.listdir(self.ctx.src_dir):
            if filename.endswith('.rst'):
                self.ctx.add_compile_task(Parse(filename))
                self.ctx.add_link_task(Link(filename))


class Parse(Task):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return f'parse({self.filename})'

    def run(self):
        self.ctx.add_compile_task(Transform(self.filename))


class Transform(Task):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return f'transform({self.filename})'

    def run(self):
        self.ctx.add_compile_task(WriteTpl(self.filename))
        self.ctx.add_compile_task(WriteTitle(self.filename))
        self.ctx.add_compile_task(WriteTocTree(self.filename))


class WriteTpl(Task):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return f'write_tpl({self.filename})'

    def run(self):
        pass


class WriteTitle(Task):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return f'write_title({self.filename})'

    def run(self):
        pass


class WriteTocTree(Task):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return f'write_toctree({self.filename})'

    def run(self):
        pass


class Link(Task):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return f'link({self.filename})'

    def run(self):
        pass
