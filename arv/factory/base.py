# -*- coding: utf-8 -*-

# marker utilitzar per les factories per indicar que s'omet un atribut

import inspect


DELETE = object()


# TODO: comprovar si un valor és un generador no és bona idea. Es pot
# simular un generador amb un objecte. Cal mirar com generalitzar-ho.

# TODO: en algunes factories de hera cal assignar valors a les
# foreignkeys. Una possibilitat es redefinir el mètode 'dict' de la
# factoria + super.

def escape(obj):
    def wrapper():
        return obj
    return wrapper


class Factory(object):
    """Class for defining dictionary factories.

    Instances of ``Factory`` classes are actual factories. Calling an
    instance creates a new dictionary.

    """

    defaults = {}

    def __init__(self, **kwargs):
        d = self._get_defaults()
        d.update(kwargs)
        self._defaults = self._process_defaults(d)

    def __call__(self, **kwargs):
        res = self._expand_dict(self._defaults, exclude=set(kwargs.keys()))
        for k, v in kwargs.items():
            if v is DELETE:
                if k in res:
                    del res[k]
            else:
                res[k] = v
        return res

    def many(self, count, **kwargs):
        res = []
        while count > 0:
            count = count - 1
            d = self._expand_dict(kwargs)
            res.append(self(**d))
        return res

    @classmethod
    def _get_defaults(cls):
        return dict.copy(cls.defaults)

    def _process_defaults(self, d):
        res = {}
        for k, v in d.items():
            if callable(v):
                res[k] = v()
            elif v is not DELETE:
                res[k] = v
        return res

    def _expand_dict(self, d, exclude=()):
        res = {}
        for k, v in d.items():
            if k not in exclude:
                if inspect.isgenerator(v):
                    res[k] = v.next()
                else:
                    res[k] = v
        return res


class ObjectFactory(Factory):
    """Class for defining object factories.

    """
    constructor = None

    def __call__(self, **kwargs):
        d = super(ObjectFactory, self).__call__(**kwargs)
        return self.constructor(**d)


def make_factory(**kwargs):
    class F(Factory):
        defaults = kwargs
    return F
