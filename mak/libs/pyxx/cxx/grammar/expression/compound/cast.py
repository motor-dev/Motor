"""
cast-expression:
    unary-expression
    ( type-id ) cast-expression
"""

import glrp
from ....parse import cxx98
from .....ast.expressions import CastExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('cast-expression : unary-expression')
@cxx98
def cast_expression_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('cast-expression : "(" begin-type-id type-id ")" cast-expression')
@cxx98
def cast_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return CastExpression(p[4], p[2])


if TYPE_CHECKING:
    from typing import Any
    from ....parse import CxxParser