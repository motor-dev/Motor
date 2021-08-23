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
from ...parser import cxx98, until_cxx17, cxx17
from motor_typing import TYPE_CHECKING


@glrp.rule('using-declaration : "using" "typename"? nested-name-specifier unqualified-id ";"')
@glrp.rule('using-declaration : "using" "::" unqualified-id ";"')
@cxx98
@until_cxx17
def using_declaration_until_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('using-declaration : "using" using-declarator-list ";"')
@cxx17
def using_declaration_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('using-declarator-list : using-declarator "..."?')
@glrp.rule('using-declarator-list : using-declarator-list "," using-declarator "..."?')
@cxx17
def using_declarator_list_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('using-declarator : "typename"? nested-name-specifier unqualified-id')
@cxx17
def using_declarator_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser