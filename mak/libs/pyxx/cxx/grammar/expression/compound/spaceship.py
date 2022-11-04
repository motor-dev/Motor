"""
compare-expression:
    shift-expression
    compare-expression <=> shift-expression
"""

import glrp
from ....parser import cxx98, cxx20
from .....ast.expressions import BinaryExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('compare-expression : shift-expression')
@glrp.rule('"compare-expression#" : "shift-expression#"')
@cxx98
def compare_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('compare-expression : compare-expression "<=>" shift-expression')
@glrp.rule('"compare-expression#" : "compare-expression#" "<=>" "shift-expression#"')
@cxx20
def compare_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1].text())


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser