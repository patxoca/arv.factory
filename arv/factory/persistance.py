# -*- coding: utf-8 -*-

# $Id:$


class PersistanceMixin(object):
    """Mixin for adding persistance to factories.

    This mixin defines a method ``make`` that creates and returns an
    object that has been persisted to the backend.

    Classes inheriting from this class must define four methods:

    - ``get_fields(obj)``: return a list of pairs ``(field_name,
      field_value)`` for ``obj``.

    - ``_is_persistable(obj)``: returns ``True`` if the object can be
      persisted by the backend.

    - ``link_to_parent(parent, name, child)``: updates the parent when
      a subobject is persisted.

    - ``_save(obj)``: persists the object in the backend and returns
      the object.

    """

    def make(self, **kwargs):
        obj = self(**kwargs)
        if self._is_persistable(obj):
            return self._persist(obj)
        raise ValueError("Non persistable object.")

    def make_many(self, count, **kwargs):
        return self._many(count, self.make, kwargs)

    def _persist(self, obj):
        for k, v in self._get_fields(obj):
            if self._is_persistable(v):
                v = self._persist(v)
                self._link_to_parent(obj, k, v)
        return self._save(obj)

    def _get_fields(self, obj):
        raise NotImplementedError()

    def _is_persistable(self, obj):
        raise NotImplementedError()

    def _link_to_parent(self, parent, name, child):
        pass

    def _save(self, obj):
        raise NotImplementedError()
