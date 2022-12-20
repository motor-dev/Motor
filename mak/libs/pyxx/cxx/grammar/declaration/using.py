"""
c++ 98-14:
using-declaration:
    using typename? nested-name-specifier unqualified-id ;
    using :: unqualified-id ;

c++ 17:
using-declaration:
    using using-declarator-list ;

using-declarator-list:
    using-declarator ...?
    using-declarator-list , using-declarator ...?

using-declarator:
    typename? nested-name-specifier unqualified-id
"""

import glrp
from ...parse import cxx98, deprecated_cxx17, cxx17
from ....ast.declarations import UsingDeclaration
from ....ast.reference import Reference, RootId
from motor_typing import TYPE_CHECKING


# TODO:attribute-specifier-seq? empty, template?
@glrp.rule(
    'using-declaration : attribute-specifier-seq? begin-declaration "using" "typename"? nested-name-specifier template? unqualified-id ";"'
)
@cxx98
@deprecated_cxx17
def using_declaration_nested_until_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    # using :: unqualified-id ; is covered here
    return UsingDeclaration(p[0], [(p[3], False, Reference(p[4] + [(p[5], p[6])]))])


# TODO:attribute-specifier-seq? empty
@glrp.rule('using-declaration : attribute-specifier-seq? begin-declaration "using" using-declarator-list ";"')
@cxx17
def using_declaration_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return UsingDeclaration(p[0], p[3])


@glrp.rule('using-declarator-list : using-declarator "..."?')
@cxx17
def using_declarator_list_last_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [(p[0][0], p[1], p[0][1])]


@glrp.rule('using-declarator-list : using-declarator-list "," using-declarator "..."?')
@cxx17
def using_declarator_list_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    result.append((p[2][0], p[3], p[2][1]))
    return result


@glrp.rule('using-declarator : "typename"? nested-name-specifier template? unqualified-id')
@cxx17
def using_declarator_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (p[0], Reference(p[1] + [(p[2], p[3])]))


@glrp.rule('"typename"? : "typename"')
@cxx98
def typename(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return True


@glrp.rule('"typename"? :')
@cxx98
def typename_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return False


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser