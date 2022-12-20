"""
pm-expression:
    cast-expression
    pm-expression .* cast-expression
    pm-expression ->* cast-expression
"""

import glrp
from ....parse import cxx98
from .....ast.expressions import MemberPtrExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('pm-expression : cast-expression')
@cxx98
def pm_expression_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('pm-expression : pm-expression ".*" cast-expression')
@glrp.rule('pm-expression : pm-expression "->*" cast-expression')
@cxx98
def pm_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return MemberPtrExpression(p[0], p[2])


if TYPE_CHECKING:
    from typing import Any
    from ....parse import CxxParser