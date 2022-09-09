"""
iteration-statement:
    while ( condition ) statement
    do statement while ( expression ) ;
    for ( init-statement condition? ; expression? ) statement
    for ( init-statement? for-range-declaration : for-range-initializer ) statement

for-range-declaration:
    attribute-specifier-seq? decl-specifier-seq declarator
    attribute-specifier-seq? decl-specifier-seq ref-qualifier? [ identifier-list ]

for-range-initializer:
    expr-or-braced-init-list
"""

import glrp
from ...parser import cxx98, cxx11
from motor_typing import TYPE_CHECKING


@glrp.rule('iteration-statement : "while" "(" condition ")" statement')
@glrp.rule('iteration-statement : "do" statement "while" "(" expression ")" ";"')
@glrp.rule('iteration-statement : "for" "(" for-range ")" statement')
@cxx98
def iteration_statement(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('for-range : init-statement condition? ";" expression?')
@cxx98
def for_range(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('for-range : for-range-declaration ":" for-range-initializer')
@glrp.rule('for-range : init-statement for-range-declaration ":" for-range-initializer')
@cxx11
def for_range_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule(
    'for-range-declaration : begin-simple-declaration attribute-specifier-seq? decl-specifier-seq begin-declarator-no-initializer declarator'
)
@glrp.rule(
    'for-range-declaration : begin-simple-declaration attribute-specifier-seq? decl-specifier-seq begin-declarator-no-initializer ref-qualifier? "[" identifier-list "]"'
)
@cxx11
def for_range_declaration_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('for-range-initializer : expr-or-braced-init-list')
@cxx11
def for_range_initializer_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser