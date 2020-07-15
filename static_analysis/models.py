import ast
from dataclasses import dataclass


@dataclass
class CodeIssue:
    filename: str = None
    line: int = 0
    column: int = 0
    code: str = None
    message: str = None

    def __str__(self):
        pattern = '{file}({line},{col}) {code}: {message}'
        return pattern.format(file=self.filename,
                              line=self.line,
                              col=self.column,
                              code=self.code,
                              message=self.message)


class AnalysisContext:
    """Manage issues for static analysis"""
    def __init__(self, filename: str):
        self.filename = filename
        self.issues = []

    def add_issue(self, node: ast.AST, code: str, message: str, lineno: int = None):
        issue = CodeIssue(filename=self.filename,
                          line=lineno or node.lineno,
                          column=node.col_offset,
                          code=code,
                          message=message)
        self.issues.append(issue)
