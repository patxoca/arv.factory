# -*- coding: utf-8 -*-

import inspect
import itertools
from unittest import TestCase

from ..base import DELETE, Factory, escape


class TestProcessDefaults(TestCase):

    def test_honors_DELETE(self):
        factory = Factory()
        d = {"foo": 1, "bar": DELETE}
        self.assertEqual(
            factory._process_defaults(d),
            {"foo": 1}
        )

    def test_calls_generator_functions(self):
        def generator():
            yield 1
        factory = Factory()
        d = {"foo": 1, "bar": generator}
        self.assertTrue(inspect.isgeneratorfunction(d["bar"]))
        res = factory._process_defaults(d)
        self.assertTrue(inspect.isgenerator(res["bar"]))

    def test_calls_functions(self):
        def function():
            return 42
        factory = Factory()
        d = {"foo": 1, "bar": function}
        res = factory._process_defaults(d)
        self.assertEqual(res["bar"], 42)

    def test_escape_callable(self):
        def function():
            return 42
        factory = Factory()
        d = {"foo": 1, "bar": escape(function)}
        res = factory._process_defaults(d)
        self.assertIs(res["bar"], function)


class TestConstructor(TestCase):

    def setUp(self):
        class MyFactory(Factory):
            defaults = {"foo": 1}
        self.MyFactory = MyFactory

    def test_kwargs_override_defaults(self):
        factory = self.MyFactory(foo=2)
        self.assertEqual(factory._defaults["foo"], 2)

    def test_kwargs_honors_DELETE(self):
        factory = self.MyFactory(foo=DELETE)
        self.assertNotIn("foo", factory._defaults)


class TestDict(TestCase):

    def setUp(self):
        def generator():
            i = 1
            while True:
                yield i
                i = i + 1

        class MyFactory(Factory):
            defaults = {
                "foo": 1,
                "bar": generator,
            }
        self.factory = MyFactory()

    def test_scalar_value(self):
        d = self.factory()
        self.assertEqual(d["foo"], 1)

    def test_generator_value(self):
        d = self.factory()
        self.assertEqual(d["bar"], 1)
        d = self.factory()
        self.assertEqual(d["bar"], 2)

    def test_honors_DELETE(self):
        d = self.factory(bar=DELETE)
        self.assertNotIn("bar", d)

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
        def generator():
            i = 1
            while True:
                yield i
                i = i + 1

        class MyFactory(Factory):
            defaults = {
                "foo": 1,
                "bar": generator,
            }
        self.factory = MyFactory()

    def test_negative_count_returns_empty_list(self):
        self.assertEqual(self.factory.many(-1), [])

    def test_number_of_objects(self):
        num_obj = 10
        res = self.factory.many(num_obj)
        self.assertEqual(len(res), num_obj)
        for i in range(num_obj):
            d = res[i]
            self.assertTrue(isinstance(d, dict))
            self.assertIn("foo", d)
            self.assertIn("bar", d)
            self.assertEqual(d["foo"], 1)
            self.assertEqual(d["bar"], i + 1)

    def test_consumes_generators_in_kwargs(self):
        num_obj = 10
        res = self.factory.many(num_obj, foo=(i * i for i in itertools.count()))
        for i in range(num_obj):
            d = res[i]
            self.assertEqual(d["foo"], i * i)
            self.assertEqual(d["bar"], i + 1)

    def test_kwarg_overriding_generator_dont_consume_generator(self):
        num_obj = 1
        res = self.factory.many(num_obj, bar=(i * i for i in itertools.count()))
        obj = self.factory()
        self.assertEqual(obj["bar"], 1)


class TestAlternateConstructor(TestCase):

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
