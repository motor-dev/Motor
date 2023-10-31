"""
exclusive-or-expression:
    and-expression
    exclusive-or-expression ^ and-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import BinaryExpression


@glrp.rule('exclusive-or-expression : and-expression')
@glrp.rule('"exclusive-or-expression#" : "and-expression#"')
@cxx98
def exclusive_or_expression_stop(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('exclusive-or-expression : exclusive-or-expression "^" and-expression')
@glrp.rule('"exclusive-or-expression#" : "exclusive-or-expression#" "^" "and-expression#"')
@cxx98
def exclusive_or_expression(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())
