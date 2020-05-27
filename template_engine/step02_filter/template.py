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
        self._filters = []

    def parse(self, content: str):
        self._varname, self._filters = parse_expr(content)

    def generate_code(self) -> str:
        result = self._varname
        for filter_name in self._filters[::-1]:
            result = f"{filter_name}({result})"
        return f"{OUTPUT_VAR}.append(str({result}))"

    def __repr__(self):
        if self._filters:
            return f"Expr({self._varname} | {' | '.join(self._filters)})"
        return f"Expr({self._varname})"


def extract_last_filter(text: str) -> (str, str):
    """
    Extract last filter from expression like 'var | filter'.
    return (var, None) when no more filters found.
    """
    m = re.search(r'(\|\s*[A-Za-z0-9_]+\s*)$', text)
    if m:
        suffix = m.group(1)
        filter_ = suffix[1:].strip()
        var_name = text[:-len(suffix)].strip()
        return var_name, filter_
    return text, None


def parse_expr(text: str) -> (str, typing.List[str]):
    """
    Parse expression to variable name and filters.
    for example, "name | upper | strip" will be converted to 'name', [ 'upper', 'strip']
    """
    var_name, filters = text, []
    while True:
        var_name, filter_ = extract_last_filter(var_name)
        if filter_:
            filters.insert(0, filter_)
        else:
            break
    return var_name, filters


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
    segments = re.split(r'({{.*?}}|{#.*?#})', text)
    segments = [x for x in segments if x]
    return [create_token(x) for x in segments]


class Template:
    """Render template in flask-like syntax."""
    def __init__(self, text: str, filters: dict = None):
        self._text = text
        self._code = None
        self._global_vars = {}
        if filters:
            self._global_vars.update(filters)

    def _generate_code(self):
        """Generate to compiled code if not done yet."""
        if not self._code:
            tokens = tokenize(self._text)
            code_lines = [x.generate_code() for x in tokens]
            code_lines = [x for x in code_lines if x]
            source_code = '\n'.join(code_lines)
            self._code = compile(source_code, '', 'exec')

    def render(self, ctx: dict) -> str:
        """bind context and generate result text"""
        self._generate_code()
        exec_ctx = (ctx or {}).copy()
        output = []
        exec_ctx[OUTPUT_VAR] = output
        exec(self._code, self._global_vars, exec_ctx)
        return "".join(output)


class TemplateEngine:
    """Factory class to create Template object."""
    def __init__(self):
        self._filters = {}
        self._register_default_filters()

    def register_filter(self, name: str, filter_):
        self._filters[name] = filter_

    def _register_default_filters(self):
        self.register_filter('upper', lambda x: x.upper())
        self.register_filter('strip', lambda x: x.strip())

    def create(self, text: str) -> Template:
        return Template(text, filters=self._filters)
