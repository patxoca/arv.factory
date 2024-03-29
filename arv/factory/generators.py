# -*- coding: utf-8 -*-

"""Value generation for factories.

"""
from __future__ import unicode_literals
from builtins import next
from builtins import object

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable

import itertools
import random


class Gen(object):
    """Base class for value generators.

    Consider the following example:

    .. code-block:: python

       >>> factory = Factory(data=[1, 2, 3])

    What does that mean? the list ``[1, 2, 3]`` is a literal value for
    ``data`` or enumerates the individual values for the attribute on
    successive calls to the factory? In order to avoid this ambiguity
    we need some mean to distinguish when an iterable should be used
    as a literal value for the attribute or as providing individual
    values.

    ``Gen`` is just a class to mark iterables as value generators. It
    implements the *iterator* protocol and defines a thin wrapper that
    delegates the calls to the underlying iterable.

    With that in mind the list in the previous example is interpreted
    as a literal value. In order to use it as a value generator we
    must do:

    .. code-block:: python

       >>> from arv.factory.api import gen
       >>> factory = Factory(data=gen.Gen([1, 2, 3]))

    .. note:: ``Gen`` instances are themselves iterables, but wrapping
              a ``Gen`` instance within another ``Gen`` instance does
              nothing apart from introducing some extra calls due to
              additional levels of nesting.

              In order to avoid that inefficiency instantiating a
              ``Gen`` from a ``Gen`` object returns the original
              ``Gen``. The magic is done in the ``__new__`` and
              ``__init__`` methods.

    """

    def __new__(cls, iterable):
        if isinstance(iterable, cls):
            return iterable
        else:
            return super(Gen, cls).__new__(cls)

    def __init__(self, iterable):
        if not isinstance(iterable, Gen):
            # NOTE: avoid infinite recursion wrapping a ``Gen``
            self._seq = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._seq)


class lazy(object):
    """Lazy callable.

    Marker class for callables and its arguments. The ``Factory``
    class recognizes instances of this class and calls them at factory
    creation time.

    """
    def __init__(self, f, *args, **kwargs):
        if not callable(f):
            raise TypeError("callable required")
        self._f = f
        self._args = args
        self._kwargs = kwargs

    def __call__(self):
        res = self._f(*self._args, **self._kwargs)
        if isinstance(res, Iterable):
            res = Gen(res)
        return res


def mkgen(f, *args, **kwargs):
    """Create a generator from a function.

    Returns a value generator (an instance of the ``Gen`` class) wich
    will call the function ``f`` with the given arguments each time
    it's consumed. The return value from the call will be the value
    produced by the generator.

    >>> import random
    >>> from arv.factory.api import gen
    >>> g = gen.mkgen(random.randint, 1, 100)

    """
    def wrapper():
        while True:
            yield f(*args, **kwargs)
    return Gen(wrapper())


def mkconstructor(iterable, *args, **kwargs):
    """Create a lazy constructor from an iterable.

    Given an iterable or a callable that returns an iterable, creates
    a constructor that will be evaluated at factory construction time.

    In other words, given an iterable or a callable that returns an
    iterable, return an object than can safely be used in metafactory
    definitions.

    >>> import itertools
    >>> from arv.factory.api import gen
    >>> Count = gen.mkconstructor(itertools.count)
    >>> Cycle = gen.mkconstructor(itertools.cycle, (1, 2, 3))

    """
    def constructor():
        if callable(iterable):
            i = iterable(*args, **kwargs)
        else:
            i = iterable
        if not isinstance(i, Iterable):
            raise TypeError("not an iterable.")
        return Gen(i)
    return lazy(constructor)


def count(start=0, step=1):
    """Generator version of ``itertools.count``.

    """
    return Gen(itertools.count(start, step))


def Count(start=0, step=1):
    """Lazy constructor for ``itertools.count``.

    """
    return lazy(count, start, step)


def cycle(seq):
    """Generator version of ``itertools.cycle``.

    """
    return Gen(itertools.cycle(seq))


def Cycle(seq):
    """Lazy constructor for ``itertools.cycle``.

    """
    return lazy(cycle, seq)


def choice(seq):
    """Generator version fo ``random.choice``.

    Since this generator never will get exhausted and generates random
    values a lazy constructor is not required.

    """
    return mkgen(random.choice, seq)


def randint(min, max):
    """Generator version for ``random.randint``.

    """
    return mkgen(random.randint, min, max)


def string(format="%i", counter=None):
    if counter is None:
        counter = itertools.count()

    def generator():
        for i in counter:
            yield format % i

    return Gen(generator())
