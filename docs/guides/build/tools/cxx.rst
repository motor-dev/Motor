.. _pyxx:

Pyxx, the C/C++/Objective-C/Objective-C++ parser
################################################

Building a complete C++ parser is a
`notoriously <http://www.yosefk.com/c++fqa/defective.html#defect-2>`_ 
`difficult <https://www.reddit.com/r/cpp/comments/h0iok/the_hard_part_about_writing_a_c_parser/>`_
`task <http://www.swig.org/article_cpp.html>`_ .
But there are benefits to being able to parse C++ while editing or building code:

- Extracting type information from the C++ header files
- Parsing comments to generate API documentation
- Automatic formatting of C++ code

Some tools have been created to handle those tasks, such as
`Qt's MOC <https://doc.qt.io/archives/qt-4.8/moc.html>`_,
`Doxygen <https://www.doxygen.nl/index.html>`_ and
`Clang Format <https://clang.llvm.org/docs/ClangFormat.html>`_.
The architecture of BugEngine relies very much on type information from the code.
The created database is used in the editor to manipulate game objects, and in the LUA and Python
plugins to allow the scripts to manipulate C++ objects.
The C++ type database is so important that a parser was created in the build system to build the
database during compilation.
The build system will automatically extract information from specific header files and create the
type database, with minimal input from the developer. Creating a class in C++ makes it immediately
available to Python and LUA scripts.


.. toctree::
    :maxdepth: 2

Scope of C++ parsing
********************

The processed headers are parsed to extract namespaces, classes and methods, and build a database
of C++.


Parsing methodology
*******************

The C++ parser is a GLR parser built with LALR tables. The parsing tool (glrp) creates LALR tables
from an annotated BNF grammar. The gramars are extracted from the
`C 23 standard draft <http://www.open-std.org/jtc1/sc22/wg14/www/docs/n2596.pdf>`__ and the 
`C++ 23 standard draft <https://eel.is/c++draft>`__. The parsing tool lists all conflicts in the
standard grammar and drives annotations, either to prioritize rules or to split parsing into
branches and schedule merges when the branches reduce to the trunk.


Analysis of the C and C++ grammars
**********************************


Conflict resolution
*******************


