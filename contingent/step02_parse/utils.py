import os


def find_first(items, predicate):
    """Find first element that match predicate in collection"""
    return next((x for x in items if predicate(x)), None)


def find_index(items, predicate):
    """Find index of first element that match predicate in collection"""
    return next((index for index, x in enumerate(items) if predicate(x)), -1)


def get_name_prefix(file_name: str) -> str:
    """get file name without extension"""
    return os.path.splitext(os.path.basename(file_name))[0]


def relative_of(base_path: str, relative_path: str) -> str:
    """Given a base file and path relative to it, get full path of it"""
    return os.path.normpath(os.path.join(os.path.dirname(base_path), relative_path))
