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
value when creating an object by passing the desired value as a
keyword argument:

.. doctest::

   >>> alice = factory(name="Alice")
   >>> alice
   {'name': 'Alice'}

The ``Factory`` class is *schemaless* so it can't check if an
attribute is allowed or not neither its type. Factories created this
way will silently accept any keyword argument of any type:

.. doctest::

    >>> factory = Factory()
    >>> eve = factory(name=42, age="Eve")
    >>> eve
    {'age': 'Eve', 'name': 42}

Another way to get objects with different values is using *value
generators*:

.. doctest::

   >>> from arv.factory.api import gen
   >>> factory = Factory(name=gen.Gen(["Bob", "Alice", "Eve"]))
   >>> factory()
   {'name': 'Bob'}
   >>> factory()
   {'name': 'Alice'}
   >>> factory()
   {'name': 'Eve'}

Note the use of ``Gen`` in the keyword argument ``name`` when creating
the factory. ``Gen`` creates a *value generator* from any iterable.
From now on we'll refer to *value generators* simply as *generators*.
Not to confuse with python generators.

.. warning:: generators are allowed only when defining or creating a
             factory not when creating objects.

.. warning:: Trying to create new objects once the generator is
             exhausted will raise an ``StopIteration`` exception:

             .. doctest::

                >>> factory()
                Traceback (most recent call last):
                ...
                StopIteration

Finally, if an attribute of our objects is itself an object we can
nest factories:

.. doctest::

   >>> pet_factory = Factory(
   ...     name="Rocky",
   ...     kind=gen.Gen(["dog", "cat", "snake"])
   ... )
   >>> factory = Factory(
   ...     name=gen.Gen(["Bob", "Alice"]),
   ...     pet=pet_factory
   ... )
   >>> factory()
   {'pet': {'kind': 'dog', 'name': 'Rocky'}, 'name': 'Bob'}
   >>> factory()
   {'pet': {'kind': 'cat', 'name': 'Rocky'}, 'name': 'Alice'}

When nesting factories we can override attributes in the subobjects
using the *double underscore* syntax:

.. doctest::

   >>> pet_factory = Factory(name="Rocky", kind="dog")
   >>> factory = Factory(name="Bob", pet=pet_factory)
   >>> factory(pet__name="Toby")
   {'pet': {'kind': 'dog', 'name': 'Toby'}, 'name': 'Bob'}

The double underscore syntax only works when creating objects.


Creating many objects
=====================

Sometimes we need to create many objects. As a matter of convenience
factories define the ``many`` method so we can create as many objects
as required with just one call:

.. doctest::

   >>> factory = Factory(
   ...     name=gen.Gen(["Bob", "Alice"]),
   ...     age=42,
   ... )
   >>> factory.many(2)
   [{'age': 42, 'name': 'Bob'}, {'age': 42, 'name': 'Alice'}]

``many`` also accepts generators as keyword arguments:

.. doctest::

   >>> factory = Factory(
   ...     name=gen.Gen(["Bob", "Alice"]),
   ...     age=42,
   ... )
   >>> factory.many(2, age=gen.Gen([42, 39]))
   [{'age': 42, 'name': 'Bob'}, {'age': 39, 'name': 'Alice'}]


Removing attributes
===================

Ocasionally, in order to perform some testing, we may need to remove
some attribute from the generated object, that can be accomplished
specifying ``DELETE`` as the attribute's value:

.. doctest::

   >>> from arv.factory.api import DELETE
   >>> factory = Factory(name="Bob")
   >>> empty = factory(name=DELETE)
   >>> empty
   {}


Metafactories
=============

A *metafactory* is just a class whose instances are factories. We
could have called them just *factory classes*, but *metafactories*
sounds fancier. ``Factory`` is the base metafactory, any metafactory
must derivate from ``Factory`` or some of it's subclasses.

The main use case for metafactories is code reuse:

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
the factory, the defaults from ``MyFactory`` are used.

