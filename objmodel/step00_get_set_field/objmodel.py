class Class:
    def __init__(self, name: str):
        self.name = name


class Instance:
    def __init__(self, cls: Class):
        self.cls = cls
        self._fields = {}

    def get_attr(self, name: str):
        if name not in self._fields:
            raise AttributeError(f"'{self.cls.name}' has no attribute {name}")
        return self._fields[name]

    def set_attr(self, name: str, value):
        self._fields[name] = value
