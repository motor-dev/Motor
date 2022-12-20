"""
relational-expression:
    compare-expression
    relational-expression < compare-expression
    relational-expression > compare-expression
    relational-expression <= compare-expression
    relational-expression >= compare-expression
"""

import glrp
from ....parse import cxx98
from .....ast.expressions import BinaryExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('relational-expression : compare-expression')
@glrp.rule('"relational-expression#" : "compare-expression#"')
@cxx98
def relational_expression_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('relational-expression : [no-merge-warning] relational-expression "<" compare-expression')
@glrp.rule('relational-expression : [no-merge-warning] relational-expression ">" compare-expression')
@glrp.rule('relational-expression : [no-merge-warning] relational-expression "<=" compare-expression')
@glrp.rule('relational-expression : [no-merge-warning] relational-expression ">=" compare-expression')
@glrp.rule('"relational-expression#" : [no-merge-warning] "relational-expression#" "<" "compare-expression#"')
@glrp.rule('"relational-expression#" : [no-merge-warning] "relational-expression#" "<=" "compare-expression#"')
@glrp.rule('"relational-expression#" : [no-merge-warning] "relational-expression#" ">=" "compare-expression#"')
@cxx98
def relational_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1].text())


if TYPE_CHECKING:
    from typing import Any
    from ....parse import CxxParser