"""
throw-expression:
    throw assignment-expression?
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import ThrowExpression


@glrp.rule('assignment-expression[prec:right,2] : [prec:right,2]"throw" assignment-expression?')
@glrp.rule('assignment-expression#[prec:right,2] : [prec:right,2]"throw" assignment-expression#?')
@cxx98
def throw_expression(self: CxxParser, p: glrp.Production) -> Any:
    return ThrowExpression(p[1])
