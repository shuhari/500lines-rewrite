class Template:
    """Render template source with context to text result."""
    def __init__(self, text: str):
        self._text = text

    def render(self, ctx: dict) -> str:
        return self._text

