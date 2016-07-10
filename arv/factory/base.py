# -*- coding: utf-8 -*-

# marker utilitzar per les factories per indicar que s'omet un atribut

from .generators import Gen
from .generators import lazy
from .generators import mkgen


DELETE = object()


class Factory(object):
    """Class for defining dictionary factories.

    Instances of ``Factory`` classes are actual factories. Calling an
    instance creates a new dictionary.

    """

    defaults = {}
    constructor = dict

    def __init__(self, **kwargs):
        d = self._process_metafactory_defaults(
            self.defaults,
            exclude=set(kwargs.keys())
        )
        d.update(kwargs)
        self._defaults = self._process_metafactory_arguments(d)

    def __call__(self, **kwargs):
        res = self._eval_factory_arguments(
            self._defaults,
            exclude=set(kwargs.keys())
        )
        for k, v in kwargs.items():
            if v is DELETE:
                if k in res:
                    del res[k]
            else:
                res[k] = v
        return self.constructor(**res)

    def many(self, count, **kwargs):
        res = []
        while count > 0:
            count = count - 1
            d = self._eval_factory_arguments(kwargs)
            res.append(self(**d))
        return res

    @classmethod
    def _get_defaults(cls):
        return dict.copy(cls.defaults)

    def _process_metafactory_defaults(self, d, exclude=()):
        res = {}
        for k, v in d.items():
            if k not in exclude:
                if self._is_contructor(v):
                    res[k] = v()
                else:
                    res[k] = v
        return res

    def _process_metafactory_arguments(self, d):
        res = {}
        for k, v in d.items():
            if isinstance(v, Factory):
                res[k] = mkgen(v)
            elif v is not DELETE:
                res[k] = v
        return res

    def _eval_factory_arguments(self, d, exclude=()):
        res = {}
        for k, v in d.items():
            if k not in exclude:
                if isinstance(v, Gen):
                    res[k] = v.next()
                else:
                    res[k] = v
        return res

    def _is_contructor(self, v):
        return (isinstance(v, type) and issubclass(v, Factory)) \
            or isinstance(v, lazy)


def make_factory(**kwargs):
    class F(Factory):
        defaults = kwargs
    return F
