import re
import typing


OUTPUT_VAR = "_output_"


class Token:
    """Token in template code"""
    def parse(self, content: str):
        raise NotImplementedError()

    def generate_code(self) -> str:
        raise NotImplementedError()

    def __eq__(self, other):
        return type(self) == type(other) and repr(self) == repr(other)


class Text(Token):
    def __init__(self, content: str = None):
        self._content = content

    def parse(self, content: str):
        self._content = content

    def generate_code(self) -> str:
        return f"{OUTPUT_VAR}.append({repr(self._content)})"

    def __repr__(self):
        return f"Text({self._content})"


class Expr(Token):
    def __init__(self, varname: str = None):
        self._varname = varname

    def parse(self, content: str):
        self._varname = content

    def generate_code(self) -> str:
        return f"{OUTPUT_VAR}.append(str({self._varname}))"

    def __repr__(self):
        return f"Expr({self._varname})"


def create_token(text: str) -> Token:
    """Create token from source code fragment."""
    if text.startswith("{{") and text.endswith("}}"):
        token, content = Expr(), text[2:-2].strip()
    else:
        token, content = Text(), text
    token.parse(content)
    return token


def tokenize(text: str) -> typing.List[Token]:
    """Parse template text to tokens."""
    segments = re.split(r'({{.*?}})', text)
    segments = [x for x in segments if x]
    return [create_token(x) for x in segments]


class Template:
    """Render template in flask-like syntax."""
    def __init__(self, text: str):
        self._text = text
        self._code = None

    def _generate_code(self):
        """Generate to compiled code if not done yet."""
        if not self._code:
            tokens = tokenize(self._text)
            code_lines = [x.generate_code() for x in tokens]
            source_code = '\n'.join(code_lines)
            self._code = compile(source_code, '', 'exec')

    def render(self, ctx: dict) -> str:
        """bind context and generate result text"""
        self._generate_code()
        exec_ctx = (ctx or {}).copy()
        output = []
        exec_ctx[OUTPUT_VAR] = output
        exec(self._code, None, exec_ctx)
        return "".join(output)
