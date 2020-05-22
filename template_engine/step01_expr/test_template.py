import unittest

from .template import Template, tokenize, Text, Expr


class TokenizeTest(unittest.TestCase):
    def test_single_variable(self):
        tokens = tokenize("Hello, {{name}}!")
        self.assertEqual(tokens, [
            Text("Hello, "),
            Expr("name"),
            Text("!")
        ])

    def test_two_variables(self):
        tokens = tokenize("Hello, {{name}} in {{year}}")
        self.assertEqual(tokens, [
            Text("Hello, "),
            Expr("name"),
            Text(" in "),
            Expr("year")
        ])


class TemplateTest(unittest.TestCase):
    def render(self, text: str, ctx: dict, expected: str):
        rendered = Template(text).render(ctx)
        self.assertEqual(expected, rendered)

    def test_plain_text(self):
        for text in [
            'This is a simple message.',
            '<h1>This is a html message.</h1>',
            'This is a multi line message\nThis is line 2 of the message',
        ]:
            self.render(text, None, text)

    def test_expr_single(self):
        self.render("Hello, {{name}}!",
                    {"name": "Alice"},
                    "Hello, Alice!")

    def test_expr_array(self):
        self.render("Hello, {{names[0]}}!",
                    {"names": ["guest"]},
                    "Hello, guest!")

    def test_expr_array(self):
        self.render("Hello, {{names['guest']}}!",
                    {"names": {"guest": 123}},
                    "Hello, 123!")

    def test_expr_multi(self):
        self.render("Hello, {{user}} at {{year}}!",
                    {"user": "Alice", "year": 2020},
                    "Hello, Alice at 2020!")

    def test_expr_variable_missing(self):
        with self.assertRaises(NameError):
            self.render("{{name}}", {}, "")


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    main()