Default values can be overriden as usual when creating a factory and
when creating objects:

.. doctest::

   >>> alice_factory = MyFactory(name="Alice")
   >>> alice_factory(age=39)
   {'age': 39, 'name': 'Alice'}

That's useful when we need to create many factories with small
variations in order to perform some specific testing.

In a metafactory definition we can also specify a factory or a
metafactory as the default value for any attribute.

..
   When specifying a factory it
   will be shared by all factories:

   .. doctest::

      >>> pet_factory = Factory(name="Rocky", kind=gen.Gen(["dog", "cat"]))
      >>> class MyFactory(Factory):
      ...     defaults = {
      ...         "name": "Bob",
      ...         "pet": pet_factory,
      ...     }
      ...
      >>> factory1 = MyFactory()
      >>> factory2 = MyFactory()
      >>> factory1()
      {'pet': {'kind': 'dog', 'name': 'Rocky'}, 'name': 'Bob'}
      >>> factory2()
      {'pet': {'kind': 'cat', 'name': 'Rocky'}, 'name': 'Bob'}

   In this example both ``factory1`` and ``factory2`` share
   ``pet_factory``, so ``factory2`` continues creating pets from where
   ``factory1`` left off.

   If we need a new *subfactory* just specify a metafactory:

   .. doctest::

      >>> class PetFactory(Factory):
      ...     defaults = {
      ...         "name": "Rocky",
      ...         "kind": gen.Gen(["dog", "cat"]),
      ...     }
      ...
      >>> class MyFactory(Factory):
      ...     defaults = {
      ...         "name": "Bob",
      ...         "pet": PetFactory,
      ...     }
      ...
      >>> factory1 = MyFactory()
      >>> factory2 = MyFactory()
      >>> factory1()
      {'pet': {'kind': 'dog', 'name': 'Rocky'}, 'name': 'Bob'}
      >>> factory2()
      {'pet': {'kind': 'dog', 'name': 'Rocky'}, 'name': 'Bob'}


Pitfalls using metafactories
============================

Consider the following example:

.. doctest::

   >>> class PetFactory(Factory):
   ...     defaults = {
   ...         "name": "Rocky",
   ...         "kind": gen.Gen(["dog", "cat"]),
   ...     }
   ...
   >>> class PersonFactory(Factory):
   ...     defaults = {
   ...         "name": "Bob",
   ...         "pet": PetFactory,
   ...     }
   ...
   >>> factory1 = PersonFactory()
   >>> factory2 = PersonFactory()
   >>> factory1()
   {'pet': {'kind': 'dog', 'name': 'Rocky'}, 'name': 'Bob'}
   >>> factory2()
   {'pet': {'kind': 'cat', 'name': 'Rocky'}, 'name': 'Bob'}

Surprisingly the pet created by ``factory2`` is a cat not a dog as we
may expect.

We specified ``PetFactory`` for the ``pet`` attribute so both
``factory1`` and ``factory2`` use different pet factories:

.. doctest::

   >>> factory1._defaults["pet"] is factory2._defaults["pet"]
   False

The reason for this behaviour is that the generator for the ``kind``
attribute is created when the ``PetFactory`` is defined and the same
value will be shared by all the factories created from ``PetFactory``,
so ``factory2``, despite using a different ``PetFactory`` from
``factory1``, will consume the same generator for the ``kind``
attribute.

.. doctest::

   >>> factory1._defaults["pet"]._defaults["kind"] is factory2._defaults["pet"]._defaults["kind"]
   True

This can be illustrated creating a new pet factory:

.. doctest::

   >>> pet_factory = PetFactory()
   >>> pet_factory()
   Traceback (most recent call last):
   ...
   StopIteration

the shared generator has been exhausted by the previous calls to
``factory1`` and ``factory2`` and raises an exception.

What we need is delaying the creation of the generator until the
factory is created so each factory gets a different generator, this
can be done using the ``lazy`` class:

.. doctest::

   >>> class PetFactory(Factory):
   ...     defaults = {
   ...         "name": "Rocky",
   ...         "kind": gen.lazy(gen.Gen, ["dog", "cat"]),
   ...     }
   ...
   >>> class PersonFactory(Factory):
   ...     defaults = {
   ...         "name": "Bob",
   ...         "pet": PetFactory,
   ...     }
   ...
   >>> factory1 = PersonFactory()
   >>> factory2 = PersonFactory()
   >>> factory1()
   {'pet': {'kind': 'dog', 'name': 'Rocky'}, 'name': 'Bob'}
   >>> factory2()
   {'pet': {'kind': 'dog', 'name': 'Rocky'}, 'name': 'Bob'}

Notice that ``lazy`` takes a callable and its arguments, not an actual
generator. Passing a generator, or any other non callable object, will
raise a ``TypeError`` exception:

.. doctest::

   >>> gen.lazy(gen.Gen([1, 2,3]))
   Traceback (most recent call last):
   ...
   TypeError

Another potential pitfall is specifying a factory as the default value
for an attribute:

.. doctest::

   >>> pet_factory = Factory(name="Rocky", kind=gen.Gen(["dog", "cat"]))
   >>> class MyFactory(Factory):
   ...     defaults = {
   ...         "name": "Bob",
   ...         "pet": pet_factory,
   ...     }
   ...
   >>> factory1 = MyFactory()
   >>> factory2 = MyFactory()
   >>> factory1()
   {'pet': {'kind': 'dog', 'name': 'Rocky'}, 'name': 'Bob'}
   >>> factory2()
   {'pet': {'kind': 'cat', 'name': 'Rocky'}, 'name': 'Bob'}
   >>> pet_factory()
   Traceback (most recent call last):
   ...
   StopIteration

In this example both ``factory1`` and ``factory2`` share the factory
``pet_factory``, so ``factory2`` will continue creating pets from
where ``factory1`` left off, and creating another pet will raise an
exception.

Notice that, in this example, using a generator for the ``kind``
attribute is not a problem since it's created when the factory is
created and will not be shared by any other factory. In fact using
``lazy`` in that context will not work:

   >>> pet_factory = Factory(
   ...     name="Rocky",
   ...     kind=gen.lazy(gen.Gen, ["dog", "cat"])
   ... )
   >>> pet_factory() #doctest: +ELLIPSIS
   {'kind': <arv.factory.generators.lazy object at 0x...>, 'name': 'Rocky'}

As a rule of thumb, when defining metafactories use lazily created
generators and metafactories as default values. When creating a
factory use generators and factories.


Creating other types of objects
===============================

In the examples we have seen so far the factories created dictionaries
but usually we want to create other types of objects, instances of
some class, a Django or SQLAlchemy model etc. That can be accomplished
defining a new metafactory with a *constructor* class attribute. The
value of that attribute must be a callable that accepts keyword
arguments an returns an *object* of the intended type, a *class* is
the natural choice but any callable can do:

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
   >>> type(obj)
   <class 'MyClass'>
   >>> obj.name
   'Bob'
   >>> obj.age
   42

As we'd expect this works with nested factories too:

.. doctest::

   >>> class Pet(object):
   ...     def __init__(self, name, kind):
   ...         self.name = name
   ...         self.kind = kind
   ...
   >>> class Person(object):
   ...     def __init__(self, name, pet):
   ...         self.name = name
   ...         self.pet = pet
   ...
   >>> class PetFactory(Factory):
   ...     defaults = {"name": "Rocky", "kind": "dog"}
   ...     constructor = Pet
   ...
   >>> class PersonFactory(Factory):
   ...     defaults = {"name": "Bob", "pet": PetFactory}
   ...     constructor = Person
   ...
   >>> factory = PersonFactory()
   >>> obj = factory()
   >>> type(obj)
   <class 'Person'>
   >>> obj.name
   'Bob'
   >>> type(obj.pet)
   <class 'Pet'>
   >>> obj.pet.name
   'Rocky'
   >>> obj.pet.kind
   'dog'


