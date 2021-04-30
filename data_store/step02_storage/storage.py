import os
import pickle
import struct
from io import BytesIO

from .binary_tree import ADDR_NONE

SIZE_INT = 8
OFFSET_ROOT, OFFSET_FREE = 0, SIZE_INT
ADDR_FREE_START = 2 * SIZE_INT
INT_FORMAT = '<Q'


class Storage:
    def __init__(self, f, is_new: bool):
        self._f = f
        if is_new:
            self.set_root_addr(ADDR_NONE)
            self.set_free_addr(ADDR_FREE_START)
        else:
            self.root_addr = self.read_int(OFFSET_ROOT)
            self.free_addr = self.read_int(OFFSET_FREE)

    def close(self):
        if self._f:
            self._f.close()
            self._f = None

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
        Use pickle to save data.
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


def memory() -> Storage:
    """create memory based storage"""
    return Storage(BytesIO(), is_new=True)


def file(file_name: str) -> Storage:
    """create file based storage"""
    if os.path.exists(file_name):
        mode, is_new = 'rb+', False
    else:
        mode, is_new = 'wb+', True
    f = open(file_name, mode)
    return Storage(f, is_new=is_new)
