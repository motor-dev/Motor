"""
equality-expression:
    relational-expression
    equality-expression == relational-expression
    equality-expression != relational-expression
"""

import glrp
from ....parser import cxx98
from .....ast.expressions import BinaryExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('equality-expression : [no-merge-warning] relational-expression')
@glrp.rule('"equality-expression#" : [no-merge-warning] "relational-expression#"')
@cxx98
def equality_expression_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('equality-expression : equality-expression "==" [no-merge-warning] relational-expression')
@glrp.rule('equality-expression : equality-expression "!=" [no-merge-warning] relational-expression')
@glrp.rule('"equality-expression#" : "equality-expression#" "==" [no-merge-warning] "relational-expression#"')
@glrp.rule('"equality-expression#" : "equality-expression#" "!=" [no-merge-warning] "relational-expression#"')
@cxx98
def equality_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1].text())


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser