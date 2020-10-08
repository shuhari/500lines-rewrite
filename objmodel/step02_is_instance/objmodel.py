class _Base:
    def __init__(self, fields: dict = None):
        self._fields = fields or {}

    def get_attr(self, name: str):
        if name not in self._fields:
            raise AttributeError(f"'{self.cls.name}' has no attribute {name}")
        return self.read_dict(name)

    def set_attr(self, name: str, value):
        self._fields[name] = value

    def read_dict(self, name: str):
        return self._fields.get(name, _MISSING)


class _Class(_Base):
    def __init__(self, name: str, base=None, fields: dict = None, user_class: bool = True):
        super().__init__(fields=fields)
        if user_class:
            self._base = base or Object
        else:
            self._base = base
        self.name = name

    def inheritance_hierarchy(self):
        yield self
        if self._base:
            for base in self._base.inheritance_hierarchy():
                yield base

    def is_instance(self, cls):
        return cls is Type


class _Instance(_Base):
    def __init__(self, cls: _Class, fields: dict = None):
        super().__init__(fields=fields)
        self.cls = cls

    def get_attr(self, name: str):
        value = self.read_dict(name)
        if value is not _MISSING:
            return value
        value = self.cls.read_dict(name)
        if value is not _MISSING:
            return value
        raise AttributeError(f"'{self.cls.name}' has no attribute {name}")

    def is_instance(self, cls):
        return cls in self.cls.inheritance_hierarchy()


_MISSING = object()


def define_class(name: str, base=None, fields: dict = None, user_class : bool = True) -> _Class:
    return _Class(name, base=base, fields=fields, user_class=user_class)


def create_instance(cls: _Class, fields: dict = None) -> _Instance:
    return _Instance(cls, fields=fields)


def is_instance(obj, cls) -> bool:
    return obj.is_instance(cls)


Object = define_class(name='Object', user_class=False)
Type = define_class(name='Type', base=Object, user_class=False)
