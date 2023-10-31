"""
multiplicative-expression:
    pm-expression
    multiplicative-expression * pm-expression
    multiplicative-expression / pm-expression
    multiplicative-expression % pm-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import BinaryExpression


@glrp.rule('multiplicative-expression : pm-expression')
@cxx98
def multiplicative_expression_stop(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('multiplicative-expression : multiplicative-expression "*" pm-expression')
@glrp.rule('multiplicative-expression : multiplicative-expression "/" pm-expression')
@glrp.rule('multiplicative-expression : multiplicative-expression "%" pm-expression')
@cxx98
def multiplicative_expression(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())
