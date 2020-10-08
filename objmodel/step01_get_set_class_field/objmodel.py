class Base:
    def __init__(self, fields: dict = None):
        self._fields = fields or {}

    def get_attr(self, name: str):
        if name not in self._fields:
            raise AttributeError(f"'{self.cls.name}' has no attribute {name}")
        return self.read_dict(name)

    def set_attr(self, name: str, value):
        self._fields[name] = value

    def read_dict(self, name: str):
        return self._fields.get(name, MISSING)


class Class(Base):
    def __init__(self, name: str, fields: dict = None):
        super().__init__(fields=fields)
        self.name = name


class Instance(Base):
    def __init__(self, cls: Class, fields: dict = None):
        super().__init__(fields=fields)
        self.cls = cls

    def get_attr(self, name: str):
        value = self.read_dict(name)
        if value is not MISSING:
            return value
        value = self.cls.read_dict(name)
        if value is not MISSING:
            return value
        raise AttributeError(f"'{self.cls.name}' has no attribute {name}")


MISSING = object()
