class TestMixin:
    def get_item(self, items, **attrs):
        for item in items:
            for k, v in attrs.items():
                if item.get(k, None) != v:
                    continue
            return item
        return None

    def assert_item(self, items, **attrs):
        item = self.get_item(items, **attrs)
        self.assertIsNotNone(item, f'item with attrs({attrs}) not found')

