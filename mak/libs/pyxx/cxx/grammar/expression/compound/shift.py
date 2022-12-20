"""
shift-expression:
    additive-expression
    shift-expression << additive-expression
    shift-expression >> additive-expression
"""

import glrp
from ....parse import cxx98, deprecated_cxx11
from .....ast.expressions import BinaryExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('">>" : "%>" ">"')
@cxx98
def rshift_symbol(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return '>>'


@glrp.rule('shift-expression : additive-expression')
@glrp.rule('"shift-expression#" : additive-expression')
@cxx98
def shift_expression_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('shift-expression : shift-expression "<<" additive-expression')
@glrp.rule('"shift-expression#" : "shift-expression#" "<<" additive-expression')
@cxx98
def shift_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1].text())


@glrp.rule('shift-expression : shift-expression ">>" additive-expression')
@cxx98
def shift_expression_right(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1])


@glrp.rule('"shift-expression#" : "shift-expression#" ">>" additive-expression')
@cxx98
@deprecated_cxx11
def shift_expression_right_cxx98_only(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1])


if TYPE_CHECKING:
    from typing import Any
    from ....parse import CxxParser