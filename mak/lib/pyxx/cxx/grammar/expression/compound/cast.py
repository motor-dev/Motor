"""
cast-expression:
    unary-expression
    ( type-id ) cast-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98, cxx20
from .....ast.expressions import CastExpression, ErrorExpression


@glrp.rule('constant-expression[prec:right,15] : [prec:right,15]"(" begin-type-id type-id ")" constant-expression')
@glrp.rule('constant-expression#[prec:right,15] : [prec:right,15]"(" begin-type-id type-id ")" constant-expression#')
@cxx98
def cast_expression(self: CxxParser, p: glrp.Production) -> Any:
    return CastExpression(p[4], p[2])


@glrp.rule('constant-expression[prec:right,15] : [prec:right,15]"(" begin-type-id "#error" ")" constant-expression')
@glrp.rule('constant-expression#[prec:right,15] : [prec:right,15]"(" begin-type-id "#error" ")" constant-expression#')
@cxx98
def cast_expression_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()
