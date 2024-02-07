"""
additive-expression:
    multiplicative-expression
    additive-expression + multiplicative-expression
    additive-expression - multiplicative-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import BinaryExpression


@glrp.rule('constant-expression[prec:left,12] : constant-expression [prec:left,12]"+" constant-expression')
@glrp.rule('constant-expression[prec:left,12] : constant-expression [prec:left,12]"-" constant-expression')
@glrp.rule('constant-expression#[prec:left,12] : constant-expression# [prec:left,12]"+" constant-expression#')
@glrp.rule('constant-expression#[prec:left,12] : constant-expression# [prec:left,12]"-" constant-expression#')
@cxx98
def additive_expression(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())
