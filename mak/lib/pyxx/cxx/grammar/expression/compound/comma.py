"""
expression:
    assignment-expression
    expression , assignment-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import BinaryExpression
from typing import TYPE_CHECKING


@glrp.rule('expression[prec:left,1] : assignment-expression')
@glrp.rule('expression?[prec:left,1] : expression')
@cxx98
def expression(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('expression[prec:left,1] : expression [prec:left,1]"," assignment-expression')
@cxx98
def expression_comma(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())


@glrp.rule('expression? : ')
@cxx98
def expression_opt(self: CxxParser, p: glrp.Production) -> Any:
    return None
