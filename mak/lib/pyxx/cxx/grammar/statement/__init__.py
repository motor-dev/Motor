"""
statement:
    labeled-statement
    attribute-specifier-seq? expression-statement
    attribute-specifier-seq? compound-statement
    attribute-specifier-seq? selection-statement
    attribute-specifier-seq? iteration-statement
    attribute-specifier-seq? jump-statement
    declaration-statement
    attribute-specifier-seq? try-block

init-statement:
    expression-statement
    simple-declaration

condition:
    expression
    attribute-specifier-seq? decl-specifier-seq declarator brace-or-equal-initializer
"""

import glrp
from typing import Any, List
from ...parse import CxxParser, cxx98, cxx98_merge
from ....ast.statements import AmbiguousStatement, ExpressionStatement, DeclarationStatement, StatementWithAttributes
from ....ast.declarations import SimpleDeclaration, InitDeclarator, InitDeclaratorList
from . import labeled
from . import expression
from . import block
from . import selection
from . import iteration
from . import jump
from . import declaration


@glrp.rule('statement : declaration-statement')
@glrp.rule('statement : labeled-statement')
@cxx98
def statement(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('statement : attribute-specifier-seq? begin-expression-statement expression-statement')
@glrp.rule('statement : attribute-specifier-seq? begin-expression-statement compound-statement')
@glrp.rule('statement : attribute-specifier-seq? begin-expression-statement selection-statement')
@glrp.rule('statement : attribute-specifier-seq? begin-expression-statement iteration-statement')
@glrp.rule('statement : attribute-specifier-seq? begin-expression-statement jump-statement')
@glrp.rule('statement : attribute-specifier-seq? begin-expression-statement try-block')
@cxx98
def statement_expression(self: CxxParser, p: glrp.Production) -> Any:
    if p[0]:
        return StatementWithAttributes(p[0], p[2])
    else:
        return p[2]


@glrp.rule('init-statement : simple-declaration')
@cxx98
def init_statement(self: CxxParser, p: glrp.Production) -> Any:
    return DeclarationStatement(p[0])


@glrp.rule('init-statement : attribute-specifier-seq? begin-expression-statement expression-statement')
@cxx98
def init_statement_expression(self: CxxParser, p: glrp.Production) -> Any:
    # TODO: attribute-specifier-seq? not allowed here
    if p[0]:
        return StatementWithAttributes(p[0], p[2])
    else:
        return p[2]


@glrp.rule('condition : attribute-specifier-seq? begin-expression-statement expression')
@glrp.rule('condition? : attribute-specifier-seq? begin-expression-statement expression')
@cxx98
def condition(self: CxxParser, p: glrp.Production) -> Any:
    # TODO: attribute-specifier-seq? expression attribute-specifier-seq should be empty
    if p[0]:
        return StatementWithAttributes(p[0], p[2])
    else:
        return p[2]


@glrp.rule(
    'condition : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? declarator-initializer brace-or-equal-initializer'
)
@glrp.rule(
    'condition? : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? declarator-initializer brace-or-equal-initializer'
)
@cxx98
def condition_decl(self: CxxParser, p: glrp.Production) -> Any:
    return DeclarationStatement(SimpleDeclaration(p[0], p[2], [[((0, 0), InitDeclarator(p[3], p[4], None))]]))


@glrp.rule('condition? :')
@cxx98
def condition_opt(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('begin-expression-statement : [split:expression_statement]')
@cxx98
def begin_statement(self: CxxParser, p: glrp.Production) -> Any:
    pass


@glrp.merge('condition')
@cxx98_merge
def ambiguous_condition(
        self: CxxParser, expression_statement: List[Any], simple_declaration: List[Any],
        ambiguous_simple_declaration: List[Any]
) -> Any:
    return AmbiguousStatement(expression_statement + simple_declaration + ambiguous_simple_declaration)


@glrp.merge('condition')
@cxx98_merge
def ambiguous_condition_2(
        self: CxxParser, decl_specifier_seq_end: List[Any], decl_specifier_seq_continue: List[Any]
) -> Any:
    return AmbiguousStatement(decl_specifier_seq_end + decl_specifier_seq_continue)


@glrp.merge('condition')
@cxx98_merge
def ambiguous_condition_final(self: CxxParser, final_keyword: List[Any], final_identifier: List[Any]) -> Any:
    if len(final_keyword) == 1:
        return final_keyword[0]
    elif len(final_keyword) > 1:
        return AmbiguousStatement(final_keyword)
    else:
        assert len(final_identifier) > 1
        return AmbiguousStatement(final_identifier)


@glrp.merge('condition?')
@cxx98_merge
def ambiguous_condition_opt(
        self: CxxParser, expression_statement: List[Any], simple_declaration: List[Any],
        ambiguous_simple_declaration: List[Any]
) -> Any:
    return AmbiguousStatement(expression_statement + simple_declaration + ambiguous_simple_declaration)


@glrp.merge('condition?')
@cxx98_merge
def ambiguous_condition_opt_2(
        self: CxxParser, decl_specifier_seq_end: List[Any], decl_specifier_seq_continue: List[Any]
) -> Any:
    return AmbiguousStatement(decl_specifier_seq_end + decl_specifier_seq_continue)


@glrp.merge('condition?')
@cxx98_merge
def ambiguous_condition_ext_final(self: CxxParser, final_keyword: List[Any], final_identifier: List[Any]) -> Any:
    if len(final_keyword) == 1:
        return final_keyword[0]
    elif len(final_keyword) > 1:
        return AmbiguousStatement(final_keyword)
    else:
        assert len(final_identifier) > 1
        return AmbiguousStatement(final_identifier)


@glrp.merge('init-statement')
@cxx98_merge
def ambiguous_init_statement(
        self: CxxParser, expression_statement: List[Any], ambiguous_simple_declaration: List[Any]
) -> Any:
    return AmbiguousStatement(expression_statement + ambiguous_simple_declaration)


@glrp.merge('statement')
@cxx98_merge
def ambiguous_statement(
        self: CxxParser, expression_statement: List[Any], ambiguous_simple_declaration: List[Any]
) -> Any:
    return AmbiguousStatement(expression_statement + ambiguous_simple_declaration)
