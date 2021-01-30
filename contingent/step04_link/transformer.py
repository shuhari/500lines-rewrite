from .core import AstDoc, AstNode, Code, BuildContext


def transform(doc: AstDoc) -> Code:
    """Transform ast model to code model"""
    code = Code(doc.data)
    code.title = doc.title()
    transform_toctree(doc, code)
    CodeVisitor(code).visit(doc)
    return code


def transform_toctree(doc: AstDoc, code: Code):
    """convert toctree to nested <ul> tag"""
    headers = doc.headers()

    def get_children(index, node):
        for sub_index in range(index + 1, len(headers)):
            child = headers[sub_index]
            if child.header_level() == node.header_level() + 1:
                yield sub_index, child
            else:
                break

    def transform_toc(index, node):
        cls_name = f'toc-{node.name}'
        target = f'{code.html_name()}'
        if node.header_level() > 1:
            target += f'#{node.slug()}'
        li = f'<a class="{cls_name}" href="{target}">{node.data}</a>'
        children = list(get_children(index, node))
        if children:
            code.add_toctree('<li>', li, '<ul>')
            for sub_index, child in children:
                transform_toc(sub_index, child)
            code.add_toctree('</ul>', '</li>')
        else:
            code.add_toctree('<li>' + li + '</li>')

    code.add_toctree('<ul>')
    for index, node in enumerate(headers):
        if node.name == 'h1':
            transform_toc(index, node)
    code.add_toctree('</ul>')


class CodeVisitor:
    """Visit structure of ast model to generate code"""
    def __init__(self, code: Code):
        self.code = code

    def visit(self, node: AstNode):
        getattr(self, node.name)(node)

    def visit_children(self, node: AstNode):
        for child in node.children or []:
            self.visit(child)

    def doc(self, node: AstNode):
        self.code.add_html('<html>',
                           '<head>',
                           f'<title>{node.title()}</title>',
                           '</head>',
                           '<body>')
        self.visit_children(node)
        self.code.add_html('</body>',
                           '</html>')
        self.code.add_dependency('doc', node.data)

    def h1(self, node: AstNode):
        self.code.add_html(f'<h1>{node.data}</h1>')

    def h2(self, node: AstNode):
        self.code.add_html(f'<a name="{node.slug()}"/>',
                           f'<h2>{node.data}</h2>')

    def p(self, node: AstNode):
        if node.children and len(node.children) == 1 and \
                node.children[0].name == 'text':
            p = f'<p>{node.children[0].data}</p>'
            self.code.add_html(p)
        else:
            self.code.add_html('<p>')
            self.visit_children(node)
            self.code.add_html('</p>')

    def text(self, node: AstNode):
        self.code.add_html(node.data)

    def a(self, node: AstNode):
        target = f'{node.data}.html'
        self.code.add_html(f'<a href="{target}>',
                           f'{{{{ ctx.get_title("{node.data}") }}}}',
                           '</a>')
        self.code.add_dependency('title', node.data)

    def toctree(self, node: AstNode):
        self.code.add_html('<ul>')
        self.visit_children(node)
        self.code.add_html('</ul>')

    def toc(self, node: AstNode):
        self.code.add_html(f"{{{{ ctx.get_toctree('{node.data}') }}}}")
        self.code.add_dependency('toctree', node.data)


