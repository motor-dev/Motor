"""
compare-expression:
    shift-expression
    compare-expression <=> shift-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98, cxx20
from .....ast.expressions import BinaryExpression


@glrp.rule('constant-expression[prec:left,10] : constant-expression [prec:left,10]"<=>" constant-expression')
@glrp.rule('constant-expression#[prec:left,10] : constant-expression# [prec:left,10]"<=>" constant-expression#')
@cxx20
def compare_expression_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())
