import os
from unittest import TestCase

from ..core import CacheFile


class CacheFileTest(TestCase):
    def test_load_save(self):
        file_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../docs/cache/test.cache'))
        save_file = CacheFile(file_path)

        dependencies = set([('doc', 'install')])
        save_file.set_output('install', dependencies)
        save_file.set_input('doc', 'install', ['1', '2'])
        save_file.save()

        load_file = CacheFile(file_path)
        self.assertEqual(dependencies, load_file.get_output('install'))
        self.assertEqual(['1', '2'], load_file.get_input('doc', 'install'))

