import contextlib

from . import storage
from .binary_tree import BinaryTree


class DB:
    def __init__(self, file_name: str):
        self._storage = storage.file(file_name)
        self._tree = BinaryTree(self._storage)
        self.commit_times = 0
        self.transaction = None

    def close(self):
        self._storage.close()

    def reload_root(self):
        self._storage.lock()
        try:
            self._tree.reload_root()
        finally:
            self._storage.unlock()

    def __getitem__(self, key):
        self.reload_root()
        return self._tree.get(key)

    def __setitem__(self, key, value):
        with self.get_current_transaction():
            self._tree.set(key, value)

    def __delitem__(self, key):
        with self.get_current_transaction():
            self._tree.delete(key)

    def commit(self):
        self._storage.lock()
        try:
            self._tree.commit()
            self.commit_times += 1
        finally:
            self._storage.unlock()

    def begin_transaction(self):
        self.transaction = ManualTransaction(self)
        return self.transaction

    def end_transaction(self):
        self.transaction = None

    def get_current_transaction(self):
        return self.transaction or auto_transaction(self)


@contextlib.contextmanager
def auto_transaction(db):
    db.reload_root()
    yield
    db.commit()


class ManualTransaction:
    def __init__(self, db):
        self.db = db
        self.db.reload_root()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def commit(self):
        self.db.commit()
        self.db.end_transaction()
