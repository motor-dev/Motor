"""
unary-expression:
    postfix-expression
    unary-operator cast-expression
    ++ cast-expression
    -- cast-expression
    await-expression
    sizeof unary-expression
    sizeof ( type-id )
    sizeof ... ( identifier )
    alignof ( type-id )
    noexcept-expression
    new-expression
    delete-expression

unary-operator: one of
    *  &  +  -  !  ~
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx98, cxx11
from ......ast.expressions import (
    UnaryExpression,
    SizeofExpression,
    SizeofTypeExpression,
    SizeofPackExpression,
    AlignofExpression,
    ErrorExpression,
)


@glrp.rule('constant-expression[prec:right,15] : unary-operator constant-expression')
@glrp.rule('constant-expression#[prec:right,15] : unary-operator constant-expression#')
@cxx98
def unary_expression(self: CxxParser, p: glrp.Production) -> Any:
    return UnaryExpression(p[1], p[0])


@glrp.rule('constant-expression : "sizeof" "..." "(" identifier ")"')
@glrp.rule('constant-expression# : "sizeof" "..." "(" identifier ")"')
@cxx11
def unary_expression_sizeof_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return SizeofPackExpression(p[3].value)


@glrp.rule('constant-expression : "sizeof" "..." "(" "#error" ")"')
@glrp.rule('constant-expression# : "sizeof" "..." "(" "#error" ")"')
@cxx11
def unary_expression_sizeof_error_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('constant-expression : "alignof" "(" type-id ")"')
@glrp.rule('constant-expression# : "alignof" "(" type-id ")"')
@cxx11
def unary_expression_alignof_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return AlignofExpression(p[0].text(), p[2])


@glrp.rule('constant-expression : "alignof-macro" "(" type-id ")"')
@glrp.rule('constant-expression# : "alignof-macro" "(" type-id ")"')
@cxx98
def unary_expression_alignof_macro(self: CxxParser, p: glrp.Production) -> Any:
    return AlignofExpression(p[0].text(), p[2])


@glrp.rule('constant-expression : "alignof" "(" "#error" ")"')
@glrp.rule('constant-expression# : "alignof" "(" "#error" ")"')
@cxx11
def unary_expression_alignof_error_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()
    return ErrorExpression()


@glrp.rule('constant-expression : "alignof-macro" "(" "#error" ")"')
@glrp.rule('constant-expression# : "alignof-macro" "(" "#error" ")"')
@cxx98
def unary_expression_alignof_macro_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('constant-expression[prec:right,15] : [prec:right,15]"sizeof" constant-expression')
@glrp.rule('constant-expression#[prec:right,15] : [prec:right,15]"sizeof" constant-expression#')
@cxx98
def sizeof_expression(self: CxxParser, p: glrp.Production) -> Any:
    return SizeofExpression(p[1])


@glrp.rule('constant-expression[prec:right,15] : "sizeof" "(" begin-type-id type-id ")"')
@glrp.rule('constant-expression#[prec:right,15] : "sizeof" "(" begin-type-id type-id ")"')
@cxx98
def sizeof_expression_type(self: CxxParser, p: glrp.Production) -> Any:
    return SizeofTypeExpression(p[3])


@glrp.rule('constant-expression[prec:right,15] : "sizeof" "(" begin-type-id "#error" ")"')
@glrp.rule('constant-expression#[prec:right,15] : "sizeof" "(" begin-type-id "#error" ")"')
@cxx98
def sizeof_expression_type_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule(
    'unary-operator : [prec:right,15]"*" | [prec:right,15]"&" | [prec:right,15]"+" | [prec:right,15]"-" | [prec:right,15]"!" | [prec:right,15]"~"[prec:right,2] | [prec:right,15]"++" | [prec:right,15]"--"')
@cxx98
def unary_operator(self: CxxParser, p: glrp.Production) -> Any:
    return p[0].text()
