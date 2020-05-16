import os
import unittest

from .template import *


class TokenizerTest(unittest.TestCase):
    def setUp(self):
        self.tokenizer = Tokenizer()

    def test_single_variable(self):
        parts = self.tokenizer.tokenize("Hello, {{name}}!")
        self.assertEqual(parts, [
            Text("Hello, "),
            Expr("name"),
            Text("!")
        ])

    def test_extract_filters(self):
        self.assertEqual(("name", []), self.tokenizer.extract_filters("name"))
        self.assertEqual(("name", ["upper"]), self.tokenizer.extract_filters("name | upper"))
        self.assertEqual(("name", ["upper", "strip"]), self.tokenizer.extract_filters("name | upper | strip"))


class TemplateTest(unittest.TestCase):
    def render(self, text: str, ctx: dict) -> str:
        engine = TemplateEngine()
        engine.register_filter('upper', lambda x: x.upper())
        engine.register_filter('strip', lambda x: x.strip())
        template = engine.create(text)
        return template.render(ctx)

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

    def test_variable_with_filter(self):
        self.assert_render("Hello, {{ name | upper}}!",
                           {"name": "Alice"},
                           "Hello, ALICE!")

    def test_variable_with_multi_filters(self):
        self.assert_render("Hello, {{ name | upper | strip }}!",
                           {"name": "  Alice  "},
                           "Hello, ALICE!")


#     def test_speed(self):
#         import time
#
#         times = 100000
#
#         def normal():
#             text = """\
# output.append("Hello, ")
# output.append(name)
# output.append("!")"""
#             ctx = {"output": [], "name": "user"}
#             exec(text, ctx)
#
#         def optimized():
#             text = """\
# ap = output.append
# ap("Hello, ")
# ap(name)
# ap("!")"""
#             ctx = {"output": [], "name": "user"}
#             exec(text, ctx)
#
#         def test(fn):
#             start = time.perf_counter()
#             for i in range(times):
#                 fn()
#             elapsed = time.perf_counter() - start
#             print(f"{fn.__name__} used {elapsed}")
#
#         test(optimized)
#         test(normal)


def main():
    test_dir = os.path.dirname(__file__)
    top_dir = os.path.normpath(os.path.join(test_dir, '../..'))
    suite = unittest.TestLoader().discover(start_dir=test_dir, top_level_dir=top_dir)
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()
