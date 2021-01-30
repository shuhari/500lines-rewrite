import os
import shutil
import sys


class Project:
    """Manage command line interface of project."""

    def __init__(self, base_dir):
        self.src_dir = os.path.join(base_dir, 'src')
        self.cache_dir = os.path.join(base_dir, 'cache')
        self.build_dir = os.path.join(base_dir, 'build')
        self.targets = ('build', 'clean', 'rebuild')

    def usage(self):
        """Show usage"""
        entry = os.path.basename(sys.argv[0])
        print('Usage:')
        for target in self.targets:
            method = getattr(self, target)
            name, doc = method.__name__, method.__doc__
            print(f'  {entry} {name} - {doc}')

    def run(self, target):
        """Run specified target"""
        assert target in self.targets, f'Unsupported target: {target}'
        method = getattr(self, target)
        method()

    def build(self):
        """Build project"""
        print('build')

    def clean(self):
        """Clean intermediate files"""
        shutil.rmtree(self.build_dir, ignore_errors=True)
        shutil.rmtree(self.cache_dir, ignore_errors=True)
        print('Cleaned up.')

    def rebuild(self):
        """Force rebuild"""
        self.clean()
        self.build()
