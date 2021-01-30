import os
import shutil
import sys

from .core import BuildContext, Task, AstDoc, Code
from .parser import parse_file
from .transformer import transform
from .linker import link


class Project:
    """Mange build process."""

    def __init__(self, base_dir):
        self.ctx = BuildContext(base_dir)
        self.supported_targets = ('build', 'clean', 'rebuild')
        self.verbose = ('--verbose' in sys.argv)

    def usage(self):
        """Show usage"""
        entry = os.path.basename(sys.argv[0])
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

    def is_outdated(self) -> bool:
        name = os.path.splitext(self.filename)[0]
        _, output_timestamp = self.ctx.cache.get_output(name)
        input_timestamp = self.ctx.get_src_timestamp(self.filename)
        return self.is_outdated_timestamp(input_timestamp, output_timestamp)

    def run(self):
        full_path = os.path.join(self.ctx.src_dir, self.filename)
        ast = parse_file(full_path)
        self.ctx.add_compile_task(Transform(ast))


class Transform(Task):
    def __init__(self, ast: AstDoc):
        self.ast = ast

    def __str__(self):
        return f'transform({self.ast.name})'

    def run(self):
        code = transform(self.ast)
        self.ctx.add_compile_task(WriteCache(code))


class WriteCache(Task):
    def __init__(self, code: Code):
        self.code = code

    def __str__(self):
        return f'write_tpl({self.code.name})'

    def run(self):
        self.code.write_cache(self.ctx.cache)
        self.ctx.cache.save()


class Link(Task):
    def __init__(self, filename):
        self.name = os.path.splitext(filename)[0]

    def __str__(self):
        return f'link({self.name})'

    def is_outdated(self) -> bool:
        output_timestamp = self.ctx.get_build_timestamp(self.name + '.html')
        output, _ = self.ctx.cache.get_output(self.name)
        for kind, name in output:
            _, timestamp = self.ctx.cache.get_input(kind, name)
            if self.is_outdated_timestamp(timestamp, output_timestamp):
                return True
        return False

    def run(self):
        lines = link(self.ctx, self.name)
        lines = [x + '\n' for x in lines]
        html_name = os.path.join(self.ctx.build_dir, self.name + '.html')
        os.makedirs(os.path.dirname(html_name), exist_ok=True)
        with open(html_name, 'w') as f:
            f.writelines([x + '\n' for x in lines])
        print(f'written {os.path.basename(html_name)}')
