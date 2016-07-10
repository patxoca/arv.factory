# -*- coding: utf-8 -*-

"""
"""

import collections
import itertools


class Gen(object):
    def __init__(self, iterable):
        self._seq = iter(iterable)

    def __iter__(self):
        return self

    def next(self):
        return self._seq.next()


class lazy(object):
    def __init__(self, f, *args, **kwargs):
        if not callable(f):
            raise TypeError("callable required")
        self._f = f
        self._args = args
        self._kwargs = kwargs

    def __call__(self):
        res = self._f(*self._args, **self._kwargs)
        if isinstance(res, collections.Iterable) and not isinstance(res, Gen):
            res = Gen(res)
        return res


def mkgen(f, *args, **kwargs):
    """Create a generator from a function.

    >>> import random
    >>> g = mkgen(random.randint, 1, 100)

    """
    def wrapper():
        while True:
            yield f(*args, **kwargs)
    return Gen(wrapper())


def mkconstructor(iterable):
    def constructor():
        if callable(iterable):
            i = iterable()
        else:
            i = iterable
        if not isinstance(i, collections.Iterable):
            raise TypeError("not an iterable.")
        i = iter(i)
        return mkgen(i.next)
    return lazy(constructor)


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


def string(format="%i", counter=None):
    if counter is None:
        counter = itertools.count()

    def generator():
        for i in counter:
            yield format % i

    return Gen(generator())
