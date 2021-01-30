from unittest import TestCase

from ..core import CacheFile
from ..utils import relative_of


class CacheFileTest(TestCase):
    def test_load_save(self):
        file_path = relative_of(__file__, '../../docs/cache/test.cache')
        save_file = CacheFile(file_path)
        save_file.purge()

        dependencies = set([('doc', 'install')])
        save_file.set_dependencies('install', dependencies)
        save_file.set_code('doc', 'install', ['1', '2'])
        save_file.save()

        load_file = CacheFile(file_path)
        self.assertEqual(dependencies, load_file.get_dependencies('install'))
        self.assertEqual(['1', '2'], load_file.get_code('doc', 'install'))

