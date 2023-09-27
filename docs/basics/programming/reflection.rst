The reflection system in Motor
==============================

Motor is designed, as most game engines (and any large applications) are, to be content-driven.
In many instances, Motor provides independent functionalities that can be configured and combined
in different ways to create applications. At the core of this flexibility is a system that collects
functionalities and publish them through a reflection system. The reflection system allows code
written in C++ to be called from a script like LUA or Python, including creating new instances
of classes.

Publishing native code
----------------------

The first step in the reflection system is to gather the reflection information directly from the C++ code.
In order to do this, a Python module parses the C++ header files looking for declarations that can be
published. The Python script is driven from the build system and will parse any file with a filename
ending with ``.meta.hh``. The parser automatically collects any namespace declaration,
class/struct/union/enum definition, method declarations and definitions, and public members, provided that
they are not template declarations or definitions. In a lot of cases, there is no extra step to take, but it is
possible to alter the behaviour of the reflection system through some attributes, either using the syntax
``[[motor::meta(...)]]`` where C++ attributes are allowed, or using the macro ``motor_meta(...)`` where C++
attributes are not allowed. For instance, attributes on namespaces and enumerators are introduced in C++17.

Meta properties
---------------

Most of the reflection system is drivn automatically. The parser will analyze C++ code and automatically
extract all public C++ entities that are not template. In case the behaviour should be changed, . The parser accepts the following syntax for attributes:

- ``motor_meta(property[=value])``
- ``motor_meta((property1[=value1][,property2[=value2]]))``
- ``[[motor::meta(property1[=value1][,property2[=value2]])[, motor::meta(...)]]]``
- ``[[using motor; meta(property1[=value1][,property2[=value2]])[, meta(...)]]]``

Moreover, if several meta attributes are added to the same declaration, they will behave as if they all
appeared in a single list.

Finally, Doxygen-style comments are also parsed and added as tags on the published values.

The following meta properties are valid:

- ``export[=yes|1|true|no|0|false]``, ``noexport``: asks the parser to export/to ignore the declaration
  or definition. If ``export`` is specified without a value, the value ``yes`` is implicitely added.

  This property can appear only once in the list of meta properties, and is valid on any object except method
  parameters.

- ``name=token``: changes the name of the declaration/definition in the reflection system. This property
  discards the C++ identifier associated with the declaration and provides a different name. The name can be any
  single C++ token, or a string, in which case the content of the string will be used as the name.
  Example: ``[[motor::meta(name=operator new)]]`` is not a valid value for the property as it consists of two
  C++ tokens. One can use the syntax ``[[motor::meta(name="operator new")]]`` instead.

  This property can appear only once in the list of meta properties, and is valid on any object.

- ``alias=token``: adds a name that can be used to lookup the declaration/definition in the reflection system.
  This property preserves the name given to the object (either the C++ identifier or the value of the ``name``
  property) and it adds an entry under a different name in the reflection system. The name can be any
  single C++ token, or a string in which case the content of the string will be used as the name.
  Example: ``[[motor::meta(name=operator new)]]`` is not a valid value for the property as it consists of two
  C++ tokens, but it is possible to use the syntax ``[[motor::meta(name="operator new")]]`` instead.

  This property can appear multiple times in the list of meta properties, each occurrence will add a new entry.
  This property is valid on any object except method parameters.

- ``tag=token sequence``: tags the object with a value. The value has no specific meaning in the reflection
  system but can be retrieved at runtime. The value must be a valid value in the reflection system (i.e. its type
  must be published) and must be written as a valid C++ object using C++ syntax.

  This property can appear multiple times in the list of meta properties, each tag will be aded to the tag list.
  This property is valid on any object.

- ``interface=(i64|u64|float|double|charp|istring|string|array|map|...)``: adds an interface to the type. An interface helps
  script engines convert values between the native types in C++ and the scripting language, allowing for instance
  a C++ object to be created from a Python integer or a Lua number.
  The interface is automatically generated and it is expected that the type provides the correct API, for instance
  a C++ object that has the ``i64`` interface should be convertible to/from an ``i64``.

  This property can appear multiple times in the list of meta properties, to add support for several interfaces.
  This property is only valid on struct, class, and union objects. Enum objects implicitely declare an
  ``i64``, ``u64`` and ``istring`` interface, which means it is possible to retrieve the names of enum values
  or convert them to a numeric value.
