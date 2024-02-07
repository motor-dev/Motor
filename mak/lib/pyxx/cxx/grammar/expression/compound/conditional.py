"""
conditional-expression:
    logical-or-expression
    logical-or-expression ? expression : assignment-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import ConditionalExpression, ErrorExpression


@glrp.rule(
    'constant-expression[prec:right,2] : constant-expression [prec:right,2]"?" expression ":" assignment-expression')
@glrp.rule(
    'constant-expression#[prec:right,2] : constant-expression# [prec:right,2]"?" expression ":" assignment-expression#')
@cxx98
def conditional_expression(self: CxxParser, p: glrp.Production) -> Any:
    return ConditionalExpression(p[0], p[2], p[4])


@glrp.rule('constant-expression[prec:right,2] : constant-expression [prec:right,2]"?" "#error" ":" expression')
@glrp.rule(
    'constant-expression#[prec:right,2] : constant-expression# [prec:right,2]"?" "#error" ":" assignment-expression#')
@cxx98
def conditional_expression_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()
