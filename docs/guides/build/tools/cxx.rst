.. _pyxx:

Pyxx, the C/C++/Objective-C/Objective-C++ parser
================================================

The architecture of Motor relies very much on type information from the code.
The created database is used in the editor to manipulate game objects, and in the LUA and Python
plugins to allow the scripts to manipulate C++ objects.
The C++ type database is so important that a parser was created in the build system to build the
database during compilation. The build system will automatically extract information from header
files and create the type database, with minimal input from the developer. Creating a class in C++
makes it immediately available to Python and LUA scripts.

For this purpose, the build system uses a tool that parses C++ code. Building a complete C++ parser
is a `notoriously <http://www.yosefk.com/c++fqa/defective.html#defect-2>`_ 
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
But the build system relies on as few dependencies as possible, and to keep the dependency count
low a C++ parser was built in Python (which is already a dependency of the build system).


.. toctree::
    :maxdepth: 2

Scope of C++ parsing
^^^^^^^^^^^^^^^^^^^^

The processed headers are parsed to extract namespaces, classes and methods, and build a database
of C++. The goal is not to create a compiled object, offer diagnostics or static code analysis. The
parser should not require the file to be preprocessed and not all declarations will be visible in
the parse tree.
In order to accomplish this, the parser accepts a superset of C++ and delays some resolution until
the semantic analysis step.


Parsing methodology
^^^^^^^^^^^^^^^^^^^

The C++ parser is a GLR parser built with LALR tables. The parsing tool (glrp) creates LALR tables
from an annotated BNF grammar. The gramars are extracted from the
`C 23 standard draft <http://www.open-std.org/jtc1/sc22/wg14/www/docs/n2596.pdf>`__ and the 
`C++ 23 standard draft <https://eel.is/c++draft>`__. The parsing tool lists all conflicts in the
standard grammar and drives annotations, either to prioritize rules or to split parsing into
branches and schedule merges when the branches reduce to the trunk.

While the parser generator is very similar to Bison, it contains more debugging tools to analyze the
state machine in order to provide better context for conflicts, more solutions to achieve conflict
resolution, and a static analyzer of merge possibilities after splitting the parsing.


Static conflict resolution
^^^^^^^^^^^^^^^^^^^^^^^^^^

This section lists the conflicts that are resolved through making explicit choices in the grammar at
the point the token is encountered (i.e. without additional lookahead). The resolutions are
documented in the C++ standard.


*selection-statement*, ``else``
"""""""""""""""""""""""""""""""

   .. container:: toggle

      .. container:: header

         ::

            selection-statement -> if constexpr? ( init-statement? condition ) statement ♦ else statement
            selection-statement -> if constexpr? ( init-statement? condition ) statement ♦ 

      ::

        shift using rule selection-statement -> if constexpr ( init-statement condition ) statement ♦ else statement
        ╭╴
        │ if constexpr? ( init-statement? condition ) if constexpr? ( init-statement? condition ) statement ♦ else statement
        │                                             ╰selection-statement─────────────────────────────────────────────────╯
        │                                             ╰statement───────────────────────────────────────────────────────────╯
        │ ╰selection-statement─────────────────────────────────────────────────────────────────────────────────────────────╯
        ╰╴
        reduce using rule selection-statement -> if constexpr ( init-statement condition ) statement ♦ 
        ╭╴
        │ if constexpr? ( init-statement? condition ) if constexpr? ( init-statement? condition ) statement ♦ else statement
        │                                             ╰selection-statement────────────────────────────────╯
        │                                             ╰statement──────────────────────────────────────────╯
        │ ╰selection-statement─────────────────────────────────────────────────────────────────────────────────────────────╯
        ╰╴

   .. container:: toggle

      .. container:: header

         ::

            selection-statement -> if !? consteval compound-statement ♦ else statement
            selection-statement -> if !? consteval compound-statement ♦ 

      ::

        shift using rule selection-statement -> if consteval compound-statement ♦ else statement
        ╭╴
        │ if constexpr? ( init-statement? condition ) if !? consteval compound-statement ♦ else statement
        │                                             ╰selection-statement──────────────────────────────╯
        │                                             ╰statement────────────────────────────────────────╯
        │ ╰selection-statement──────────────────────────────────────────────────────────────────────────╯
        ╰╴
        reduce using rule selection-statement -> if !? consteval compound-statement ♦ 
        ╭╴
        │ if constexpr? ( init-statement? condition ) if !? consteval compound-statement ♦ else statement
        │                                             ╰selection-statement─────────────╯
        │                                             ╰statement───────────────────────╯
        │ ╰selection-statement──────────────────────────────────────────────────────────────────────────╯
        ╰╴


The conflict arises when the ``else`` token is encountered. In the sequence of symbols shown in the
counterexample, it is not clear in the grammar if the ``else`` keyword opens the *else clause* of
the rightmost *selection-statement*, or if it reduces the rightmost *selection-statement* and
continues the leftmost *selection-statement*. The C++ standard explicitely excludes the second
possibility in section 8.5.2:

  In the second form of *if statement* (the one including *else*), if the first substatement is also
  an *if statement* then that inner *if statement* shall contain an *else* part.

The conflict is resolved by annotating the grammar with a priority for the first form of the
*selection-statement*.

*new-expression*, ``{``
"""""""""""""""""""""""

   .. container:: toggle

      .. container:: header

         ::

            braced-init-list ->  ♦ { initializer-list? ,? }
            braced-init-list ->  ♦ { designated-initializer-list ,? }
            new-expression -> ::? new new-placement? new-type-id ♦ 
            new-expression -> ::? new new-placement? ( type-id ) ♦ 

      ::

        shift using rule braced-init-list ->  ♦ { initializer-list? ,? }
        ╭╴
        │ identifier? attribute-specifier-seq? : ::? new new-placement? ( type-id ) ♦ { initializer-list? ,? }
        │                                                                           ╰braced-init-list────────╯
        │                                                                           ╰new-initializer─────────╯
        │                                        ╰new-expression─────────────────────────────────────────────╯
        │                                        ╰unary-expression───────────────────────────────────────────╯
        │                                        ╰cast-expression────────────────────────────────────────────╯
        │                                        ╰pm-expression──────────────────────────────────────────────╯
        │                                        ╰multiplicative-expression──────────────────────────────────╯
        │                                        ╰additive-expression────────────────────────────────────────╯
        │                                        ╰shift-expression───────────────────────────────────────────╯
        │                                        ╰compare-expression─────────────────────────────────────────╯
        │                                        ╰relational-expression──────────────────────────────────────╯
        │                                        ╰equality-expression────────────────────────────────────────╯
        │                                        ╰and-expression─────────────────────────────────────────────╯
        │                                        ╰exclusive-or-expression────────────────────────────────────╯
        │                                        ╰inclusive-or-expression────────────────────────────────────╯
        │                                        ╰logical-and-expression─────────────────────────────────────╯
        │                                        ╰logical-or-expression──────────────────────────────────────╯
        │                                        ╰conditional-expression─────────────────────────────────────╯
        │                                        ╰constant-expression────────────────────────────────────────╯
        │ ╰member-declarator─────────────────────────────────────────────────────────────────────────────────╯
        ╰╴
        shift using rule braced-init-list ->  ♦ { designated-initializer-list? ,? }
        ╭╴
        │ identifier? attribute-specifier-seq? : ::? new new-placement? ( type-id ) ♦ { designated-initializer-list? ,? }
        │                                                                           ╰braced-init-list───────────────────╯
        │                                                                           ╰new-initializer────────────────────╯
        │                                        ╰new-expression────────────────────────────────────────────────────────╯
        │                                        ╰unary-expression──────────────────────────────────────────────────────╯
        │                                        ╰cast-expression───────────────────────────────────────────────────────╯
        │                                        ╰pm-expression─────────────────────────────────────────────────────────╯
        │                                        ╰multiplicative-expression─────────────────────────────────────────────╯
        │                                        ╰additive-expression───────────────────────────────────────────────────╯
        │                                        ╰shift-expression──────────────────────────────────────────────────────╯
        │                                        ╰compare-expression────────────────────────────────────────────────────╯
        │                                        ╰relational-expression─────────────────────────────────────────────────╯
        │                                        ╰equality-expression───────────────────────────────────────────────────╯
        │                                        ╰and-expression────────────────────────────────────────────────────────╯
        │                                        ╰exclusive-or-expression───────────────────────────────────────────────╯
        │                                        ╰inclusive-or-expression───────────────────────────────────────────────╯
        │                                        ╰logical-and-expression────────────────────────────────────────────────╯
        │                                        ╰logical-or-expression─────────────────────────────────────────────────╯
        │                                        ╰conditional-expression────────────────────────────────────────────────╯
        │                                        ╰constant-expression───────────────────────────────────────────────────╯
        │ ╰member-declarator────────────────────────────────────────────────────────────────────────────────────────────╯
        ╰╴
        reduce using rule new-expression -> ::? new new-placement? ( type-id ) ♦ 
        ╭╴
        │ identifier? attribute-specifier-seq? : ::? new new-placement? ( type-id ) ♦ { }
        │                                        ╰new-expression────────────────────╯ ╰braced-init-list╯
        │                                        ╰unary-expression──────────────────╯ ╰brace-or-equal-initializer╯
        │                                        ╰cast-expression───────────────────╯
        │                                        ╰pm-expression─────────────────────╯
        │                                        ╰multiplicative-expression─────────╯
        │                                        ╰additive-expression───────────────╯
        │                                        ╰shift-expression──────────────────╯
        │                                        ╰compare-expression────────────────╯
        │                                        ╰relational-expression─────────────╯
        │                                        ╰equality-expression───────────────╯
        │                                        ╰and-expression────────────────────╯
        │                                        ╰exclusive-or-expression───────────╯
        │                                        ╰inclusive-or-expression───────────╯
        │                                        ╰logical-and-expression────────────╯
        │                                        ╰logical-or-expression─────────────╯
        │                                        ╰conditional-expression────────────╯
        │                                        ╰constant-expression───────────────╯
        │ ╰member-declarator─────────────────────────────────────────────────────────────────────────────────────╯
        ╰╴
        reduce using rule new-expression -> ::? new new-placement new-type-id ♦ 
        ╭╴
        │ identifier? attribute-specifier-seq? : ::? new new-placement? new-type-id ♦ { }
        │                                        ╰new-expression────────────────────╯ ╰braced-init-list╯
        │                                        ╰unary-expression──────────────────╯ ╰brace-or-equal-initializer╯
        │                                        ╰cast-expression───────────────────╯
        │                                        ╰pm-expression─────────────────────╯
        │                                        ╰multiplicative-expression─────────╯
        │                                        ╰additive-expression───────────────╯
        │                                        ╰shift-expression──────────────────╯
        │                                        ╰compare-expression────────────────╯
        │                                        ╰relational-expression─────────────╯
        │                                        ╰equality-expression───────────────╯
        │                                        ╰and-expression────────────────────╯
        │                                        ╰exclusive-or-expression───────────╯
        │                                        ╰inclusive-or-expression───────────╯
        │                                        ╰logical-and-expression────────────╯
        │                                        ╰logical-or-expression─────────────╯
        │                                        ╰conditional-expression────────────╯
        │                                        ╰constant-expression───────────────╯
        │ ╰member-declarator─────────────────────────────────────────────────────────────────────────────────────╯
        ╰╴

The conflict arises after a *new-expression* has been parsed. The following ``{`` token will be
opening a *braced-init-list*. The counterexample context shows that when parsing a
*member-declarator*, if the bitfield specifier (a *constant-expression*) expands to a
*new-expression*, there is a conflict between applying the *braced-init-list* to the
*new-expression* or to the *member-declarator*. The C++ standard declares in section 11.4.1:

   In a *member-declarator* for a bit-field, the *constant-expression* is parsed as the longest
   sequence of tokens that could syntactically form a *constant-expression*.

   .. code-block:: C++

    struct S {
      int z : 1 || new int { 0 };   // OK, brace-or-equal-initializer is absent
    };

The conflict is resolved by assigning a priority to shifing into the *brace-init-list*.


*nested-name-specifier*, ``::``
"""""""""""""""""""""""""""""""

The ``::`` being used both as a binary operator (name lookup operator) and a unary operator (root
namespace name lookup), it is ambiguous when encountering a ``::`` token if it continues a previous
name lookup or closes the previous name lookup and starts a new name lookup in the root namespace.

The resolution is to always continue the previous name lookup.


*conversion-type-id*, *attribute-specifier-seq* and *cv-qualifier-seq*
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Example shown with the ``*`` operator and ``[[`` token. Variations of the conflict exist for all
*ptr-operator* constructs, and all *attribute-specifier*\ s and *cv-qualifier* \ s.


   .. container:: toggle

      .. container:: header

         ::

            attribute-specifier ->  ♦ [[ attribute-using-prefix? attribute-list ] ]
            ptr-operator -> && ♦ 

      ::

        shift using rule attribute-specifier ->  ♦ [[ attribute-using-prefix? attribute-list ] ]
        ╭╴
        │ operator type-specifier-seq && ♦ [[ attribute-using-prefix? attribute-list ] ]
        │                                ╰attribute-specifier──────────────────────────╯
        │                                ╰attribute-specifier-seq──────────────────────╯
        │                             ╰ptr-operator────────────────────────────────────╯
        │                             ╰conversion-declarator───────────────────────────╯
        │          ╰conversion-type-id─────────────────────────────────────────────────╯
        │ ╰conversion-function-id──────────────────────────────────────────────────────╯
        │ ╰unqualified-id──────────────────────────────────────────────────────────────╯
        │ ╰id-expression───────────────────────────────────────────────────────────────╯
        │ ╰declarator-id───────────────────────────────────────────────────────────────╯
        │ ╰noptr-declarator────────────────────────────────────────────────────────────╯
        ├╴
        │ lambda-introducer < template-parameter-list > requires operator type-specifier-seq && ♦ [[ attribute-using-prefix? attribute-list ] ] lambda-declarator compound-statement
        │                                                                                       ╰attribute-specifier──────────────────────────╯
        │                                                                                       ╰attribute-specifier-seq──────────────────────╯
        │                                                                                    ╰ptr-operator────────────────────────────────────╯
        │                                                                                    ╰conversion-declarator───────────────────────────╯
        │                                                                 ╰conversion-type-id─────────────────────────────────────────────────╯
        │                                                        ╰conversion-function-id──────────────────────────────────────────────────────╯
        │                                                        ╰unqualified-id──────────────────────────────────────────────────────────────╯
        │                                                        ╰id-expression───────────────────────────────────────────────────────────────╯
        │                                                        ╰primary-expression──────────────────────────────────────────────────────────╯
        │                                                        ╰constraint-logical-and-expression───────────────────────────────────────────╯
        │                                                        ╰constraint-logical-or-expression────────────────────────────────────────────╯
        │                                               ╰requires-clause──────────────────────────────────────────────────────────────────────╯
        │ ╰lambda-expression───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
        ├╴
        │ template < template-parameter-list > requires operator type-specifier-seq && ♦ [[ attribute-using-prefix? attribute-list ] ] declaration
        │                                                                              ╰attribute-specifier──────────────────────────╯
        │                                                                              ╰attribute-specifier-seq──────────────────────╯
        │                                                                           ╰ptr-operator────────────────────────────────────╯
        │                                                                           ╰conversion-declarator───────────────────────────╯
        │                                                        ╰conversion-type-id─────────────────────────────────────────────────╯
        │                                               ╰conversion-function-id──────────────────────────────────────────────────────╯
        │                                               ╰unqualified-id──────────────────────────────────────────────────────────────╯
        │                                               ╰id-expression───────────────────────────────────────────────────────────────╯
        │                                               ╰primary-expression──────────────────────────────────────────────────────────╯
        │                                               ╰constraint-logical-and-expression───────────────────────────────────────────╯
        │                                               ╰constraint-logical-or-expression────────────────────────────────────────────╯
        │                                      ╰requires-clause──────────────────────────────────────────────────────────────────────╯
        │ ╰template-head─────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
        │ ╰template-declaration──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
        ╰╴
        reduce using rule ptr-operator -> && ♦ 
        ╭╴
        │ operator type-specifier-seq && ♦                    [[ attribute-using-prefix? attribute-list ] ]
        │                             ╰ptr-operator╯          ╰attribute-specifier────────────────────────╯
        │                             ╰conversion-declarator╯ ╰attribute-specifier-seq────────────────────╯
        │          ╰conversion-type-id──────────────────────╯
        │ ╰conversion-function-id───────────────────────────╯
        │ ╰unqualified-id───────────────────────────────────╯
        │ ╰id-expression────────────────────────────────────╯
        │ ╰declarator-id────────────────────────────────────╯
        │ ╰noptr-declarator───────────────────────────────────────────────────────────────────────────────╯
        ├╴
        │ lambda-introducer < template-parameter-list > requires operator type-specifier-seq && ♦                    [[ attribute-using-prefix? attribute-list ] ]     lambda-declarator compound-statement
        │                                                                                    ╰ptr-operator╯          ╰attribute-specifier────────────────────────╯
        │                                                                                    ╰conversion-declarator╯ ╰attribute-specifier-seq────────────────────╯
        │                                                                 ╰conversion-type-id──────────────────────╯ ╰lambda-specifiers──────────────────────────╯
        │                                                        ╰conversion-function-id───────────────────────────╯ ╰lambda-declarator──────────────────────────╯
        │                                                        ╰unqualified-id───────────────────────────────────╯
        │                                                        ╰id-expression────────────────────────────────────╯
        │                                                        ╰primary-expression───────────────────────────────╯
        │                                                        ╰constraint-logical-and-expression────────────────╯
        │                                                        ╰constraint-logical-or-expression─────────────────╯
        │                                               ╰requires-clause───────────────────────────────────────────╯
        │ ╰lambda-expression──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
        ├╴
        │ template < template-parameter-list > requires operator type-specifier-seq && ♦                    [[ attribute-using-prefix? attribute-list ] ]     declarator function-body
        │                                                                           ╰ptr-operator╯          ╰attribute-specifier────────────────────────╯
        │                                                                           ╰conversion-declarator╯ ╰attribute-specifier-seq────────────────────╯
        │                                                        ╰conversion-type-id──────────────────────╯ ╰function-definition─────────────────────────────────────────────────────╯
        │                                               ╰conversion-function-id───────────────────────────╯ ╰declaration─────────────────────────────────────────────────────────────╯
        │                                               ╰unqualified-id───────────────────────────────────╯
        │                                               ╰id-expression────────────────────────────────────╯
        │                                               ╰primary-expression───────────────────────────────╯
        │                                               ╰constraint-logical-and-expression────────────────╯
        │                                               ╰constraint-logical-or-expression─────────────────╯
        │                                      ╰requires-clause───────────────────────────────────────────╯
        │ ╰template-head──────────────────────────────────────────────────────────────────────────────────╯
        │ ╰template-declaration──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
        ╰╴

The counter-examples show three different contexts where a *type-id* (to be precise, a
*conversion-type-id*) can be directly followed by an *attribute-specifier-sequence*, which prompts
the parser to decide if an *attribute-specifier* applies to the *conversion-type-id*, or to the
parent item that includes it. The three different contexts are:

- declaring a *conversion-function*,
- specifying a *requires-clause* for a *lambda-expression*,
- specifying a *requires-clause* for a template declaration.

The attribute specifier sequence is consumed by the *conversion-type-id* by applying a priority on
shifting the *attribute-specifier*\ s and *cv-qualifier*\ s over the reductions of
*ptr-operator*\ s. (TODO: C++ standard reference)


*explicit-specifier*, ``(``
"""""""""""""""""""""""""""


   .. container:: toggle

      .. container:: header

         ::

            explicit-specifier -> explicit ♦ ( constant-expression )
            explicit-specifier -> explicit ♦ 

      ::

            reduce using rule explicit-specifier -> explicit ♦ 
            ╭╴
            │ attribute-specifier-seq explicit ♦           ( ptr-declarator ) parameters-and-qualifiers trailing-return-type declarator function-body
            │                         ╰explicit-specifier╯ ╰noptr-declarator╯
            │                         ╰function-specifier╯ ╰declarator─────────────────────────────────────────────────────╯
            │                         ╰decl-specifier────╯
            │                         ╰decl-specifier-seq╯
            │ ╰function-definition──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │ ╰declaration──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            ╰╴
            shift using rule explicit-specifier -> explicit ♦ ( constant-expression )
            ╭╴
            │ attribute-specifier-seq explicit ♦ ( constant-expression ) declarator function-body
            │                         ╰explicit-specifier──────────────╯
            │                         ╰function-specifier──────────────╯
            │                         ╰decl-specifier──────────────────╯
            │                         ╰decl-specifier-seq──────────────╯
            │ ╰function-definition──────────────────────────────────────────────────────────────╯
            │ ╰declaration──────────────────────────────────────────────────────────────────────╯
            ╰╴

The conflict arises in all declarations (narrowed down to one counter-example here) after
encountering the ``explicit`` keyword. The standard disambiguates the conflict in section 9.2.3:

    A ``(`` token that follows ``explicit`` is parsed as part of the *explicit-specifier*.

The grammar conflict is resolved by prioritizing the shift.


``new``, ``new[]``, ``delete``, ``delete[]``
""""""""""""""""""""""""""""""""""""""""""""


   .. container:: toggle

      .. container:: header

         ::

            overloadable-operator -> new ♦ [ ]
            overloadable-operator -> new ♦ 

      ::

            shift using rule overloadable-operator -> new ♦ [ ]
            ╭╴
            │ operator new ♦ [ ]
            │          ╰overloadable-operator╯
            │ ╰operator-function-id──────────╯
            │ ╰unqualified-id────────────────╯
            │ ╰id-expression─────────────────╯
            │ ╰declarator-id─────────────────╯
            │ ╰noptr-declarator──────────────╯
            ├╴
            │ operator new ♦ [ ]
            │          ╰overloadable-operator╯
            │ ╰operator-function-id──────────╯
            │ ╰unqualified-id────────────────╯
            │ ╰id-expression─────────────────╯
            │ ╰primary-expression────────────╯
            │ ╰postfix-expression────────────╯
            ╰╴
            reduce using rule overloadable-operator -> new ♦ 
            ╭╴
            │ operator new ♦                   [ constant-expression? ] attribute-specifier-seq?
            │          ╰overloadable-operator╯
            │ ╰operator-function-id──────────╯
            │ ╰unqualified-id────────────────╯
            │ ╰id-expression─────────────────╯
            │ ╰declarator-id─────────────────╯
            │ ╰noptr-declarator──────────────╯
            │ ╰noptr-declarator────────────────────────────────────────────────────────────────╯
            ├╴
            │ operator new ♦                   [ expr-or-braced-init-list ]
            │          ╰overloadable-operator╯
            │ ╰operator-function-id──────────╯
            │ ╰unqualified-id────────────────╯
            │ ╰id-expression─────────────────╯
            │ ╰primary-expression────────────╯
            │ ╰postfix-expression────────────╯
            │ ╰postfix-expression─────────────────────────────────────────╯
            ╰╴

   .. container:: toggle

      .. container:: header

         ::
            overloadable-operator -> delete ♦ [ ]
            overloadable-operator -> delete ♦ 

      ::

            shift using rule overloadable-operator -> delete ♦ [ ]
            ╭╴
            │ operator delete ♦ [ ]
            │          ╰overloadable-operator╯
            │ ╰operator-function-id──────────╯
            │ ╰unqualified-id────────────────╯
            │ ╰id-expression─────────────────╯
            │ ╰declarator-id─────────────────╯
            │ ╰noptr-declarator──────────────╯
            ├╴
            │ operator delete ♦ [ ]
            │          ╰overloadable-operator╯
            │ ╰operator-function-id──────────╯
            │ ╰unqualified-id────────────────╯
            │ ╰id-expression─────────────────╯
            │ ╰primary-expression────────────╯
            │ ╰postfix-expression────────────╯
            ╰╴
            reduce using rule overloadable-operator -> delete ♦ 
            ╭╴
            │ operator delete ♦                [ constant-expression? ] attribute-specifier-seq?
            │          ╰overloadable-operator╯
            │ ╰operator-function-id──────────╯
            │ ╰unqualified-id────────────────╯
            │ ╰id-expression─────────────────╯
            │ ╰declarator-id─────────────────╯
            │ ╰noptr-declarator──────────────╯
            │ ╰noptr-declarator────────────────────────────────────────────────────────────────╯
            ├╴
            │ operator delete ♦                [ expr-or-braced-init-list ]
            │          ╰overloadable-operator╯
            │ ╰operator-function-id──────────╯
            │ ╰unqualified-id────────────────╯
            │ ╰id-expression─────────────────╯
            │ ╰primary-expression────────────╯
            │ ╰postfix-expression────────────╯
            │ ╰postfix-expression─────────────────────────────────────────╯
            ╰╴

   .. container:: toggle

      .. container:: header

         ::

            delete [ ] ♦ cast-expression
            lambda-introducer -> [ ] ♦ 

      ::

            shift using rule delete [ ] ♦ cast-expression
            ╭╴
            │ delete [ ] ♦ cast-expression
            │ ╰delete-expression─────────╯
            ╰╴
            reduce using rule lambda-introducer -> [ ] ♦ 
            ╭╴
            │ delete [ ] ♦               lambda-declarator
            │        ╰lambda-introducer╯
            │        ╰lambda-expression──────────────────╯
            │        ╰primary-expression─────────────────╯
            │        ╰postfix-expression─────────────────╯
            │        ╰unary-expression───────────────────╯
            │        ╰cast-expression────────────────────╯
            │ ╰delete-expression─────────────────────────╯
            ╰╴



TODO: prefer array version.


*type-id*, *ptr-operator*
"""""""""""""""""""""""""

also *conversion-type-id*, *new-type-id*


*global-module-fragment*
""""""""""""""""""""""""
   .. container:: toggle

      .. container:: header

         ::

            global-module-fragment -> module ; declaration-seq? ♦ 
            export-declaration ->  ♦ export { noexport-declaration-seq? }
            export-declaration ->  ♦ export noexport-declaration
            export-declaration ->  ♦ export module-import-declaration

      ::

            reduce using rule global-module-fragment -> module ; declaration-seq? ♦ 
            ╭╴
            │ module ; declaration-seq? ♦ export module module-name ; declaration-seq? private-module-fragment?
            │ ╰global-module-fragment───╯ ╰module-declaration───────╯
            │ ╰translation-unit───────────────────────────────────────────────────────────────────────────────╯
            ╰╴
            shift using rule export-declaration ->  ♦ export module-import-declaration
            ╭╴
            │ module ; declaration-seq ♦ export module-import-declaration module-declaration
            │                          ╰export-declaration──────────────╯
            │                          ╰declaration─────────────────────╯
            │          ╰declaration-seq─────────────────────────────────╯
            │ ╰global-module-fragment───────────────────────────────────╯
            │ ╰translation-unit────────────────────────────────────────────────────────────╯
            ╰╴
            shift using rule export-declaration ->  ♦ export { noexport-declaration-seq? }
            ╭╴
            │ module ; declaration-seq ♦ export { noexport-declaration-seq? } module-declaration
            │                          ╰export-declaration──────────────────╯
            │                          ╰declaration─────────────────────────╯
            │          ╰declaration-seq─────────────────────────────────────╯
            │ ╰global-module-fragment───────────────────────────────────────╯
            │ ╰translation-unit────────────────────────────────────────────────────────────────╯
            ╰╴
            shift using rule export-declaration ->  ♦ export noexport-declaration
            ╭╴
            │ module ; declaration-seq ♦ export noexport-declaration module-declaration
            │                          ╰export-declaration─────────╯
            │                          ╰declaration────────────────╯
            │          ╰declaration-seq────────────────────────────╯
            │ ╰global-module-fragment──────────────────────────────╯
            │ ╰translation-unit───────────────────────────────────────────────────────╯
            ╰╴

Is the *declaration-seq* part of the *global-module-fragment*?
Resolved as reduce. In reality, the only declarations part of the *global-module-fragment* should be
preprocessor.

*requirement-expression*, *nested-requirement*
""""""""""""""""""""""""""""""""""""""""""""""

In places allowing a requirement, the ``requires`` keyword leads to two possible expansions: it
could introduce a *requirement-expression* as part of a *simple-requirement*, or it could start a
*nested-requirement*. The possible expansions lead to conflicts after a few tokens have been parsed.
The standard indicates that the ``requires`` keyword in this situation always introduces a
*nested-requirement*. It is therefore possible to resolve all conflicts by prefering the
*nested-requirement* option. This would lead to a lot of annotations spread accross the grammar.

In order to simplify the grammar, it is modified to introduce an earlier conflict, an empty
production before the ``requires`` keyword. This empty production causes a shift-reduce conflict
that hides all subsequent conflicts in the expansion. Resolving this single conflicts removes the
possibility of expanding a *requirement-expression* altogether, thus also hiding all unambiguous
expansions.

   .. container:: toggle

      .. container:: header

         ::

            requires-disambiguation ->  ♦ 
            nested-requirement ->  ♦ requires constraint-expression ;

      ::
         shift using rule nested-requirement ->  ♦ requires constraint-expression ;
         ╭╴
         │ ♦ requires constraint-expression ;
         │ ╰nested-requirement──────────────╯
         │ ╰requirement─────────────────────╯
         ╰╴
         reduce using rule requires-disambiguation ->  ♦ 
         ╭╴
         │ ♦                         requires requirement-parameter-list? requirement-body assignment-operator initializer-clause ;
         │ ╰requires-disambiguation╯
         │ ╰requires-expression──────────────────────────────────────────────────────────╯
         │ ╰primary-expression───────────────────────────────────────────────────────────╯
         │ ╰postfix-expression───────────────────────────────────────────────────────────╯
         │ ╰unary-expression─────────────────────────────────────────────────────────────╯
         │ ╰cast-expression──────────────────────────────────────────────────────────────╯
         │ ╰pm-expression────────────────────────────────────────────────────────────────╯
         │ ╰multiplicative-expression────────────────────────────────────────────────────╯
         │ ╰additive-expression──────────────────────────────────────────────────────────╯
         │ ╰shift-expression─────────────────────────────────────────────────────────────╯
         │ ╰compare-expression───────────────────────────────────────────────────────────╯
         │ ╰relational-expression────────────────────────────────────────────────────────╯
         │ ╰equality-expression──────────────────────────────────────────────────────────╯
         │ ╰and-expression───────────────────────────────────────────────────────────────╯
         │ ╰exclusive-or-expression──────────────────────────────────────────────────────╯
         │ ╰inclusive-or-expression──────────────────────────────────────────────────────╯
         │ ╰logical-and-expression───────────────────────────────────────────────────────╯
         │ ╰logical-or-expression────────────────────────────────────────────────────────╯
         │ ╰assignment-expression───────────────────────────────────────────────────────────────────────────────────────────────╯
         │ ╰expression──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
         │ ╰simple-requirement────────────────────────────────────────────────────────────────────────────────────────────────────╯
         │ ╰requirement───────────────────────────────────────────────────────────────────────────────────────────────────────────╯
         ╰╴

In this modified grammar, resolvig as shift prioritizes the *nested-requirement* over a
*requires-expression*.

Dynamic conflict resolution
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This section lists the conflicts that can't be decided with the next lookahead. The resolution
depends on information that is not available to the parser at the moment it has to make a decision.
The parser then splits parsing into two or more branches that will be resolved at a later point.

The parser will continue to maintain several branches until either the lookaheads generate parse
errors in some of the tentative branches, or the branches reduce in the same state and the state
can execute a merge action.

*explicit-specifier*, ``identifier``
""""""""""""""""""""""""""""""""""""


   .. container:: toggle

      .. container:: header

         ::

            function-specifier -> explicit-specifier ♦ 
            template-name ->  ♦ identifier

      ::

            reduce using rule function-specifier -> explicit-specifier ♦ 
            ╭╴
            │ explicit-specifier ♦ identifier                declarator function-body
            │ ╰function-specifier╯ ╰template-name╯
            │ ╰decl-specifier────╯ ╰simple-type-specifier╯
            │                      ╰type-specifier───────╯
            │                      ╰defining-type-specifier╯
            │                      ╰decl-specifier─────────╯
            │                      ╰decl-specifier-seq─────╯
            │ ╰decl-specifier-seq──────────────────────────╯
            │ ╰function-definition──────────────────────────────────────────────────╯
            │ ╰declaration──────────────────────────────────────────────────────────╯
            ╰╴
            shift using rule template-name ->  ♦ identifier
            ╭╴
            │ explicit-specifier ♦ identifier    ( parameter-declaration-clause ) -> simple-template-id ;
            │                    ╰template-name╯
            │ ╰deduction-guide──────────────────────────────────────────────────────────────────────────╯
            │ ╰declaration──────────────────────────────────────────────────────────────────────────────╯
            ╰╴

The conflict arises in a *declaration* or *member-declaration*. *explicit-specifier* could introduce
either a *function-definition*, or a *deduction-guide*. The parser does not know yet if an
``identifier`` represents a *template-name*, so it attempts both parse solutions.

*template-id*, ``<``
""""""""""""""""""""

   .. container:: toggle

      .. container:: header

         ::

            unqualified-id -> literal-operator-id ♦ 
            template-id -> literal-operator-id ♦ < template-argument-list? >

      ::

            reduce using rule unqualified-id -> literal-operator-id ♦ 
            ╭╴
            │ literal-operator-id ♦       < compare-expression
            │ ╰unqualified-id─────╯
            │ ╰id-expression──────╯
            │ ╰primary-expression─╯
            │ ╰postfix-expression─╯
            │ ╰unary-expression───╯
            │ ╰cast-expression────╯
            │ ╰pm-expression──────╯
            │ ╰multiplicative-expression╯
            │ ╰additive-expression──────╯
            │ ╰shift-expression─────────╯
            │ ╰compare-expression───────╯
            │ ╰relational-expression────╯
            │ ╰relational-expression─────────────────────────╯
            ╰╴
            shift using rule template-id -> literal-operator-id ♦ < template-argument-list >
            ╭╴
            │ literal-operator-id ♦ < template-argument-list? >
            │ ╰template-id────────────────────────────────────╯
            │ ╰unqualified-id─────────────────────────────────╯
            │ ╰id-expression──────────────────────────────────╯
            │ ╰primary-expression─────────────────────────────╯
            │ ╰postfix-expression─────────────────────────────╯
            │ ╰unary-expression───────────────────────────────╯
            │ ╰cast-expression────────────────────────────────╯
            │ ╰pm-expression──────────────────────────────────╯
            │ ╰multiplicative-expression──────────────────────╯
            │ ╰additive-expression────────────────────────────╯
            │ ╰shift-expression───────────────────────────────╯
            │ ╰compare-expression─────────────────────────────╯
            │ ╰relational-expression──────────────────────────╯
            ╰╴

The conflict arises when encountering the ``<`` token. Depending on the resolution of the entity
in front of the ``<`` token, it could be part of a *template-id* or a *relational-expression*.


*initializer*, *parameters-and-qualifiers*
""""""""""""""""""""""""""""""""""""""""""


   .. container:: toggle

      .. container:: header

         ::

            ptr-declarator -> noptr-declarator ♦ 
            parameters-and-qualifiers ->  ♦ ( parameter-declaration-clause ) cv-qualifier-seq? ref-qualifier? exception-specification? attribute-specifier-seq?

      ::

            reduce using rule ptr-declarator -> noptr-declarator ♦ 
            ╭╴
            │ attribute-specifier-seq decl-specifier-seq noptr-declarator ♦ ( expression-list ) ;
            │                                            ╰ptr-declarator──╯ ╰initializer──────╯
            │                                            ╰declarator──────╯
            │                                            ╰init-declarator─────────────────────╯
            │                                            ╰init-declarator-list────────────────╯
            │ ╰simple-declaration───────────────────────────────────────────────────────────────╯
            │ ╰block-declaration────────────────────────────────────────────────────────────────╯
            │ ╰declaration──────────────────────────────────────────────────────────────────────╯
            ╰╴
            shift using rule parameters-and-qualifiers ->  ♦ ( parameter-declaration-clause ) cv-qualifier-seq ref-qualifier exception-specification attribute-specifier-seq
            ╭╴
            │ attribute-specifier-seq decl-specifier-seq noptr-declarator ♦ ( parameter-declaration-clause ) cv-qualifier-seq? ref-qualifier? exception-specification attribute-specifier-seq? parameters-and-qualifiers trailing-return-type function-body
            │                                                             ╰parameters-and-qualifiers─────────────────────────────────────────────────────────────────────────────────────────╯
            │                                            ╰noptr-declarator───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │                                            ╰declarator────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │ ╰function-definition────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │ ╰declaration────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            ╰╴

A ``(`` token could introduce either a *parameters-and-qualifiers* clause, or an *initializer*. In
some cases, the additional tokens will disambiguate the declaration. In other cases, the statement
is truly ambiguous.

*trailing-return-type*, *abstract-declarator* / *parameters-and-qualifiers* / *initializer*
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

In the context of a trailing return type, there are ambiguities when encountering the ``(`` token.

   .. container:: toggle

      .. container:: header

         ::

            parameters-and-qualifiers ->  ♦ ( parameter-declaration-clause ) cv-qualifier-seq? ref-qualifier? exception-specification? attribute-specifier-seq?
            type-id -> type-specifier-seq ♦ 
            noptr-abstract-declarator ->  ♦ ( ptr-abstract-declarator )

      ::

            shift using rule parameters-and-qualifiers ->  ♦ ( parameter-declaration-clause )
            ╭╴
            │ decl-specifier-seq noptr-declarator parameters-and-qualifiers -> type-specifier-seq ♦ ( parameter-declaration-clause ) cv-qualifier-seq? ref-qualifier? exception-specification? attribute-specifier-seq? trailing-return-type ;
            │                                                                                     ╰parameters-and-qualifiers──────────────────────────────────────────────────────────────────────────────────────────╯
            │                                                                                     ╰abstract-declarator─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │                                                                  ╰type-id────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │                                                               ╰trailing-return-type──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │                    ╰declarator───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │                    ╰init-declarator──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │                    ╰init-declarator-list─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │ ╰simple-declaration────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │ ╰block-declaration─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │ ╰declaration───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            ╰╴
            reduce using rule type-id -> type-specifier-seq ♦ 
            ╭╴
            │ decl-specifier-seq noptr-declarator parameters-and-qualifiers -> type-specifier-seq ♦ ( expression-list ) ;
            │                                                                  ╰type-id───────────╯ ╰initializer──────╯
            │                                                               ╰trailing-return-type─╯
            │                    ╰declarator──────────────────────────────────────────────────────╯
            │                    ╰init-declarator─────────────────────────────────────────────────────────────────────╯
            │                    ╰init-declarator-list────────────────────────────────────────────────────────────────╯
            │ ╰simple-declaration───────────────────────────────────────────────────────────────────────────────────────╯
            │ ╰block-declaration────────────────────────────────────────────────────────────────────────────────────────╯
            │ ╰declaration──────────────────────────────────────────────────────────────────────────────────────────────╯
            ╰╴
            shift using rule noptr-abstract-declarator ->  ♦ ( ptr-abstract-declarator )
            ╭╴
            │ decl-specifier-seq noptr-declarator parameters-and-qualifiers -> type-specifier-seq ♦ ( ptr-abstract-declarator ) parameters-and-qualifiers trailing-return-type ;
            │                                                                                     ╰noptr-abstract-declarator──╯
            │                                                                                     ╰abstract-declarator───────────────────────────────────────────────────────╯
            │                                                                  ╰type-id──────────────────────────────────────────────────────────────────────────────────────╯
            │                                                               ╰trailing-return-type────────────────────────────────────────────────────────────────────────────╯
            │                    ╰declarator─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │                    ╰init-declarator────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │                    ╰init-declarator-list───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │ ╰simple-declaration──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │ ╰block-declaration───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            │ ╰declaration─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
            ╰╴

``type`` template parameter, ``non-type`` class template parameter
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

  class-key -> class ♦ 
  type-parameter-key -> class ♦ 

   reduce using rule class-key -> class ♦ 
   ╭╴
   │ class ♦                        identifier identifier
   │ ╰class-key╯
   │ ╰elaborated-type-specifier──────────────╯
   │ ╰type-specifier─────────────────────────╯
   │ ╰defining-type-specifier────────────────╯
   │ ╰decl-specifier─────────────────────────╯
   │ ╰decl-specifier-seq─────────────────────╯
   │ ╰parameter-declaration─────────────────────────────╯
   │ ╰template-parameter────────────────────────────────╯
   ╰╴
   reduce using rule type-parameter-key -> class ♦ 
   ╭╴
   │ class ♦              identifier
   │ ╰type-parameter-key╯
   │ ╰type-parameter───────────────╯
   │ ╰template-parameter───────────╯
   ╰╴

*elaborated-enum-specifier* / *opaque-enum-declaration*
"""""""""""""""""""""""""""""""""""""""""""""""""""""""
  enum-head-name -> identifier ♦ 
  elaborated-enum-specifier -> enum-key identifier ♦ 

    reduce using rule enum-head-name -> identifier ♦ 
   ╭╴
   │ enum-key identifier ♦     ;
   │          ╰enum-head-name╯
   │ ╰opaque-enum-declaration──╯
   │ ╰block-declaration────────╯
   │ ╰declaration-statement────╯
   │ ╰statement────────────────╯
   ╰╴
    reduce using rule elaborated-enum-specifier -> enum-key identifier ♦ 
   ╭╴
   │ enum-key identifier ♦       ;
   │ ╰elaborated-enum-specifier╯
   │ ╰elaborated-type-specifier╯
   │ ╰type-specifier───────────╯
   │ ╰defining-type-specifier──╯
   │ ╰decl-specifier───────────╯
   │ ╰decl-specifier-seq───────╯
   │ ╰simple-declaration─────────╯
   │ ╰block-declaration──────────╯
   │ ╰declaration-statement──────╯
   │ ╰statement──────────────────╯
   ╰╴
