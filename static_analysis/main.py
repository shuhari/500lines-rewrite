import ast
import os

from models import AnalysisContext
from visitors import LineLengthVisitor, ExceptionTypeVisitor, VariableUsageVisitor, PreferIsNotVisitor


class CodeAnalyzer:
    """Use available visitors to analysis code issues"""

    def visitors(self, ctx: AnalysisContext):
        yield LineLengthVisitor(ctx)
        yield ExceptionTypeVisitor(ctx)
        yield VariableUsageVisitor(ctx)
        yield PreferIsNotVisitor(ctx)

    def analysis(self, filename: str, code: str):
        """Analysis code issues"""
        self.ctx = AnalysisContext(filename)
        ast_root = ast.parse(code)
        for visitor in self.visitors(self.ctx):
            visitor.visit(ast_root)

    def print(self):
        """Print found issues to console"""
        for issue in self.ctx.issues:
            print(issue)


CODE = """
# Line length exceed max characters
print('the quick brown fox jumps over a lazy dog. the quick brown fox jumps over a lazy dog.')

# try-catch with generic exception type
try:
  print('exception handler')
except Exception as e:
  print(e)
  
# Variable declared but not used
def unused():
  name = 'user'
  print(nme) 
  
# Prefer is not over not is
if not name is None:
  print('name is not none')   
"""


def main():
    # Change work directory to module folder
    # to ensure dump files generated correctly
    os.chdir(os.path.dirname(__file__))
    analyzer = CodeAnalyzer()
    analyzer.analysis('test.py', CODE)
    analyzer.print()


if __name__ == '__main__':
    main()
