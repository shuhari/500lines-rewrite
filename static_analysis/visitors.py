import ast

from models import AnalysisContext


class BaseVisitor(ast.NodeVisitor):
    def __init__(self, ctx: AnalysisContext):
        super().__init__()
        self.ctx = ctx


class LineLengthVisitor(BaseVisitor):
    """Check if code line exceed max allowed length (default 80 characters)"""
    max_length = 80

    def visit(self, node: ast.AST):
        if 'end_col_offset' in node._attributes and node.end_col_offset >= self.max_length:
            self.ctx.add_issue(node, 'W0001', f'Exceed max line length({self.max_length})')
        else:
            self.generic_visit(node)


class ExceptionTypeVisitor(BaseVisitor):
    """Check for generic exception type"""
    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        exp_type = node.type
        if isinstance(exp_type, ast.Name) and exp_type.id == 'Exception':
            self.ctx.add_issue(node, 'W0002', f'Avoid catch generic Exception.')
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

    def check(self, ctx: AnalysisContext):
        unused_vars = set(self.declare_vars) - self.used_vars
        for var_name in unused_vars:
            node = self.declare_vars[var_name]
            ctx.add_issue(node, 'W0003', f"Variable '{var_name}' declared but never used")


class VariableUsageVisitor(BaseVisitor):
    """Check variable declared but not used"""
    def __init__(self, filename: str):
        super().__init__(filename)
        self.in_assign = False
        self.func_stack = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        scope = VariableScope(node)
        self.func_stack.append(scope)
        self.generic_visit(node)
        self.func_stack.remove(scope)
        scope.check(self.ctx)

    def visit_Assign(self, node: ast.Assign):
        """Used Name in assign treated as variable declare, otherwise as usage"""
        self.in_assign = True
        self.generic_visit(node)
        self.in_assign = False

    def visit_Name(self, node: ast.Name):
        if self.func_stack:
            scope = self.func_stack[-1]
            var_name = node.id
            if self.in_assign:
                scope.declare_vars[var_name] = node
            else:
                scope.used_vars.add(var_name)


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
