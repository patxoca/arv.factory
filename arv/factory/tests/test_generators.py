# -*- coding: utf-8 -*-

from unittest import TestCase

import mock

from ..generators import Gen, count, cycle, mkgen
from ..generators import string


class TestGenerator(TestCase):

    def setUp(self):
        self.generator = Gen([1, 2])

    def test_iterates_over_sequence(self):
        self.assertEqual(self.generator.next(), 1)
        self.assertEqual(self.generator.next(), 2)

    def test_raises_StopIteration_when_iterable_exhausted(self):
        self.generator.next()
        self.generator.next()
        with self.assertRaises(StopIteration):
            self.generator.next()


class TestMkgen(TestCase):

    def test_type(self):
        self.assertIsInstance(mkgen(mock.Mock()), Gen)

    def test_function_is_called(self):
        function = mock.Mock()
        gen = mkgen(function)
        self.assertEqual(function.call_count, 0)
        gen.next()
        self.assertEqual(function.call_count, 1)
        gen.next()
        self.assertEqual(function.call_count, 2)

    def test_call_with_arguments(self):
        function = mock.Mock()
        gen = mkgen(function, 1, foo=1234)
        gen.next()
        self.assertEqual(function.call_args, ((1, ), {"foo": 1234}))
        gen.next()
        self.assertEqual(function.call_args, ((1, ), {"foo": 1234}))

    def test_return_value(self):
        function = mock.Mock(side_effect=[1, 2])
        gen = mkgen(function)
        self.assertEqual(gen.next(), 1)
        self.assertEqual(gen.next(), 2)


class TestCount(TestCase):

    def test_type(self):
        self.assertIsInstance(count(), Gen)

    def test_starts_by_zero_and_steps_by_one(self):
        c = count()
        self.assertEqual(c.next(), 0)
        self.assertEqual(c.next(), 1)
        self.assertEqual(c.next(), 2)
        self.assertEqual(c.next(), 3)

    def test_honors_start(self):
        c = count(start=42)
        self.assertEqual(c.next(), 42)
        self.assertEqual(c.next(), 43)
        self.assertEqual(c.next(), 44)
        self.assertEqual(c.next(), 45)

    def test_honors_step(self):
        c = count(step=3)
        self.assertEqual(c.next(), 0)
        self.assertEqual(c.next(), 3)
        self.assertEqual(c.next(), 6)
        self.assertEqual(c.next(), 9)


class TestCycle(TestCase):

    def test_type(self):
        self.assertIsInstance(cycle((1, 2)), Gen)

    def test_walks_over_sequence(self):
        c = cycle((1, 2))
        self.assertEqual(c.next(), 1)
        self.assertEqual(c.next(), 2)

    def test_restarts_walk_when_sequence_exhausted(self):
        c = cycle((1, 2))
        c.next()
        c.next()
        self.assertEqual(c.next(), 1)


class TestString(TestCase):

    def test_type(self):
        self.assertIsInstance(string(), Gen)

    def test_default_behaviour(self):
        c = string()
        self.assertEqual(c.next(), "0")
        self.assertEqual(c.next(), "1")
        self.assertEqual(c.next(), "2")

    def test_honors_format(self):
        c = string(format="%(value)02i")
        self.assertEqual(c.next(), "00")
        self.assertEqual(c.next(), "01")
        self.assertEqual(c.next(), "02")

    def test_honors_counter(self):
        c = string(counter=count(42, 3))
        self.assertEqual(c.next(), "42")
        self.assertEqual(c.next(), "45")
