"""
pm-expression:
    cast-expression
    pm-expression .* cast-expression
    pm-expression ->* cast-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import MemberPtrExpression


@glrp.rule('pm-expression : cast-expression')
@cxx98
def pm_expression_stop(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('pm-expression : pm-expression ".*" cast-expression')
@glrp.rule('pm-expression : pm-expression "->*" cast-expression')
@cxx98
def pm_expression(self: CxxParser, p: glrp.Production) -> Any:
    return MemberPtrExpression(p[0], p[2], p[1].text())
