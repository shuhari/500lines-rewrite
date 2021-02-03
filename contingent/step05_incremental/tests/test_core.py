import time
from unittest import TestCase

from ..core import CacheFile
from ..utils import relative_of


class CacheFileTest(TestCase):
    def setUp(self):
        self.path = relative_of(__file__, '../../docs/cache/test.cache')
        self.file = CacheFile(self.path)
        self.file.purge()

    def test_load_save(self):
        dependencies = set([('doc', 'install')])
        self.file.set_dependencies('install', dependencies)
        self.file.set_code('doc', 'install', ['1', '2'])
        self.file.save()

        load_file = CacheFile(self.path)
        self.assertEqual(dependencies, load_file.get_dependencies('install'))
        self.assertEqual(['1', '2'], load_file.get_code('doc', 'install'))

    def test_set_twice_timestamp_updated(self):
        self.file.set_code('doc', 'install', ['1', '2'])
        self.file.save()
        timestamp1 = self.file.get_code_timestamp('doc', 'install')
        time.sleep(0.1)

        self.file.set_code('doc', 'install', ['1', '2', '3'])
        self.file.save()
        timestamp2 = self.file.get_code_timestamp('doc', 'install')
        self.assertTrue(timestamp2 > timestamp1)

    def test_set_same_content_stamp_unchange(self):
        self.file.set_code('doc', 'install', ['1', '2'])
        self.file.save()
        timestamp1 = self.file.get_code_timestamp('doc', 'install')
        time.sleep(0.1)

        self.file.set_code('doc', 'install', ['1', '2'])
        self.file.save()
        timestamp2 = self.file.get_code_timestamp('doc', 'install')
        self.assertEqual(timestamp1, timestamp2)
