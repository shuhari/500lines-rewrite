import os
import shutil
import sys


class Project:
    """Mange build process."""

    def __init__(self, base_dir):
        self.src_dir = os.path.join(base_dir, 'src')
        self.cache_dir = os.path.join(base_dir, 'cache')
        self.build_dir = os.path.join(base_dir, 'build')
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
        print('build')

    def clean(self):
        """Clean intermedate files"""
        shutil.rmtree(self.build_dir, ignore_errors=True)
        shutil.rmtree(self.cache_dir, ignore_errors=True)
        print('Cleaned up.')

    def rebuild(self):
        """Force rebuild"""
        self.clean()
        self.build()
