import re
import typing


CTX_VAR = "_ctx_"
INDENT_SPACES = 2
INDENT = 1
UNINDENT = 2


class Loop:
    """Helper to use loop.index0, index1, ... in code"""
    def __init__(self, index: int):
        self.index = index
        self.index0 = index
        self.index1 = index + 1


class CodeContext:
    """Help for executing code"""
    def __init__(self, variables: dict, filters: dict = None):
        self._variables = variables or {}
        self._filters = filters or {}
        self._lines = []

    def filter_name(self, name: str) -> str:
        """Give each filter a unique name to avoid conflict with normal variables."""
        return f"_f_{name}"

    def global_variables(self) -> dict:
        variables = {}
        for name, filter_ in self._filters.items():
            variables[self.filter_name(name)] = filter_
        return variables

    def local_variables(self) -> dict:
        variables = {}
        variables.update(self._variables)
        variables[CTX_VAR] = self
        variables['Loop'] = Loop
        return variables

    def output(self, line: str):
        self._lines.append(line)

    def result(self) -> str:
        return "".join(self._lines)


class CodeGenContext(CodeContext):
    """Help for executing code"""
    def __init__(self, variables: dict, filters: dict = None, dump: bool = False):
        super(CodeGenContext, self).__init__(variables, filters)
        self._controls = []
        self._index_count = 0
        self._dump = dump

    def last_control(self):
        return self._controls[-1] if self._controls else None

    def push_control(self, control):
        self._controls.append(control)

    def pop_last_control(self):
        if self._controls:
            self._controls.pop(len(self._controls) - 1)

    def add_code(self, code: str):
        self.output(code)

    def indent(self):
        self.output(INDENT)

    def unindent(self):
        self.output(UNINDENT)

    def index_var_name(self) -> str:
        result = f"_idx_{self._index_count}"
        self._index_count += 1
        return result

    def generate_code(self, text: str):
        """Generate compiled code from source"""
        tokens = Tokenizer().tokenize(text)
        for token in tokens:
            token.generate(self)
        code_lines = self.build_source()
        code = '\n'.join(code_lines)
        # print('code:', code)
        # print('source:', code)
        return compile(code, '', 'exec')

    def build_source(self):
        indent = 0
        for instrument in self._lines:
            if isinstance(instrument, str):
                line = ' ' * indent * INDENT_SPACES + instrument
                yield line
            elif isinstance(instrument, int) and instrument in (INDENT, UNINDENT):
                indent += instrument


class Code:
    """Base class for all code item."""
    def __eq__(self, other):
        return type(self) == type(other) and repr(self) == repr(other)

    def parse(self, text: str):
        """Parse source text to internal structure"""
        pass

    def generate(self, ctx: CodeGenContext):
        pass


class SingleCode(Code):
    """Simple code sunch as Text, Expr, Comment."""
    def __init__(self, text):
        self.parse(text)

    def to_code(self, ctx) -> str:
        """Generate code for template function"""
        raise NotImplementedError()

    def generate(self, ctx: CodeGenContext):
        code = self.to_code(ctx)
        if code:
            ctx.add_code(code)


class Text(SingleCode):
    """Simple Text."""
    def parse(self, text: str):
        self._text = text

    def __repr__(self):
        return f"Text({self._text})"

    def to_code(self, ctx) -> str:
        return f"{CTX_VAR}.output({repr(self._text)})"


class Comment(SingleCode):
    def parse(self, text: str):
        self._text = text

    def __repr__(self):
        return f"Comment({self._text})"

    def to_code(self, ctx) -> str:
        return None


class Expr(SingleCode):
    """Expression in {{xxx}} format"""
    def parse(self, text: str):
        varname, filters = Tokenizer().parse_expr(text)
        self._varname = varname
        self._filters = filters

    def __repr__(self):
        if self._filters:
            return f"Expr({self._varname} | {' | '.join(self._filters)})"
        return f"Expr({self._varname})"

    def to_code(self, ctx) -> str:
        """Convert filters to function call"""
        result = self._varname
        for filter_ in self._filters[::-1]:
            filter_name = ctx.filter_name(filter_)
            result = f"{filter_name}({result})"
        return f"{CTX_VAR}.output(str({result}))"


