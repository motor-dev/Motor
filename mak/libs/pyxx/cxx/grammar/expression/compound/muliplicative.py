"""
multiplicative-expression:
    pm-expression
    multiplicative-expression * pm-expression
    multiplicative-expression / pm-expression
    multiplicative-expression % pm-expression
"""

import glrp
from ....parse import cxx98
from .....ast.expressions import BinaryExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('multiplicative-expression : pm-expression')
@cxx98
def multiplicative_expression_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('multiplicative-expression : multiplicative-expression "*" pm-expression')
@glrp.rule('multiplicative-expression : multiplicative-expression "/" pm-expression')
@glrp.rule('multiplicative-expression : multiplicative-expression "%" pm-expression')
@cxx98
def multiplicative_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1].text())


if TYPE_CHECKING:
    from typing import Any
    from ....parse import CxxParser