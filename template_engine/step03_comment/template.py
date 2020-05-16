import re
import typing


CTX_VAR = "_ctx_"


class Code:
    """Base class for all code item."""
    def __init__(self, text):
        self.parse(text)

    def __eq__(self, other):
        return type(self) == type(other) and repr(self) == repr(other)

    def parse(self, text: str):
        """Parse source text to internal structure"""
        raise NotImplementedError()

    def to_code(self, ctx) -> str:
        """Generate code for template function"""
        raise NotImplementedError()


class Text(Code):
    """Simple Text."""
    def parse(self, text: str):
        self._text = text

    def __repr__(self):
        return f"Text({self._text})"

    def to_code(self, ctx) -> str:
        return f"{CTX_VAR}.add({repr(self._text)})"


class Comment(Code):
    def parse(self, text: str):
        self._text = text

    def __repr__(self):
        return f"Text({self._text})"

    def to_code(self, ctx) -> str:
        return None


class Expr(Code):
    """Expression in {{xxx}} format"""
    def parse(self, text: str):
        varname, filters = Tokenizer().extract_filters(text)
        self._varname = varname
        self._filters = filters

    def __repr__(self):
        if self._filters:
            return f"Expr({self._varname} | {' | '.join(self._filters)})"
        return f"Expr({self._varname})"

    def to_code(self, ctx) -> str:
        """
        _output_.append(str(strip(append(var))))
        """
        result = self._varname
        for filter in self._filters[::-1]:
            filter_name = ctx.filter_name(filter)
            result = f"{filter_name}({result})"
        return f"{CTX_VAR}.add(str({result}))"


class Tokenizer:
    def tokenize(self, text: str) -> typing.List[Code]:
        parts = re.split(r'({{.*?}}|{#.*?#})', text)
        return [self.create_code(x) for x in parts]

    def create_code(self, text: str) -> Code:
        if text.startswith("{{") and text.endswith("}}"):
            return Expr(text[2:-2].strip())
        elif text.startswith("{#") and text.endswith("#}"):
            return Comment(text[2:-2])
        return Text(text)

    def extract_filters(self, text: str) -> (str, typing.List[str]):
        varname, filters = text, []
        while True:
            varname, filter = self.extract_last_filter(varname)
            if filter:
                filters.insert(0, filter)
            else:
                break
        return varname, filters

    def extract_last_filter(self, text: str) -> (str, str):
        """
        Extract last filter from expression like 'var | filter'.
        If filter not found, then return (var, None)
        """
        m = re.search(r'(\|\s*\w+\s*)$', text)
        if m:
            suffix = m.group(1)
            filter = suffix[1:].strip()
            varname = text[:-len(suffix)].strip()
            return varname, filter
        return text, None


class Template:
    def __init__(self, text: str, filters: dict = None):
        self._filters = filters or {}
        self._output_lines = []
        self._global_ctx = {}
        for name, filter in self._filters.items():
            self._global_ctx[self.filter_name(name)] = filter

        tokenizers = Tokenizer().tokenize(text)
        code_lines = [x.to_code(self) for x in tokenizers]
        code_lines = [x for x in code_lines if x]
        self._code = '\n'.join(code_lines)

    def filter_name(self, name: str) -> str:
        return f"f_{name}"

    def add(self, line: str):
        self._output_lines.append(line)

    def render(self, ctx: dict = None) -> str:
        self._output_lines.clear()
        exec_ctx = (ctx or {}).copy()
        for name, filter in self._filters.items():
            exec_ctx[self.filter_name(name)] = filter
        exec_ctx[CTX_VAR] = self
        exec(self._code, self._global_ctx, exec_ctx)
        return "".join(self._output_lines)


class TemplateEngine:
    def __init__(self):
        self._filters = {}

    def register_filter(self, name: str, filter):
        self._filters[name] = filter

    def create(self, text: str) -> Template:
        return Template(text, filters=self._filters)
