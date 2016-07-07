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

Callables are more useful when used in *metafactories*.


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
values for the factories.

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

Both factories share the same generator. If we require independent
generators for each factory we can use a callable as the attribute's
value:

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
long as it returns a generator.
