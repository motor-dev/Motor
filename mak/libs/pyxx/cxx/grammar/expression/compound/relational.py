"""
relational-expression:
    compare-expression
    relational-expression < compare-expression
    relational-expression > compare-expression
    relational-expression <= compare-expression
    relational-expression >= compare-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import BinaryExpression


@glrp.rule('relational-expression : compare-expression')
@glrp.rule('"relational-expression#" : "compare-expression#"')
@cxx98
def relational_expression_stop(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('relational-expression : [no-merge-warning] relational-expression "<" compare-expression')
@glrp.rule('relational-expression : [no-merge-warning] relational-expression ">" compare-expression')
@glrp.rule('relational-expression : [no-merge-warning] relational-expression "<=" compare-expression')
@glrp.rule('relational-expression : [no-merge-warning] relational-expression ">=" compare-expression')
@glrp.rule('"relational-expression#" : [no-merge-warning] "relational-expression#" "<" "compare-expression#"')
@glrp.rule('"relational-expression#" : [no-merge-warning] "relational-expression#" "<=" "compare-expression#"')
@glrp.rule('"relational-expression#" : [no-merge-warning] "relational-expression#" ">=" "compare-expression#"')
@cxx98
def relational_expression(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())
