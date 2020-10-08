import functools


class AttrMap:
    def __init__(self, attrs: dict):
        self._attrs = attrs
        self._next = {}

    def index_of(self, name: str):
        return self._attrs.get(name, -1)

    def next(self, name):
        if name in self._attrs:
            return self
        if name in self._next:
            return self._next[name]
        attrs = self._attrs.copy()
        attrs[name] = len(attrs)
        new_map = AttrMap(attrs)
        self._next[name] = new_map
        return new_map


EMPTY_MAP = AttrMap({})


class _Base:
    def __init__(self, fields: dict = None):
        self._map = EMPTY_MAP
        self._values = []
        if fields:
            for k, v in fields.items():
                self.set_attr(k, v)

    def get_attr(self, name: str):
        if name not in self._map._attrs:
            raise AttributeError(f"'{self.cls.name}' has no attribute '{name}'")
        return self.read_dict(name)

    def set_attr(self, name: str, value):
        index = self._map.index_of(name)
        if index >= 0:
            self._values[index] = value
        else:
            self._map = self._map.next(name)
            self._values.append(value)

    def read_dict(self, name: str):
        index = self._map.index_of(name)
        if index < 0:
            return _MISSING
        return self._values[index]


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

    def read_dict(self, name: str):
        value = super().read_dict(name)
        if value is not _MISSING:
            return value
        return self._base.read_dict(name) if self._base else _MISSING


class _Instance(_Base):
    def __init__(self, cls: _Class, fields: dict = None):
        super().__init__(fields=fields)
        self.cls = cls

    def get_attr(self, name: str):
        value = self.read_dict(name)
        if value is _MISSING:
            value = self.cls.read_dict(name)
        if value is _MISSING:
            getter = self.cls.read_dict('__getattr__')
            if getter is not _MISSING:
                return getter(self, name)
        if value is _MISSING:
            raise AttributeError(f"'{self.cls.name}' has no attribute {name}")
        if callable(value):
            # return functools.partial(value, self)
            return self.make_bound_method(value)
        else:
            return value

    def set_attr(self, name: str, value):
        setter = self.cls.read_dict('__setter__')
        if setter is not _MISSING:
            return setter(name, value)
        return super().set_attr(name, value)

    def make_bound_method(self, fn):
        def method(*args, **kwargs):
            return fn(self, *args, **kwargs)
        return method

    def is_instance(self, cls):
        return cls in self.cls.inheritance_hierarchy()

    def call_method(self, name: str, *args, **kwargs):
        fn = self.get_attr(name)
        return fn(*args, **kwargs)


_MISSING = object()


def define_class(name: str, base=None, fields: dict = None, user_class : bool = True) -> _Class:
    return _Class(name, base=base, fields=fields, user_class=user_class)


def create_instance(cls: _Class, fields: dict = None) -> _Instance:
    return _Instance(cls, fields=fields)


def is_instance(obj, cls) -> bool:
    return obj.is_instance(cls)


Object = define_class(name='Object', user_class=False)
Type = define_class(name='Type', base=Object, user_class=False)
