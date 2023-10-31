"""
and-expression:
    equality-expression
    and-expression & equality-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import BinaryExpression


@glrp.rule('and-expression : equality-expression')
@glrp.rule('"and-expression#" : "equality-expression#"')
@cxx98
def and_expression_stop(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('and-expression : and-expression "&" equality-expression')
@glrp.rule('"and-expression#" : "and-expression#" "&" "equality-expression#"')
@cxx98
def and_expression(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())
