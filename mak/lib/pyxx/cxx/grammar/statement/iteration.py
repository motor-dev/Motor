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
from typing import Any, List
from ...parse import CxxParser, cxx98, cxx11, cxx17, cxx20, cxx98_merge
from ....ast.statements import WhileStatement, DoWhileStatement, ForStatement, AmbiguousForCondition, ForConditionInit, \
    ForConditionRange, ErrorStatement
from ....ast.declarations import SimpleDeclaration, AmbiguousDeclaration, InitDeclarator, InitDeclaratorList, \
    StructuredBindingDeclaration
from ....ast.expressions import ErrorExpression


@glrp.rule('iteration-statement : "while" "(" condition ")" statement')
@cxx98
def iteration_statement_while(self: CxxParser, p: glrp.Production) -> Any:
    return WhileStatement(p[2], p[4])


@cxx98
def iteration_statement_while_error(self: CxxParser, p: glrp.Production) -> Any:
    return WhileStatement(p[2], p[4])


@glrp.rule('iteration-statement : "do" statement "while" "(" expression ")" ";"')
@cxx98
def iteration_statement_do_while(self: CxxParser, p: glrp.Production) -> Any:
    return DoWhileStatement(p[4], p[1])


@glrp.rule('iteration-statement : "for" "(" for-range ")" statement')
@cxx98
def iteration_statement_for(self: CxxParser, p: glrp.Production) -> Any:
    return ForStatement(p[2], p[4])


@glrp.rule('for-range : init-statement condition? ";" expression?')
@cxx98
def for_range(self: CxxParser, p: glrp.Production) -> Any:
    return ForConditionInit(p[0], p[1], p[3])


@glrp.rule('for-range : init-statement condition? ";" #error')
@cxx98
def for_range_error(self: CxxParser, p: glrp.Production) -> Any:
    return ForConditionInit(p[0], p[1], ErrorExpression())


@glrp.rule('for-range : for-range-declaration-declarator')
@cxx11
def for_range_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return ForConditionRange(None, p[0])


@glrp.rule('for-range : for-range-declaration-no-declarator')
@cxx17
def for_range_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return ForConditionRange(None, p[0])


@glrp.rule('for-range : init-statement for-range-declaration-declarator')
@glrp.rule('for-range : init-statement for-range-declaration-no-declarator')
@cxx20
def for_range_init_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return ForConditionRange(p[0], p[1])


@glrp.rule(
    'for-range-declaration-declarator : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? declarator  ":" for-range-initializer'
)
@cxx11
def for_range_declaration_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleDeclaration(p[0], p[2], [[((0, 0), InitDeclarator(p[3], p[5], None))]])


@glrp.rule(
    'for-range-declaration-no-declarator : attribute-specifier-seq? begin-declaration decl-specifier-seq? ref-qualifier? "[" identifier-list "]"  ":" for-range-initializer'
)
@cxx17
def for_range_declaration_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return StructuredBindingDeclaration(p[0], p[2], p[3], p[5], p[8])


@glrp.rule('for-range-initializer : expr-or-braced-init-list')
@cxx11
def for_range_initializer_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('iteration-statement : "for" "(" [prec:right,-1]"#error" ")" statement')
@glrp.rule('iteration-statement : "while" "(" "#error" ")" statement')
@glrp.rule('iteration-statement : "do" statement "while" "(" "#error" ")" ";"')
@cxx98
def statement_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorStatement()


@glrp.merge('for-range-declaration-declarator')
@cxx98_merge
def ambiguous_for_range_declaration(
        self: CxxParser, decl_specifier_seq_end: List[Any], decl_specifier_seq_continue: List[Any]
) -> Any:
    return AmbiguousDeclaration(decl_specifier_seq_end + decl_specifier_seq_continue)


@glrp.merge('for-range-declaration-no-declarator')
@cxx98_merge
def ambiguous_for_range_declaration_no_declarator_final(
        self: CxxParser, final_keyword: List[Any], final_identifier: List[Any]
) -> Any:
    if len(final_keyword) == 1:
        return final_keyword[0]
    elif len(final_keyword) > 1:
        return AmbiguousDeclaration(final_keyword)
    else:
        assert len(final_identifier) > 1
        return AmbiguousDeclaration(final_identifier)


@glrp.merge('for-range-declaration-declarator')
@cxx98_merge
def ambiguous_for_range_declaration_final(
        self: CxxParser, final_keyword: List[Any], final_identifier: List[Any]
) -> Any:
    if len(final_keyword) == 1:
        return final_keyword[0]
    elif len(final_keyword) > 1:
        return AmbiguousDeclaration(final_keyword)
    else:
        assert len(final_identifier) > 1
        return AmbiguousDeclaration(final_identifier)


@glrp.merge('for-range')
@cxx98_merge
def ambiguous_for_range(
        self: CxxParser, ambiguous_for_range_declaration: List[Any], ambiguous_init_statement: List[Any],
        ambiguous_condition_opt: List[Any], ambiguous_condition_opt_2: List[Any],
        decl_specifier_seq_continue: List[Any],
        ambiguous_simple_declaration: List[Any]
) -> Any:
    return AmbiguousForCondition(
        ambiguous_for_range_declaration + ambiguous_init_statement + ambiguous_condition_opt +
        ambiguous_condition_opt_2 + decl_specifier_seq_continue + ambiguous_simple_declaration
    )


@glrp.merge('for-range')
@cxx98_merge
def ambiguous_for_range_2(
        self: CxxParser, continue_declarator_list: List[Any], ambiguous_init_declarator_initializer: List[Any]
) -> Any:
    return AmbiguousForCondition(continue_declarator_list + ambiguous_init_declarator_initializer)
