"""
logical-or-expression:
    logical-and-expression
    logical-or-expression || logical-and-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import BinaryExpression


@glrp.rule('logical-or-expression : logical-and-expression')
@glrp.rule('"logical-or-expression#" : "logical-and-expression#"')
@cxx98
def logical_or_expression_stop(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('logical-or-expression : logical-or-expression "||" logical-and-expression')
@glrp.rule('"logical-or-expression#" : "logical-or-expression#" "||" "logical-and-expression#"')
@cxx98
def logical_or_expression(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())
