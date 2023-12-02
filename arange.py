def arange(start, stop, step):
    current = start
    while current < stop:
        yield current
        current += step