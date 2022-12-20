"""
exclusive-or-expression:
    and-expression
    exclusive-or-expression ^ and-expression
"""

import glrp
from ....parse import cxx98
from .....ast.expressions import BinaryExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('exclusive-or-expression : and-expression')
@glrp.rule('"exclusive-or-expression#" : "and-expression#"')
@cxx98
def exclusive_or_expression_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('exclusive-or-expression : exclusive-or-expression "^" and-expression')
@glrp.rule('"exclusive-or-expression#" : "exclusive-or-expression#" "^" "and-expression#"')
@cxx98
def exclusive_or_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1].text())


if TYPE_CHECKING:
    from typing import Any
    from ....parse import CxxParser