import unittest

from .test_parser import ParserTest
from .test_core import CacheFileTest
from .test_transformer import TransformerTest
from .test_linker import LinkerTest


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    main()
