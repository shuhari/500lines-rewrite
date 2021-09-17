def shape(batch) -> (int, int):
    """Get count of machine/tasks of a batch"""
    return len(batch), len(batch[0])
