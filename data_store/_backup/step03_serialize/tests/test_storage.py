import os
import tempfile
from unittest import TestCase

from .. import storage


class StorageTest(TestCase):
    def setUp(self):
        self.storage = storage.memory()

    def test_init_info(self):
        self.assertEqual(storage.ADDR_NONE, self.storage.root_addr)
        self.assertEqual(storage.ADDR_FREE_START, self.storage.free_addr)

    def test_write_read_data(self):
        data = {'key': 'k', 'value_addr': 0, 'left_addr': 1, 'right_addr': 2}
        addr = self.storage.write_data(data)
        self.assertTrue(self.storage.free_addr > storage.ADDR_FREE_START)

        read_data = self.storage.read_data(addr)
        self.assertEqual(data, read_data)

    def test_save_load(self):
        data1 = {'k1': 'v1'}
        data2 = {'k2': 'v2'}
        filename = tempfile.mktemp()

        save_store = storage.file(filename)
        addr1 = save_store.write_data(data1)
        addr2 = save_store.write_data(data2)
        save_store.set_root_addr(addr1)
        save_store.close()

        load_store = storage.file(filename)
        self.assertEqual(data1, load_store.read_data(addr1))
        self.assertEqual(data2, load_store.read_data(addr2))
        self.assertEqual(addr1, load_store.root_addr)
        load_store.close()

        os.unlink(filename)
