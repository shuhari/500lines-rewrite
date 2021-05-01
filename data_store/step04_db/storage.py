import os
import pickle
import struct
from io import BytesIO

import portalocker

from .binary_tree import ADDR_NONE


SIZE_INT = 8
OFFSET_ROOT, OFFSET_FREE = 0, SIZE_INT
ADDR_FREE_START = 2 * SIZE_INT
INT_FORMAT = '<Q'


class Storage:
    """Save/load data from file-like storage, including memory/file"""
    def __init__(self, f, is_new: bool):
        self._f = f
        self.locked = False
        if is_new:
            self.set_root_addr(ADDR_NONE)
            self.set_free_addr(ADDR_FREE_START)
        else:
            self.reload()

    def reload(self):
        self.root_addr = self.read_int(OFFSET_ROOT)
        self.free_addr = self.read_int(OFFSET_FREE)

    def close(self):
        if self._f:
            self._f.close()
            self._f = None

    def flush(self):
        self._f.flush()

    def set_root_addr(self, addr: int):
        self.root_addr = addr
        self.write_int(OFFSET_ROOT, addr)

    def set_free_addr(self, addr: int):
        self.free_addr = addr
        self.write_int(OFFSET_FREE, addr)

    def seek(self, offset: int):
        self._f.seek(offset, os.SEEK_SET)

    def read_int(self, offset: int) -> int:
        self.seek(offset)
        buffer = self._f.read(SIZE_INT)
        return struct.unpack(INT_FORMAT, buffer)[0]

    def write_int(self, offset: int, value: int):
        self.seek(offset)
        self._f.write(struct.pack(INT_FORMAT, value))

    def write_data(self, data) -> int:
        """
        Use pickle to save data, and update free address
        :return address of data
        """
        data_addr = self.free_addr
        self.seek(data_addr)
        pickle.dump(data, self._f)
        self.set_free_addr(self._f.tell())
        return data_addr

    def read_data(self, addr: int):
        """
        Use pickle to load data
        """
        self.seek(addr)
        return pickle.load(self._f)

    def lock(self):
        if not self.locked:
            portalocker.lock(self._f, portalocker.LOCK_EX)
            self.locked = True

    def unlock(self):
        if self.locked:
            portalocker.unlock(self._f)
            self.locked = False


class MemoryStorage(Storage):
    def __init__(self, data: bytes = None):
        is_new = (data is None)
        super().__init__(BytesIO(data), is_new=is_new)

    def copy(self):
        return MemoryStorage(self._f.getvalue())


def memory() -> Storage:
    """create memory based storage"""
    return MemoryStorage()


def file(file_name: str) -> Storage:
    """create file based storage"""
    if os.path.exists(file_name):
        mode, is_new = 'rb+', False
    else:
        mode, is_new = 'wb+', True
    f = open(file_name, mode)
    return Storage(f, is_new=is_new)
