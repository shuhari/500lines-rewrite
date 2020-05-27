import unittest

from .template import Template


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
            self.render(text, {}, text)


def main():
    unittest.main(__name__)


if __name__ == '__main__':
    main()
