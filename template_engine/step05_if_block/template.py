import re
import typing


OUTPUT_VAR = "_output_"
INDENT = 1
UNINDENT = -1
INDENT_SPACES = 2
INDEX_VAR = "index"


class LoopVar:
    def __init__(self, index: int):
        self.index = index
        self.index0 = index
        self.index1 = index + 1


class CodeBuilder:
    """Manage code generating context."""
    def __init__(self):
        self.codes = []
        self._block_stack = []

    def add_code(self, line: str):
        self.codes.append(line)

    def add_expr(self, expr: str):
        code = f"{OUTPUT_VAR}.append(str({expr}))"
        self.codes.append(code)

    def add_text(self, text: str):
        code = f"{OUTPUT_VAR}.append({repr(text)})"
        self.codes.append(code)

    def indent(self):
        self.codes.append(INDENT)

    def unindent(self):
        self.codes.append(UNINDENT)

    def code_lines(self):
        indent = 0
        for code in self.codes:
            if isinstance(code, str):
                prefix = ' ' * indent * 2 * INDENT_SPACES
                line = prefix + code
                yield line
            elif code in (INDENT, UNINDENT):
                indent += code

    def source(self) -> str:
        return "\n".join(self.code_lines())

    def check_code(self):
        if self._block_stack:
            last_control = self._block_stack.pop(-1)
            raise SyntaxError(f"{last_control.name} has no end tag")

    def push_control(self, ctrl):
        self._block_stack.append(ctrl)

    def end_block(self, begin_token_type):
        block_name = begin_token_type.name
        if not self._block_stack:
            raise SyntaxError(f'End of block {block_name} does not found matching start tag')
        top_block = self._block_stack.pop(-1)
        if type(top_block) != begin_token_type:
            raise SyntaxError(f'Expected end of {block_name} block, got {top_block.name}')
        self.unindent()
        return top_block


class Token:
    """Token in template code"""
    def parse(self, content: str):
        raise NotImplementedError()

    def generate_code(self, builder: CodeBuilder):
        raise NotImplementedError()

    def __eq__(self, other):
        return type(self) == type(other) and repr(self) == repr(other)


class Text(Token):
    def __init__(self, content: str = None):
        self._content = content

    def parse(self, content: str):
        self._content = content

    def generate_code(self, builder: CodeBuilder):
        builder.add_text(self._content)

    def __repr__(self):
        return f"Text({self._content})"


class Expr(Token):
    def __init__(self, varname: str = None):
        self._varname = varname
        self._filters = []

    def parse(self, content: str):
        self._varname, self._filters = parse_expr(content)

    def generate_code(self, builder: CodeBuilder):
        result = self._varname
        for filter_name in self._filters[::-1]:
            result = f"{filter_name}({result})"
        builder.add_expr(result)

    def __repr__(self):
        if self._filters:
            return f"Expr({self._varname} | {' | '.join(self._filters)})"
        return f"Expr({self._varname})"


class Comment(Token):
    def __init__(self, content: str = None):
        self._content = content

    def parse(self, content: str):
        self._content = content

    def __repr__(self):
        return f"Comment({self._content})"

    def generate_code(self, builder: CodeBuilder):
        pass


class For(Token):
    name = 'for'

    def __init__(self, var_name: str = None, target: str = None):
        self._varname = var_name
        self._target = target

    def parse(self, content: str):
        m = re.match(r'for\s+(\w+)\s+in\s+(\w+)', content)
        if not m:
            raise SyntaxError(f"Invalid for block: {content}")
        self._varname, self._target = m.group(1), m.group(2)

    def __repr__(self):
        return f"For({self._varname} in {self._target})"

    def generate_code(self, builder: CodeBuilder):
        builder.add_code(f"for {INDEX_VAR}, {self._varname} in enumerate({self._target}):")
        builder.indent()
        builder.push_control(self)
        builder.add_code(f"loop = LoopVar({INDEX_VAR})")


class If(Token):
    name = 'if'

    def __init__(self, repr_: str = None):
        self._repr = repr_

    def parse(self, content: str):
        m = re.match(r'if\s+(\w+)', content)
        if not m:
            raise SyntaxError(f"Invalid if block: {content}")
        self._repr = m.group(1)

    def __repr__(self):
        return f"If({self._repr})"

    def generate_code(self, builder: CodeBuilder):
        builder.add_code(f"if {self._repr}:")
        builder.indent()
        builder.push_control(self)


class ElseIf(Token):
    def __init__(self, repr_: str = None):
        self._repr = repr_

    def parse(self, content: str):
        m = re.match(r'elif\s+(\w+)', content)
        if not m:
            raise SyntaxError(f"Invalid elif block: {content}")
        self._repr = m.group(1)

    def __repr__(self):
        return f"ElseIf({self._repr})"

    def generate_code(self, builder: CodeBuilder):
        builder.unindent()
        builder.add_code(f"elif {self._repr}:")
        builder.indent()


class Else(Token):
    def __repr__(self):
        return "Else"

    def parse(self, content: str):
        pass

    def generate_code(self, builder: CodeBuilder):
        builder.unindent()
        builder.add_code(f"else:")
        builder.indent()


class EndFor(Token):
    def parse(self, content: str):
        pass

    def __repr__(self):
        return 'EndFor'

    def generate_code(self, builder: CodeBuilder):
        builder.end_block(For)


class EndIf(Token):
    def parse(self, content: str):
        pass

    def __repr__(self):
        return 'EndIf'

    def generate_code(self, builder: CodeBuilder):
        builder.end_block(If)


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


def create_control_token(text: str) -> Token:
    """Create control token() from source code fragment."""
    text = text.strip()
    m = re.match(r'^(\w+)', text)
    if not m:
        raise SyntaxError(f'Unknown control token: {text}')
    keywords = m.group(1)
    token_types = {
        'for': For,
        'endfor': EndFor,
        'if': If,
        'elif': ElseIf,
        'else': Else,
        'endif': EndIf,
    }
    if keywords not in token_types:
        raise SyntaxError(f'Unknown control token: {text}')
    return token_types[keywords]()


def create_token(text: str) -> Token:
    """Create token from source code fragment."""
    if text.startswith("{{") and text.endswith("}}"):
        token, content = Expr(), text[2:-2].strip()
    elif text.startswith("{%") and text.endswith("%}"):
        content = text[2:-2].strip()
        token = create_control_token(content)
    elif text.startswith("{#") and text.endswith("#}"):
        token, content = Comment(), text[2:-2].strip()
    else:
        token, content = Text(), text
    token.parse(content)
    return token


def tokenize(text: str) -> typing.List[Token]:
    """Parse template text to tokens."""
    segments = re.split(r'({{.*?}}|{#.*?#}|{%.*?%})', text)
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
            builder = CodeBuilder()
            for token in tokens:
                token.generate_code(builder)
            builder.check_code()
            self._code = compile(builder.source(), '', 'exec')

    def render(self, ctx: dict) -> str:
        """bind context and generate result text"""
        self._generate_code()
        output = []
        exec_ctx = (ctx or {}).copy()
        exec_ctx.update({
            OUTPUT_VAR: output,
            'LoopVar': LoopVar,
        })
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
