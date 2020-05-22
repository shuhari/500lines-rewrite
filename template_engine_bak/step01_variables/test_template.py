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


class TemplateTest(unittest.TestCase):
    def render(self, text: str, ctx: dict) -> str:
        return Template(text).render(ctx)

    def assert_render(self, text: str, ctx: dict, expected: str):
        rendered = self.render(text, ctx)
        self.assertEqual(expected, rendered)

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


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    main()
