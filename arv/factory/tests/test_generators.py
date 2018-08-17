# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from builtins import next
from builtins import range

from unittest import TestCase

import mock

from ..generators import Gen, choice, count, cycle, lazy, mkconstructor, mkgen
from ..generators import string


class TestGenerator(TestCase):

    def setUp(self):
        self.generator = Gen([1, 2])

    def test_iterates_over_sequence(self):
        self.assertEqual(next(self.generator), 1)
        self.assertEqual(next(self.generator), 2)

    def test_raises_StopIteration_when_iterable_exhausted(self):
        next(self.generator)
        next(self.generator)
        with self.assertRaises(StopIteration):
            next(self.generator)

    def test_wrapping_a_Gen_in_a_Gen_returns_the_original_Gen(self):
        g = Gen(self.generator)
        self.assertIs(g, self.generator)


class TestLazy(TestCase):

    def test_calling_lazy_object_calls_function(self):
        f = mock.Mock(return_value=iter([]))
        l = lazy(f, 1, foo=42)
        self.assertEqual(f.call_count, 0)
        r = l()
        self.assertEqual(f.call_count, 1)
        self.assertEqual(f.call_args, ((1, ), {"foo": 42}))

    def test_lazy_returns_a_value_generator(self):
        f = mock.Mock(return_value=iter([]))
        l = lazy(f)
        r = l()
        self.assertIsInstance(r, Gen)

    def test_raises_TypeError_if_argument_not_callable(self):
        with self.assertRaises(TypeError):
            lazy(2)


class TestMkgen(TestCase):

    def test_type(self):
        self.assertIsInstance(mkgen(mock.Mock()), Gen)

    def test_function_is_called(self):
        function = mock.Mock()
        gen = mkgen(function)
        self.assertEqual(function.call_count, 0)
        next(gen)
        self.assertEqual(function.call_count, 1)
        next(gen)
        self.assertEqual(function.call_count, 2)

    def test_call_with_arguments(self):
        function = mock.Mock()
        gen = mkgen(function, 1, foo=1234)
        next(gen)
        self.assertEqual(function.call_args, ((1, ), {"foo": 1234}))
        next(gen)
        self.assertEqual(function.call_args, ((1, ), {"foo": 1234}))

    def test_return_value(self):
        function = mock.Mock(side_effect=[1, 2])
        gen = mkgen(function)
        self.assertEqual(next(gen), 1)
        self.assertEqual(next(gen), 2)


class TestCount(TestCase):

    def test_type(self):
        self.assertIsInstance(count(), Gen)

    def test_starts_by_zero_and_steps_by_one(self):
        c = count()
        self.assertEqual(next(c), 0)
        self.assertEqual(next(c), 1)
        self.assertEqual(next(c), 2)
        self.assertEqual(next(c), 3)

    def test_honors_start(self):
        c = count(start=42)
        self.assertEqual(next(c), 42)
        self.assertEqual(next(c), 43)
        self.assertEqual(next(c), 44)
        self.assertEqual(next(c), 45)

    def test_honors_step(self):
        c = count(step=3)
        self.assertEqual(next(c), 0)
        self.assertEqual(next(c), 3)
        self.assertEqual(next(c), 6)
        self.assertEqual(next(c), 9)


class TestCycle(TestCase):

    def test_type(self):
        self.assertIsInstance(cycle((1, 2)), Gen)

    def test_walks_over_sequence(self):
        c = cycle((1, 2))
        self.assertEqual(next(c), 1)
        self.assertEqual(next(c), 2)

    def test_restarts_walk_when_sequence_exhausted(self):
        c = cycle((1, 2))
        next(c)
        next(c)
        self.assertEqual(next(c), 1)


class TestString(TestCase):

    def test_type(self):
        self.assertIsInstance(string(), Gen)

    def test_default_behaviour(self):
        c = string()
        self.assertEqual(next(c), "0")
        self.assertEqual(next(c), "1")
        self.assertEqual(next(c), "2")

    def test_honors_format(self):
        c = string(format="%02i")
        self.assertEqual(next(c), "00")
        self.assertEqual(next(c), "01")
        self.assertEqual(next(c), "02")

    def test_honors_counter(self):
        c = string(counter=count(42, 3))
        self.assertEqual(next(c), "42")
        self.assertEqual(next(c), "45")


class TestMkConstructor(TestCase):

    def setUp(self):
        pass

    def test_returns_a_lazy_object(self):
        c = mkconstructor([])
        self.assertIsInstance(c, lazy)

    def test_returns_a_Gen_factory(self):
        c = mkconstructor([])
        g = c()
        self.assertIsInstance(g, Gen)

    def test_creates_a_new_iterable_on_each_call(self):
        c = mkconstructor([1, 2])
        g1 = c()
        g2 = c()
        self.assertEqual(next(g1), 1)
        self.assertEqual(next(g2), 1)

    def test_evaluates_callables(self):
        def generator_function():
            yield 1
        c = mkconstructor(generator_function)
        g = c()
        self.assertEqual(next(g), 1)

    def test_evaluates_callables_on_each_call(self):
        def generator_function():
            yield 1
        c = mkconstructor(generator_function)
        g1 = c()
        self.assertEqual(next(g1), 1)
        g2 = c()
        self.assertEqual(next(g2), 1)

    def test_passes_arguments_to_callable(self):
        def generator_function(a, b):
            while a <= b:
                yield a
                a += 1
        c = mkconstructor(generator_function, 3, 5)
        g = c()
        self.assertEqual(next(g), 3)
        self.assertEqual(next(g), 4)
        self.assertEqual(next(g), 5)
        with self.assertRaises(StopIteration):
            next(g)


class TestChoice(TestCase):

    def test_type(self):
        self.assertIsInstance(choice((1, 2)), Gen)

    def test_returns_elements_from_the_sequence(self):
        choices = list(range(10))  # py 3
        c = choice(choices)
        for i in range(10 * len(choices)):
            self.assertIn(next(c), choices)
