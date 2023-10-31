"""
compare-expression:
    shift-expression
    compare-expression <=> shift-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98, cxx20
from .....ast.expressions import BinaryExpression


@glrp.rule('compare-expression : shift-expression')
@glrp.rule('"compare-expression#" : "shift-expression#"')
@cxx98
def compare_expression(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('compare-expression : compare-expression "<=>" shift-expression')
@glrp.rule('"compare-expression#" : "compare-expression#" "<=>" "shift-expression#"')
@cxx20
def compare_expression_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())
