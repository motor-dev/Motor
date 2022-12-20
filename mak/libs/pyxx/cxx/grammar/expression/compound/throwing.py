"""
throw-expression:
    throw assignment-expression?
"""

import glrp
from ....parse import cxx98
from .....ast.expressions import ThrowExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('throw-expression : "throw" assignment-expression?')
@glrp.rule('"throw-expression#" : "throw" "assignment-expression#"?')
@cxx98
def throw_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ThrowExpression(p[1])


if TYPE_CHECKING:
    from typing import Any
    from ....parse import CxxParser