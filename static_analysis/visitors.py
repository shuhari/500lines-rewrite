import ast

from models import AnalysisContext


class BaseVisitor(ast.NodeVisitor):
    def __init__(self, ctx: AnalysisContext):
        super().__init__()
        self.ctx = ctx


class LineLengthVisitor(BaseVisitor):
    """Check if code line exceed max allowed length (default 80 characters)"""
    max_length = 79
    max_docstring_length = 72

    def visit(self, node: ast.AST):
        if isinstance(node, ast.FunctionDef):
            self.check_docstring(node)
        if 'end_col_offset' in node._attributes and node.end_col_offset >= self.max_length:
            self.ctx.add_issue(node, 'W0001', f'Exceed max line length({self.max_length})')
        else:
            self.generic_visit(node)

    def get_docstring_node(self, node):
        """Return the AST node of docstring"""
        if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.ClassDef, ast.Module)):
            raise TypeError("%r can't have docstrings" % node.__class__.__name__)
        if not(node.body and isinstance(node.body[0], ast.Expr)):
            return None
        value_node = node.body[0].value
        if isinstance(value_node, ast.Constant) and isinstance(value_node.value, str):
            return value_node
        return None

    def check_docstring(self, node: ast.AST):
        doc_node = self.get_docstring_node(node)
        if not doc_node:
            return self.generic_visit(node)
        for offset, line in enumerate(doc_node.value.split('\n')):
            if len(line) >= self.max_docstring_length:
                lineno = doc_node.lineno + offset
                self.ctx.add_issue(node, 'W0001',
                                   f'Docstring for {node.name} exceed max length({self.max_docstring_length})',
                                   lineno=lineno)


class ExceptionTypeVisitor(BaseVisitor):
    """Check for generic exception type"""
    AVOID_TYPES = ('Exception', 'BaseException')

    def iter_exception_types(self, node: ast.AST):
        # handler type can be simple name of tuple(name, name, ...)
        if isinstance(node, ast.Name):
            yield node
        elif isinstance(node, ast.Tuple):
            for name_node in node.elts:
                if isinstance(name_node, ast.Name):
                    yield name_node

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        if not node.type:
            self.ctx.add_issue(node, 'W0002', f'Please specify exception type to catch.')
        for name_node in self.iter_exception_types(node.type):
            if name_node.id in self.AVOID_TYPES:
                self.ctx.add_issue(name_node, 'W0002', f'Avoid catch generic Exception.')
        self.generic_visit(node)


class VariableScope:
    """
    Record declared/used variables in function scope,
    and check which is not used
    """
    def __init__(self, node: ast.FunctionDef):
        self.node = node
        self.declare_vars = {}
        self.used_vars = set()

    def use(self, node: ast.Name, is_assign: bool):
        var_name = node.id
        if is_assign:
            self.declare_vars[var_name] = node
        else:
            self.used_vars.add(var_name)

    def check(self, ctx: AnalysisContext):
        unused_vars = set(self.declare_vars) - self.used_vars
        for var_name in unused_vars:
            node = self.declare_vars[var_name]
            ctx.add_issue(node, 'W0003', f"Variable '{var_name}' declared but never used")


class VariableUsageVisitor(BaseVisitor):
    def __init__(self, ctx: AnalysisContext):
        super().__init__(ctx)
        self.in_assign = False
        self.scope_stack = []

    def visit(self, node: ast.AST):
        is_scope_ast = isinstance(node,
                                  (ast.Module, ast.FunctionDef, ast.ClassDef))
        if is_scope_ast:
            scope = VariableScope(node)
            self.scope_stack.append(scope)
        super().visit(node)
        if is_scope_ast:
            self.scope_stack.remove(scope)
            scope.check(self.ctx)

    def visit_Assign(self, node: ast.Assign):
        self.in_assign = True
        self.generic_visit(node)
        self.in_assign = False

    def visit_Name(self, node: ast.Name):
        if self.scope_stack:
            scope = self.scope_stack[-1]
            scope.use(node, self.in_assign)
        self.generic_visit(node)


class PreferIsNotVisitor(BaseVisitor):
    """Use is not ... rather than not is ..."""
    def visit_If(self, node: ast.If):
        if isinstance(node.test, ast.UnaryOp) and \
                isinstance(node.test.op, ast.Not):
            operand = node.test.operand
            if isinstance(operand, ast.Compare) and \
                    len(operand.ops) == 1 and \
                    isinstance(operand.ops[0], ast.Is):
                self.ctx.add_issue(node, 'W0004', 'Use if ... is not instead')
        self.generic_visit(node)
