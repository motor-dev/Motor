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
from ...parser import cxx98, cxx11, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('iteration-statement : "while" "(" condition ")" statement')
@glrp.rule('iteration-statement : "do" statement "while" "(" expression ")" ";"')
@glrp.rule('iteration-statement : "for" "(" for-range ")" statement')
@cxx98
def iteration_statement(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('for-range : begin-init-statement init-statement condition? ";" expression?')
@cxx98
def for_range(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule(
    'for-range : begin-for-range-declaration-declarator for-range-declaration-declarator ":" for-range-initializer'
)
@glrp.rule(
    'for-range : begin-for-range-declaration-no-declarator for-range-declaration-no-declarator ":" for-range-initializer'
)
@glrp.rule(
    'for-range : begin-init-statement init-statement begin-for-range-declaration-declarator for-range-declaration-declarator ":" for-range-initializer'
)
@glrp.rule(
    'for-range : begin-init-statement init-statement begin-for-range-declaration-no-declarator for-range-declaration-no-declarator ":" for-range-initializer'
)
@cxx11
def for_range_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule(
    'for-range-declaration-declarator : begin-simple-declaration attribute-specifier-seq? [no-merge-warning] decl-specifier-seq begin-declarator-no-initializer declarator'
)
@glrp.rule(
    'for-range-declaration-no-declarator : begin-simple-declaration attribute-specifier-seq? decl-specifier-seq begin-declarator-no-initializer ref-qualifier? "[" identifier-list "]"'
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


@glrp.rule('begin-for-range-declaration-declarator : [split:for_range_declaration_declarator]')
@glrp.rule('begin-for-range-declaration-no-declarator : [split:for_range_declaration_no_declarator]')
@cxx11
def begin_for_range_declaration_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('for-range')
@cxx98_merge
def ambiguous_for_range(
    self, init_statement, for_range_declaration_declarator, for_range_declaration_no_declarator, ambiguous_condition_opt
):
    # type: (CxxParser, Any, Any, Any, Any) -> Any
    pass


@glrp.merge('for-range-declaration-declarator')
@cxx98_merge
def ambiguous_for_range_declaration_declarator(self, decl_specifier_seq_end, decl_specifier_seq_continue):
    # type: (CxxParser, Any, Any) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ...parser import CxxParser