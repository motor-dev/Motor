"""
shift-expression:
    additive-expression
    shift-expression << additive-expression
    shift-expression >> additive-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98, deprecated_cxx11
from .....ast.expressions import BinaryExpression


@glrp.rule('">>" : [prec:left,11]"%>" ">"')
@cxx98
def rshift_symbol(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('constant-expression[prec:left,11] : constant-expression [prec:left,11]"<<" constant-expression')
@glrp.rule('constant-expression#[prec:left,11] : constant-expression# [prec:left,11]"<<" constant-expression#')
@cxx98
def shift_expression(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())


@glrp.rule('constant-expression[prec:left,11] : constant-expression [prec:left,11]">>" constant-expression')
@cxx98
def shift_expression_right(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], '>>')


@glrp.rule('constant-expression#[prec:left,11] : constant-expression# [prec:left,11]">>" constant-expression#')
@cxx98
@deprecated_cxx11
def shift_expression_right_cxx98_only(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], '>>')
