def find_first(items, predicate):
    return next((x for x in items if predicate(x)), None)


def find_index(items, predicate):
    return next((index for index, x in enumerate(items) if predicate(x)), -1)
