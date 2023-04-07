"""
conditional-expression:
    logical-or-expression
    logical-or-expression ? expression : assignment-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import ConditionalExpression, ErrorExpression


@glrp.rule('conditional-expression : logical-or-expression')
@glrp.rule('"conditional-expression#" : "logical-or-expression#"')
@cxx98
def conditional_expression_stop(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('conditional-expression : logical-or-expression "?" expression ":" assignment-expression')
@glrp.rule('"conditional-expression#" : "logical-or-expression#" "?" expression ":" "assignment-expression#"')
@cxx98
def conditional_expression(self: CxxParser, p: glrp.Production) -> Any:
    return ConditionalExpression(p[0], p[2], p[4])


@glrp.rule('conditional-expression : logical-or-expression "?" "#error" ":" assignment-expression')
@glrp.rule('"conditional-expression#" : "logical-or-expression#" "?" "#error" ":" "assignment-expression#"')
@glrp.rule('conditional-expression : logical-or-expression "?" expression ":" "#error"')
@glrp.rule('"conditional-expression#" : "logical-or-expression#" "?" expression ":" "#error"')
@glrp.rule('conditional-expression : logical-or-expression "?" "#error" ":" "#error" ')
@glrp.rule('"conditional-expression#" : "logical-or-expression#" "?" "#error" ":" "#error" ')
@cxx98
def conditional_expression_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()
