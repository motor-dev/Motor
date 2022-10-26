"""
logical-and-expression:
    inclusive-or-expression
    logical-and-expression && inclusive-or-expression
"""

import glrp
from ....parser import cxx98
from .....ast.expressions import BinaryExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('logical-and-expression : inclusive-or-expression')
@cxx98
def logical_and_expression_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('logical-and-expression : logical-and-expression "&&" inclusive-or-expression')
@cxx98
def logical_and_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1].text())


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser