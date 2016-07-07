.. -*- ispell-local-dictionary: "british" -*-

********
Tutorial
********

In the simplest case creating a factory requires one line of code, not
counting the imports:

.. doctest::

   >>> from arv.factory.api import Factory
   >>> factory = Factory(name="Bob")

From now on we can use the factory to create objects:

.. doctest::

   >>> obj = factory()
   >>> obj
   {'name': 'Bob'}

Objects created with the factory may look the same but are independent
from each other:

.. doctest::

   >>> obj1 = factory()
   >>> obj2 = factory()
   >>> obj1, obj2
   ({'name': 'Bob'}, {'name': 'Bob'})
   >>> obj1["name"] = "Alice"
   >>> obj1, obj2
   ({'name': 'Alice'}, {'name': 'Bob'})

The factory we just created is a bit boring, objects always have the
same value for the ``name`` attribute. We can override an attribute's
value by passing the desired value to the factory as a keyword
argument:

.. doctest::

   >>> alice = factory(name="Alice")
   >>> alice
   {'name': 'Alice'}

The class ``Factory`` is *schemaless* so it can't check if an
attribute is allowed or not. Factories created this way will accept
silently any keyword argument:

.. doctest::

    >>> eve = factory(name="Eve", age=42)
    >>> eve
    {'age': 42, 'name': 'Eve'}


Special value types
===================

``Factory`` accepts generators as values for the attributes:

.. doctest::

   >>> names = ("Bob", "Alice")
   >>> factory = Factory(name=(i for i in names))
   >>> for i in range(2):
   ...     obj = factory()
   ...     print(obj["name"])
   Bob
   Alice

Every object created by the factory consumes one item from the
generator. Creating an object when the generator is exhausted will
raise an exception.

An exception for the previous rule is that specifying a value for a
*generated* attribute don't consumes the generator:

.. doctest::

   >>> factory = Factory(name=(i for i in names))
   >>> factory()
   {'name': 'Bob'}
   >>> factory(name="Eve")
   {'name': 'Eve'}
   >>> factory()
   {'name': 'Alice'}

.. note:: at that point explaining callables may be confusing,
          consider moving it after explaining how factories work.

Callables also are treated specially when creating a factory, they are
called without arguments, when creating the factory not the objects,
and the returned value is used as the attribute's default value:

.. doctest::

   >>> def function():
   ...     return 42
   ...
   >>> factory = Factory(name="Bob", age=function)
   >>> factory()
   {'age': 42, 'name': 'Bob'}

If the actual value is a function we need to *escape* it in order to
avoid the call:

.. doctest::

   >>> from arv.factory.api import escape
   >>> factory = Factory(called=function, not_called=escape(function))
   >>> obj = factory()
   >>> callable(obj["called"])
   False
   >>> callable(obj["not_called"])
   True

In that context we can think about callables as constructors for the
actual value of the attribute. The primary usage of callables is in
conjunction with generators in *metafactories* and in more advanced
usage patterns (see :ref:`sect-complex-objects`).


.. note:: generators and callables are treated specially only when
          creating the factory, when creating the objects they are
          copied verbatim to the resulting object.


Removing attributes
===================

Ocasionally, in order to perform some testing, we may need to remove
an attribute from the generated object, that can be accomplished
specifying ``DELETE`` as the attribute's value:

.. doctest::

   >>> from arv.factory.api import DELETE
   >>> factory = Factory(name="Bob")
   >>> empty = factory(name=DELETE)
   >>> empty
   {}


Creating many objects
=====================

If we need to create many objects we can create them with just one
call to the ``many`` method:

.. doctest::

   >>> factory = Factory(
   ...     name=(i for i in ("Bob", "Alice")),
   ...     age=42,
   ... )
   >>> factory.many(2)
   [{'age': 42, 'name': 'Bob'}, {'age': 42, 'name': 'Alice'}]

``many`` also accepts generators as keyword arguments:

.. doctest::

   >>> factory = Factory(
   ...     name=(i for i in ("Bob", "Alice")),
   ...     age=42,
   ... )
   >>> factory.many(2, age=(i for i in (42, 39)))
   [{'age': 42, 'name': 'Bob'}, {'age': 39, 'name': 'Alice'}]


Metafactories
=============

A *metafactory* is just a class whose instances are factories.
``Factory`` is a metafactory.

The main use case for defining metafactories is providing default
values for the factories and easing code reusage.

.. doctest::

   >>> class MyFactory(Factory):
   ...     defaults = {
   ...         "name": "Bob",
   ...         "age": 42,
   ...     }
   ...
   >>> factory = MyFactory()
   >>> factory()
   {'age': 42, 'name': 'Bob'}

In the previous example we don't provide default values when creating
the factory.

Default values can be overriden as usual when creating a factory:

.. doctest::

   >>> factory = MyFactory(name="Alice")
   >>> factory()
   {'age': 42, 'name': 'Alice'}

That's useful when the objects have a lot of attributes and we need to
create many factories with small variations i order to perform some
specific testing.


Creating other types of objects
===============================

In the examples we have seen so far the factories created dictionaries
but usually we want to create other types of objects, instances for
som class a django model etc. That can be accomplished defining a new
metafactory with a *constructor* class attribute. The value of that
attribute must be a callable that accepts keyword arguments an returns
an *object* of the intended type, a *class* is the natural choice but
any callable can do:

.. doctest::

   >>> class MyClass(object):
   ...     def __init__(self, name, age):
   ...         self.name = name
   ...         self.age = age
   ...
   >>> class MyFactory(Factory):
   ...     defaults = {"name": "Bob", "age": 42}
   ...     constructor = MyClass
   ...
   >>> factory = MyFactory()
   >>> obj = factory()
   >>> isinstance(obj, MyClass)
   True
   >>> obj.name
   'Bob'
   >>> obj.age
   42


How does factory creation work
==============================



Generators and metafactories
============================

Consider the following example:

.. doctest::

   >>> class MyFactory(Factory):
   ...     defaults = {
   ...         "name": "Bob",
   ...         "age": (i for i in xrange(10)),
   ...     }
   ...
   >>> factory_1 = MyFactory()
   >>> factory_2 = MyFactory()
   >>> factory_1()["age"]
   0
   >>> factory_2()["age"]
   1
   >>> factory_1()["age"]
   2

The problem here is that the generator for the ``age`` attribute is
created when the metafactory is defined, not when the factories are
created, so both ``factory_1`` and ``factory_2`` share the same
generator.

If we require independent generators for each factory we can use a
callable as the attribute's value so that the generator creation is
delayed until the factory is created:

.. doctest::

   >>> def my_generator():
   ...     for i in xrange(10):
   ...         yield i
   ...
   >>> class MyFactory(Factory):
   ...     defaults = {
   ...         "name": "Bob",
   ...         "age": my_generator,
   ...     }
   ...
   >>> factory_1 = MyFactory()
   >>> factory_2 = MyFactory()
   >>> factory_1()["age"]
   0
   >>> factory_2()["age"]
   0
   >>> factory_1()["age"]
   1

In the example we used a *generator function* but any callable will do
(any object for wich the ``callable`` builtin returns ``True``) as
long as it returns a generator:

.. doctest::

   >>> class MyFactory(Factory):
   ...     defaults = {
   ...         "name": "Bob",
   ...         "age": lambda: (i for i in xrange(10)),
   ...     }
   ...
   >>> factory_1 = MyFactory()
   >>> factory_2 = MyFactory()
   >>> factory_1()["age"]
   0
   >>> factory_2()["age"]
   0
   >>> factory_1()["age"]
   1

In that example whe use ``lambda`` to create an anonymous function.


Builtin generators
==================

``arv.factory`` defines some generators that may be useful when
defining factories. Take a look at the API documentation for a
complete list.

For the sake of the tutorial we will introduce the ``mkgen`` and
``cycle`` generators.

``mkgen`` takes a function (any callable) and its arguments and
creates an infinite generator that calls the function every time the
generator is consumed:

