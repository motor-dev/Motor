"""
additive-expression:
    multiplicative-expression
    additive-expression + multiplicative-expression
    additive-expression - multiplicative-expression
"""

import glrp
from ....parser import cxx98
from .....ast.expressions import BinaryExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('additive-expression : multiplicative-expression')
@cxx98
def additive_expression_end(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('additive-expression : additive-expression "+" multiplicative-expression')
@glrp.rule('additive-expression : additive-expression "-" multiplicative-expression')
@cxx98
def additive_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1].text())


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser