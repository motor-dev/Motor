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
from ...parser import cxx98, cxx11, cxx11_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('iteration-statement : "while" "(" condition ")" statement')
@glrp.rule('iteration-statement : "do" statement "while" "(" expression ")" ";"')
@glrp.rule('iteration-statement : "for" "(" init-statement condition? ";" expression? ")" statement')
@cxx98
def iteration_statement(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('iteration-statement : "for" "(" for-range-declaration ":" for-range-initializer ")" statement')
@glrp.rule(
    'iteration-statement : "for" "(" init-statement for-range-declaration ":" for-range-initializer ")" statement'
)
@cxx11
def iteration_statement_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('for-range-declaration : attribute-specifier-seq? decl-specifier-seq declarator')
@glrp.rule('for-range-declaration : attribute-specifier-seq? decl-specifier-seq ref-qualifier? "[" identifier-list "]"')
@cxx11
def for_range_declaration_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('for-range-initializer : expr-or-braced-init-list')
@cxx11
def for_range_initializer_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('for-range-declaration')
@cxx11_merge
def for_range_declaration(self, ambiguous_type_specifier):
    # type: (CxxParser, Optional[glrp.Production]) -> None
    # Simple rename
    pass


@glrp.merge('iteration-statement')
@cxx11_merge
def ambiguous_iteration_statement(self, for_range_declaration, ambiguous_condition_opt, ambiguous_init_statement):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


if TYPE_CHECKING:
    from typing import Optional
    from ...parser import CxxParser