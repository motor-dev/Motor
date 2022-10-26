"""
constraint-expression:
    logical-or-expression
"""

import glrp
from ...parser import cxx20, cxx20_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('constraint-expression : logical-or-expression')
@cxx20
def constraint_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('constraint-expression')
@cxx20_merge
def ambiguous_constraint_expression(self, ambiguous_relational_expression):
    # type: (CxxParser, List[Any]) -> None
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ...parser import CxxParser