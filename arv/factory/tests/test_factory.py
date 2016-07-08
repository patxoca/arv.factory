# -*- coding: utf-8 -*-

from unittest import TestCase

from ..base import DELETE, Factory
from ..generators import Gen


class TestProcessMetafactoryArguments(TestCase):

    def test_honors_DELETE(self):
        factory = Factory()
        d = {"foo": 1, "bar": DELETE}
        self.assertEqual(
            factory._process_metafactory_arguments(d),
            {"foo": 1}
        )

    def test_Gen_instances_are_not_evaluated(self):
        factory = Factory()
        d = {"foo": 1, "bar": Gen([1])}
        res = factory._process_metafactory_arguments(d)
        self.assertTrue(isinstance(res["bar"], Gen))

    def test_makes_value_generators_from_metafactories(self):
        factory = Factory()
        d = {"foo": 1, "bar": Factory}
        res = factory._process_metafactory_arguments(d)
        self.assertIsInstance(res["bar"], Gen)


class TestFactoryConstructor(TestCase):

    def setUp(self):
        class MyFactory(Factory):
            defaults = {"foo": 1, "bar": Gen([1, 2, 3])}
        self.MyFactory = MyFactory

    def test_collected_defaults(self):
        factory = self.MyFactory()
        self.assertEqual(len(factory._defaults), 2)
        self.assertIn("foo", factory._defaults)
        self.assertIn("bar", factory._defaults)

    def test_Gen_instances_are_not_evaluated(self):
        factory = self.MyFactory()
        self.assertIsInstance(factory._defaults["bar"], Gen)

    def test_kwargs_override_defaults(self):
        factory = self.MyFactory(foo=2)
        self.assertEqual(factory._defaults["foo"], 2)

    def test_kwargs_honors_DELETE(self):
        factory = self.MyFactory(foo=DELETE)
        self.assertNotIn("foo", factory._defaults)


class TestObjectCreation(TestCase):

    def setUp(self):
        self.factory = Factory(foo=1, bar=Gen([1, 2, 3, 4]))

    def test_literal_value(self):
        d = self.factory()
        self.assertEqual(d["foo"], 1)

    def test_generators_are_consumed(self):
        d = self.factory()
        self.assertEqual(d["bar"], 1)
        d = self.factory()
        self.assertEqual(d["bar"], 2)

    def test_honors_DELETE(self):
        d = self.factory(bar=DELETE)
        self.assertNotIn("bar", d)

    def test_DELETE_ignores_missing_attributes(self):
        self.assertNotIn("baz", self.factory._defaults)
        d = self.factory(baz=DELETE)
        self.assertNotIn("baz", d)

    def test_kwargs_override_defaults(self):
        d = self.factory(foo=3)
        self.assertEqual(d["foo"], 3)

    def test_kwarg_overriding_generator_dont_comsume_generator(self):
        d = self.factory(bar=42)
        self.assertEqual(d["bar"], 42)
        d = self.factory()
        self.assertEqual(d["bar"], 1)


class TestMany(TestCase):

    def setUp(self):
        self.factory = Factory(foo=1, bar=Gen([1, 2, 3, 4]))

    def test_negative_count_returns_empty_list(self):
        self.assertEqual(self.factory.many(-1), [])

    def test_number_of_objects(self):
        num_obj = 3
        res = self.factory.many(num_obj)
        self.assertEqual(len(res), num_obj)

    def test_objects_generated(self):
        res = self.factory.many(3)
        for i, d in enumerate(res):
            self.assertTrue(isinstance(d, dict))
            self.assertIn("foo", d)
            self.assertIn("bar", d)
            self.assertEqual(d["foo"], 1)
            self.assertEqual(d["bar"], i + 1)

    def test_consumes_generators_in_kwargs(self):
        res = self.factory.many(3, foo=Gen([0, 1, 4, 9]))
        for i, d in enumerate(res):
            self.assertEqual(d["foo"], i * i)
            self.assertEqual(d["bar"], i + 1)

    def test_kwarg_overriding_generator_dont_consume_generator(self):
        self.factory.many(2, bar=42)
        obj = self.factory()
        self.assertEqual(obj["bar"], 1)


class TestSpecifyingAlternateObjectConstructor(TestCase):

    def setUp(self):
        class Class(object):
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        class MyFactory(Factory):
            constructor = Class

        self.Class = Class
        self.MyFactory = MyFactory
        self.factory = MyFactory()

    def test_object_class(self):
        obj = self.factory(foo=1)
        self.assertIsInstance(obj, self.Class)

    def test_object_attributes(self):
        obj = self.factory(foo=1)
        self.assertEqual(obj.foo, 1)
