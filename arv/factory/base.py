# -*- coding: utf-8 -*-

# marker utilitzar per les factories per indicar que s'omet un atribut

import six

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
        attrs = self._classify_arguments(kwargs)
        res = self._eval_factory_arguments(
            self._defaults,
            attrs,
            exclude=set(attrs[""].keys())
        )
        for k, v in attrs[""].items():
            if v is DELETE:
                if k in res:
                    del res[k]
            else:
                res[k] = v
        return self.constructor(**res)

    def many(self, count, **kwargs):
        return self._many(count, self.__call__, kwargs)

    def _many(self, count, builder, kwargs):
        res = []
        while count > 0:
            count = count - 1
            d = self._eval_factory_arguments(kwargs)
            res.append(builder(**d))
        return res

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
            if v is not DELETE:
                res[k] = v
        return res

    def _eval_factory_arguments(self, d, attrs={}, exclude=()):
        res = {}
        for k, v in d.items():
            if k not in exclude:
                if isinstance(v, Factory):
                    kwargs = attrs.get(k, {})
                    res[k] = v(**kwargs)
                elif isinstance(v, Gen):
                    res[k] = six.next(v)
                else:
                    res[k] = v
        return res

    @staticmethod
    def _classify_arguments(d):
        res = {"": {}}
        for k, v in d.items():
            if "__" in k:
                p1, p2 = k.split("__", 1)
                if p1 in res[""]:
                    raise ValueError(k)
            else:
                p1, p2 = "", k
                if p2 in res:
                    raise ValueError(k)
            res.setdefault(p1, {})[p2] = v
        return res

    def _is_contructor(self, v):
        return (isinstance(v, type) and issubclass(v, Factory)) \
            or isinstance(v, lazy)


class PersistanceMixin(object):
    """Mixin for adding persistance to factories.

    This mixin defines a method ``make`` that creates and returns an
    object that has been persisted to the backend.

    Classes inheriting from this class must define two methods:

    - ``_save(obj)``: persists the object in the backend.

    - ``_is_persistable(obj)``: returns ``True`` if the object can be
      persisted.

    """

    def make(self, **kwargs):
        obj = self(**kwargs)
        if self._is_persistable(obj):
            return self._persist(obj)
        raise ValueError("Non persistable object.")

    def make_many(self, count, **kwargs):
        return self._many(count, self.make, kwargs)

    def _persist(self, obj):
        for k, v in obj.__dict__.items():
            if self._is_persistable(v):
                self._persist(v)
        return self._save(obj)

    def _save(self, obj):
        raise NotImplementedError()

    def _is_persistable(self, obj):
        raise NotImplementedError()


class DjangoFactory(PersistanceMixin, Factory):
    """Factory for creating django models.
    """

    def _is_persistable(self, obj):
        return hasattr(obj, "save") and callable(obj.save)

    def _save(self, obj):
        return obj.save()


def make_factory(**kwargs):
    class F(Factory):
        defaults = kwargs
    return F
