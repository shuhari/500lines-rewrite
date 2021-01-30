import os

from ..core import AstDoc
from ..parser import parse_file


def parse_ast(file_name: str) -> AstDoc:
    file_path = os.path.join(os.path.dirname(__file__), '../../docs/src/' + file_name)
    return parse_file(file_path)
