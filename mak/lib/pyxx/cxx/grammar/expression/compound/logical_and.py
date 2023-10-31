"""
logical-and-expression:
    inclusive-or-expression
    logical-and-expression && inclusive-or-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import BinaryExpression


@glrp.rule('logical-and-expression : inclusive-or-expression')
@glrp.rule('"logical-and-expression#" : "inclusive-or-expression#"')
@cxx98
def logical_and_expression_stop(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('logical-and-expression : logical-and-expression "&&" inclusive-or-expression')
@glrp.rule('"logical-and-expression#" : "logical-and-expression#" "&&" "inclusive-or-expression#"')
@cxx98
def logical_and_expression(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())