# -*- coding: utf-8 -*-

# marker utilitzar per les factories per indicar que s'omet un atribut

import inspect


DELETE = object()


# TODO: comprovar si un valor és un generador no és bona idea. Es pot
# simular un generador amb un objecte. Cal mirar com generalitzar-ho.

# TODO: en algunes factories de hera cal assignar valors a les
# foreignkeys. Una possibilitat es redefinir el mètode 'dict' de la
# factoria + super.


class Factory(object):
    """Class for defining factories.

    Instances of ``Factory`` classes are actual factories. Calling an
    instance creates a new object.

    """

    defaults = {}

    def __init__(self, **kwargs):
        d = self._get_defaults()
        d.update(kwargs)
        self._defaults = self._process_defaults(d)

    def __call__(self, **kwargs):
        res = {}
        for k, v in self._defaults.items():
            if k not in kwargs:
                if inspect.isgenerator(v):
                    res[k] = v.next()
                else:
                    res[k] = v
        for k, v in kwargs.items():
            if v is DELETE:
                if k in res:
                    del res[k]
            else:
                res[k] = v
        return res

    @classmethod
    def _get_defaults(cls):
        return dict.copy(cls.defaults)

    def _process_defaults(self, d):
        res = {}
        for k, v in d.items():
            if inspect.isgeneratorfunction(v):
                res[k] = v()
            elif v is not DELETE:
                res[k] = v
        return res


def make_factory(defaults):
    class F(Factory):
        defaults = defaults
    return F