Persisting objects
==================

Usually you'll need to save the objects created by the factory to some
persistent storage in order to perform the testing. ``arv.factory``
implements functionality to ease defining *persistent metafactories*.

Persistent factories are just factories that define the ``make``
method. This method just creates and returns an object that has been
saved to the storage backend.

In order to avoid dependency problems ``arv.factory`` does no provide
any persistent factory by itself. The companion package
``arv.factory_django`` defines a base metafactory for persisting
Django models:

.. code-block:: python

   >>> from arv.factory_django.api import DjangoFactory
   >>> class MyModelFactory(DjangoFactory):
   ...     defaults = {"name": "Bob"}
   ...     constructor = MyModel
   ...
   >>> factory = MyModelFactory()
   >>> obj = factory.make()

.. note:: Creating a persisted object will automatically persist all
          persistable subobjects, if any.

In order to get a non persisted object just call the factory as usual:

.. code-block:: python

   >>> obj = factory()

``make`` accepts keyword arguments as does the factory:

.. code-block:: python

   >>> obj = factory.make(name="Alice")
   >>> obj.name
   'Alice'

Persistent factories also define the ``make_many`` method, equivalent
to the ``many`` method but persisting the objects.


Builtin generators
==================

In the examples of this tutorial we have used *finite* generators for
illustration purposes but in a real scenario we usually need
*infinite* generators so that an spurious ``StopIteration`` don't
breaks our tests.

``arv.factory`` defines some generators that may be useful when
defining factories. Take a look at the API documentation for a
complete list.

For the sake of the tutorial we will introduce the ``mkgen`` and
``string`` generators.

mkgen
-----

``mkgen`` takes a function (any callable in fact) and its arguments
and creates an infinite generator that calls the function every time
the generator is consumed:

.. doctest::

   >>> def myfunction(a, b):
   ...     return "a=%s b=%s" % (a, b)
   ...
   >>> g = gen.mkgen(myfunction, 1, b=2)
   >>> g.next()
   'a=1 b=2'
   >>> g.next()
   'a=1 b=2'

A more useful example would be using a function that returns different
values each time it's called, for example a random number generator:

.. code-block:: python

   >>> from random import randint
   >>> g = gen.mkgen(randint, 0, 100)
   >>> g.next()
   50
   >>> g.next()
   85

or the ``next`` method from an iterator:

.. doctest::

   >>> l = [1, 2, 3]
   >>> g = gen.mkgen(iter(l).next)
   >>> g.next()
   1
   >>> g.next()
   2

This is how some of the generators are implemented.

string
------

``string`` is a generator that creates string values from a format
specification and a counter generator:

.. doctest::

   >>> g = gen.string()
   >>> g.next()
   '0'
   >>> g.next()
   '1'

We can specify a format string when creating the generator:

.. doctest::

   >>> g = gen.string("pet_%02i")
   >>> g.next()
   'pet_00'
   >>> g.next()
   'pet_01'

Internally ``string`` uses the ``%`` operator, so we can use any
format specification supported by ``%``.

Additionally we can specify a counter:

.. doctest::

   >>> g = gen.string(counter=[1, 4, 9])
   >>> g.next()
   '1'
   >>> g.next()
   '4'
   >>> g.next()
   '9'

A counter it's just an iterable. In practice we'll probably use some
python generator in order to generate an infinite sequence of values,
but as said, the only requirement for the counter is being iterable.

We can be more creative making the counter produce tuples:

.. doctest::

   >>> g = gen.string(format="%02i-%02i", counter=((1, 1), (1, 2), (3, 2)))
   >>> g.next()
   '01-01'
   >>> g.next()
   '01-02'
   >>> g.next()
   '03-02'
