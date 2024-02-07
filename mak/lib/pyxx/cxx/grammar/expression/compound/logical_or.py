"""
logical-or-expression:
    logical-and-expression
    logical-or-expression || logical-and-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98, cxx20
from .....ast.expressions import BinaryExpression


@glrp.rule('constant-expression[prec:left,3] : constant-expression [prec:left,3]"||" constant-expression')
@glrp.rule('constant-expression#[prec:left,3] : constant-expression# [prec:left,3]"||" constant-expression#')
@cxx98
def logical_or_expression(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())


@glrp.rule(
    'constraint-logical-expression[prec:left,3] : constraint-logical-expression [prec:left,3]"||" constraint-logical-expression')
@cxx20
def logical_or_expression_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())