.. doctest::

   >>> from arv.factory.api import gen
   >>> def myfunction(a, b):
   ...     return "a=%s b=%s" % (a, b)
   ...
   >>> g = gen.mkgen(myfunction, 1, b=2)
   >>> g.next()
   'a=1 b=2'
   >>> g.next()
   'a=1 b=2'

A more useful example would be using a random number generator:

.. code-block:: python

   >>> from random import randint
   >>> g = gen.mkgen(randint, 0, 100)
   >>> g.next()
   50
   >>> g.next()
   85

In the section :ref:`sect-complex-objects` we'll see a more powerful
usage of ``mkgen``.

``cycle`` is the generator version of the ``itertools.cycle``
function:

.. doctest::

   >>> g = gen.cycle((1, 2))
   >>> g.next()
   1
   >>> g.next()
   2
   >>> g.next()
   1


.. _sect-complex-objects:

Complex objects
===============

Let's say we have *persons* and *pets*, where each person has one pet
in its ``pet`` attribute. How do we define a factory for creating
persons with pets?

First at all we need a factory for pets:

.. doctest::

   >>> pet_factory = Factory(
   ...     name="Rocky",
   ...     kind=gen.cycle(("dog", "cat", "snake"))
   ... )

We use the ``cycle`` generator to make the example a bit more
interesting.

Now we need a factory for persons wich, somehow, uses the
``pet_factory`` to create pets. Well, note that in order to create
objects we call the factory, factories are callables so we can use
``mkgen`` to create a generator that calls ``pet_factory`` in order to
create pets:

.. doctest::

   >>> person_factory = Factory(
   ...     name="Bob",
   ...     pet=gen.mkgen(pet_factory)
   ... )
   >>> person_factory()
   {'pet': {'kind': 'dog', 'name': 'Rocky'}, 'name': 'Bob'}
   >>> person_factory(name="Alice")
   {'pet': {'kind': 'cat', 'name': 'Rocky'}, 'name': 'Alice'}

In that example there is only one factory for pets, so creating more
pets will continue from where it left off:

.. doctest::

   >>> pet_factory()
   {'kind': 'snake', 'name': 'Rocky'}

If that's a problem we can resort to metafactories:

.. doctest::

   >>> class PetFactory(Factory):
   ...     defaults = {
   ...         "name": "Rocky",
   ...         "kind": lambda: gen.cycle(("dog", "cat", "snake")),
   ...     }
   ...
   >>> class PersonFactory(Factory):
   ...     defaults = {
   ...         "name": "Bob",
   ...         "pet": lambda: gen.mkgen(PetFactory())
   ...     }
   ...
   >>> factory = PersonFactory()
   >>> factory()
   {'pet': {'kind': 'dog', 'name': 'Rocky'}, 'name': 'Bob'}
   >>> factory()
   {'pet': {'kind': 'cat', 'name': 'Rocky'}, 'name': 'Bob'}
   >>> factory2 = PersonFactory()
   >>> factory2()
   {'pet': {'kind': 'dog', 'name': 'Rocky'}, 'name': 'Bob'}
   >>> factory2()
   {'pet': {'kind': 'cat', 'name': 'Rocky'}, 'name': 'Bob'}

Note the usage of ``lambda`` to create anonymous functions in order to
delay the creation of the ``kind`` and ``pet`` generators until the
factory is created.

Those examples may seem a bit contribed at first but that's because
they try to illustrate factory reusability. The first example could be
rewriten as:

.. doctest::

   >>> person_factory = Factory(
   ...     name="Bob",
   ...     pet=gen.mkgen(Factory(
   ...         name="Rocky",
   ...         kind=gen.cycle(("dog", "cat", "snake"))
   ...     ))
   ... )
   >>> person_factory()
   {'pet': {'kind': 'dog', 'name': 'Rocky'}, 'name': 'Bob'}
   >>> person_factory(name="Alice")
   {'pet': {'kind': 'cat', 'name': 'Rocky'}, 'name': 'Alice'}

But this is less readable and will introduce code duplication if you
need another pet factory somewhere.
