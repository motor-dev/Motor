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
from ...parser import cxx98, cxx11, cxx17, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('iteration-statement : "while" "(" condition ")" statement')
@glrp.rule('iteration-statement : "do" statement "while" "(" expression ")" ";"')
@glrp.rule('iteration-statement : "for" "(" for-range ")" statement')
@cxx98
def iteration_statement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('for-range : init-statement condition? ";" expression?')
@cxx98
def for_range(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('for-range : for-range-declaration-declarator ":" for-range-initializer')
@glrp.rule('for-range : init-statement for-range-declaration-declarator ":" for-range-initializer')
@cxx11
def for_range_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('for-range : for-range-declaration-no-declarator ":" for-range-initializer')
@glrp.rule('for-range : init-statement for-range-declaration-no-declarator ":" for-range-initializer')
@cxx17
def for_range_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule(
    'for-range-declaration-declarator : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? declarator'
)
@cxx11
def for_range_declaration_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule(
    'for-range-declaration-no-declarator : attribute-specifier-seq? begin-declaration decl-specifier-seq? ref-qualifier? "[" identifier-list "]"'
)
@cxx17
def for_range_declaration_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('for-range-initializer : expr-or-braced-init-list')
@cxx11
def for_range_initializer_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('for-range-declaration-declarator')
@cxx98_merge
def ambiguous_for_range_declaration(self, decl_specifier_seq_end, decl_specifier_seq_continue):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('for-range-declaration-no-declarator')
@cxx98_merge
def ambiguous_for_range_declaration_no_declarator_final(self, final_keyword, final_identifier):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    if len(final_keyword) == 1:
        return final_keyword[0]
    elif len(final_keyword) > 1:
        return None    # TODO
    else:
        assert len(final_identifier) > 1
        return None    # TODO


@glrp.merge('for-range-declaration-declarator')
@cxx98_merge
def ambiguous_for_range_declaration_final(self, final_keyword, final_identifier):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    if len(final_keyword) == 1:
        return final_keyword[0]
    elif len(final_keyword) > 1:
        return None    # TODO
    else:
        assert len(final_identifier) > 1
        return None    # TODO


@glrp.merge('for-range')
@cxx98_merge
def ambiguous_for_range(
    self, ambiguous_for_range_declaration, ambiguous_init_statement, ambiguous_condition_opt, ambiguous_condition_opt_2,
    decl_specifier_seq_continue, ambiguous_simple_declaration
):
    # type: (CxxParser, List[Any], List[Any], List[Any], List[Any], List[Any], List[Any]) -> Any
    pass


@glrp.merge('for-range')
@cxx98_merge
def ambiguous_for_range_2(self, continue_declarator_list, ambiguous_init_declarator_initializer):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ...parser import CxxParser