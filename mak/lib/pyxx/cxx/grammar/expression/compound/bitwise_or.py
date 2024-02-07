"""
inclusive-or-expression:
    exclusive-or-expression
    inclusive-or-expression | exclusive-or-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import BinaryExpression


@glrp.rule('constant-expression[prec:left,5] : constant-expression [prec:left,5]"|" constant-expression')
@glrp.rule('constant-expression#[prec:left,5] : constant-expression# [prec:left,5]"|" constant-expression#')
@cxx98
def inclusive_or_expression(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())
