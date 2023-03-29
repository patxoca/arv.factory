# -*- coding: utf-8 -*-

# $Id:$

from __future__ import unicode_literals
from builtins import object

from unittest import TestCase
try:
    from unittest import mock
except ImportError:
    import mock

from ..base import Factory
from ..persistance import PersistanceMixin


class TestPersistanceMixin(TestCase):

    def setUp(self):
        class Object(object):
            def __init__(self, persistable=True, **kwargs):
                self.__dict__.update(kwargs)
                self.persistable = persistable
                self.persisted = False

            def persist(self):
                self.persisted = True

        class MyFactory(PersistanceMixin, Factory):
            constructor = Object

            def _get_fields(self, obj):
                d = dict(obj.__dict__)
                del d["persistable"]
                del d["persisted"]
                return list(d.items())

            def _is_persistable(self, obj):
                return getattr(obj, "persistable", False)

            def _save(self, obj):
                obj.persist()
                return obj

        self.Object = Object
        self.MyFactory = MyFactory
        self.factory = MyFactory(foo=42)

    def test_save_called_only_for_persistable_subobjects(self):
        sobj1 = self.Object(False, foo=42)
        sobj2 = self.Object(True, foo=42)
        obj = self.Object(True, foo=42, sobj1=sobj1, sobj2=sobj2)
        self.assertFalse(obj.persisted)
        self.assertFalse(sobj1.persisted)
        self.assertFalse(sobj2.persisted)
        self.factory._persist(obj)
        self.assertTrue(obj.persisted)
        self.assertFalse(sobj1.persisted)
        self.assertTrue(sobj2.persisted)

    def test_make_returns_persisted_object(self):
        obj = self.factory.make()
        self.assertTrue(obj.persisted)

    def test_make_overrides_defaults(self):
        obj = self.factory.make(foo=1)
        self.assertEqual(obj.foo, 1)

    def test_make_raises_ValueError_if_not_persistable(self):
        with self.assertRaisesRegexp(ValueError, "Non persistable object."):
            self.factory.make(persistable=False)

    def test_make_many(self):
        with mock.patch.object(self.factory, "_many") as method:
            self.factory.make_many(5, foo=1, bar="Hello")
            self.assertEqual(method.call_count, 1)
            args, kwargs = method.call_args
            self.assertEqual(
                args,
                (5, self.factory.make, {"foo": 1, "bar": "Hello"})
            )
            self.assertEqual(kwargs, {})
