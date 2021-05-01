import unittest

from .test_binary_tree import NodeTest, BinaryTreeTest, \
    BinaryTreeSerializeTest
from .test_storage import MemoryStorageTest, FileStorageTest


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    main()
