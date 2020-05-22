import unittest

from .template import *


class TokenizerTest(unittest.TestCase):
    def setUp(self):
        self.tokenizer = Tokenizer()

    def test_tokenize_single_variable(self):
        parts = self.tokenizer.tokenize("Hello, {{name}}!")
        self.assertEqual(parts, [
            Text("Hello, "),
            Expr("name"),
            Text("!")
        ])

    def test_tokenize_multi_variables(self):
        parts = self.tokenizer.tokenize("Hello, {{name}}, Now is {{year}}!")
        self.assertEqual(parts, [
            Text("Hello, "),
            Expr("name"),
            Text(", Now is "),
            Expr("year"),
            Text("!"),
        ])

    def test_tokenize_comments(self):
        parts = self.tokenizer.tokenize("Prefix {# Comment #} Suffix")
        self.assertEqual(parts, [
            Text("Prefix "),
            Comment(" Comment "),
            Text(" Suffix"),
        ])

    def test_tokenize_for_loop(self):
        parts = self.tokenizer.tokenize("{% for row in rows %}Loop {{ row }}{% endfor %}")
        self.assertEqual(parts, [
            For("row", "rows"),
            Text("Loop "),
            Expr("row"),
            EndFor(),
        ])

    def test_tokenize_if(self):
        parts = self.tokenizer.tokenize("{% if flag %}OK{% endif %}")
        self.assertEqual(parts, [
            If("flag"),
            Text("OK"),
            EndIf(),
        ])

    def test_parse_repr(self):
        self.assertEqual(("name", []), self.tokenizer.parse_expr("name"))
        self.assertEqual(("name", ["upper"]), self.tokenizer.parse_expr("name | upper"))
        self.assertEqual(("name", ["upper", "strip"]), self.tokenizer.parse_expr("name | upper | strip"))


class TemplateTest(unittest.TestCase):
    def render(self, text: str, ctx: dict, dump: bool = False) -> str:
        engine = TemplateEngine()
        engine.register_filter('upper', lambda x: x.upper())
        engine.register_filter('strip', lambda x: x.strip())
        template = engine.create(text, dump=dump)
        return template, template.render(ctx)

    def assert_render(self, text: str, ctx: dict, expected: str, dump: bool = False):
        tpl = None
        try:
            tpl, rendered = self.render(text, ctx, dump=dump)
            self.assertEqual(expected, rendered,
                             f"Expected: {expected}, Actual: {rendered}\n{tpl.dump()}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            if tpl:
                self.fail(tpl.dump())


    def test_simple(self):
        texts = [
            'This is a simple message.',
            '<h1>This is a html message.</h1>',
            'This is a multi line message\nThis is line 2 of the message',
        ]
        for text in texts:
            self.assert_render(text, None, text)

    def test_variable_single(self):
        self.assert_render("Hello, {{name}}!",
                           {"name": "Alice"},
                           "Hello, Alice!")

    def test_variable_array(self):
        self.assert_render("Hello, {{users[0]}}!",
                           {"users": ["guest"]},
                           "Hello, guest!")

    def test_variable_dict(self):
        self.assert_render("Hello, {{users['guest']}}!",
                           {"users": {"guest": 2020}},
                           "Hello, 2020!")

    def test_variables_multi(self):
        self.assert_render("Hello, {{user}} at {{year}}!",
                           {"user": "Alice", "year": 2020},
                           "Hello, Alice at 2020!")

    def test_variable_invalid_expr(self):
        with self.assertRaises(NameError):
            self.render("{{name}}", {})

    def test_variable_with_filter(self):
        self.assert_render("Hello, {{ name | upper}}!",
                           {"name": "Alice"},
                           "Hello, ALICE!")

    def test_variable_with_multi_filters(self):
        self.assert_render("Hello, {{ name | upper | strip }}!",
                           {"name": "  Alice  "},
                           "Hello, ALICE!")

    def test_render_multi_templates(self):
        source = "Hello, {{name}}!"
        self.assert_render(source, {"name": "Alice"}, "Hello, Alice!")
        self.assert_render(source, {"name": "Bob"}, "Hello, Bob!")

    def test_comment(self):
        self.assert_render("Hello.{# This is a comment. #}",
                           {},
                           "Hello.", dump=True)

    def test_comment_with_variable(self):
        self.assert_render("Hello, {# This is a comment. #}{{name}}!",
                           {"name": "Alice"},
                           "Hello, Alice!")

    def test_render_for_loop(self):
        self.assert_render("{% for msg in messages %}Item {{msg}}!{% endfor %}",
                           {"messages": ["a", "b", "c"]},
                           "Item a!Item b!Item c!")

    def test_render_if(self):
        source = "{%if flag%}OK{%endif%}"
        self.assert_render(source,
                           {"flag": True},
                           "OK")
        self.assert_render(source,
                           {"flag": False},
                           "")

    def test_render_if(self):
        source = "{%if flag%}Flag1{%elif flag2%}Flag2{%else%}None{%endif%}"
        self.assert_render(source,
                           {"flag": True, "flag2": False},
                           "Flag1")
        self.assert_render(source,
                           {"flag": False, "flag2": True},
                           "Flag2")
        self.assert_render(source,
                           {"flag": False, "flag2": False},
                           "None")

def main():
    unittest.main(__name__)


if __name__ == '__main__':
    main()
