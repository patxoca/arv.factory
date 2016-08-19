# -*- coding: utf-8 -*-

# $Id:$

from unittest import TestCase

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
                return d.items()

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
