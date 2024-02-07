"""
relational-expression:
    compare-expression
    relational-expression < compare-expression
    relational-expression > compare-expression
    relational-expression <= compare-expression
    relational-expression >= compare-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import BinaryExpression


@glrp.rule('constant-expression[prec:left,9] : constant-expression [prec:left,9]"<" constant-expression')
@glrp.rule('constant-expression[prec:left,9] : constant-expression [prec:left,9]">" constant-expression')
@glrp.rule('constant-expression[prec:left,9] : constant-expression [prec:left,9]"<=" constant-expression')
@glrp.rule('constant-expression[prec:left,9] : constant-expression [prec:left,9]">=" constant-expression')
@glrp.rule('constant-expression#[prec:left,9] : constant-expression# [prec:left,9]"<" constant-expression#')
# @glrp.rule('constant-expression# : constant-expression# ">" constant-expression#')
@glrp.rule('constant-expression#[prec:left,9] : constant-expression# [prec:left,9]"<=" constant-expression#')
@glrp.rule('constant-expression#[prec:left,9] : constant-expression# [prec:left,9]">=" constant-expression#')
@cxx98
def relational_expression(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())
