.. -*- ispell-local-dictionary: "british" -*-

**************
Advanced usage
**************

.. _sect_advanced_usage-lazy:

lazy
====

As an special case, if the callable returns an iterable ``lazy`` will
wrap the returned value within a ``Gen`` instance:

.. doctest::

   >>> from itertools import cycle
   >>> class PetFactory(Factory):
   ...     defaults = {
   ...         "name": "Rocky",
   ...         "kind": lazy(cycle, ["dog", "cat"]),
   ...     }
   ...
   >>> factory = PetFactory()
   >>> factory()
   {'kind': 'dog', 'name': 'Rocky'}
   >>> factory()
   {'kind': 'cat', 'name': 'Rocky'}
   >>> factory()
   {'kind': 'dog', 'name': 'Rocky'}

Another usage for ``lazy`` is overriding default values when creating
factories. Metafactories as default values are already lazily
evaluated but they receive no arguments. Wrapping them with ``lazy``
allow us to override the default values:

.. doctest::

   >>> class PersonFactory(Factory):
   ...     defaults = {
   ...         "name": "Bob",
   ...         "pet": lazy(PetFactory, name="Toby"),
   ...     }
   ...
   >>> factory1 = PersonFactory()
   >>> factory2 = PersonFactory()
   >>> factory1()
   {'pet': {'kind': 'dog', 'name': 'Toby'}, 'name': 'Bob'}
   >>> factory2()
   {'pet': {'kind': 'dog', 'name': 'Toby'}, 'name': 'Bob'}

Defining a custom generator
===========================

Let's say we need a value generator for the fibonacci sequence. All we
need is an iterable with the sequence's values, a python generator
function is a good choice:

.. doctest::

   >>> def fib():
   ...     a, b = 0, 1
   ...     while True:
   ...         yield a
   ...         a, b = b, a + b
   ...
   >>> g = fib()
   >>> g.next()
   0
   >>> g.next()
   1
   >>> g.next()
   1
   >>> g.next()
   2

Now we can create a factory:

.. doctest::

   >>> g = fib()
   >>> factory = Factory(n=Gen(g))
   >>> factory()
   {'n': 0}
   >>> factory()
   {'n': 1}

Alternatively we can use the ``mkgen`` function:

.. doctest::

   >>> g = fib()
   >>> factory = Factory(n=gen.mkgen(g.next))
   >>> factory()
   {'n': 0}
   >>> factory()
   {'n': 1}

If we plan to use the generator in many factories it would be better
definning a *constructor* and a metafactory:

.. doctest::

   >>> def Fib():
   ...     iterable = fib()
   ...     return gen.mkgen(fib().next)

Here we create an interable, a python generator, calling the
*generator function* ``fib``, then we call ``mkgen`` passing the
``next`` method from the iterable. Remember? ``mkgen`` creates a value
generator wich will call the function it receives as argument each
time it's consumed.

.. doctest::

   >>> class MyFactory(Factory):
   ...     defaults = {"n": lazy(Fib)}
   ...
   >>> factory = MyFactory()
   >>> factory()
   {'n': 0}

``Fib`` is a function and metafactories don't evaluate functions, only
``lazy`` instances, so we need to wrap ``Fib`` with ``lazy`` in order
to get it called at factory creation time.

If we want to avoid having to use lazy explicitly we can do:

.. doctest::

   >>> FIB = lazy(Fib)
   >>> class MyFactory(Factory):
   ...     defaults = {"n": FIB}
   ...
   >>> factory = MyFactory()
   >>> factory()
   {'n': 0}

That's a lot of repetitive work so ``arv.factory`` defines a shortcut
for this:

.. doctest::

   >>> Fib = gen.mkconstructor(fib)
   >>> class MyFactory(Factory):
   ...     defaults = {"n": Fib}
   ...
   >>> factory = MyFactory()
   >>> factory()
   {'n': 0}

In a previous example (:ref:`sect_advanced_usage-lazy`) we have seen
how to use ``lazy`` + ``cycle``. Alternatively we can create a lazy
constructor:

.. doctest::

   >>> Cycle = gen.mkconstructor(cycle, (2, 4, 8))


Defining a persistent factory
=============================

In case that ``arv.factory`` does not provide a persitent factory for
your backend defining a new one is easy as cake.

A persistent factory must inherit from :class:`PersitanceMixin` and
some factory class and must implement the methods ``_is_persistable``
and ``_save``.

- ``_is_persistable`` receives a value and returns ``True`` if it's
  persistable by the backend. Usually it's enough testing is the
  object is an instance of some class, ``django.db.models.Model`` by
  the way, or if it has some *distinguished* attribute or method.

- ``_save`` receives an object and is responsible for persisting the
  object to the backend. It's guaranteed that it will be called only
  for objects that pass the ``_is_persistable`` check.

As an example here's the implementations for ``DjangoFactory``:

.. code-block:: python


   class DjangoFactory(PersistanceMixin, Factory):
       """Factory for creating django models.
       """

       def _is_persistable(self, obj):
           return hasattr(obj, "save") and callable(obj.save)

       def _save(self, obj):
           return obj.save()

The only thing worth noting is that ``_is_persistable`` checks for the
presence of ``save`` method in the object instead of checking if it's
an instance of ``django.db.models.Model``. It's done that way in order
to avoid a dependency from django, so that people using the library
for other backends don't get django installed.
