# -*- coding: utf-8 -*-

from unittest import TestCase

import mock

from ..base import DELETE, Factory
from ..generators import Gen, lazy


class TestProcessMetafactoryDefaults(TestCase):

    def setUp(self):
        self.factory = Factory()

    def test_returns_a_new_dictionary(self):
        d = {"foo": 1}
        res = self.factory._process_metafactory_defaults(d)
        self.assertIsInstance(res, dict)
        self.assertIsNot(res, d)

    def test_literal_values_are_copied_verbatim(self):
        d = {"foo": 1}
        res = self.factory._process_metafactory_defaults(d)
        self.assertEqual(res["foo"], 1)

    def test_ignores_DELETE(self):
        d = {"foo": DELETE}
        res = self.factory._process_metafactory_arguments(d)
        self.assertIn("foo", res)
        self.assertIs(res["foo"], DELETE)

    def test_Gen_instances_are_not_evaluated(self):
        d = {"foo": 1, "bar": Gen([1])}
        res = self.factory._process_metafactory_defaults(d)
        self.assertTrue(isinstance(res["bar"], Gen))

    def test_evaluates_metafactories(self):
        d = {"foo": 1, "bar": Factory}
        res = self.factory._process_metafactory_defaults(d)
        self.assertIsInstance(res["bar"], Factory)

    def test_evaluates_lazy_objects(self):
        f = mock.Mock(return_value=iter([]))
        d = {"foo": lazy(f)}
        self.assertEqual(f.call_count, 0)
        res = self.factory._process_metafactory_defaults(d)
        self.assertEqual(f.call_count, 1)
        self.assertIsInstance(res["foo"], Gen)

    def test_attribute_exclusion(self):
        d = {"foo": 1, "bar": 2}
        res = self.factory._process_metafactory_defaults(d, exclude=("bar", ))
        self.assertNotIn("bar", res)


class TestProcessMetafactoryArguments(TestCase):

    def setUp(self):
        self.factory = Factory()

    def test_returns_a_new_dictionary(self):
        d = {"foo": 1}
        res = self.factory._process_metafactory_arguments(d)
        self.assertIsInstance(res, dict)
        self.assertIsNot(res, d)

    def test_literal_values_are_copied_verbatim(self):
        d = {"foo": 1}
        res = self.factory._process_metafactory_arguments(d)
        self.assertEqual(res["foo"], 1)

    def test_honors_DELETE(self):
        d = {"foo": DELETE}
        res = self.factory._process_metafactory_arguments(d)
        self.assertNotIn("foo", res)

    def test_Gen_instances_are_not_evaluated(self):
        d = {"foo": Gen([1])}
        res = self.factory._process_metafactory_arguments(d)
        self.assertTrue(isinstance(res["foo"], Gen))

    def test_evaluates_factories(self):
        d = {"foo": Factory()}
        res = self.factory._process_metafactory_arguments(d)
        self.assertIsInstance(res["foo"], Gen)


class TestEvalFactoryArguments(TestCase):

    def setUp(self):
        self.factory = Factory()

    def test_returns_a_new_dictionary(self):
        d = {"foo": 1}
        res = self.factory._eval_factory_arguments(d)
        self.assertIsInstance(res, dict)
        self.assertIsNot(res, d)

    def test_literal_values_are_copied_verbatim(self):
        d = {"foo": 1}
        res = self.factory._eval_factory_arguments(d)
        self.assertEqual(res["foo"], 1)

    def test_consumes_value_generators(self):
        d = {"foo": Gen([42])}
        res = self.factory._eval_factory_arguments(d)
        self.assertEqual(res["foo"], 42)

    def test_ignores_DELETE(self):
        d = {"foo": DELETE}
        res = self.factory._eval_factory_arguments(d)
        self.assertIn("foo", res)
        self.assertIs(res["foo"], DELETE)

    def test_attribute_exclusion(self):
        d = {"foo": 1, "bar": 2}
        res = self.factory._eval_factory_arguments(d, exclude=("bar", ))
        self.assertNotIn("bar", res)


class TestIsConstructor(TestCase):

    def setUp(self):
        self.factory = Factory()

    def test_metafactories_are_constructors(self):
        self.assertTrue(self.factory._is_contructor(Factory))

    def test_lazy_objects_are_constructors(self):
        f = mock.Mock(return_value=iter([]))
        self.assertTrue(self.factory._is_contructor(lazy(f)))

    def test_functions_are_not_constructors(self):
        self.assertFalse(self.factory._is_contructor(lambda x: x))

    def test_classes_are_not_constructors(self):
        self.assertFalse(self.factory._is_contructor(object))


class TestMetafactoryConstructor(TestCase):

    def setUp(self):
        class MyFactory(Factory):
            defaults = {
                "foo": 1,
                "bar": Gen([1, 2, 3]),
                "baz": Factory
            }
        self.MyFactory = MyFactory

    def test_collected_defaults(self):
        factory = self.MyFactory()
        self.assertEqual(len(factory._defaults), 3)
        self.assertIn("foo", factory._defaults)
        self.assertIn("bar", factory._defaults)
        self.assertIn("baz", factory._defaults)

    def test_kwargs_override_defaults(self):
        factory = self.MyFactory(foo=2)
        self.assertEqual(factory._defaults["foo"], 2)

    def test_kwargs_honors_DELETE(self):
        factory = self.MyFactory(foo=DELETE)
        self.assertNotIn("foo", factory._defaults)

    def test_kwargs_honors_factories(self):
        factory = self.MyFactory(foo=Factory())
        self.assertIsInstance(factory._defaults["baz"], Gen)

    def test_makes_value_generators_from_metafactories(self):
        factory = self.MyFactory()
        self.assertIsInstance(factory._defaults["baz"], Gen)


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
