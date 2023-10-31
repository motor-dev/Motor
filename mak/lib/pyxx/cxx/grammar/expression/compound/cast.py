"""
cast-expression:
    unary-expression
    ( type-id ) cast-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import CastExpression, ErrorExpression


@glrp.rule('cast-expression : unary-expression')
@cxx98
def cast_expression_stop(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('cast-expression : "(" begin-type-id type-id ")" cast-expression')
@cxx98
def cast_expression(self: CxxParser, p: glrp.Production) -> Any:
    return CastExpression(p[4], p[2])


@glrp.rule('cast-expression : "(" begin-type-id "#error" ")" cast-expression')
@cxx98
def cast_expression_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()
