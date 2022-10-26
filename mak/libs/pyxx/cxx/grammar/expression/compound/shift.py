"""
shift-expression:
    additive-expression
    shift-expression << additive-expression
    shift-expression >> additive-expression
"""

import glrp
from ....parser import cxx98
from .....ast.expressions import BinaryExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('shift-expression : additive-expression')
@cxx98
def shift_expression_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('shift-expression : shift-expression "<<" additive-expression')
@glrp.rule('shift-expression : shift-expression ">>" additive-expression')
@cxx98
def shift_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1].text())


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser