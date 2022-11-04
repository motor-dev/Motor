"""
constant-expression:
    conditional-expression
"""

import glrp
from ...parser import cxx98, cxx98_merge
from ....ast.expressions import AmbiguousExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('constant-expression : conditional-expression')
@glrp.rule('"constant-expression#" : "conditional-expression#"')
@glrp.rule('constant-expression? : constant-expression')
@cxx98
def constant_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('constant-expression? :')
@cxx98
def constant_expression_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return None


@glrp.merge('constant-expression')
@cxx98_merge
def ambiguous_constant_expression(self, ambiguous_constant_expression, ambiguous_relational_expression):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    return AmbiguousExpression(ambiguous_relational_expression)


@glrp.merge('constant-expression#')
@glrp.merge_result('ambiguous_constant_expression')
@cxx98_merge
def ambiguous_constant_expression_ext(self, ambiguous_constant_expression, ambiguous_relational_expression):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    return AmbiguousExpression(ambiguous_relational_expression)


if TYPE_CHECKING:
    from typing import Any, List
    from ...parser import CxxParser