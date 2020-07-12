import ast

from xml.dom.minidom import Document, Element


class AstXml(Document):
    """Helper class to dump ast structure to xml"""

    def __init__(self, node: ast.AST):
        super().__init__()
        self.generate(None, node)

    def append_element(self, parent, name: str, attrs: dict = None):
        """Create a child element and attache to parent"""
        elem = self.createElement(name)
        if attrs:
            for k, v in attrs.items():
                elem.setAttribute(k, str(v))
        if parent:
            parent.appendChild(elem)
        else:
            self.appendChild(elem)
        return elem

    def generate(self, parent, node):
        """
        Generate xml node based on ast node, with children recursively
        """
        if isinstance(node, ast.AST):
            attrs = {x: getattr(node, x) for x in node._attributes}
            attrs['type'] = node.__class__.__name__
            elem = self.append_element(parent, 'ast', attrs)
            for field in node._fields:
                # Each field can be a single ast or list of ast nodes
                field_elem = self.append_element(elem, field)
                value = getattr(node, field)
                if isinstance(value, list):
                    for child_node in value:
                        self.generate(field_elem, child_node)
                else:
                    self.generate(field_elem, value)
        elif node:
            elem = self.append_element(parent, 'value', {'type': node.__class__.__name__})
            elem.appendChild(self.createTextNode(str(node)))

    def save_file(self, file_path: str):
        """Save xml content to file"""
        with open(file_path, 'w') as f:
            f.write(self.toprettyxml(indent='  '))