class Control(Code):
    """Control blocks such as for/if"""
    pass


class Block(Control):
    """Begin block"""
    def generate(self, ctx: CodeGenContext):
        ctx.push_control(self)


class EndBlock(Control):
    begin_control = None

    def generate(self, ctx: CodeGenContext):
        if type(ctx.last_control()) != self.begin_control:
            raise SyntaxError(f"Expected begin block {self.begin_control.__name__} not found")
        ctx.pop_last_control()
        ctx.unindent()

    def __repr__(self):
        return f"{self.__class__.__name__}"


class For(Block):
    """For Loop"""
    def __init__(self, *args):
        if len(args) == 2:
            self._varname, self._target = args[0], args[1]
        else:
            self.parse(args[0])

    def parse(self, text: str):
        m = re.match(r'for\s+(\w+)\s+in\s+(\w+)', text)
        if m:
            self._varname, self._target = m.group(1), m.group(2)
        else:
            raise SyntaxError(f"Invalid for block: {text}")

    def __repr__(self):
        return f"For({self._varname} in {self._target})"

    def generate(self, ctx: CodeGenContext):
        super(For, self).generate(ctx)
        index_var = ctx.index_var_name()
        ctx.add_code(f"for {index_var}, {self._varname} in enumerate({self._target}):")
        ctx.indent()
        ctx.add_code(f"loop = Loop({index_var})")


class EndFor(EndBlock):
    begin_control = For


class Tokenizer:
    """Parse template text to tokens"""
    def tokenize(self, text: str) -> typing.List[Code]:
        parts = re.split(r'({{.*?}}|{#.*?#}|{%.*?%})', text)
        parts = [x for x in parts if x]
        return [self.create_code(x) for x in parts]

    def create_code(self, text: str) -> Code:
        """Create code item from source text."""
        if text.startswith("{{") and text.endswith("}}"):
            return Expr(text[2:-2].strip())
        elif text.startswith("{%") and text.endswith("%}"):
            return self.create_control_code(text[2:-2].strip())
        elif text.startswith("{#") and text.endswith("#}"):
            return Comment(text[2:-2])
        return Text(text)

    def create_control_code(self, text: str) -> Code:
        if text == 'endfor':
            return EndFor()
        elif text.startswith('for'):
            return For(text)
        raise SyntaxError(f'Unknown control code: {text}')

    def parse_expr(self, text: str) -> (str, typing.List[str]):
        """
        Parse expression to variable name and filters.
        for example, name | upper | strip
        converted to 'name', [ 'upper', 'strip']
        """
        varname, filters = text, []
        while True:
            varname, filter_ = self.extract_last_filter(varname)
            if filter_:
                filters.insert(0, filter_)
            else:
                break
        return varname, filters

    def extract_last_filter(self, text: str) -> (str, str):
        """
        Extract last filter from expression like 'var | filter'.
        return (var, None) when no more filters found.
        """
        m = re.search(r'(\|\s*\w+\s*)$', text)
        if m:
            suffix = m.group(1)
            filter_ = suffix[1:].strip()
            varname = text[:-len(suffix)].strip()
            return varname, filter_
        return text, None


class Template:
    """Render template source with context to text result."""
    def __init__(self, text: str, filters: dict = None, dump: bool = False):
        self._filters = filters
        self._code = CodeGenContext(None, filters, dump=dump).generate_code(text)

    def render(self, variables: dict = None) -> str:
        ctx = CodeContext(variables, filters=self._filters)
        exec(self._code, ctx.global_variables(), ctx.local_variables())
        return ctx.result()


class TemplateEngine:
    """Factory class to create Template object."""
    def __init__(self):
        self._filters = {}

    def register_filter(self, name: str, filter_):
        self._filters[name] = filter_

    def create(self, text: str, dump: bool = False) -> Template:
        return Template(text, filters=self._filters, dump=dump)
