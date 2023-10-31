"""
equality-expression:
    relational-expression
    equality-expression == relational-expression
    equality-expression != relational-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import BinaryExpression


@glrp.rule('equality-expression : [no-merge-warning] relational-expression')
@glrp.rule('"equality-expression#" : [no-merge-warning] "relational-expression#"')
@cxx98
def equality_expression_stop(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('equality-expression : equality-expression "==" [no-merge-warning] relational-expression')
@glrp.rule('equality-expression : equality-expression "!=" [no-merge-warning] relational-expression')
@glrp.rule('"equality-expression#" : "equality-expression#" "==" [no-merge-warning] "relational-expression#"')
@glrp.rule('"equality-expression#" : "equality-expression#" "!=" [no-merge-warning] "relational-expression#"')
@cxx98
def equality_expression(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())
