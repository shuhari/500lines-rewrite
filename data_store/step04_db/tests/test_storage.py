import os
import tempfile
from unittest import TestCase

from .. import storage


class MemoryStorageTest(TestCase):
    def setUp(self):
        self.storage = storage.memory()

    def test_addrs(self):
        self.assertEqual(storage.ADDR_NONE, self.storage.root_addr)
        self.assertEqual(storage.ADDR_FREE_START, self.storage.free_addr)

    def test_root_addr(self):
        addr = 123
        self.storage.set_root_addr(addr)
        self.assertEqual(addr, self.storage.root_addr)

    def test_write_read_data(self):
        data = {'key': 'k', 'addr': 1}
        addr = self.storage.write_data(data)
        self.assertTrue(self.storage.free_addr > storage.ADDR_FREE_START)

        read_data = self.storage.read_data(addr)
        self.assertEqual(data, read_data)


class FileStorageTest(TestCase):
    def setUp(self):
        self.filename = tempfile.mktemp()
        self.storage = storage.file(self.filename)

    def tearDown(self):
        self.storage.close()
        os.unlink(self.filename)

    def test_save_load(self):
        data1 = {'k1': 'v1'}
        data2 = {'k2': 'v2'}
        addr1 = self.storage.write_data(data1)
        addr2 = self.storage.write_data(data2)
        self.storage.set_root_addr(addr1)
        self.storage.flush()

        storage2 = storage.file(self.filename)
        self.assertEqual(data1, storage2.read_data(addr1))
        self.assertEqual(data2, storage2.read_data(addr2))
        self.assertEqual(self.storage.root_addr, storage2.root_addr)
        storage2.close()
