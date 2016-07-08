# -*- coding: utf-8 -*-

"""
"""

import itertools


class Gen(object):
    def __init__(self, iterable):
        self._seq = iter(iterable)

    def __iter__(self):
        return self

    def next(self):
        return self._seq.next()


def mkgen(f, *args, **kwargs):
    """Create a generator from a function.

    >>> import random
    >>> g = mkgen(random.randint, 1, 100)

    """
    def wrapper():
        while True:
            yield f(*args, **kwargs)
    return Gen(wrapper())


def count(start=0, step=1):
    """Generator version of ``itertools.count``.

    """
    iterator = itertools.count(start, step)
    return mkgen(iterator.next)


def cycle(seq):
    """Generator version of ``itertools.cycle``.

    """
    iterator = itertools.cycle(seq)
    return mkgen(iterator.next)


def string(format="%(value)s", counter=None):
    if counter is None:
        counter = itertools.count()

    def generator():
        for i in counter:
            yield format % {"value": i}

    return Gen(generator())
