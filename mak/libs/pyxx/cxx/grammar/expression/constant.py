"""
constant-expression:
    conditional-expression
"""

import glrp
from ...parser import cxx98, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('constant-expression : conditional-expression')
@cxx98
def constant_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('constant-expression? : constant-expression')
@glrp.rule('constant-expression? :')
@cxx98
def constant_expression_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('constant-expression')
@cxx98_merge
def ambiguous_constant_expression(
    self, ambiguous_postfix_expression, ambiguous_new_type_id_constraint, ambiguous_conversion_type_id_constraint,
    id_template
):
    # type: (CxxParser, List[Any], List[Any], List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ...parser import CxxParser