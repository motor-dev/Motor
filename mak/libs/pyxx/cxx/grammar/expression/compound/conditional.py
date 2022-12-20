"""
conditional-expression:
    logical-or-expression
    logical-or-expression ? expression : assignment-expression
"""

import glrp
from ....parse import cxx98
from .....ast.expressions import ConditionalExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('conditional-expression : logical-or-expression')
@glrp.rule('"conditional-expression#" : "logical-or-expression#"')
@cxx98
def conditional_expression_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('conditional-expression : logical-or-expression "?" expression ":" assignment-expression')
@glrp.rule('"conditional-expression#" : "logical-or-expression#" "?" expression ":" "assignment-expression#"')
@cxx98
def conditional_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ConditionalExpression(p[0], p[2], p[4])


if TYPE_CHECKING:
    from typing import Any
    from ....parse import CxxParser