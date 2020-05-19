import unittest

from .template import Template


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


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    main()
