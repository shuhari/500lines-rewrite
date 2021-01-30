from ..core import AstDoc, Code
from ..parser import parse_file
from ..transformer import transform
from ..utils import relative_of


def parse_test_file(file_name: str) -> AstDoc:
    file_path = relative_of(__file__, '../../docs/src/' + file_name)
    return parse_file(file_path)


def transform_test_file(file_name: str) -> Code:
    ast = parse_test_file(file_name)
    code = transform(ast)
    return code
