import unittest

from .template import Template, TemplateEngine, tokenize, parse_expr, \
    Text, Expr, Comment, For, EndFor, If, ElseIf, Else, EndIf


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

    def test_comment(self):
        tokens = tokenize("Prefix {# Comment #} Suffix")
        self.assertEqual(tokens, [
            Text("Prefix "),
            Comment("Comment"),
            Text(" Suffix"),
        ])

    def test_parse_repr(self):
        cases = [
            ("name", "name", []),
            ("name | upper", "name", ["upper"]),
            ("name | upper | strip", "name", ["upper", "strip"]),
            ("'a string with | inside' | upper | strip", "'a string with | inside'", ["upper", "strip"])
        ]
        for expr, varname, filters in cases:
            parsed_varname, parsed_filters = parse_expr(expr)
            self.assertEqual(varname, parsed_varname)
            self.assertEqual(filters, parsed_filters)

    def test_tokenize_for_loop(self):
        tokens = tokenize("{% for row in rows %}Loop {{ row }}{% endfor %}")
        self.assertEqual(tokens, [
            For("row", "rows"),
            Text("Loop "),
            Expr("row"),
            EndFor(),
        ])

    def test_tokenize_invalid_control(self):
        with self.assertRaises(SyntaxError):
            tokenize("{% nokeyword %}")

    def test_tokenize_if(self):
        tokens = tokenize("{% if flag %}OK{% endif %}")
        self.assertEqual(tokens, [
            If("flag"),
            Text("OK"),
            EndIf(),
        ])

    def test_tokenize_if_else(self):
        tokens = tokenize("{% if flag1 %}flag1{% elif flag2 %}flag2{% else %}none{% endif %}")
        self.assertEqual(tokens, [
            If("flag1"),
            Text("flag1"),
            ElseIf("flag2"),
            Text("flag2"),
            Else(),
            Text("none"),
            EndIf(),
        ])


class TemplateTest(unittest.TestCase):
    def render(self, text: str, ctx: dict, expected: str, filters: dict = None):
        engine = TemplateEngine()
        if filters:
            for filter_name, fn in filters.items():
                engine.register_filter(filter_name, fn)
        template = engine.create(text)
        rendered = template.render(ctx)
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

    def test_expr_with_filter_1(self):
        self.render("Hello, {{ name | upper }}!",
                    {"name": "Alice"},
                    "Hello, ALICE!")

    def test_expr_with_filter_2(self):
        self.render("Hello, {{ name | upper | strip }}!",
                    {"name": "  Alice  "},
                    "Hello, ALICE!")

    def test_expr_with_addition_filter(self):
        first = lambda x: x[0]
        self.render("Hello, {{ name | upper | first }}!",
                    {"name": "Alice"},
                    "Hello, A!",
                    filters={"first": first})

    def test_comment(self):
        self.render("Hello, {# This is a comment. #}World!",
                    {},
                    "Hello, World!")

    def test_comment_with_expr(self):
        self.render("Hello, {# This is a comment. #}{{name}}!",
                    {"name": "Alice"},
                    "Hello, Alice!")

    def test_render_for_loop(self):
        self.render("{% for msg in messages %}Item {{msg}}!{% endfor %}",
                    {"messages": ["a", "b", "c"]},
                    "Item a!Item b!Item c!")

    def test_render_for_loop_with_index(self):
        self.render("{% for msg in messages %}{{loop.index1}}.{{msg}}!{% endfor %}",
                    {"messages": ["a", "b", "c"]},
                    "1.a!2.b!3.c!")

    def test_render_for_loop_no_start_tag(self):
        with self.assertRaises(SyntaxError):
            self.render("{% endfor %}",
                        {"messages": ["a", "b", "c"]},
                        "")

    def test_render_for_loop_no_end_tag(self):
        with self.assertRaises(SyntaxError):
            self.render("{% for msg in messages %}{{msg}}",
                        {"messages": ["a", "b", "c"]},
                        "")

    def test_render_if_simple(self):
        source = "{%if flag%}OK{%endif%}"
        self.render(source, {"flag": True}, "OK")
        self.render(source, {"flag": False}, "")

    def test_render_if_else(self):
        source = "{% if flag1 %}flag1{% elif flag2 %}flag2{% else %}none{% endif %}"
        self.render(source, {"flag1": True, "flag2": False}, "flag1")
        self.render(source, {"flag1": False, "flag2": True}, "flag2")
        self.render(source, {"flag1": False, "flag2": False}, "none")


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    main()
